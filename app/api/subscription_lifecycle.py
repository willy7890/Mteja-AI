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

router = APIRouter(prefix="/subscriptions", 
                   tags=["Subscription Lifecycle"])



@router.get(
    "/{subscription_id}/cancellation",
    response_model=Optional[CancellationResponse],
    summary="Get cancellation info of a subscription",
)
async def get_cancellation(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cancellation = await SubscriptionLifecycleService.get_cancellation(
        db, subscription_id, current_user.id
    )
    return cancellation


@router.post(
    "/{subscription_id}/cancel",
    response_model=CancellationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a subscription",
)
async def cancel_subscription(
    subscription_id: int,
    data: CancelSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cancellation = await SubscriptionLifecycleService.cancel_subscription(
        db=db,
        subscription_id=subscription_id,
        user_id=current_user.id,
        data=data,
    )
    return cancellation


