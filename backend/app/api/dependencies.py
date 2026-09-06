from functools import lru_cache
from typing import Dict

from app.services.message import MessageService
from app.intergration.telegram.adapter import TelegramAdapter

from app.intergration.telegram.adapter import TelegramAdapter
from app.intergration.email.adapter import EmailAdapter
from app.intergration.sms.adapter import SmsAdapter


@lru_cache()
def get_adapters() -> Dict[str, object]:
    """
    Sajili adapters zote hapa.
    Ongeza channel mpya = ongeza line moja tu.
    """
    return {
        "telegram": TelegramAdapter(),
         "email": EmailAdapter(),
         "sms": SmsAdapter(),
    
    }


def get_message_service():
    
    adapters = get_adapters()
    return MessageService(adapters=adapters)




@lru_cache()
def get_adapters() -> Dict[str, object]:
    return {
        "telegram": TelegramAdapter(),
        "email": EmailAdapter(),
        "sms": SmsAdapter(),
    }
