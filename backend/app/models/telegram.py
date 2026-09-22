from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class TelegramLink(Base):
    __tablename__ = "telegram_links"

    id = Column(Integer, primary_key=True, index=True)

    # Which Telegram bot/integration this chat belongs to
    integration_id = Column(
        Integer,
        ForeignKey("channel_integrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    telegram_chat_id = Column(String, nullable=False, index=True)
    telegram_username = Column(String, nullable=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    linked_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    integration = relationship("ChannelIntegration")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "integration_id",
            "telegram_chat_id",
            name="uq_telegram_link_integration_chat",
        ),
    )


class TelegramSession(Base):
    __tablename__ = "telegram_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Which Telegram bot/integration owns this session
    integration_id = Column(
        Integer,
        ForeignKey("channel_integrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    telegram_chat_id = Column(String, nullable=False, index=True)

    state = Column(
        String,
        nullable=False,
        default="idle",
    )

    temp_data = Column(
        JSON,
        default=dict,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    integration = relationship("ChannelIntegration")

    __table_args__ = (
        UniqueConstraint(
            "integration_id",
            "telegram_chat_id",
            name="uq_telegram_session_integration_chat",
        ),
    )