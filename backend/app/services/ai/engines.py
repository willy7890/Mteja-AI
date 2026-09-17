from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, HandlerType
from app.services.handoff_service import escalate_conversation


class AIEngine:
    async def process_chat_message(
        self,
        db: AsyncSession,
        conversation: Conversation,
        user_message: str,
    ) -> Dict[str, Any]:
        """Engine entry point: Bypasses AI generation if current_handler is HUMAN,
        and auto-escalates when AI detects handoff intent.
        """
        # 1. Check current handler state
        if conversation.current_handler == HandlerType.HUMAN.value:
            return {
                "handled_by": "human",
                "message": None,
                "escalated": False,
            }

        # 2. Check for escalation intent keywords/rules
        escalation_keywords = ["agent", "human", "representative", "support", "help desk"]
        if any(keyword in user_message.lower() for keyword in escalation_keywords):
            await escalate_conversation(
                db_session=db,
                conversation=conversation,
                reason=f"Auto-escalated by AI engine. Keyword matched in message: '{user_message}'",
                triggered_by="ai",
            )
            return {
                "handled_by": "ai",
                "message": "I'm transferring your request to a support agent now. Someone will be with you shortly.",
                "escalated": True,
            }

        # 3. Standard AI response generation logic
        ai_response = f"Thank you for reaching out. How else can I assist you with '{user_message}'?"
        return {
            "handled_by": "ai",
            "message": ai_response,
            "escalated": False,
        }


# Global instance imported by app.integrations.telegram.webhook
ai_engine = AIEngine()