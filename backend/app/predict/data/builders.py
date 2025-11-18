from typing import Dict, Any, List, Tuple
import numpy as np
from datetime import timedelta
from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.models.rating import AppRatings
from app.predict.data.features import to_date, dow_feats, hash_bow, SeqFeatureConfig, StaticFeatureConfig
from app.predict.core.types import BuildOutput

MAX_RANK = 200
BRAND_KEY = {"free": "rank_a", "paid": "rank_b", "grossing": "rank_c"}

def brand_key(brand: str) -> str:
    k = BRAND_KEY.get((brand or "").lower())
    if not k: raise ValueError("brand must be one of: free, paid, grossing")
    return k

def _rank_of(blob) -> int | None:
    if blob is None:
        return None
    # dict JSON
    if isinstance(blob, dict):
        val = blob.get("ranking")
    else:
        # try JSON string first
        try:
            obj = json.loads(blob)
            val = obj.get("ranking")
        except Exception:
            # maybe it's a plain number string like "123"
            try:
                return int(blob)
            except Exception:
                return None
    try:
        return int(val) if val is not None else None
    except Exception:
        try:
            return int(float(val))
        except Exception:
            return None

async def fetch_partition_rows(session: AsyncSession, *, country: str, device: str, brand: str):
    rk = brand_key(brand)
    stmt = (select(
                AppRatings.app_id, AppRatings.app_name, AppRatings.publisher,
                AppRatings.raw_json, AppRatings.is_ad, AppRatings.rating, AppRatings.rating_num,
                AppRatings.last_release_time, AppRatings.keyword_cover, AppRatings.keyword_cover_top3,
                AppRatings.update_time, getattr(AppRatings, rk)
            )
            .where(AppRatings.country==country, AppRatings.device==device, AppRatings.brand==brand)
            .order_by(asc(AppRatings.app_id), asc(AppRatings.update_time)))
    rs = await session.execute(stmt)
    return rs.all()

def _extract_price(raw_json) -> float:
    if raw_json is None:
        return 0.0
    candidate = None
    if isinstance(raw_json, str):
        try:
            candidate = json.loads(raw_json)
        except Exception:
            # try to extract numeric from string by removing non-digit/non-dot chars
            import re
            s = re.sub(r"[^\d\.]", "", raw_json)
            try:
                return float(s)
            except Exception:
                return 0.0
    else:
        candidate = raw_json
    if isinstance(candidate, dict):
        candidate = candidate.get("appInfo", {}).get("price")
    if candidate is None:
        return 0.0
    if isinstance(candidate, str):
        # strip currency symbols and convert to float
        import re
        s = re.sub(r"[^\d\.]", "", candidate)
        try:
            return float(s)
        except Exception:
            return 0.0
    try:
        return float(candidate)
    except Exception:
        return 0.0

def _by_app(rows) -> Dict[str, List[Any]]:
    by = {}
    for r in rows:
        (app_id, app_name, publisher, raw_json, is_ad, rating, rating_num,
         lastReleaseTime, keyword_cover, keyword_cover_top3, update_time, rank_blob) = r
        price = _extract_price(raw_json)
        by.setdefault(app_id, []).append((update_time, rank_blob, {
            "app_name": app_name, "publisher": publisher,
            "price": price, "is_ad": is_ad,
            "rating": rating, "rating_num": rating_num,
            "lastReleaseTime": lastReleaseTime,
            "kw": keyword_cover, "kw3": keyword_cover_top3
        }))
    return by

def _build_continuous_series(app_rows: List[Any], start, end):
    raw = {}
    last_meta = None
    last_rank = None
    for (ut, rank_blob, meta) in app_rows:
        d = to_date(ut)
        if not d: continue
        last_meta = meta
        if start <= d <= end:
            raw[d] = (_rank_of(rank_blob), meta)
    seq = []
    cur = start
    while cur <= end:
        r, meta = raw.get(cur, (None, last_meta))
        if r is None: r = last_rank
        else: last_rank = r
        seq.append((cur, r, meta))
        cur += timedelta(days=1)
    return seq  # list of (date, rank, meta)

def _seq_feats(seq, cfg: SeqFeatureConfig) -> np.ndarray:
    # per-day features: rank_norm, diff, ma7, dow_sin, dow_cos
    ranks = []
    for (_, r, _) in seq:
        r = r if r else MAX_RANK
        ranks.append(min(MAX_RANK, max(1, r)) / MAX_RANK)
    ranks = np.array(ranks, dtype=np.float32)
    feats = []
    if cfg.use_rank_norm:
        feats.append(ranks)
    if cfg.use_diff:
        diffs = np.concatenate([[0.0], np.diff(ranks)])
        feats.append(diffs)
    if cfg.use_ma7:
        ma7 = np.convolve(ranks, np.ones(7)/7.0, mode="same")
        feats.append(ma7.astype(np.float32))
    if cfg.use_dow:
        dow = np.array([dow_feats(d) for (d,_,_) in seq], dtype=np.float32).T  # [2, T]
        feats.append(dow[0]); feats.append(dow[1])
    return np.stack(feats, axis=1)  # [T, F_seq]

