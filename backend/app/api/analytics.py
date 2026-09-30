from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.analytics import (
    AnalyticsDateRange,
    AnalyticsOverviewResponse,
    ConversationAnalyticsResponse,
    AIPerformanceResponse,
    ChannelAnalyticsResponse,
    ResponseTimeResponse,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db=db)


def _validate_date_range(start_date: date, end_date: date) -> None:
    try:
        AnalyticsDateRange(start_date=start_date, end_date=end_date)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.errors()[0]["msg"],
        ) from exc


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user=Depends(require_admin),
    service: AnalyticsService = Depends(get_analytics_service),
):
    _validate_date_range(start_date, end_date)
    return await service.get_overview(
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/conversations", response_model=ConversationAnalyticsResponse)
async def get_analytics_conversations(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user=Depends(require_admin),
    service: AnalyticsService = Depends(get_analytics_service),
):
    _validate_date_range(start_date, end_date)
    return await service.get_conversation_analytics(
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/ai-performance", response_model=AIPerformanceResponse)
async def get_analytics_ai_performance(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user=Depends(require_admin),
    service: AnalyticsService = Depends(get_analytics_service),
):
    _validate_date_range(start_date, end_date)
    return await service.get_ai_performance(
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/channels", response_model=ChannelAnalyticsResponse)
async def get_analytics_channels(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user=Depends(require_admin),
    service: AnalyticsService = Depends(get_analytics_service),
):
    _validate_date_range(start_date, end_date)
    return await service.get_channel_analytics(
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/response-times", response_model=ResponseTimeResponse)
async def get_analytics_response_times(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user=Depends(require_admin),
    service: AnalyticsService = Depends(get_analytics_service),
):
    _validate_date_range(start_date, end_date)
    return await service.get_response_times(
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
    )