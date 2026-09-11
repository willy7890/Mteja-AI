# followup_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution

from app.agents.base_agent import BaseAgent
from app.services.messaging_window import refresh_window_status
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

    async def execute(self, db, conversation):
        """
        Check the WhatsApp 24-hour messaging window before sending
        a proactive follow-up. Falls back to a template if the window
        has closed.
        """
        window_status = await refresh_window_status(db, conversation)

        if window_status == "closed":
            return await self.send_template_followup(db, conversation)

        return await self.send_normal_followup(db, conversation)

    async def send_template_followup(self, db, conversation):
        # TODO: implement approved WhatsApp template sending
        raise NotImplementedError("Template-based follow-up not yet implemented")

    async def send_normal_followup(self, db, conversation):
        # TODO: implement normal free-form follow-up sending
        raise NotImplementedError("Normal follow-up sending not yet implemented")