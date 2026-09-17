from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    channel: str
    status: str
    mode: str
    assigned_to: int | None
    updated_at: datetime


class AdminAgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool


class CreateAgentRequest(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=8)
    role: str = "agent"


class AssignAgentRequest(BaseModel):
    agent_id: int


class SettingsUpdate(BaseModel):
    values: dict = Field(default_factory=dict)


class SettingsOut(BaseModel):
    organization_id: int
    values: dict
