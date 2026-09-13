# leads API endpoints for MTEJA AI
# REST routes for leads resource (CRUD + domain actions)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.deal import Deal


router = APIRouter(tags=["Lead Management"])


class DealCreate(BaseModel):
  customer_id: int
  title: str
  value: float = 0.0
  stage: str = "lead"


class DealUpdate(BaseModel):
  title: Optional[str] = None
  value: Optional[float] = None
  stage: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_deal(
    payload: DealCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  """Create a new sales deal for a customer."""
  deal = Deal(
      organization_id=current_user.organization_id,
      customer_id=payload.customer_id,
      title=payload.title,
      value=payload.value,
      stage=payload.stage,
  )
  db.add(deal)
  await db.commit()
  await db.refresh(deal)
  return deal


@router.get("/", status_code=status.HTTP_200_OK)
async def list_deals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  """List all sales deals in the pipeline for the organization."""
  result = await db.execute(
      select(Deal).where(Deal.organization_id == current_user.organization_id)
  )
  deals = result.scalars().all()
  return deals


@router.patch("/{deal_id}", status_code=status.HTTP_200_OK)
async def update_deal_stage(
    deal_id: int,
    payload: DealUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  """Update deal stage (Kanban board movement) or value."""
  result = await db.execute(
      select(Deal).where(
          Deal.id == deal_id, Deal.organization_id == current_user.organization_id
      )
  )
  deal = result.scalar_one_or_none()
  if not deal:
    raise HTTPException(status_code=404, detail="Deal not found")

  if payload.title:
    deal.title = payload.title
  if payload.value is not None:
    deal.value = payload.value
  if payload.stage:
    deal.stage = payload.stage

  await db.commit()
  await db.refresh(deal)
  return deal