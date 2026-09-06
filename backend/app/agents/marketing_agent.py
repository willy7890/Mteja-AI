# marketing_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
# marketing_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution

from app.agents.base_agent import BaseAgent
from app.tools.marketing_tools import MARKETING_TOOLS


class MarketingAgent(BaseAgent):
    
    def __init__(self):
        super().__init__(
            name="marketing_agent",
            tools=MARKETING_TOOLS
        )

    async def handle(self, message: str) -> dict:
        
        message_lower = message.lower()

        if "idea" in message_lower or "campaign" in message_lower or "ads" in message_lower:
            result = await self.call_tool(
                "get_campaign_ideas",
                product="product",
                audience="audience"
            )
            return {
                "agent": self.name,
                "action": "get_campaign_ideas",
                "result": result
            }

        elif "message" in message_lower or "copy" in message_lower:
            result = await self.call_tool(
                "create_marketing_message",
                product="product",
                tone="professional"
            )
            return {
                "agent": self.name,
                "action": "create_marketing_message",
                "result": result
            }

       
        return {
            "agent": self.name,
            "action": "none",
            "result": {
                "message": "I am the Marketing Agent. I can help with campaign ideas or marketing messages."
            }
        }