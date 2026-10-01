import uuid
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.payment import Payment
from app.models.user_subscription import UserSubscription
from app.services.billing_service import BillingService
from app.schemas.payment import PaymentCreate, PaymentStatusUpdate, PaymentWebhookPayload


ALLOWED_STATUSES = {"pending", "successful", "failed", "cancelled"}

VALID_TRANSITIONS = {
    "pending": {"successful", "failed", "cancelled"},
    "successful": set(),      
    "failed": set(),          
    "cancelled": set(),       
}


class PaymentService:

    @staticmethod
    async def create_payment(
        db: AsyncSession,
        user_id: int,
        organization_id: int,
        data: PaymentCreate,
    ):
        
        result = await db.execute(
            select(UserSubscription).where(
                and_(
                    UserSubscription.id == data.subscription_id,
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
        
        transaction_reference = f"PAY-{uuid.uuid4().hex[:16].upper()}"

        payment = Payment(
            user_id=user_id,
            organization_id=organization_id,
            subscription_id=data.subscription_id,
            amount=data.amount,
            currency=data.currency,
            provider=data.provider.lower(),
            transaction_reference=transaction_reference,
            status="pending",
        )

        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment



    @staticmethod
    async def get_payment(
        db: AsyncSession,
        payment_id: int,
        user_id: int,
    ):
        
        result = await db.execute(
            select(Payment).where(
                and_(
                    Payment.id == payment_id,
                    Payment.user_id == user_id,
                )
            )
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        return payment

    @staticmethod
    async def get_payment_by_reference(
        db: AsyncSession,
        transaction_reference: str,
        user_id: Optional[int] = None,
    ) -> Payment:
        query = select(Payment).where(
            Payment.transaction_reference == transaction_reference
        )
        if user_id is not None:
            query = query.where(Payment.user_id == user_id)

        result = await db.execute(query)
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        return payment

    @staticmethod
    async def list_user_payments(
        db: AsyncSession,
        user_id: int,
    ) -> List[Payment]:
        result = await db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())



    @staticmethod
    async def update_status(
        db: AsyncSession,
        payment_id: int,
        user_id: int,
        data: PaymentStatusUpdate,
    ):
        payment = await PaymentService.get_payment(db, payment_id, user_id)

        if data.status not in ALLOWED_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid status. Allowed: {', '.join(ALLOWED_STATUSES)}")

        
        allowed = VALID_TRANSITIONS.get(payment.status, set())
        if data.status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change status from '{payment.status}' to '{data.status}'",
            )

        payment.status = data.status

        if data.provider_reference:
            payment.provider_reference = data.provider_reference
        if data.notes:
            payment.notes = data.notes
        if data.status == "successful":
            payment.paid_at = datetime.now(timezone.utc)
            await PaymentService._activate_subscription(db, payment.subscription_id)

        await db.commit()
        await db.refresh(payment)
        return payment



    @staticmethod
    async def handle_webhook(
        db: AsyncSession,
        payload: PaymentWebhookPayload,
    ):
        
        result = await db.execute(
            select(Payment).where(
                Payment.transaction_reference == payload.transaction_reference
            )
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found for this reference",
            )

        if payment.status in ("successful", "failed", "cancelled"):
            return payment

       
        if payload.status not in ("successful", "failed", "cancelled"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook status",
            )

        payment.status = payload.status

        if payload.provider_reference:
            payment.provider_reference = payload.provider_reference

        if payload.message:
            payment.notes = payload.message

        if payload.status == "successful":
            payment.paid_at = datetime.now(timezone.utc)
            await PaymentService._activate_subscription(db, payment.subscription_id)
    # Create Billing Record + Invoice
            await BillingService.create_billing_and_invoice(db, payment)

        await db.commit()
        await db.refresh(payment)
        return payment



    @staticmethod
    async def _activate_subscription(
        db: AsyncSession,
        subscription_id: int,
    ):
        
        result = await db.execute(
            select(UserSubscription).where(UserSubscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        if subscription and subscription.status in ("pending", "past_due"):
            subscription.status = "active"
            if not subscription.start_date:
                subscription.start_date = datetime.now(timezone.utc)
          
            await db.commit()