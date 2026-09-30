import os
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.services.classification_service import classifier_service
from app.services.knowledge_service import kb_service
from app.services.language_detection_service import LanguageDetectionService

# Define categories that MUST always go to human agents
HUMAN_ONLY_CATEGORIES = [
    "complaint",
    "pricing_dispute",
    "refund",
    "legal",
    "human_request",
]
CONFIDENCE_THRESHOLD = 0.65  # If ML model confidence is < 65%, escalate


def requires_human_handoff(user_message: str) -> bool:
    prediction = classifier_service.classify_message(user_message)
    return (
        prediction.get("category") in HUMAN_ONLY_CATEGORIES
        or prediction.get("confidence", 0.0) < CONFIDENCE_THRESHOLD
    )


def get_llm() -> ChatOpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(model="gpt-4o", temperature=0.3)


async def generate_agent_reply(user_message: str) -> str:
    """Generate a contextual agent reply using ML classification, KB search, and LLM."""
    # 1. ML Classification Guard
    prediction = classifier_service.classify_message(user_message)
    category = prediction.get("category")
    confidence = prediction.get("confidence", 0.0)

    if category in HUMAN_ONLY_CATEGORIES or confidence < CONFIDENCE_THRESHOLD:
        return "I need a human agent to review your message. Someone will reply shortly."

    # 2. Detect language / Sheng / code-switching
    detection = LanguageDetectionService.detect(user_message)

    # 3. Retrieve relevant knowledge
    retrieved_context = kb_service.search(user_message, k=2)

    # 4. Build system prompt with language context
    system_prompt = f"""
You are MtejaAI, an AI customer support assistant for a Tanzanian business.

Customer language detection:
- Detected language: {detection['language']}
- Dominant language: {detection['dominant_language']}
- Is Sheng: {detection['is_sheng']}
- Is Code-Switching: {detection['is_code_switching']}

Instructions:
- Respond in a natural way that matches the customer's language style.
- If the customer is using Sheng, reply in a friendly Sheng or mixed style.
- If the customer is mixing Kiswahili and English, you can also mix naturally.
- If the customer is using pure Kiswahili, reply mainly in Kiswahili.
- If the customer is using pure English, reply in English.
- Always be clear, helpful and professional.

Use ONLY the following knowledge base context to answer the customer's question accurately.
If the answer is not in the knowledge base, politely state that you cannot help and offer to hand over to human staff.

Knowledge Base:
{retrieved_context}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    llm = get_llm()
    if llm is None:
        return kb_service.best_answer(user_message) or (
            f"Thank you for asking about {category}. How can we assist you further?"
        )

    try:
        response = await llm.ainvoke(messages)
        return str(response.content)
    except Exception:
        return f"Thank you for asking about {category}. How can we assist you further?"


async def handle_inbound_message(
    db: AsyncSession,
    organization_id: int,
    contact_id: str,
    message_text: str,
) -> Dict[str, Any]:
    """Handle inbound user message with classification and escalation logic."""
    # 1. Run trained ML Model on customer message
    prediction = classifier_service.classify_message(message_text)
    category = prediction.get("category")
    confidence = prediction.get("confidence", 0.0)

    # 2. Check if Escalation is required
    is_dispute_category = category in HUMAN_ONLY_CATEGORIES
    is_low_confidence = confidence < CONFIDENCE_THRESHOLD

    if is_dispute_category or is_low_confidence:
        return {
            "status": "ESCALATED",
            "category": category,
            "confidence": confidence,
            "reply": "Your message has been routed to our support team. An agent will reply shortly.",
        }

    # 3. Standard AI Response via LLM Engine
    ai_reply = await generate_agent_reply(message_text)

    return {
        "status": "AI_REPLIED",
        "category": category,
        "confidence": confidence,
        "reply": ai_reply,
    }