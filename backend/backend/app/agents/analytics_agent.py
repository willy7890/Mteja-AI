# analytics_agent for MTEJA AI agentic system
# Specialized agent logic, tool selection, and controlled execution
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


def get_llm():
  """Initialize the chat model for analytics"""
  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    return None
  return ChatOpenAI(model="gpt-4o", temperature=0.1)


async def analyze_customer_sentiment(message_content: str) -> str:
  """Analyze customer message sentiment and intent for analytics logging."""
  llm = get_llm()
  if not llm:
    return "neutral"

  system_prompt = (
      "You are an analytics assistant for MtejaAI. Analyze the incoming"
      " customer message and classify its sentiment into exactly one of these"
      " categories: 'positive', 'neutral', 'negative', or 'urgent_escalation'."
      " Return ONLY the category name."
  )

  messages = [
      SystemMessage(content=system_prompt),
      HumanMessage(content=message_content),
  ]

  response = await llm.ainvoke(messages)
  return response.content.strip().lower()


async def generate_business_insight(conversation_summary: str) -> str:
  """Generate business insights based on recent customer conversations and trends."""
  llm = get_llm()
  if not llm:
    return "Analytics unavailable: Missing OpenAI API Key."

  system_prompt = (
      "You are a business intelligence assistant for MtejaAI in Tanzania."
      " Review the provided conversation summaries and synthesize 3 key"
      " operational insights or recurring customer pain points to help staff"
      " improve service."
  )

  messages = [
      SystemMessage(content=system_prompt),
      HumanMessage(content=conversation_summary),
  ]

  response = await llm.ainvoke(messages)
  return response.content