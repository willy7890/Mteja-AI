import uuid
from datetime import datetime, timezone, timedelta
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.billing import BillingRecord
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.user_subscription import UserSubscription
from app.schemas.billing import InvoiceCreate, InvoiceUpdate


class BillingService:


    @staticmethod
    async def create_billing_and_invoice(
        db: AsyncSession,
        payment: Payment,
    ):
        # Check if billing already exists
        result = await db.execute(
            select(BillingRecord).where(BillingRecord.payment_id == payment.id)
        )
        existing_billing = result.scalar_one_or_none()

        if existing_billing:
            result = await db.execute(
                select(Invoice).where(Invoice.payment_id == payment.id)
            )
            existing_invoice = result.scalar_one_or_none()
            if existing_invoice:
                return existing_billing, existing_invoice

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Billing exists but invoice is missing",
            )

        result = await db.execute(
            select(UserSubscription).where(
                UserSubscription.id == payment.subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Related subscription not found",
            )
            
        billing = BillingRecord(
            user_id=payment.user_id,
            organization_id=payment.organization_id,
            subscription_id=payment.subscription_id,
            plan_id=subscription.plan_id,
            payment_id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            transaction_reference=payment.transaction_reference,
            payment_status=payment.status,
            payment_date=payment.paid_at or datetime.now(timezone.utc),
        )
        db.add(billing)
        await db.flush()

        invoice_number = BillingService._generate_invoice_number()

        invoice = Invoice(
            invoice_number=invoice_number,
            user_id=payment.user_id,
            organization_id=payment.organization_id,
            subscription_id=payment.subscription_id,
            plan_id=subscription.plan_id,
            payment_id=payment.id,
            billing_id=billing.id,
            amount=payment.amount,
            currency=payment.currency,
            status="issued",
            issued_at=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(invoice)

        await db.commit()
        await db.refresh(billing)
        await db.refresh(invoice)

        return billing, invoice



    @staticmethod
    async def create_invoice_manually(
        db: AsyncSession,
        user_id: int,
        data: InvoiceCreate,
    ):
       
        result = await db.execute(
            select(Payment).where(
                and_(
                    Payment.id == data.payment_id,
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

       
        if payment.status != "successful":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice can only be created for successful payments",
            )

        
        result = await db.execute(
            select(Invoice).where(Invoice.payment_id == payment.id)
        )
        existing_invoice = result.scalar_one_or_none()
        if existing_invoice:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invoice already exists for this payment",
            )

       
        result = await db.execute(
            select(BillingRecord).where(BillingRecord.payment_id == payment.id)
        )
        billing = result.scalar_one_or_none()

        if not billing:
            # Create both billing + invoice
            billing, invoice = await BillingService.create_billing_and_invoice(
                db, payment
            )
            if data.notes:
                invoice.notes = data.notes
                await db.commit()
                await db.refresh(invoice)
            return invoice

        
        result = await db.execute(
            select(UserSubscription).where(
                UserSubscription.id == payment.subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Related subscription not found",
            )

        invoice_number = BillingService._generate_invoice_number()

        invoice = Invoice(
            invoice_number=invoice_number,
            user_id=payment.user_id,
            organization_id=payment.organization_id,
            subscription_id=payment.subscription_id,
            plan_id=subscription.plan_id,
            payment_id=payment.id,
            billing_id=billing.id,
            amount=payment.amount,
            currency=payment.currency,
            status="issued",
            issued_at=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
            notes=data.notes,
        )
        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)
        return invoice



    @staticmethod
    async def get_billing_record(
        db: AsyncSession,
        billing_id: int,
        user_id: int,
    ) -> BillingRecord:
        result = await db.execute(
            select(BillingRecord).where(
                and_(
                    BillingRecord.id == billing_id,
                    BillingRecord.user_id == user_id,
                )
            )
        )
        billing = result.scalar_one_or_none()
        if not billing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Billing record not found",
            )
        return billing

    @staticmethod
    async def list_user_billing(
        db: AsyncSession,
        user_id: int,
    ) -> List[BillingRecord]:
        result = await db.execute(
            select(BillingRecord)
            .where(BillingRecord.user_id == user_id)
            .order_by(BillingRecord.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_subscription_billing(
        db: AsyncSession,
        subscription_id: int,
        user_id: int,
    ) -> List[BillingRecord]:
        result = await db.execute(
            select(BillingRecord)
            .where(
                and_(
                    BillingRecord.subscription_id == subscription_id,
                    BillingRecord.user_id == user_id,
                )
            )
            .order_by(BillingRecord.created_at.desc())
        )
        return list(result.scalars().all())



    @staticmethod
    async def get_invoice(
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
    ) -> Invoice:
        result = await db.execute(
            select(Invoice).where(
                and_(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id,
                )
            )
        )
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )
        return invoice

    @staticmethod
    async def get_invoice_by_number(
        db: AsyncSession,
        invoice_number: str,
        user_id: int,
    ) -> Invoice:
        result = await db.execute(
            select(Invoice).where(
                and_(
                    Invoice.invoice_number == invoice_number,
                    Invoice.user_id == user_id,
                )
            )
        )
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )
        return invoice

    @staticmethod
    async def get_invoice_by_payment(
        db: AsyncSession,
        payment_id: int,
        user_id: int,
    ) -> Invoice:
        result = await db.execute(
            select(Invoice).where(
                and_(
                    Invoice.payment_id == payment_id,
                    Invoice.user_id == user_id,
                )
            )
        )
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found for this payment",
            )
        return invoice

    @staticmethod
    async def list_user_invoices(
        db: AsyncSession,
        user_id: int,
    ):
        result = await db.execute(
            select(Invoice)
            .where(Invoice.user_id == user_id)
            .order_by(Invoice.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_invoice(
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
        data: InvoiceUpdate,
    ):
        invoice = await BillingService.get_invoice(db, invoice_id, user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(invoice, field, value)

        await db.commit()
        await db.refresh(invoice)
        return invoice



    @staticmethod
    def _generate_invoice_number() -> str:
        date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
        unique_part = uuid.uuid4().hex[:8].upper()
        return f"INV-{date_part}-{unique_part}"