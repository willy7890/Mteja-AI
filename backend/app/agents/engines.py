import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def process_chat_message(conversation_id: int, message_content: str) -> Dict[str, Any]:
    """
    Inachakata ujumbe unaoingia kutoka kwa mteja na kutoa majibu ya AI.
    """
    logger.info(f"Processing message for conversation {conversation_id}: {message_content}")
    
    
    return {
        "reply": "Habari! Karibu Mteja AI. Nikiwa kama msaidizi wako, ninawezaje kukusaidia leo?",
        "handled_by": "ai"
    }