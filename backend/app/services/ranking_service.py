

from typing import List, Dict, Any
import json
from sqlalchemy import text
from app.db.base import SessionLocal

# -----------------------------
# Qimai Rankings Upsert Service
# -----------------------------
# 职责：提供面向爬虫/任务层的批量写入接口；
#      爬虫只管抓，CRUD 统一在此集中处理。
# 说明：依赖数据库中存在唯一键：
#   UNIQUE KEY uq_daily_idx (chart_date, brand_id, genre, `index`, country, device)
# 与模型表 app.db.models.ranking.AppStoreRankingDaily 对应。

UPSERT_SQL = text(
    """
    INSERT INTO appstore_rankings_daily (
      chart_date, brand_id, country, device, genre, app_genre,
      `index`, ranking, `change`, is_ad,
      app_id, app_name, subtitle, icon_url, publisher, publisher_id, price,
      file_size_bytes, file_size_mb, continuous_first_days,
      source, raw_json, crawled_at
    ) VALUES (
      :chart_date, :brand_id, :country, :device, :genre, :app_genre,
      :index, :ranking, :change, :is_ad,
      :app_id, :app_name, :subtitle, :icon_url, :publisher, :publisher_id, :price,
      :file_size_bytes, :file_size_mb, :continuous_first_days,
      :source, :raw_json, NOW()
    )
    ON DUPLICATE KEY UPDATE
      ranking=VALUES(ranking),
      `change`=VALUES(`change`),
      is_ad=VALUES(is_ad),
      app_name=VALUES(app_name),
      subtitle=VALUES(subtitle),
      icon_url=VALUES(icon_url),
      publisher=VALUES(publisher),
      publisher_id=VALUES(publisher_id),
      price=VALUES(price),
      file_size_bytes=VALUES(file_size_bytes),
      file_size_mb=VALUES(file_size_mb),
      continuous_first_days=VALUES(continuous_first_days),
      app_genre=VALUES(app_genre),
      source=VALUES(source),
      raw_json=VALUES(raw_json),
      updated_at=NOW();
    """
)


def _to_int(x):
    try:
        return int(x)
    except Exception:
        return None


def _to_dec(x):
    try:
        return float(x)
    except Exception:
        return None


def _build_row(date_str: str, brand_id: int, genre: int, item: Dict[str, Any]) -> Dict[str, Any]:
    """将七麦 list 单条记录扁平化为写库所需的行字典。"""
    app = (item.get("appInfo") or {})
    klass = (item.get("class") or {})

    file_size_bytes = _to_int(app.get("file_size"))  # 原始为字节
    file_size_mb = round((file_size_bytes or 0) / (1024.0 * 1024.0), 2)

    return {
        "chart_date": date_str,
        "brand_id": brand_id,
        "country": app.get("country") or "cn",
        "device": "iphone",
        "genre": genre,
        "app_genre": item.get("appGenre") or item.get("genre"),
        "index": item.get("index"),
        "ranking": _to_int(klass.get("ranking")),
        "change": item.get("change"),
        "is_ad": 1 if item.get("is_ad") else 0,
        "app_id": app.get("appId"),
        "app_name": app.get("appName"),
        "subtitle": app.get("subtitle"),
        "icon_url": app.get("icon"),
        "publisher": app.get("publisher"),
        "publisher_id": item.get("publisher_id"),
        "price": _to_dec(app.get("price")),
        "file_size_bytes": file_size_bytes,
        "file_size_mb": file_size_mb,
        "continuous_first_days": _to_int(app.get("continuousFirstDays")),
        "source": "qimai",
        "raw_json": json.dumps(item, ensure_ascii=False),
    }


def upsert_page(date_str: str, brand_id: int, genre: int, items: List[Dict[str, Any]]) -> int:
    """
    批量写入（幂等）：同一天/同榜单/同分类/同国家/同设备/同 index 冲突则更新。
    :return: 成功写入/更新的记录数
    """
    if not items:
        return 0

    rows = [_build_row(date_str, brand_id, genre, it) for it in items]

    db = SessionLocal()
    try:
        db.execute(UPSERT_SQL, rows)
        db.commit()
        return len(rows)
    finally:
        db.close()