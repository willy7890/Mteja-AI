<<<<<<< HEAD
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from sqlalchemy import DateTime, ForeignKey, Integer, String
=======
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Boolean, func, JSON
>>>>>>> origin/develop
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

<<<<<<< HEAD
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Standardized state fields across system
    current_handler: Mapped[str] = mapped_column(String(20), default=HandlerType.AI.value, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=ConversationStatus.OPEN.value, nullable=False)
    assigned_agent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Escalation & Resolution audit fields
    escalation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    escalated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    escalation_logs = relationship("EscalationLog", back_populates="conversation", cascade="all, delete-orphan")
=======
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    mode: Mapped[str] = mapped_column(String(30), default="ai", nullable=False)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    external_participant_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True, default=dict)
    last_customer_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    whatsapp_window_open: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
>>>>>>> origin/develop
