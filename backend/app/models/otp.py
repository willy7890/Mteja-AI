from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class OTPChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class OTPPurpose(str, enum.Enum):
    REGISTRATION = "registration"
    LOGIN = "login"
    RESET_PASSWORD = "reset_password"
    SENSITIVE_ACTION = "sensitive_action"


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    
    code = Column(String(6), nullable=False)
    channel = Column(Enum(OTPChannel), nullable=False)
    purpose = Column(Enum(OTPPurpose), default=OTPPurpose.REGISTRATION, nullable=False)
    
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)

    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired() and self.attempts < self.max_attempts