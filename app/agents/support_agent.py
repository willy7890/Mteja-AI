# support_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
# support_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution

from app.agents.base_agent import BaseAgent
from app.tools.support_tools import SUPPORT_TOOLS


class SupportAgent(BaseAgent):
    
    def __init__(self):
        super().__init__(
            name="support_agent",
            tools=SUPPORT_TOOLS
        )

    async def handle(self, message: str) -> dict:
        message_lower = message.lower()

        if "status" in message_lower or "where is my order" in message_lower or "track" in message_lower:
            result = await self.call_tool(
                "check_order_status",
                order_id="unknown"
            )
            return {
                "agent": self.name,
                "action": "check_order_status",
                "result": result
            }

        elif "problem" in message_lower or "issue" in message_lower or "help" in message_lower or "complaint" in message_lower:
            result = await self.call_tool(
                "create_support_ticket",
                customer_name="customer",
                issue=message
            )
            return {
                "agent": self.name,
                "action": "create_support_ticket",
                "result": result
            }

        return {
            "agent": self.name,
            "action": "none",
            "result": {
                "message": "I am the Support Agent. I can check order status or open a support ticket."
            }
        }