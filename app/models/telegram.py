from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TelegramLink(Base):
    __tablename__ = "telegram_links"

    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(String, unique=True, index=True, nullable=False)
    telegram_username = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    linked_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User")


class TelegramSession(Base):
    __tablename__ = "telegram_sessions"

    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(String, unique=True, index=True, nullable=False)
    state = Column(String, nullable=False, default="idle")
    temp_data = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)