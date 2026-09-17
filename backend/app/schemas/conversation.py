from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# --- Message Schemas ---
class MessageBase(BaseModel):
    content: str
    sender_type: str  # "customer", "agent", or "ai"


class MessageCreate(BaseModel):
    content: str
    sender_type: str = "customer"


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Handoff & Escalation Request Schemas ---
class EscalateRequest(BaseModel):
    reason: str = "manual_takeover"
    agent_id: Optional[int] = None


# --- Conversation Schemas ---
class ConversationBase(BaseModel):
    status: str
    current_handler: str
    assigned_agent_id: Optional[int] = None


class ConversationCreate(BaseModel):
    customer_id: int
    organization_id: int


class ConversationResponse(ConversationBase):
    id: int
    customer_id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)