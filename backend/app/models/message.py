
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Boolean, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.core.database import Base


class SenderType(str, Enum):
    CUSTOMER = "customer"
    AI = "ai"
    AGENT = "agent"
    SYSTEM = "system"


def resolve_sender_name(
    sender_type: str,
    user_name: Optional[str] = None,
    agent_name: Optional[str] = None,
) -> str:
    """Helper to auto-generate or enforce valid sender_name based on sender_type."""
    if sender_type == SenderType.CUSTOMER or sender_type == "customer":
        return user_name or "Customer"
    elif sender_type == SenderType.AI or sender_type == "ai":
        return agent_name or "AI Assistant"
    elif sender_type == SenderType.AGENT or sender_type == "agent":
        return user_name or agent_name or "Support Agent"
    elif sender_type == SenderType.SYSTEM or sender_type == "system":
        return "System"
    return user_name or "Unknown"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)
    sender_name: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    conversation = relationship("Conversation", back_populates="messages")

    @validates("content")
    def validate_content(self, key, content: str) -> str:
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")
        return content.strip()

    @validates("sender_type")
    def validate_sender_type(self, key, sender_type: str) -> str:
        allowed = {s.value for s in SenderType}
        if sender_type not in allowed:
            raise ValueError(f"Invalid sender_type: '{sender_type}'. Must be one of {allowed}")
        return sender_type

    @validates("sender_name")
    def validate_sender_name(self, key, sender_name: Optional[str]) -> str:
        if not sender_name or not sender_name.strip():
            raise ValueError("sender_name is required")
        return sender_name.strip()
