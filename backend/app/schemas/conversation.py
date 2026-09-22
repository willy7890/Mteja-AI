from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


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


class MessageCreate(BaseModel):
    sender_type: str
    content: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    sender_name: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


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
    channel: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = Field(default_factory=list)

    model_config = {
        "from_attributes": True
    }


class AssignRequest(BaseModel):
    agent_id: int


class EscalateRequest(BaseModel):
    reason: str
    agent_id: Optional[int] = None