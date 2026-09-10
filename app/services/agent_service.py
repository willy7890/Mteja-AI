import os
from app.services.knowledge_service import kb_service
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


# Initialize LLM only if API key is available
def get_llm():
    """Get or initialize the LLM instance"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(model="gpt-4o", temperature=0.3)


async def generate_agent_reply(user_message: str) -> str:
  # 1. Retrieve relevant knowledge chunks based on the user's question
  retrieved_context = kb_service.search(user_message, k=2)

  # 2. Construct the system prompt with injected knowledge
  system_prompt = (
      "You are MtejaAI, an AI customer support assistant for a Tanzanian"
      " business.\nUse ONLY the following knowledge base context to answer the"
      " customer's question accurately.\nIf the answer is not in the knowledge"
      " base, politely state that you cannot help and offer to hand over to"
      f" human staff.\n\nKnowledge Base:\n{retrieved_context}"
  )

  messages = [
      SystemMessage(content=system_prompt),
      HumanMessage(content=user_message),
  ]

  llm = get_llm()
  if llm is None:
    # Return a default response if no API key is set
    return "I apologize, but I'm unable to process your request at this moment. Please contact our support team."

  response = await llm.ainvoke(messages)
  return response.content