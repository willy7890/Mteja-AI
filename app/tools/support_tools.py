from typing import Any
from app.tools.base_tool import BaseTool


class CheckOrderStatusTool(BaseTool):
    name = "check_order_status"
    description = "Checks the status of a customer's order"

    async def run(self, **kwargs) -> Any:
        order_id = kwargs.get("order_id", "")

        return {
            "order_id": order_id,
            "status": "processing",  # dummy for now
        }


class CreateSupportTicketTool(BaseTool):
    name = "create_support_ticket"
    description = "Creates a support ticket for a customer issue"

    async def run(self, **kwargs) -> Any:
        customer_name = kwargs.get("customer_name", "")
        issue = kwargs.get("issue", "")

        return {
            "status": "ticket_created",
            "message": f"Support ticket created for {customer_name}: {issue}",
        }



SUPPORT_TOOLS = [
    CheckOrderStatusTool(),
    CreateSupportTicketTool(),
]