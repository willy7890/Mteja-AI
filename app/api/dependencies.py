from functools import lru_cache
from typing import Dict
from fastapi import HTTPException, status

from dataclasses import dataclass

from app.intergration.email.adapter import EmailAdapter
from app.intergration.meta_adapter import MetaAdapter
from app.intergration.sms.adapter import SmsAdapter
from app.intergration.telegram.adapter import TelegramAdapter
from app.services.message import MessageService


@lru_cache()
def get_adapters() -> Dict[str, object]:
    return {
        "telegram": TelegramAdapter(),
        "email": EmailAdapter(),
        "sms": SmsAdapter(),
        "whatsapp": MetaAdapter("whatsapp"),
        "facebook": MetaAdapter("facebook"),
        "instagram": MetaAdapter("instagram"),
    }


def get_message_service():
    return MessageService(adapters=get_adapters())



@dataclass
class CurrentUser:
    """Lightweight view of the authenticated user, used throughout the API."""
    id: str
    org_id: str
    role: str
    email: str | None = None
 
 
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
 

