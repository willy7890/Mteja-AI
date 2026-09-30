# campaign business logic service for MTEJA AI
# Domain operations, orchestration, and multi-tenant isolation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.customer import Customer
from app.models.campaign import Campaign
from app.services.client import SMSClient, EmailClient
from datetime import datetime


class CampaignService:

  @staticmethod
  async def execute_campaign(
      db: AsyncSession, organization_id: int, campaign_id: int
  ) -> dict:
    """Execute a scheduled or draft broadcast campaign."""
    # 1. Fetch campaign details
    camp_res = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.organization_id == organization_id,
        )
    )
    campaign = camp_res.scalar_one_or_none()
    if not campaign:
      return {"status": "error", "detail": "Campaign not found"}

    # 2. Fetch target customers
    cust_res = await db.execute(
        select(Customer).where(Customer.organization_id == organization_id)
    )
    customers = cust_res.scalars().all()

    success_count = 0
    fail_count = 0

    # 3. Broadcast messages
    for customer in customers:
      if campaign.channel == "sms" and customer.phone:
        success = await SMSClient.send_sms_reply(customer.phone, campaign.message)
        if success:
          success_count += 1
        else:
          fail_count += 1

      elif campaign.channel == "email" and customer.email:
        success = EmailClient.send_email_reply(
            recipient=customer.email,
            subject=campaign.title,
            reply_content=campaign.message,
        )
        if success:
          success_count += 1
        else:
          fail_count += 1

    # 4. Update campaign status
    campaign.status = "sent"
    campaign.sent_at = datetime.utcnow()
    await db.commit()

    return {
        "status": "success",
        "campaign_id": campaign.id,
        "total_sent": success_count,
        "total_failed": fail_count,
    }


campaign_service = CampaignService()