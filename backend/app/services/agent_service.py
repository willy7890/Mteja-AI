from sqlalchemy.ext.asyncio import AsyncSession
from app.services.classification_service import classifier_service

# Define categories that MUST always go to human agents
HUMAN_ONLY_CATEGORIES = ["complaint", "pricing_dispute", "refund", "legal", "human_request"]
CONFIDENCE_THRESHOLD = 0.65  # If ML model confidence is < 65%, escalate


async def generate_agent_reply(message_text: str) -> str:
    """Generate a bounded reply using the trained message classifier."""
    prediction = classifier_service.classify_message(message_text)
    category = prediction["category"]
    confidence = prediction["confidence"]

    if confidence < CONFIDENCE_THRESHOLD:
        return "I need a human agent to review your message. Someone will reply shortly."
    return f"Thank you for asking about {category}. How can we assist you further?"

async def handle_inbound_message(
    db: AsyncSession,
    organization_id: int,
    contact_id: str,
    message_text: str
):
    # 1. Run trained ML Model on customer message
    prediction = classifier_service.classify_message(message_text)
    category = prediction["category"]
    confidence = prediction["confidence"]

    print(f"ML Analysis -> Category: '{category}', Confidence: {confidence}")

    # 2. Check if Escalation is required
    is_dispute_category = category in HUMAN_ONLY_CATEGORIES
    is_low_confidence = confidence < CONFIDENCE_THRESHOLD

    if is_dispute_category or is_low_confidence:
        reason = f"ML Category '{category}' requires human attention" if is_dispute_category else f"Low AI Confidence ({confidence:.2f})"

        # Trigger Issue #59 Handoff
        # Handoff persistence is handled by the channel-specific workflow.
        return {
            "status": "ESCALATED",
            "category": category,
            "confidence": confidence,
            "reply": "Your message has been routed to our support team. An agent will reply shortly."
        }

    # 3. Standard AI Response (If confidence is high & safe category)
    ai_reply = f"Thank you for asking about {category}. How can we assist you further?"
    
    return {
        "status": "AI_REPLIED",
        "category": category,
        "confidence": confidence,
        "reply": ai_reply
    }