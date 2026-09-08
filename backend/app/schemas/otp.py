from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class OTPChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"


class OTPPurpose(str, Enum):
    REGISTRATION = "registration"
    LOGIN = "login"
    RESET_PASSWORD = "reset_password"


class SendOTPRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    channel: OTPChannel
    purpose: OTPPurpose = OTPPurpose.REGISTRATION


class VerifyOTPRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    code: str = Field(..., min_length=6, max_length=6)
    purpose: OTPPurpose = OTPPurpose.REGISTRATION


class OTPResponse(BaseModel):
    message: str
    expires_in: int = 600 