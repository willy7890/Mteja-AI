from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict




class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="TZS", max_length=10)
    provider: str = Field(..., min_length=2, max_length=50)


class PaymentCreate(PaymentBase):
    subscription_id: int



class PaymentStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        pattern="^(pending|successful|failed|cancelled)$"
    )
    provider_reference: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = None



class PaymentResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    subscription_id: int
    amount: Decimal
    currency: str
    provider: str
    transaction_reference: str
    provider_reference: Optional[str] = None
    status: str
    notes: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentListResponse(BaseModel):
    items: List[PaymentResponse]
    total: int



class PaymentWebhookPayload(BaseModel):
    transaction_reference: str
    provider_reference: Optional[str] = None
    status: str = Field(..., pattern="^(successful|failed|cancelled)$")
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    message: Optional[str] = None