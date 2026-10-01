
from typing import List, Optional
from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.billing import (
    BillingRecordResponse,BillingRecordListResponse,
    InvoiceResponse,InvoiceListResponse,InvoiceCreate,
    InvoiceUpdate,)
from app.services.billing_service import BillingService

router = APIRouter(tags=["Invoices"])




@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create invoice manually for a successful payment",
)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = await BillingService.create_invoice_manually(
        db=db,
        user_id=current_user.id,
        data=data,
    )
    return invoice


@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
    summary="List all invoices of current user",
)
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoices = await BillingService.list_user_invoices(db, current_user.id)
    return InvoiceListResponse(items=invoices, total=len(invoices))


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get a specific invoice by ID",
)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = await BillingService.get_invoice(db, invoice_id, current_user.id)
    return invoice


@router.get(
    "/invoices/number/{invoice_number}",
    response_model=InvoiceResponse,
    summary="Get invoice by invoice number",
)
async def get_invoice_by_number(
    invoice_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = await BillingService.get_invoice_by_number(
        db, invoice_number, current_user.id
    )
    return invoice


@router.get(
    "/payments/{payment_id}/invoice",
    response_model=InvoiceResponse,
    summary="Get invoice related to a payment",
)
async def get_invoice_by_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = await BillingService.get_invoice_by_payment(
        db, payment_id, current_user.id
    )
    return invoice


@router.patch(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Update invoice (status, notes, due_date)",
)
async def update_invoice(
    invoice_id: int,
    data: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = await BillingService.update_invoice(
        db, invoice_id, current_user.id, data
    )
    return invoice