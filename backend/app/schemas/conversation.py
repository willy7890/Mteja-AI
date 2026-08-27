from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageCreate(BaseModel):
    content: str
    sender_type: str  # 'customer', 'agent', 'ai'


class ConversationCreate(BaseModel):
    customer_id: int
    channel: str
    status: str = "open"

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    content: str
    sender_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    organization_id: int
    customer_id: int
    channel: str  # 'whatsapp', 'instagram', 'tiktok'
    status: str   # 'open', 'pending', 'closed'
    mode: str     # 'ai', 'human'
    assigned_to: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None

class AssignRequest(BaseModel):
    agent_id: int