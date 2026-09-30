from typing import Any
from app.tools.base_tool import BaseTool


class ScheduleFollowUpTool(BaseTool):
    name = "schedule_followup"
    description = "Schedules a follow-up with a customer"

    async def run(self, **kwargs) -> Any:
        customer_name = kwargs.get("customer_name", "")
        days = kwargs.get("days", 1)

        return {
            "status": "scheduled",
            "message": f"Follow-up for {customer_name} has been scheduled in {days} day(s)"
        }


class SendReminderTool(BaseTool):
    name = "send_reminder"
    description = "Sends a reminder to a customer"

    async def run(self, **kwargs) -> Any:
        customer_name = kwargs.get("customer_name", "")
        message = kwargs.get("message", "")

        return {
            "status": "sent",
            "message": f"Reminder sent to {customer_name}: {message}"
        }



FOLLOWUP_TOOLS = [
    ScheduleFollowUpTool(),
    SendReminderTool(),
]