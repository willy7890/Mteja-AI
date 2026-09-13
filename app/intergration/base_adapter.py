from abc import ABC, abstractmethod
from typing import Any


class ChannelAdapter(ABC):
    """
    Base class kwa channel adapters zote (Telegram, Email, SMS, WhatsApp, n.k.).
    
    Strong separation:
    - Adapter = Transport only
    - MessageService = Conversation logic
    """

    channel_name: str

    @abstractmethod
    async def send(self, to: str, content: str, **kwargs) -> dict:
        """
        Tuma ujumbe.
        Lazima irudishe:
        {
            "external_id": str | None,
            "status": "sent" | "failed",
            "error": str | None
        }
        """
        pass

    @abstractmethod
    def normalize_incoming(self, raw_payload: dict) -> dict:
        """
        Badilisha payload ghafi → standard format.
        
        Lazima irudishe:
        {
            "external_id": str,
            "from": str,                    # external participant id
            "content": str,
            "channel_metadata": dict,
            "timestamp": str | None         # ISO format
        }
        """
        pass