# lead business logic service for MTEJA AI
# Domain operations, orchestration, and multi-tenant isolation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.leads import Lead
from typing import List, Optional


class LeadService:

  @staticmethod
  async def create_lead(
      db: AsyncSession,
      organization_id: int,
      name: str,
      phone: Optional[str] = None,
      email: Optional[str] = None,
      source: str = "website",
  ) -> Lead:
    """Register a new incoming prospect lead."""
    lead = Lead(
        organization_id=organization_id,
        name=name,
        phone=phone,
        email=email,
        source=source,
        status="new",
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead

  @staticmethod
  async def update_lead_status(
      db: AsyncSession, lead_id: int, organization_id: int, new_status: str
  ) -> Optional[Lead]:
    """Update lead status (e.g., contacted, qualified, converted)."""
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id, Lead.organization_id == organization_id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
      return None

    lead.status = new_status
    await db.commit()
    await db.refresh(lead)
    return lead

  @staticmethod
  async def list_leads(
      db: AsyncSession, organization_id: int
  ) -> List[Lead]:
    """List all leads for the organization."""
    result = await db.execute(
        select(Lead).where(Lead.organization_id == organization_id)
    )
    return result.scalars().all()


lead_service = LeadService()