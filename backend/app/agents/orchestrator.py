import logging
from typing import Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.followup_agent import FollowupAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.sales_agent import SalesAgent
from app.agents.supervisor import Supervisor
from app.agents.support_agent import SupportAgent
from app.models.activity_log import ActivityLog
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)


class Orchestrator:

    def __init__(self):
        self.supervisor = Supervisor()
        self.agents = {
            "marketing_agent": MarketingAgent(),
            "followup_agent": FollowupAgent(),
            "sales_agent": SalesAgent(),
            "support_agent": SupportAgent(),
        }

    async def run(
        self,
        db: AsyncSession,
        organization_id: int,
        conversation_id: str,
        message: str,
    ) -> Dict[str, Any]:
        # 1. Hakikisha conversation ipo na ipo kwenye mode ya AI
        conv_id_int = int(conversation_id)
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conv_id_int,
                Conversation.organization_id == organization_id,
            )
        )
        conversation = result.scalar_one_or_none()

        if conversation is None or conversation.mode != "ai" or conversation.status != "open":
            return {"blocked": True, "reason": "Conversation is owned by a human agent or closed"}

        # 2. Supervisor Routing (tumia await kama ni Async LLM Call)
        try:
            chosen_agent_name = await self.supervisor.route(message)
        except AttributeError:
            # Kama route() haikuwa async, itatumia sync routing kwa usalama
            chosen_agent_name = self.supervisor.route(message)

        await self._log(
            db,
            organization_id=organization_id,
            conversation_id=conversation_id,
            actor="supervisor",
            action_type="route",
            description=f"Routed message to {chosen_agent_name}",
        )

        # 3. Handle Unknown au Agent asiyepatikana
        if chosen_agent_name not in self.agents:
            return {
                "agent": "none",
                "result": {
                    "message": "Samahani, sijaelewa ombi lako vizuri. Unaweza kufafanua zaidi?"
                },
            }

        # 4. Tekeleza Agent aliyechaguliwa
        agent = self.agents[chosen_agent_name]
        try:
            agent_result = await agent.handle(message)
        except Exception as e:
            logger.error(f"Error executing agent '{chosen_agent_name}': {str(e)}")
            return {
                "agent": chosen_agent_name,
                "result": {
                    "message": "Kuna hitilafu ilitokea wakati wa kuchakata ombi lako. Tafadhali jaribu tena."
                },
            }

        # 5. Hifadhi Log
        action_name = agent_result.get("action", "respond") if isinstance(agent_result, dict) else "respond"
        await self._log(
            db,
            organization_id=organization_id,
            conversation_id=conversation_id,
            actor=chosen_agent_name,
            action_type="tool_call",
            description=f"Executed action: {action_name}",
        )

        # 6. Sanitize na Standardize Return Payload kwa ajili ya Chat Router
        if isinstance(agent_result, str):
            return {
                "agent": chosen_agent_name,
                "result": {"message": agent_result}
            }

        return {
            "agent": chosen_agent_name,
            "result": agent_result
        }

    async def _log(
        self,
        db: AsyncSession,
        organization_id: int,
        conversation_id: str,
        actor: str,
        action_type: str,
        description: str,
    ) -> None:
        log_entry = ActivityLog(
            organization_id=organization_id,
            conversation_id=int(conversation_id),
            actor=actor,
            action_type=action_type,
            description=description,
        )
        db.add(log_entry)
        # Tumia flush badala ya commit ili kuzuia ku-break active transaction ya router
        await db.flush()