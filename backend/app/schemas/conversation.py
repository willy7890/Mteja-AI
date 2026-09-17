from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# --- Message Schemas ---
class MessageBase(BaseModel):
    content: str
<<<<<<< HEAD
    sender_type: str  # "customer", "agent", or "ai"
=======
    sender_type: str = "customer"  # 'customer', 'agent', 'ai'
    sender_name: Optional[str] = None
>>>>>>> origin/develop


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

<<<<<<< HEAD
    model_config = ConfigDict(from_attributes=True)
=======
class AssignRequest(BaseModel):
    agent_id: int


class HandoffRequest(BaseModel):
    reason: str = "Manual handoff"
    agent_id: Optional[int] = None


class HandoffStatusResponse(BaseModel):
    conversation_id: int
    mode: str
    status: str
    assigned_to: Optional[int] = None
    handoff_reason: Optional[str] = None
    handed_off_at: Optional[datetime] = None


class ReturnToAIRequest(BaseModel):
    reason: str = "Returned to AI"
>>>>>>> origin/develop
