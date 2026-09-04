from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    conversation_id: Optional[int] = None  
    customer_id: int
    content: str
    channel: str = "web"


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    sender_name: Optional[str]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: int
    customer_id: int
    channel: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SendMessageResponse(BaseModel):
    conversation_id: int
    user_message: MessageOut
    agent_response: MessageOut