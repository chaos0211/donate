# app/db/models/user.py
from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    username = Column(String(50), unique=True, index=True, nullable=False)

    # 密码摘要（SHA1）
    password_sha1 = Column(String(100), nullable=False)

    # 用户角色：admin / org / donor
    role = Column(String(20), default="donor", nullable=False)

    # 用户状态：active / disabled
    status = Column(String(20), default="active", nullable=False)

    # 创建 & 更新
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)