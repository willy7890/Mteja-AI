# campaigns API endpoints for MTEJA AI
# REST routes for campaigns resource (CRUD + domain actions)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.customer import Customer
from app.models.user import User
from app.services.client import EmailClient
from app.services.client import SMSClient  # Or your SMS dispatch client

router = APIRouter(tags=["Broadcast Campaigns"])


class CampaignRequest(BaseModel):
  title: str
  message: str
  channel: str  # "sms" or "email"
  target_segment: Optional[str] = "all"


@router.post("/broadcast", status_code=status.HTTP_200_OK)
async def send_broadcast_campaign(
    payload: CampaignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  """Broadcast an SMS or Email campaign to all organization customers."""
  
  # 1. Fetch all customers for this organization
  cust_result = await db.execute(
      select(Customer).where(
          Customer.organization_id == current_user.organization_id
      )
  )
  customers = cust_result.scalars().all()

  if not customers:
    raise HTTPException(status_code=404, detail="No customers found to broadcast.")

  success_count = 0
  fail_count = 0

  # 2. Iterate and dispatch broadcast messages
  for customer in customers:
    if payload.channel == "sms" and customer.phone:
      success = await SMSClient.send_sms_reply(customer.phone, payload.message)
      if success:
        success_count += 1
      else:
        fail_count += 1

    elif payload.channel == "email" and customer.email:
      success = EmailClient.send_email_reply(
          recipient=customer.email,
          subject=payload.title,
          reply_content=payload.message,
      )
      if success:
        success_count += 1
      else:
        fail_count += 1

  return {
      "status": "completed",
      "channel": payload.channel,
      "total_targeted": len(customers),
      "successful_sends": success_count,
      "failed_sends": fail_count,
  }