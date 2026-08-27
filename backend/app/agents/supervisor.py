# supervisor for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
# supervisor for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution




from typing import Literal


class Supervisor:
    

    def analyze_intent(self, message: str) -> Literal["marketing", "followup", "unknown"]:
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

        
        for word in marketing_keywords:
            if word in message:
                return "marketing"

        for word in followup_keywords:
            if word in message:
                return "followup"

        
        return "unknown"

    def route(self, message: str) -> str:
        
        intent = self.analyze_intent(message)

        if intent == "marketing":
            return "marketing_agent"
        elif intent == "followup":
            return "followup_agent"
        else:
            return "unknown"

