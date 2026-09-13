# conversation business logic service for MTEJA AI
# Domain operations, orchestration, and multi-tenant isolation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Conversation
from app.models.message import Message
from typing import List, Optional


class ConversationService:

  @staticmethod
  async def get_conversation_by_id(
      db: AsyncSession, conversation_id: int, organization_id: int
  ) -> Optional[Conversation]:
    """Fetch a specific conversation ensuring multi-tenant isolation."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()

  @staticmethod
  async def switch_to_human_mode(
      db: AsyncSession, conversation_id: int, agent_id: int, organization_id: int
  ) -> Optional[Conversation]:
    """Take over an AI conversation, switching mode to human and assigning staff."""
    conv = await ConversationService.get_conversation_by_id(
        db, conversation_id, organization_id
    )
    if not conv:
      return None

    conv.mode = "human"
    conv.assigned_to = agent_id
    await db.commit()
    await db.refresh(conv)
    return conv

  @staticmethod
  async def add_message(
      db: AsyncSession, conversation_id: int, content: str, sender_type: str
  ) -> Message:
    """Save a new message to a conversation thread."""
    message = Message(
        conversation_id=conversation_id,
        content=content,
        sender_type=sender_type,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


conversation_service = ConversationService()