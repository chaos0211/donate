import os
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Tuple, List

import numpy as np
import torch
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.rating import AppRatings
from app.predict.data.features import SeqFeatureConfig, StaticFeatureConfig
from app.predict.data.builders import build_global_samples
from app.predict.io.paths import global_model_path
from app.predict.io.save_load import load_bundle, build_model_from_meta

# -----------------------------
# Helpers for model path resolve
# -----------------------------
APP_ROOT = Path(__file__).resolve().parents[3]  # backend/app
MODELS_ROOT = APP_ROOT / 'predict' / 'models'
UPLOAD_DIR = MODELS_ROOT / 'upload'
TRAINED_LSTM_DIR = MODELS_ROOT / 'lstm'
LEGACY_LSTM_DIR = APP_ROOT.parent / 'models' / 'lstm'  # backend/models/lstm


def _default_model_name(country: str, device: str, brand: str, algo: str = 'lstm') -> str:
    return f"global_{country}_{device}_{brand}_{algo}.pt"


def _resolve_model_path(*, country: str, device: str, brand: str,
                        model_source: Optional[str], model_name: Optional[str],
                        algo: str = 'lstm') -> Optional[Path]:
    """Resolve a model file path according to frontend contract.
    - If model_source and model_name are provided: use the specific directory.
    - Else try default filename with preference: upload -> trained -> legacy.
    Returns None if not found.
    """
    candidates: List[Path] = []

    # 1) Explicit selection
    if model_source and model_name:
        if model_source == 'upload':
            candidates.append(UPLOAD_DIR / model_name)
        elif model_source == 'trained':
            candidates.append(TRAINED_LSTM_DIR / model_name)
        elif model_source == 'legacy':
            candidates.append(LEGACY_LSTM_DIR / model_name)

    # 2) Fallback by convention name
    fname = model_name or _default_model_name(country, device, brand, algo)
    candidates.extend([
        UPLOAD_DIR / fname,
        TRAINED_LSTM_DIR / fname,
        LEGACY_LSTM_DIR / fname,
    ])

    for p in candidates:
        if p and p.exists() and p.is_file():
            return p
    return None


