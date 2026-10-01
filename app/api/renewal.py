
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.subscription_lifecycle import (
    CancelSubscriptionRequest,
    CancellationResponse,
    RenewSubscriptionRequest,
    RenewalResponse,
    RenewalListResponse,
)
from app.services.subscription_lifecycle_service import SubscriptionLifecycleService

router = APIRouter(prefix="/subscriptions", tags=["Renewal Lifecycle"])



@router.post(
    "/{subscription_id}/renew",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Renew a subscription (creates pending payment)",
)
async def renew_subscription(
    subscription_id: int,
    data: RenewSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = await SubscriptionLifecycleService.renew_subscription(
        db=db,
        subscription_id=subscription_id,
        user_id=current_user.id,
        data=data,
    )
    return renewal


@router.get(
    "/{subscription_id}/renewals",
    response_model=RenewalListResponse,
    summary="List renewal history of a subscription",
)
async def list_renewals(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewals = await SubscriptionLifecycleService.list_renewals(
        db, subscription_id, current_user.id
    )
    return RenewalListResponse(items=renewals, total=len(renewals))


@router.get(
    "/{subscription_id}/renewals/{renewal_id}",
    response_model=RenewalResponse,
    summary="Get a specific renewal",
)
async def get_renewal(
    subscription_id: int,
    renewal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = await SubscriptionLifecycleService.get_renewal(
        db, subscription_id, renewal_id, current_user.id
    )
    return renewal