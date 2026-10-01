import os
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# App Imports
from app.services.knowledge_service import kb_service

# 1. Anzisha LLM Model
llm = ChatOpenAI(
    model="gpt-3.5-turbo", # Au "llama3-8b-8192" kama unatumia Groq
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY", "")
)

# 2. Tengeneza System Prompt ya Mazungumzo
SYSTEM_PROMPT = """
Wewe ni Mteja AI, msaidizi rasmi wa huduma kwa wateja.
Kazi yako ni kujibu maswali ya mteja kwa ustaarabu, umakini, na lugha iliyonyooka (Kiswahili au Kiingereza).

Miongozo ya Kazi:
1. Tumia TAARIFA ZILIZOPO KWENYE KNOWLEDGE BASE (Trained Data) pekee kujibu maswali ya biashara au huduma.
2. Tumia HISTORIA YA MAZUNGUMZO kuelewa kile ambacho mteja anakirejelea (k.m. "bei gani?" inarejelea huduma mliyoizungumzia awali).
3. Kama jibu HAKIPO kwenye Trained Data, sema kwa adabu: 
   "Samahani, sina taarifa hizo kwa sasa. Nitaunganisha mazungumzo haya na mhudumu wetu ili akusaidie."
4. USITUNGE au kubuni taarifa ambazo hazipo kwenye Trained Data.

TRAINED DATA / KNOWLEDGE BASE CONTEXT:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

async def get_trained_rag_response(
    db_session: AsyncSession,
    user_id: str,
    user_query: str,
    chat_history_list: List[dict] = None
) -> str:
    """Inapokea swali la mteja, inasoma Trained Data (RAG), na kutengeneza jibu la mazungumzo kupitia LLM."""

    # ---------------------------------------------------------
    # HATUA YA 1: Pata Relevant Context kutoka Trained Data (RAG)
    # ---------------------------------------------------------
    context_str = ""
    
    if hasattr(kb_service, "similarity_search"):
        # Vector Store Search (kama una PGVector / FAISS)
        docs = await kb_service.similarity_search(user_query, k=3)
        context_str = "\n\n".join([doc.page_content for doc in docs])
    elif hasattr(kb_service, "documents"):
        # Text Match Fallback kwenye CSV / PDF Chunks
        query_words = user_query.lower().split()
        matched_chunks = []
        for doc in kb_service.documents:
            doc_text = getattr(doc, "page_content", str(doc)).lower()
            if any(word in doc_text for word in query_words):
                matched_chunks.append(getattr(doc, "page_content", str(doc)))
            if len(matched_chunks) >= 3:
                break
        context_str = "\n\n".join(matched_chunks)

    if not context_str:
        context_str = "Hakuna taarifa za ziada zilizopatikana kwenye Knowledge Base."

    # ---------------------------------------------------------
    # HATUA YA 2: Panga Historia ya Mazungumzo (Memory)
    # ---------------------------------------------------------
    formatted_history = []
    if chat_history_list:
        for msg in chat_history_list[-6:]: # Chukua ujumbe 6 wa mwisho (turn 3 za mazungumzo)
            if msg.get("role") == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                formatted_history.append(AIMessage(content=msg["content"]))

    # ---------------------------------------------------------
    # HATUA YA 3: Tuma kwenda kwenye LLM ili kupata Jibu
    # ---------------------------------------------------------
    try:
        chain = prompt | llm
        response = await chain.ainvoke({
            "context": context_str,
            "chat_history": formatted_history,
            "question": user_query
        })
        return response.content
    except Exception as e:
        print(f"⚠️ Error in RAG Conversation Engine: {e}")
        return "Samahani, mfumo unapitia changamoto kidogo. Jaribu tena baada ya muda mfupi."