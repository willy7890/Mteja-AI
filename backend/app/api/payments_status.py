
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

router = APIRouter(prefix="/payments status", 
                   tags=["Payments status"])


@router.get(
    "/{payment_id}/status",
    response_model=PaymentResponse,
    summary="Get current status of a payment",
)
async def get_payment_status(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  
    payment = await PaymentService.get_payment(db, payment_id, current_user.id)
    return payment


@router.patch(
    "/{payment_id}/status",
    response_model=PaymentResponse,
    summary="Update payment status (manual / internal)",
)
async def update_payment_status(
    payment_id: int,
    data: PaymentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await PaymentService.update_status(
        db=db,
        payment_id=payment_id,
        user_id=current_user.id,
        data=data,
    )
    return payment


@router.post(
    "/webhook",
    response_model=PaymentResponse,
    summary="Payment provider webhook / callback",
)
async def payment_webhook(
    payload: PaymentWebhookPayload,
    db: AsyncSession = Depends(get_db),
):
   
    payment = await PaymentService.handle_webhook(db, payload)
    return payment