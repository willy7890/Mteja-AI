# followup_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
# followup_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
from app.agents.base_agent import BaseAgent
from app.tools.followup_tools import FOLLOWUP_TOOLS


class FollowupAgent(BaseAgent):
    

    def __init__(self):
        super().__init__(
            name="followup_agent",
            tools=FOLLOWUP_TOOLS
        )

    async def handle(self, message: str) -> dict:
        message_lower = message.lower()

        if "remind" in message_lower or "reminder" in message_lower:
            result = await self.call_tool(
                "send_reminder",
                customer_name="customer",
                message=message
            )
            return {
                "agent": self.name,
                "action": "send_reminder",
                "result": result
            }

        elif "schedule" in message_lower or "follow up" in message_lower or "follow-up" in message_lower:
            result = await self.call_tool(
                "schedule_followup",
                customer_name="customer",
                days=1
            )
            return {
                "agent": self.name,
                "action": "schedule_followup",
                "result": result
            }

        return {
            "agent": self.name,
            "action": "none",
            "result": {
                "message": "I am the Follow-up Agent. I can schedule follow-ups or send reminders."
            }
        }