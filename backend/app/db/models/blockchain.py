from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Index
from sqlalchemy.sql import func
from app.db.base import Base


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    index = Column(Integer, unique=True, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data = Column(Text, nullable=False)  # JSON字符串存储交易数据
    previous_hash = Column(String(64), nullable=False, index=True)
    hash = Column(String(64), unique=True, nullable=False, index=True)
    nonce = Column(Integer, nullable=False, default=0)
    difficulty = Column(Integer, nullable=False, default=4)

    __table_args__ = (
        Index('idx_block_timestamp', 'timestamp'),
        Index('idx_block_hash_prev', 'hash', 'previous_hash'),
    )