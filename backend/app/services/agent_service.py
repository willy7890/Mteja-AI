import os
from app.services.knowledge_service import kb_service
from app.services.language_detection_service import LanguageDetectionService
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(model="gpt-4o", temperature=0.3)


async def generate_agent_reply(user_message: str) -> str:
    # 1. Detect language / Sheng / code-switching
    detection = LanguageDetectionService.detect(user_message)

    # 2. Retrieve relevant knowledge
    retrieved_context = kb_service.search(user_message, k=2)

    # 3. Build system prompt with language context
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
        return "Samahani, sijaweza kuchakata ombi lako kwa sasa. Tafadhali wasiliana na timu yetu ya msaada."

    response = await llm.ainvoke(messages)
    return response.content