# -----------------------------
# Data helpers
# -----------------------------
async def _latest_chart_date(session: AsyncSession, *, country: str, device: str, brand: str) -> Optional[date]:
    stmt = select(func.max(AppRatings.chart_date)).where(
        AppRatings.country == country,
        AppRatings.device == device,
        AppRatings.brand == brand,
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def _fetch_rankc_series(session: AsyncSession, *, country: str, device: str, brand: str,
                              app_id: str, upto: date, genre: Optional[str]) -> List[Tuple[date, Optional[int]]]:
    """Fetch (chart_date, ranking) from rank_c JSON for an app up to cutoff date.
    If genre is None, use the genre observed at the cutoff date row (or latest available).
    """
    # First, determine genre when missing: pick latest genre for this app up to cutoff
    g = genre
    if g is None:
        stmt_g = (
            select(func.json_extract(AppRatings.rank_c, '$.genre'))
            .where(AppRatings.country == country)
            .where(AppRatings.device == device)
            .where(AppRatings.brand == brand)
            .where(AppRatings.app_id == app_id)
            .where(AppRatings.chart_date <= upto)
            .order_by(AppRatings.chart_date.desc())
            .limit(1)
        )
        r = await session.execute(stmt_g)
        val = r.scalar_one_or_none()
        if isinstance(val, str) and val:
            g = val.strip('"')  # MySQL json_extract may return quoted string

    # Now fetch the time series filtered by that genre (if present)
    stmt = (
        select(AppRatings.chart_date,
               func.json_extract(AppRatings.rank_c, '$.genre'),
               func.json_extract(AppRatings.rank_c, '$.ranking'))
        .where(AppRatings.country == country)
        .where(AppRatings.device == device)
        .where(AppRatings.brand == brand)
        .where(AppRatings.app_id == app_id)
        .where(AppRatings.chart_date <= upto)
        .order_by(AppRatings.chart_date.asc())
    )
    rows = (await session.execute(stmt)).all()

    out: List[Tuple[date, Optional[int]]] = []
    for d, gval, rval in rows:
        # Normalize JSON_EXTRACT outputs
        gval_s = None
        if gval is not None:
            gval_s = gval if isinstance(gval, str) else str(gval)
            gval_s = gval_s.strip('"')
        if g is not None and gval_s is not None and gval_s != g:
            # skip rows whose rank_c.genre doesn't match target genre
            continue
        # ranking may be None
        if rval is None:
            out.append((d, None))
        else:
            # json_extract may return string/decimal; coerce to int safely
            try:
                rv = int(str(rval).strip('"'))
            except Exception:
                rv = None
            out.append((d, rv))

    return out


def _pad_and_fill_series(series: List[Tuple[date, Optional[int]]], *, cutoff: date, lookback: int,
                         max_rank: int = 200) -> List[int]:
    """Build a dense daily series ending at cutoff of length lookback.
    Steps: make daily index, map known values, forward-fill, left-pad with last known (or max_rank when none).
    Returns a python list of length lookback.
    """
    # Map existing values
    m = {d: v for d, v in series if d is not None}
    vals: List[int] = []
    last = None
    for i in range(lookback - 1, -1, -1):  # from oldest to newest
        day = cutoff - timedelta(days=i)
        v = m.get(day, None)
        if v is None:
            v = last
        if v is None:
            v = max_rank
        vals.append(int(v))
        last = v
    return vals


# -----------------------------
# Public API (called by routers)
# -----------------------------
async def forecast_global(session: AsyncSession, *, country: str, device: str, brand: str,
                          app_id: str, lookback: int, horizon: int,
                          model_source: Optional[str] = None, model_name: Optional[str] = None,
                          genre: Optional[str] = None) -> List[int]:
    """
    Real prediction using a trained model bundle (.pt) with meta.
    - Model selection: prefer explicit (model_source, model_name); else try upload->trained->legacy by convention name.
    - cutoff_date = latest chart_date in (country, device, brand).
    - Target series = rank_c.ranking under the provided (or inferred) genre.
    - History shortfall is handled by forward-fill and left-padding to meet lookback.
    Returns list of length `horizon` (predicted ranks for T+1..T+horizon).
    """
    # 1) Resolve cutoff date
    cutoff = await _latest_chart_date(session, country=country, device=device, brand=brand)
    if cutoff is None:
        return []

    # 2) Resolve model path
    path = _resolve_model_path(country=country, device=device, brand=brand,
                               model_source=model_source, model_name=model_name, algo='lstm')
    if path is None:
        # As a last resort, keep legacy resolver
        path = global_model_path(country, device, brand, 'lstm')
        if not Path(path).exists():
            return []

    # 3) Load bundle & model
    bundle = load_bundle(path)
    meta = bundle.get("meta", {})
    model = build_model_from_meta(meta)
    model.load_state_dict(bundle["state_dict"])
    model.eval()

    # Helper: infer sequence input dimension
    def _infer_seq_dim(meta_dict, mdl) -> int:
        # 1) prefer meta hint
        val = meta_dict.get('seq_input_dim')
        try:
            if val is not None:
                return int(val)
        except Exception:
            pass
        # 2) try common module names
        for attr in ('lstm', 'rnn', 'gru'):
            sub = getattr(mdl, attr, None)
            if sub is not None and hasattr(sub, 'input_size'):
                try:
                    return int(sub.input_size)
                except Exception:
                    continue
        # 3) safe fallback
        return 1

    # 4) Try builder path first (keeps compatibility with your current pipeline)
    try:
        cfg_s = SeqFeatureConfig()
        cfg_t = StaticFeatureConfig()
        out = await build_global_samples(
            session,
            country=country, device=device, brand=brand,
            days=max(lookback + horizon + 60, 120),
            lookback=lookback, horizon=horizon,
            seq_cfg=cfg_s, static_cfg=cfg_t,
            cutoff_date=cutoff  # if builder supports it; otherwise it will ignore
        )
        x_seq, x_static, ids = out["X_seq"], out["X_static"], out["ids"]
        idx = [i for i, u in enumerate(ids) if u == app_id]
        if idx:
            i = idx[-1]
            xs = torch.tensor(x_seq[i:i + 1], dtype=torch.float32)
            xt = torch.tensor(x_static[i:i + 1], dtype=torch.float32)
            with torch.no_grad():
                yhat = model(xs, xt)[0].numpy().tolist()
            max_rank = int(meta.get('max_rank', 200))
            preds = [max(1, int(round(p * max_rank))) for p in yhat[:horizon]]
            return preds
    except Exception:
        # fall back to manual series path
        pass

    # 5) Fallback: build rank_c.ranking series for the app/genre and run through seq-only input
    series = await _fetch_rankc_series(session, country=country, device=device, brand=brand,
                                       app_id=app_id, upto=cutoff, genre=genre)
    if not series:
        return []

    seq_vals = _pad_and_fill_series(series, cutoff=cutoff, lookback=lookback, max_rank=200)
    # normalize to 0-1 as training assumed rank/200
    max_rank = int(meta.get('max_rank', 200))
    seq_norm = np.array(seq_vals, dtype=np.float32) / float(max_rank)

    # Build x_seq to match model's expected seq feature dimension
    seq_dim = _infer_seq_dim(meta, model)
    # Debug print for sequence input dimension
    # try:
    #     print("[predict.debug] seq_input_dim(meta)=", meta.get('seq_input_dim'),
    #           " inferred=", seq_dim)
    # except Exception:
    #     pass
    if seq_dim < 1:
        seq_dim = 1
    x_seq_np = np.zeros((1, lookback, seq_dim), dtype=np.float32)
    # channel 0 = normalized rank; other channels left as zeros
    x_seq_np[0, :, 0] = seq_norm
    xs = torch.tensor(x_seq_np, dtype=torch.float32)

    # static features per meta/model (infer when meta is missing)
    def _infer_static_dim(meta_dict, mdl) -> int:
        # 1) prefer meta hint
        val = meta_dict.get('static_input_dim')
        try:
            if val is not None:
                return int(val)
        except Exception:
            pass
        # 2) try to probe model: expect a Sequential named `static_mlp` whose first layer is Linear
        mlp = getattr(mdl, 'static_mlp', None)
        try:
            import torch.nn as nn  # local import to avoid top-level dependency
            if isinstance(mlp, nn.Sequential) and len(mlp) > 0:
                first = mlp[0]
                if isinstance(first, nn.Linear) and hasattr(first, 'in_features'):
                    return int(first.in_features)
        except Exception:
            pass
        # 3) safe fallback: 0 (no static)
        return 0

    static_dim = _infer_static_dim(meta, model)
    # try:
    #     print("[predict.debug] static_input_dim(meta)=", meta.get('static_input_dim'), " inferred=", static_dim)
    # except Exception:
    #     pass

    xt = torch.zeros((1, static_dim), dtype=torch.float32) if static_dim > 0 else torch.zeros((1, 0), dtype=torch.float32)

    with torch.no_grad():
        out = model(xs, xt)
        # Some models return (y, aux), ensure we pick the tensor
        if isinstance(out, (list, tuple)):
            out = out[0]
        yhat = out.detach().cpu().numpy().reshape(-1).tolist()
    if len(yhat) < horizon:
        last = yhat[-1] if len(yhat) > 0 else 1.0 / float(max_rank)
        yhat = yhat + [last] * (horizon - len(yhat))

    preds = [max(1, int(round(p * max_rank))) for p in yhat[:horizon]]
    return preds
