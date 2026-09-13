from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.webhook_logs import WebhookLogListResponse, WebhookLogDetailOut, WebhookLogStatsResponse
from app.services.webhook_logs import WebhookLogService, WebhookLogNotFoundError

router = APIRouter(prefix="/api/v1/admin/webhooks", tags=["webhook-logs"])


def get_webhook_log_service(db: AsyncSession = Depends(get_db)) -> WebhookLogService:
    return WebhookLogService(db=db)


@router.get("/logs", response_model=WebhookLogListResponse)
async def list_webhook_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    channel: str | None = Query(None),
    direction: str | None = Query(None, pattern="^(inbound|outbound)$"),
    processing_status: str | None = Query(None, alias="status"),
    event_type: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user=Depends(require_admin),
    service: WebhookLogService = Depends(get_webhook_log_service),
):
    items, total = await service.list_logs(
        organization_id=current_user.organization_id,
        page=page,
        page_size=page_size,
        channel=channel,
        direction=direction,
        processing_status=processing_status,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )
    return WebhookLogListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/logs/stats", response_model=WebhookLogStatsResponse)
async def get_webhook_log_stats(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user=Depends(require_admin),
    service: WebhookLogService = Depends(get_webhook_log_service),
):
    result = await service.get_stats(
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
    )
    return result


@router.get("/logs/{log_id}", response_model=WebhookLogDetailOut)
async def get_webhook_log(
    log_id: int,
    current_user=Depends(require_admin),
    service: WebhookLogService = Depends(get_webhook_log_service),
):
    try:
        log = await service.get_log_by_id(organization_id=current_user.organization_id, log_id=log_id)
    except WebhookLogNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return log