import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, Float, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    merchant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    merchant_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    card_last_four: Mapped[str | None] = mapped_column(String(4), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    decline_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rule_triggered: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("ix_txn_user_status", "user_id", "status"),
    )
