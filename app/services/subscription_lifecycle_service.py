from datetime import datetime, timezone, timedelta
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user_subscription import UserSubscription
from app.models.subscription_plan import SubscriptionPlan
from app.models.subscription_cancellation import SubscriptionCancellation
from app.models.subscription_renewal import SubscriptionRenewal
from app.models.payment import Payment
from app.schemas.subscription_lifecycle import (
    CancelSubscriptionRequest,
    RenewSubscriptionRequest,
)
from app.schemas.payment import PaymentCreate


class SubscriptionLifecycleService:

    @staticmethod
    async def cancel_subscription(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
        data: CancelSubscriptionRequest,
    ) -> SubscriptionCancellation:
        result = await db.execute(
            select(UserSubscription).where(
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

        if subscription.status not in ("active", "past_due"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel subscription with status '{subscription.status}'",
            )

        cancellation = SubscriptionCancellation(
            subscription_id=subscription.id,
            user_id=user_id,
            organization_id=subscription.organization_id,
            status="processed",
            reason=data.reason,
            cancelled_at=datetime.now(timezone.utc),
            effective_immediately=data.effective_immediately,
        )
        db.add(cancellation)

        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(cancellation)
        return cancellation

    @staticmethod
    async def get_cancellation(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
    ) -> Optional[SubscriptionCancellation]:
        result = await db.execute(
            select(SubscriptionCancellation)
            .where(
                and_(
                    SubscriptionCancellation.subscription_id == subscription_id,
                    SubscriptionCancellation.user_id == user_id,
                )
            )
            .order_by(SubscriptionCancellation.created_at.desc())
        )
        return result.scalars().first()

    @staticmethod
    async def renew_subscription(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
        data: RenewSubscriptionRequest,
    ) -> SubscriptionRenewal:
        
        from app.services.payment_service import PaymentService

        result = await db.execute(
            select(UserSubscription).where(
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

        if subscription.status not in ("active", "expired", "past_due", "cancelled"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot renew subscription with status '{subscription.status}'",
            )

        result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == subscription.plan_id)
        )
        plan = result.scalar_one_or_none()
        if not plan or not plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Related plan is not available",
            )

        amount = data.amount if data.amount is not None else plan.price
        currency = data.currency or plan.currency

        payment_data = PaymentCreate(
            subscription_id=subscription.id,
            amount=amount,
            currency=currency,
            provider=data.provider,
        )
        payment = await PaymentService.create_payment(
            db=db,
            user_id=user_id,
            organization_id=subscription.organization_id,
            data=payment_data,
        )

        previous_end = subscription.end_date
        now = datetime.now(timezone.utc)

        if plan.billing_interval == "monthly":
            new_end = (previous_end or now) + timedelta(days=30)
        else:
            new_end = (previous_end or now) + timedelta(days=365)

        renewal = SubscriptionRenewal(
            subscription_id=subscription.id,
            user_id=user_id,
            organization_id=subscription.organization_id,
            payment_id=payment.id,
            status="pending",
            previous_end_date=previous_end,
            new_end_date=new_end,
            amount=amount,
            currency=currency,
        )
        db.add(renewal)
        await db.commit()
        await db.refresh(renewal)
        return renewal

    @staticmethod
    async def complete_renewal_after_payment(
        db: AsyncSession,
        payment: Payment,
    ) -> None:
        result = await db.execute(
            select(SubscriptionRenewal).where(
                SubscriptionRenewal.payment_id == payment.id
            )
        )
        renewal = result.scalar_one_or_none()
        if not renewal or renewal.status == "successful":
            return

        renewal.status = "successful"

        result = await db.execute(
            select(UserSubscription).where(
                UserSubscription.id == renewal.subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            subscription.end_date = renewal.new_end_date
            subscription.status = "active"
            if not subscription.start_date:
                subscription.start_date = datetime.now(timezone.utc)

        await db.commit()

    @staticmethod
    async def list_renewals(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
    ) -> List[SubscriptionRenewal]:
        result = await db.execute(
            select(SubscriptionRenewal)
            .where(
                and_(
                    SubscriptionRenewal.subscription_id == subscription_id,
                    SubscriptionRenewal.user_id == user_id,
                )
            )
            .order_by(SubscriptionRenewal.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_renewal(
        db: AsyncSession,
        subscription_id: int,
        renewal_id: int,
        user_id: int,
    ) -> SubscriptionRenewal:
        result = await db.execute(
            select(SubscriptionRenewal).where(
                and_(
                    SubscriptionRenewal.id == renewal_id,
                    SubscriptionRenewal.subscription_id == subscription_id,
                    SubscriptionRenewal.user_id == user_id,
                )
            )
        )
        renewal = result.scalar_one_or_none()
        if not renewal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Renewal not found",
            )
        return renewal