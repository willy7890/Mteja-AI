# analytics business logic service for MTEJA AI
# Domain operations, orchestration, and multi-tenant isolation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.customer import Customer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os


class AnalyticService:

  @staticmethod
  async def get_metrics(db: AsyncSession, organization_id: int) -> dict:
    """Fetch aggregated dashboard metrics from the database."""
    cust_res = await db.execute(
        select(func.count(Customer.id)).where(
            Customer.organization_id == organization_id
        )
    )
    total_customers = cust_res.scalar() or 0

    conv_res = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.organization_id == organization_id
        )
    )
    total_conversations = conv_res.scalar() or 0

    open_res = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.organization_id == organization_id,
            Conversation.status == "open",
        )
    )
    open_conversations = open_res.scalar() or 0

    ai_res = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.organization_id == organization_id,
            Conversation.mode == "ai",
        )
    )
    ai_mode_conversations = ai_res.scalar() or 0

    msg_res = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.organization_id == organization_id)
    )
    total_messages = msg_res.scalar() or 0

    return {
        "total_customers": total_customers,
        "total_conversations": total_conversations,
        "open_conversations": open_conversations,
        "closed_conversations": total_conversations - open_conversations,
        "ai_handled": ai_mode_conversations,
        "human_handled": total_conversations - ai_mode_conversations,
        "total_messages": total_messages,
    }

  @staticmethod
  async def generate_ai_insights(summary_text: str) -> str:
    """Generate business intelligence insights using OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
      return "OpenAI API Key not configured for generating insights."

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    system_prompt = (
        "You are an expert business analyst for MtejaAI. Review the provided"
        " customer support data summary and output 3 concise, actionable"
        " operational insights to help improve student or customer support."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=summary_text),
    ]

    response = await llm.ainvoke(messages)
    return response.content


analytic_service = AnalyticService()