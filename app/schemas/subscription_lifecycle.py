from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ======================
# Cancellation
# ======================

class CancelSubscriptionRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)
    effective_immediately: bool = False


class CancellationResponse(BaseModel):
    id: int
    subscription_id: int
    user_id: int
    organization_id: int
    status: str
    reason: Optional[str] = None
    cancelled_at: datetime
    effective_immediately: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======================
# Renewal
# ======================

class RenewSubscriptionRequest(BaseModel):
    provider: str = Field(..., min_length=2, max_length=50)
    # amount inaweza kuchukuliwa kutoka plan, lakini tunaiacha optional
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: str = Field(default="TZS", max_length=10)


class RenewalResponse(BaseModel):
    id: int
    subscription_id: int
    user_id: int
    organization_id: int
    payment_id: Optional[int] = None
    status: str
    previous_end_date: Optional[datetime] = None
    new_end_date: Optional[datetime] = None
    amount: Decimal
    currency: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RenewalListResponse(BaseModel):
    items: List[RenewalResponse]
    total: int