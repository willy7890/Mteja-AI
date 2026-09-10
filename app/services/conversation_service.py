# conversation business logic service for MTEJA AI
# Domain operations, orchestration, and multi-tenant isolation

# backend/app/services/conversation_service.py

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


async def get_conversation_or_404(db: AsyncSession,conversation_id: int,organization_id: int,):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == organization_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


async def get_conversation_by_id(db: AsyncSession,conversation_id: int,):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    return result.scalar_one_or_none()


async def list_conversations_for_customer( db: AsyncSession, customer_id: int, organization_id: int,):
   
    result = await db.execute(
        select(Conversation).where(
            Conversation.customer_id == customer_id,
            Conversation.organization_id == organization_id,
        )
    )
    return list(result.scalars().all())


async def create_conversation(db: AsyncSession,*,organization_id: int,customer_id: int,):
    
    conversation = Conversation(
        organization_id=organization_id,
        customer_id=customer_id,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation