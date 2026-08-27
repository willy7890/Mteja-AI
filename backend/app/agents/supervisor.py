# Supervisor for MTEJA AI agentic system
# Analyzes user intent and routes the message to the correct agent

from typing import Literal


class Supervisor:

    def analyze_intent(self, message: str) -> Literal["marketing", "followup", "sales", "unknown"]:
        message = message.lower()

        marketing_keywords = [
            "campaign", "ads", "marketing", "promotion",
            "facebook", "instagram", "advert", "content",
            "brand", "audience"
        ]

        followup_keywords = [
            "follow up", "follow-up", "reminder", "schedule",
            "call back", "check in", "next step", "followup"
        ]

        sales_keywords = [
            "price", "cost", "how much", "buy", "order",
            "purchase", "payment", "discount"
        ]

        support_keywords = [
        "problem", "issue", "help", "complaint",
        "not working", "broken", "status", "track", "refund"
    ]

        for word in marketing_keywords:
            if word in message:
                return "marketing"

        for word in followup_keywords:
            if word in message:
                return "followup"

        for word in sales_keywords:
            if word in message:
                return "sales"

        return "unknown"

    def route(self, message: str) -> str:
        intent = self.analyze_intent(message)

        if intent == "marketing":
            return "marketing_agent"
        elif intent == "followup":
            return "followup_agent"
        elif intent == "sales":
            return "sales_agent"
        else:
            return "unknown"