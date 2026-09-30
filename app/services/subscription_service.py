from datetime import datetime, timezone, timedelta
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.subscription import SubscriptionPlanCreate,SubscriptionPlanUpdate,UserSubscriptionCreate,ChangePlanRequest



ALLOWED_STATUSES = {"pending", "active", "cancelled", "expired", "past_due"}

VALID_TRANSITIONS = {
    "pending": {"active", "cancelled"},
    "active": {"cancelled", "expired", "past_due"},
    "past_due": {"active", "cancelled", "expired"},
    "cancelled": set(),      
    "expired": set(),        
}


class SubscriptionService:
    @staticmethod
    async def create_plan(db: AsyncSession,data: SubscriptionPlanCreate,):

        result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == data.name))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Plan name already exists")

        plan = SubscriptionPlan(
            name=data.name,
            description=data.description,
            price=data.price,
            currency=data.currency,
            billing_interval=data.billing_interval,
            features=data.features,
            is_active=data.is_active,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan

    @staticmethod
    async def get_plan(db: AsyncSession, plan_id: int) -> SubscriptionPlan:
        result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Subscription plan not found",)
        return plan

    @staticmethod
    async def list_plans(db: AsyncSession,active_only: bool = False,):
        query = select(SubscriptionPlan)
        if active_only:
            query = query.where(SubscriptionPlan.is_active == True)
        query = query.order_by(SubscriptionPlan.price.asc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_plan(db: AsyncSession,plan_id: int,data: SubscriptionPlanUpdate,):
        plan = await SubscriptionService.get_plan(db, plan_id)

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != plan.name:
            result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == update_data["name"]))
            if result.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Plan name already exists")

        for field, value in update_data.items():
            setattr(plan, field, value)

        await db.commit()
        await db.refresh(plan)
        return plan

    @staticmethod
    async def deactivate_plan(db: AsyncSession, plan_id: int):
        plan = await SubscriptionService.get_plan(db, plan_id)
        plan.is_active = False
        await db.commit()
        await db.refresh(plan)
        return plan

    @staticmethod
    async def create_subscription(db: AsyncSession,user_id: int,organization_id: int,data: UserSubscriptionCreate,):
        plan = await SubscriptionService.get_plan(db, data.plan_id)
        if not plan.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This plan is not active and cannot be selected" )

        result = await db.execute(
            select(UserSubscription).where(
                and_(
                    UserSubscription.user_id == user_id,
                    UserSubscription.status == "active",
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active subscription. Please change plan instead.",
            )

        # 3. Weka tarehe
        now = datetime.now(timezone.utc)
        if plan.billing_interval == "monthly":
            end_date = now + timedelta(days=30)
        else:  # yearly
            end_date = now + timedelta(days=365)

        subscription = UserSubscription(
            user_id=user_id,
            organization_id=organization_id,
            plan_id=plan.id,
            status="active", 
            start_date=now,
            end_date=end_date,
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        return subscription

    @staticmethod
    async def get_subscription(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
    ) -> UserSubscription:
        """User anaweza kuona subscription yake tu"""
        result = await db.execute(
            select(UserSubscription)
            .options(selectinload(UserSubscription.plan))
            .where(
                and_(
                    UserSubscription.id == subscription_id,
                    UserSubscription.user_id == user_id,
                )
            )
        )
        subscription = result.scalar_one_or_none()
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found",
            )
        return subscription

    @staticmethod
    async def get_current_subscription(
        db: AsyncSession,
        user_id: int,
    ) -> Optional[UserSubscription]:
        """Inarudisha subscription active ya sasa (kama ipo)"""
        result = await db.execute(
            select(UserSubscription)
            .options(selectinload(UserSubscription.plan))
            .where(
                and_(
                    UserSubscription.user_id == user_id,
                    UserSubscription.status == "active",
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_subscription_history(
        db: AsyncSession,
        user_id: int,
    ) -> List[UserSubscription]:
        """Historia yote ya subscriptions za user"""
        result = await db.execute(
            select(UserSubscription)
            .options(selectinload(UserSubscription.plan))
            .where(UserSubscription.user_id == user_id)
            .order_by(UserSubscription.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_status(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
        new_status: str,
    ) -> UserSubscription:
        if new_status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Allowed: {', '.join(ALLOWED_STATUSES)}",
            )

        subscription = await SubscriptionService.get_subscription(
            db, subscription_id, user_id
        )

        # Angalia kama transition inaruhusiwa
        allowed = VALID_TRANSITIONS.get(subscription.status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change status from '{subscription.status}' to '{new_status}'",
            )

        subscription.status = new_status

        if new_status == "cancelled":
            subscription.cancelled_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(subscription)
        return subscription

    @staticmethod
    async def change_plan(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
        data: ChangePlanRequest,
    ) -> UserSubscription:
        """Upgrade au Downgrade"""
        subscription = await SubscriptionService.get_subscription(
            db, subscription_id, user_id
        )

        if subscription.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active subscriptions can change plan",
            )

        # Hakikisha plan mpya ipo na ni active
        new_plan = await SubscriptionService.get_plan(db, data.new_plan_id)
        if not new_plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New plan is not active",
            )

        if new_plan.id == subscription.plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already on this plan",
            )

        # Badilisha plan
        subscription.plan_id = new_plan.id

        # Sasisha end_date kulingana na interval mpya
        now = datetime.now(timezone.utc)
        if new_plan.billing_interval == "monthly":
            subscription.end_date = now + timedelta(days=30)
        else:
            subscription.end_date = now + timedelta(days=365)

        await db.commit()
        await db.refresh(subscription)
        return subscription