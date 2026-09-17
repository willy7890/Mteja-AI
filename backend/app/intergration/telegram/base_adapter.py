from abc import ABC, abstractmethod
from typing import Any


class ChannelAdapter(ABC):
  
    channel_name: str

    @abstractmethod
    async def send(self, to: str, content: str, **kwargs):
       
       pass
    @abstractmethod   
    def normalize_incoming(self, raw_payload: dict) -> dict:
        pass