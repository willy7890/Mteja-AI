


from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user   # from auth
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    SubscriptionPlanListResponse,
    UserSubscriptionCreate,
    UserSubscriptionResponse,
    UserSubscriptionListResponse,
    UserSubscriptionStatusUpdate,
ChangePlanRequest,
)
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/User subscriptions", tags=["User Subscriptions"])




@router.post("",
    
    response_model=UserSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a subscription (User selects a plan)",
)
async def create_subscription(
    data: UserSubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = await SubscriptionService.create_subscription(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        data=data,
    )
    return subscription


@router.get(
    "/current",
    response_model=Optional[UserSubscriptionResponse],
    summary="Get current active subscription",
)
async def get_current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = await SubscriptionService.get_current_subscription(
        db, current_user.id
    )
    return subscription


@router.get(
    "/history",
    response_model=UserSubscriptionListResponse,
    summary="Get subscription history",
)
async def get_subscription_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscriptions = await SubscriptionService.get_subscription_history(
        db, current_user.id
    )
    return UserSubscriptionListResponse(
        items=subscriptions,
        total=len(subscriptions),
    )


@router.get(
    "/{subscription_id}",
    response_model=UserSubscriptionResponse,
    summary="Get a specific subscription",
)
async def get_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = await SubscriptionService.get_subscription(
        db, subscription_id, current_user.id
    )
    return subscription


@router.patch(
    "/{subscription_id}/status",
    response_model=UserSubscriptionResponse,
    summary="Update subscription status",
)
async def update_subscription_status(
    subscription_id: int,
    data: UserSubscriptionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = await SubscriptionService.update_status(
        db=db,
        subscription_id=subscription_id,
        user_id=current_user.id,
        new_status=data.status,
    )
    return subscription


@router.post(
    "/{subscription_id}/change-plan",
    response_model=UserSubscriptionResponse,
    summary="Upgrade or Downgrade plan",
)
async def change_plan(
    subscription_id: int,
    data: ChangePlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = await SubscriptionService.change_plan(
        db=db,
        subscription_id=subscription_id,
        user_id=current_user.id,
        data=data,
    )
    return subscription