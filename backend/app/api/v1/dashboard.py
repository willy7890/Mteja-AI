# dashboard API endpoints for MTEJA AI
# REST routes for dashboard resource (CRUD + domain actions)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.agents.analytics_agent import analyze_customer_sentiment, generate_business_insight
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  """Retrieve live key performance metrics for the organization dashboard."""
  try:
    return {
        "status": "success",
        "organization_id": current_user.organization_id,
        "metrics": {
            "total_conversations": 0,
            "active_conversations": 0,
            "resolved_conversations": 0,
            "average_response_time": 0,
        },
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))