def _parse_rating_num(val) -> float:
    if val is None:
        return 0.0
    # already numeric
    try:
        return float(val)
    except Exception:
        pass
    import re
    s = str(val).strip().replace(',', '')
    m = re.match(r"^([\d\.]+)\s*([a-zA-Z\u4e00-\u9fa5]?)$", s)
    if not m:
        # try to keep only digits and dot
        s2 = re.sub(r"[^\d\.]", "", s)
        try:
            return float(s2) if s2 else 0.0
        except Exception:
            return 0.0
    num, unit = m.group(1), m.group(2).lower()
    try:
        x = float(num)
    except Exception:
        return 0.0
    if unit in ("k",):
        x *= 1e3
    elif unit in ("m",):
        x *= 1e6
    elif unit in ("b",):
        x *= 1e9
    elif unit in ("万",):
        x *= 1e4
    elif unit in ("亿",):
        x *= 1e8
    return float(x)

def _static_vec(meta: Dict[str,Any], at_date, cfg: StaticFeatureConfig) -> np.ndarray:
    cols = []
    price = float(meta.get("price") or 0.0)
    is_ad = 1.0 if meta.get("is_ad") else 0.0
    rating = float(meta.get("rating") or 0.0) / 5.0
    rnum = _parse_rating_num(meta.get("rating_num"))
    rnum = np.log1p(rnum) / 10.0
    lrt = meta.get("lastReleaseTime")
    try:
        from datetime import datetime
        if isinstance(lrt, str):
            lrt = datetime.fromisoformat(lrt)
    except Exception:
        lrt = None
    age = 0.0
    try:
        if hasattr(lrt, "date"):
            age = max(0.0, (at_date - lrt.date()).days / 365.0)
    except Exception:
        age = 0.0

    if cfg.use_price: cols.append(price)
    if cfg.use_is_ad: cols.append(is_ad)
    if cfg.use_rating: cols.append(rating)
    if cfg.use_rating_num_log: cols.append(rnum)
    if cfg.use_age: cols.append(age)
    if cfg.use_keyword_hash:
        bow = hash_bow([meta.get("kw") or "", meta.get("kw3") or ""], cfg.keyword_hash_dim)
        cols.extend(bow.tolist())
    return np.array(cols, dtype=np.float32)

async def build_global_samples(session: AsyncSession, *,
    country: str, device: str, brand: str,
    days: int, lookback: int, horizon: int,
    seq_cfg: SeqFeatureConfig, static_cfg: StaticFeatureConfig
) -> BuildOutput:
    rows = await fetch_partition_rows(session, country=country, device=device, brand=brand)
    if not rows: 
        return {"X_seq": np.zeros((0,lookback,1),dtype=np.float32),
                "X_static": np.zeros((0,1),dtype=np.float32),
                "y": np.zeros((0,horizon),dtype=np.float32),
                "ids": [], "dates": []}
    end = to_date(rows[-1][10])
    start = end - timedelta(days=days-1)

    by_app = _by_app(rows)
    Xs, Xt, Y, ids, dates = [], [], [], [], []
    for app_id, app_rows in by_app.items():
        seq = _build_continuous_series(app_rows, start, end)
        if len(seq) < lookback + horizon + 5: 
            continue
        F = _seq_feats(seq, seq_cfg)  # [T, F_seq]
        T = len(seq)
        for i in range(lookback, T - horizon + 1):
            win = seq[i-lookback:i]
            x_seq = F[i-lookback:i]  # [L, F_seq]
            # 静态用窗口末日元信息
            _, _, meta = win[-1]
            x_static = _static_vec(meta, win[-1][0], static_cfg)
            y = []
            for k in range(horizon):
                r = seq[i+k][1] or MAX_RANK
                y.append(min(MAX_RANK, max(1, r))/MAX_RANK)
            Xs.append(x_seq.astype(np.float32))
            Xt.append(x_static.astype(np.float32))
            Y.append(np.array(y, dtype=np.float32))
            ids.append(app_id)
            dates.append(win[-1][0])

    if not Xs:
        return {"X_seq": np.zeros((0,lookback,1),dtype=np.float32),
                "X_static": np.zeros((0,1),dtype=np.float32),
                "y": np.zeros((0,horizon),dtype=np.float32),
                "ids": [], "dates": []}
    return {"X_seq": np.stack(Xs), "X_static": np.stack(Xt), "y": np.stack(Y), "ids": ids, "dates": dates}
