from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class SubscriptionCancellation(Base):
    __tablename__ = "subscription_cancellations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    subscription_id: Mapped[int] = mapped_column( ForeignKey("user_subscriptions.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column( ForeignKey("organizations.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="processed", nullable=False)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelled_at: Mapped[datetime] = mapped_column( DateTime(timezone=True), server_default=func.now())
    effective_immediately: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column( DateTime(timezone=True), server_default=func.now())