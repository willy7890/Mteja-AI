from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict




class SubscriptionPlanBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    currency: str = Field(default="TZS", max_length=10)
    billing_interval: str = Field(..., pattern="^(monthly|yearly)$")
    features: Optional[str] = None
    is_active: bool = True


class SubscriptionPlanCreate(BaseModel):
        name: str = Field(..., min_length=2, max_length=100)
        description: Optional[str] = None
        price: Decimal = Field(..., ge=0)
        currency: str = Field(default="TZS", max_length=10)
        billing_interval: str = Field(..., pattern="^(monthly|yearly)$")
        features: Optional[str] = None
        is_active: bool = True


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    billing_interval: Optional[str] = Field(None, pattern="^(monthly|yearly)$")
    features: Optional[str] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSubscriptionCreate(BaseModel):
    plan_id: int


class UserSubscriptionStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|active|cancelled|expired|past_due)$")


class UserSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    plan_id: int
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    plan: Optional[SubscriptionPlanResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ChangePlanRequest(BaseModel):
    new_plan_id: int


class SubscriptionPlanListResponse(BaseModel):
    items: List[SubscriptionPlanResponse]
    total: int


class UserSubscriptionListResponse(BaseModel):
    items: List[UserSubscriptionResponse]
    total: int