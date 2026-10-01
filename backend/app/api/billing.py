from typing import List, Optional
from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.billing import (
    BillingRecordResponse,
    BillingRecordListResponse,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceCreate,
    InvoiceUpdate,
)
from app.services.billing_service import BillingService

router = APIRouter(tags=["Billing"])



@router.get(
    "/billing",
    response_model=BillingRecordListResponse,
    summary="Get billing history of current user",
)
async def list_billing_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = await BillingService.list_user_billing(db, current_user.id)
    return BillingRecordListResponse(items=records, total=len(records))


@router.get(
    "/billing/{billing_id}",
    response_model=BillingRecordResponse,
    summary="Get a specific billing record",
)
async def get_billing_record(
    billing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = await BillingService.get_billing_record(
        db, billing_id, current_user.id
    )
    return record


@router.get(
    "/subscriptions/{subscription_id}/billing",
    response_model=BillingRecordListResponse,
    summary="Get billing history for a specific subscription",
)
async def get_subscription_billing(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = await BillingService.list_subscription_billing(
        db, subscription_id, current_user.id
    )
    return BillingRecordListResponse(items=records, total=len(records))