from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
	__tablename__ = "messages"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	sender_type: Mapped[str] = mapped_column(String(30), nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

	conversation = relationship("Conversation", back_populates="messages")
