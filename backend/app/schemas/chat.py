from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SendMessageRequest(BaseModel):
    conversation_id: Optional[int] = None  # None = create a new conversation
    customer_id: int
    content: str


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    sender_name: Optional[str] = None
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    id: int
    customer_id: int
    status: str
    current_handler: str
    assigned_agent_id: Optional[int] = None
    escalation_reason: Optional[str] = None
    escalated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SendMessageResponse(BaseModel):
    conversation_id: int
    user_message: MessageOut
    agent_response: Optional[MessageOut] = None