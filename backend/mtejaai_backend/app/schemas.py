from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ContactCreate(BaseModel):
    name: str = Field(..., examples=["Amina J."])
    channel_id: str = Field(..., description="Phone number or email address", examples=["+255712345678"])


class Contact(BaseModel):
    id: int
    name: str
    channel_id: str
    stage: Literal["new", "in_conversation", "escalated", "filtered"] = "new"
    created_at: datetime


class MessageIn(BaseModel):
    channel: Literal["sms", "email"] = "sms"
    text: str = Field(..., examples=["Hi, what time do you open tomorrow?"])


class Message(BaseModel):
    id: int
    contact_id: int
    channel: str
    direction: Literal["in", "out"]
    text: str
    created_at: datetime


class ClassifyResult(BaseModel):
    classification: Literal["customer", "non_customer"]
    reason: str
    escalate: bool
    escalate_reason: Optional[str] = None
    reply: Optional[str] = None
    mock_mode: bool = Field(..., description="True if this ran on the offline fallback logic, not a live model call")


class MessageResponse(BaseModel):
    contact: Contact
    inbound_message: Message
    classification: ClassifyResult
    outbound_message: Optional[Message] = None


class Task(BaseModel):
    id: int
    contact_id: int
    reason: str
    status: Literal["open", "resolved"] = "open"
    created_at: datetime


class ProductCreate(BaseModel):
    name: str = Field(..., examples=["Basic Haircut"])
    details: str = Field(..., examples=["Includes wash and style, 30 minutes"])
    price: float = Field(..., examples=[15000])
    quantity: int = Field(..., examples=[999])
    image_url: Optional[str] = Field(None, examples=["https://example.com/haircut.jpg"])


class Product(BaseModel):
    id: int
    name: str
    details: str
    price: float
    quantity: int
    image_url: Optional[str] = None


class DashboardSummary(BaseModel):
    total_messages: int
    total_leads: int
    escalated: int
    filtered: int
    mock_mode: bool
