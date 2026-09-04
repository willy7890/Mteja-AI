from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversation(Base):
	__tablename__ = "conversations"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
	customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
	channel: Mapped[str] = mapped_column(String(50), nullable=False)
	status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
	mode: Mapped[str] = mapped_column(String(30), default="ai", nullable=False)
	assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

	messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
