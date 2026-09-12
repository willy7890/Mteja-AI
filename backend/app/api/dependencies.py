from functools import lru_cache
from typing import Dict

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
