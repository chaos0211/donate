# app/services/rating_service.py
from typing import List, Dict, Any
from sqlalchemy.dialects.mysql import insert
from app.db.base import SessionLocal
from app.db.models.rating import AppRatings

def upsert_app_ratings(records: List[Dict[str, Any]]) -> int:
    if not records:
        return 0
    with SessionLocal() as db:
        # 构建 INSERT ... ON DUPLICATE KEY UPDATE
        # 建议你在 app_ratings 上加一个唯一索引：
        # UNIQUE (chart_date, country, device, app_id)
        stmt = insert(AppRatings).values(records)
        update_cols = {c.name: stmt.inserted[c.name] for c in AppRatings.__table__.columns if c.name not in ("id",)}
        ondup = stmt.on_duplicate_key_update(**update_cols)
        result = db.execute(ondup)
        db.commit()
        return result.rowcount or len(records)