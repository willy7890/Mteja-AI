# analytics API endpoints for MTEJA AI
# REST routes for analytics resource (CRUD + domain actions)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.customer import Customer


async def get_platform_analytics(db: AsyncSession, organization_id: int) -> dict:
  """Aggregate core platform metrics for the organization's analytics dashboard."""
  
  # 1. Total Customers Count
  cust_count_res = await db.execute(
      select(func.count(Customer.id)).where(
          Customer.organization_id == organization_id
      )
  )
  total_customers = cust_count_res.scalar() or 0

  # 2. Total Conversations Count
  conv_count_res = await db.execute(
      select(func.count(Conversation.id)).where(
          Conversation.organization_id == organization_id
      )
  )
  total_conversations = conv_count_res.scalar() or 0

  # 3. Open vs Closed Conversations
  open_conv_res = await db.execute(
      select(func.count(Conversation.id)).where(
          Conversation.organization_id == organization_id,
          Conversation.status == "open",
      )
  )
  open_conversations = open_conv_res.scalar() or 0

  # 4. AI Mode vs Human Mode Conversations
  ai_mode_res = await db.execute(
      select(func.count(Conversation.id)).where(
          Conversation.organization_id == organization_id,
          Conversation.mode == "ai",
      )
  )
  ai_mode_conversations = ai_mode_res.scalar() or 0

  # 5. Total Messages Count
  msg_count_res = await db.execute(
      select(func.count(Message.id))
      .join(Conversation, Message.conversation_id == Conversation.id)
      .where(Conversation.organization_id == organization_id)
  )
  total_messages = msg_count_res.scalar() or 0

  return {
      "total_customers": total_customers,
      "total_conversations": total_conversations,
      "open_conversations": open_conversations,
      "closed_conversations": total_conversations - open_conversations,
      "ai_handled_conversations": ai_mode_conversations,
      "human_handled_conversations": total_conversations - ai_mode_conversations,
      "total_messages": total_messages,
  }