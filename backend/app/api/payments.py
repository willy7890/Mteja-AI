from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentListResponse,
    PaymentStatusUpdate,
    PaymentWebhookPayload,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])



@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payment (start payment process)",
)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
   
    payment = await PaymentService.create_payment(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        data=data,
    )
    return payment


@router.get(
    "",
    response_model=PaymentListResponse,
    summary="List all payments of the current user",
)
async def list_payments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payments = await PaymentService.list_user_payments(db, current_user.id)
    return PaymentListResponse(items=payments, total=len(payments))


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get a specific payment by ID",
)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await PaymentService.get_payment(db, payment_id, current_user.id)
    return payment


@router.get(
    "/reference/{transaction_reference}",
    response_model=PaymentResponse,
    summary="Get payment by transaction reference",
)
async def get_payment_by_reference(
    transaction_reference: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await PaymentService.get_payment_by_reference(
        db, transaction_reference, user_id=current_user.id
    )
    return payment
