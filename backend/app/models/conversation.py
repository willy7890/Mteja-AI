from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HandlerType(str, Enum):
    AI = "ai"
    HUMAN = "human"


class ConversationStatus(str, Enum):
    OPEN = "open"
    ACTIVE = "active"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Channel used for this conversation
    # e.g. telegram, whatsapp, sms, web
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # External ID of the customer on the channel
    # e.g. Telegram chat/user ID
    external_participant_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    current_handler: Mapped[str] = mapped_column(
        String(20),
        default=HandlerType.AI.value,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=ConversationStatus.OPEN.value,
        nullable=False,
    )

    assigned_agent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    escalation_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    escalated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    last_customer_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    whatsapp_window_open: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    escalation_logs = relationship(
        "EscalationLog",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
