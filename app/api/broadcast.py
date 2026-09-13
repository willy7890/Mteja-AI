from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role

from app.schemas.broadcast import (
    BroadcastCreateRequest,
    BroadcastCampaignOut,
    BroadcastListResponse,
    BroadcastScheduleRequest,
    BroadcastRecipientListResponse,
)
from app.models.broadcast import RecipientStatus
from app.services.broadcast import BroadcastService,BroadcastError,CampaignNotFoundError,CampaignNotSendableError,CampaignNotScheduleableError
from app.services.rate_limit import enforce_rate_limit
from app.services.audience import DefaultAudienceResolver
from app.services.outbound import ToolQueueClient

router = APIRouter(prefix="/api/v1/broadcasts", tags=["broadcasts"])


def get_broadcast_service(db: AsyncSession = Depends(get_db)) -> BroadcastService:
    return BroadcastService(
        db=db,
        audience_resolver=DefaultAudienceResolver(db),
        queue_client=ToolQueueClient(),
    )


@router.post(
    "",
    response_model=BroadcastCampaignOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_broadcast(
    payload: BroadcastCreateRequest,
    current_user=Depends(require_role("admin")),
    service: BroadcastService = Depends(get_broadcast_service),
):
    await enforce_rate_limit(
        key=f"broadcast_create:{current_user.organization_id}",
        max_calls=10,
        window_seconds=3600,
    )

    try:
        campaign = await service.create_campaign(
            organization_id=current_user.organization_id,
            created_by=current_user.id,
            payload=payload,
        )
    except BroadcastError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return campaign


@router.get(
    "",
    response_model=BroadcastListResponse,
)
async def list_broadcasts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(require_role("admin")),
    service: BroadcastService = Depends(get_broadcast_service),
):
    items, total = await service.list_campaigns(
        organization_id=current_user.organization_id, page=page, page_size=page_size
    )
    return BroadcastListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{campaign_id}",
    response_model=BroadcastCampaignOut,
)
async def get_broadcast(
    campaign_id: int,
    current_user=Depends(require_role("admin")),
    service: BroadcastService = Depends(get_broadcast_service),
):
    try:
        campaign = await service.get_campaign_by_id(
            organization_id=current_user.organization_id, campaign_id=campaign_id
        )
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return campaign


@router.post(
    "/{campaign_id}/send",
    response_model=BroadcastCampaignOut,
)
async def send_broadcast(
    campaign_id: int,
    current_user=Depends(require_role("admin")),
    service: BroadcastService = Depends(get_broadcast_service),
):
    await enforce_rate_limit(
        key=f"broadcast_send:{current_user.organization_id}",
        max_calls=10,
        window_seconds=3600,
    )

    try:
        campaign = await service.send_campaign(
            organization_id=current_user.organization_id, campaign_id=campaign_id
        )
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CampaignNotSendableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except BroadcastError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return campaign


@router.post(
    "/{campaign_id}/schedule",
    response_model=BroadcastCampaignOut,
)
async def schedule_broadcast(
    campaign_id: int,
    payload: BroadcastScheduleRequest,
    current_user=Depends(require_role("admin")),
    service: BroadcastService = Depends(get_broadcast_service),
):
    try:
        campaign = await service.schedule_campaign(
            organization_id=current_user.organization_id,
            campaign_id=campaign_id,
            scheduled_at=payload.scheduled_at,
        )
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CampaignNotScheduleableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return campaign


@router.get(
    "/{campaign_id}/recipients",
    response_model=BroadcastRecipientListResponse,
)
async def list_broadcast_recipients(
    campaign_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status_filter: RecipientStatus | None = Query(None, alias="status"),
    current_user=Depends(require_role("admin")),
    service: BroadcastService = Depends(get_broadcast_service),
):
    try:
        items, total = await service.list_recipients(
            organization_id=current_user.organization_id,
            campaign_id=campaign_id,
            page=page,
            page_size=page_size,
            status_filter=status_filter,
        )
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return BroadcastRecipientListResponse(items=items, total=total, page=page, page_size=page_size)