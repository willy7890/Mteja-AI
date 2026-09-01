# agents API endpoints for MTEJA AI
# REST routes for agents resource (CRUD + domain actions)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.agents.analytics_agent import (
    analyze_customer_sentiment,
    generate_business_insight,
)
from app.services.knowledge_service import kb_service
from app.models.user import User

router = APIRouter(tags=["AI & Analytics Agent"])


class SentimentRequest(BaseModel):
  message: str


class InsightRequest(BaseModel):
  conversation_summary: str


class KnowledgeSearchRequest(BaseModel):
  query: str
  k: int = 2


@router.post("/sentiment", status_code=status.HTTP_200_OK)
async def analyze_sentiment_endpoint(
    payload: SentimentRequest,
    current_user: User = Depends(get_current_user),
):
  """Analyze customer sentiment and intent."""
  try:
    sentiment = await analyze_customer_sentiment(payload.message)
    return {"status": "success", "sentiment": sentiment}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights", status_code=status.HTTP_200_OK)
async def generate_insights_endpoint(
    payload: InsightRequest,
    current_user: User = Depends(get_current_user),
):
  """Generate business intelligence insights from conversation summaries."""
  try:
    insights = await generate_business_insight(payload.conversation_summary)
    return {"status": "success", "insights": insights}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-search", status_code=status.HTTP_200_OK)
async def search_knowledge_base_endpoint(
    payload: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user),
):
  """Test semantic search directly against the FAISS vector knowledge base."""
  try:
    results = kb_service.search(payload.query, k=payload.k)
    return {"status": "success", "query": payload.query, "results": results}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))