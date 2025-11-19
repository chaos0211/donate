from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum, Index
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class DonationStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_name = Column(String(100), nullable=False, index=True)
    donor_email = Column(String(100), nullable=True, index=True)
    recipient = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="CNY")
    message = Column(Text, nullable=True)
    status = Column(Enum(DonationStatus), nullable=False, default=DonationStatus.PENDING, index=True)
    transaction_hash = Column(String(64), nullable=True, unique=True, index=True)
    block_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('idx_donation_status_date', 'status', 'created_at'),
        Index('idx_donation_amount_date', 'amount', 'created_at'),
    )