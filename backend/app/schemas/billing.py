from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict




class BillingRecordResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    subscription_id: int
    plan_id: int
    payment_id: int
    amount: Decimal
    currency: str
    transaction_reference: str
    payment_status: str
    payment_date: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillingRecordListResponse(BaseModel):
    items: List[BillingRecordResponse]
    total: int




class InvoiceCreate(BaseModel):
    payment_id: int
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    status: Optional[str] = Field(
        None, pattern="^(issued|paid|void|refunded)$"
    )
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    user_id: int
    organization_id: int
    subscription_id: int
    plan_id: int
    payment_id: int
    billing_id: int
    amount: Decimal
    currency: str
    status: str
    issued_at: datetime
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int