from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead


async def create_lead(
    db: AsyncSession,
    organization_id: int,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    source: Optional[str] = "web",
    status: str = "new",
    notes: Optional[str] = None,
) -> Lead:
    """Creates and stores a new Lead entity."""
    lead = Lead(
        organization_id=organization_id,
        name=name.strip(),
        email=email.strip() if email else None,
        phone=phone.strip() if phone else None,
        source=source,
        status=status,
        notes=notes,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


async def get_lead_by_id(db: AsyncSession, lead_id: int, organization_id: int) -> Optional[Lead]:
    """Retrieves a single Lead by ID scoped to the organization."""
    query = select(Lead).where(
        Lead.id == lead_id,
        Lead.organization_id == organization_id,
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_leads(
    db: AsyncSession,
    organization_id: int,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Lead]:
    """Lists leads for an organization with optional status filtering."""
    query = select(Lead).where(Lead.organization_id == organization_id)
    if status:
        query = query.where(Lead.status == status)

    query = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_lead_status(
    db: AsyncSession,
    lead_id: int,
    organization_id: int,
    new_status: str,
) -> Optional[Lead]:
    """Updates the status of an existing lead."""
    lead = await get_lead_by_id(db, lead_id, organization_id)
    if not lead:
        return None

    lead.status = new_status
    await db.commit()
    await db.refresh(lead)
    return lead