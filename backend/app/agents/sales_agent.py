# sales_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution

from app.agents.base_agent import BaseAgent
from app.tools.sales_tools import SALES_TOOLS


class SalesAgent(BaseAgent):
    

    def __init__(self):
        super().__init__(
            name="sales_agent",
            tools=SALES_TOOLS
        )

    async def handle(self, message: str) -> dict:
        message_lower = message.lower()

        if "price" in message_lower or "cost" in message_lower or "how much" in message_lower:
            result = await self.call_tool(
                "get_product_price",
                product="product"
            )
            return {
                "agent": self.name,
                "action": "get_product_price",
                "result": result
            }

        elif "order" in message_lower or "buy" in message_lower or "purchase" in message_lower:
            result = await self.call_tool(
                "create_order",
                customer_name="customer",
                product="product"
            )
            return {
                "agent": self.name,
                "action": "create_order",
                "result": result
            }

        return {
            "agent": self.name,
            "action": "none",
            "result": {
                "message": "I am the Sales Agent. I can help with pricing or placing an order."
            }
        }