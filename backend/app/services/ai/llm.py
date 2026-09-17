import os
from langchain_openai import ChatOpenAI


def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        max_tokens=600,
        timeout=30,
    )