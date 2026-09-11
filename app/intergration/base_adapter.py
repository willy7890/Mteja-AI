from abc import ABC, abstractmethod
from typing import Any

from app.services.messaging_window import (
    assert_can_send_free_form,
    record_customer_message,
    MessagingWindowClosedError,
)

class ChannelAdapter(ABC):
     channel_name: str
     @abstractmethod
     async def send(self, to: str, content: str, **kwargs) :
           
      @abstractmethod
      def normalize_incoming(self, raw_payload: dict):
        pass
        
        
        
class WhatsAppAdapter(ChannelAdapter):

  async def handle_incoming_message(self, db, conversation, payload):
       
         await record_customer_message(db, conversation)
       

async def send_free_form(self, db, conversation, text: str):
        try:
            
            await assert_can_send_free_form(db, conversation)
        except MessagingWindowClosedError:
          
            return await self.send_template_fallback(db, conversation)

       
        return await self._send_to_meta_api(conversation, text)

        async def send_template_fallback(self, db, conversation):
        
         raise NotImplementedError("Template-based sending not yet implemented")