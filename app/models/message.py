from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Boolean, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender_type: Mapped[str] = mapped_column(String(30), nullable=False)
    sender_name: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False, default="inbound")
    channel: Mapped[str] = mapped_column(String(50), nullable=False, default="web")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="sent")
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    channel_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    detected_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_sheng: Mapped[bool] = mapped_column(Boolean, default=False)
    is_code_switching: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")