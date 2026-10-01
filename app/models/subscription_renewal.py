from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class SubscriptionRenewal(Base):
    __tablename__ = "subscription_renewals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    subscription_id: Mapped[int] = mapped_column(ForeignKey("user_subscriptions.id"), nullable=False, index=True )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column( ForeignKey("organizations.id"), nullable=False, index=True )

    payment_id: Mapped[int | None] = mapped_column(ForeignKey("payments.id"), nullable=True, index=True )

    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    previous_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    new_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="TZS", nullable=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column( DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column( DateTime(timezone=True), server_default=func.now(), onupdate=func.now())