# orchestrator for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
# orchestrator for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.supervisor import Supervisor
from app.agents.marketing_agent import MarketingAgent
from app.agents.followup_agent import FollowupAgent
from app.models.activity_log import ActivityLog


class Orchestrator:
    

    def __init__(self):
        self.supervisor = Supervisor()
        self.agents = {
            "marketing_agent": MarketingAgent(),
            "followup_agent": FollowupAgent(),
        }

    async def run(
        self,
        db: AsyncSession,
        organization_id: int,
        conversation_id: str,
        message: str,
    ) -> dict:
    
        chosen_agent_name = self.supervisor.route(message)

        await self._log(
            db,
            organization_id=organization_id,
            conversation_id=conversation_id,
            actor="supervisor",
            action_type="route",
            description=f"Routed message to {chosen_agent_name}",
        )

        
        if chosen_agent_name == "unknown":
            return {
                "agent": "none",
                "message": "Sorry, I didn't understand what you need. Could you clarify?",
            }

        
        agent = self.agents[chosen_agent_name]
        result = await agent.handle(message)

        
        await self._log(
            db,
            organization_id=organization_id,
            conversation_id=conversation_id,
            actor=chosen_agent_name,
            action_type="tool_call",
            description=f"Executed action: {result.get('action')}",
        )

        return result

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
            conversation_id=conversation_id,
            actor=actor,
            action_type=action_type,
            description=description,
        )
        db.add(log_entry)
        await db.commit()