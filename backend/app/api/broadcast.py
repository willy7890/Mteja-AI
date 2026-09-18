
import os
import uuid
 

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.broadcast import CampaignStatus
from app.schemas.broadcast import (
    BroadcastCampaignCreate, BroadcastCampaignOut, BroadcastCampaignList,
    BroadcastCampaignScheduleRequest, BroadcastRecipientOut, CampaignMetrics,
)
from app.services import broadcast_service
from app.rate_limit import rate_limit




MEDIA_DIR = "static/broadcast_media"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
 


router = APIRouter(prefix="/broadcasts", tags=["Broadcast Messaging"])


async def require_admin(user: User = Depends(get_current_user)) -> User:
    # same rule as admin.py - superuser, or org admin/owner role
    if not user.is_superuser and user.role not in {UserRole.ADMIN, UserRole.OWNER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


async def _get_campaign_or_404(db: AsyncSession, campaign_id: int, organization_id: int):
    campaign = await broadcast_service.get_campaign(db, campaign_id, organization_id)
    if not campaign:
        # 404 not 403 - don't confirm cross-org ids exist
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return campaign


async def _to_out(db: AsyncSession, campaign) -> BroadcastCampaignOut:
    metrics = await broadcast_service.aggregate_metrics(db, campaign.id)
    out = BroadcastCampaignOut.model_validate(campaign)
    out.metrics = CampaignMetrics(**{k: v for k, v in metrics.items() if k in CampaignMetrics.model_fields})
    return out




@router.post("/upload-media", status_code=status.HTTP_201_CREATED)
async def upload_broadcast_media(file: UploadFile = File(...), current_user: User = Depends(require_admin)):
    """
    Upload a promo image. Returns {"media_url": "..."} - pass that
    straight into media_url when creating the campaign.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WEBP images are allowed")
 
    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
 
    os.makedirs(MEDIA_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(MEDIA_DIR, filename)
 
    with open(filepath, "wb") as f:
        f.write(contents)
 
    # served via app.mount("/static", StaticFiles(directory="static")) in main.py
    return {"media_url": f"/static/broadcast_media/{filename}"}
 





@router.post("", response_model=BroadcastCampaignOut, status_code=status.HTTP_201_CREATED)
async def create_broadcast(payload: BroadcastCampaignCreate, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    campaign = await broadcast_service.create_campaign(
        db, organization_id=current_user.organization_id, created_by=current_user.id, payload=payload
    )
    return await _to_out(db, campaign)


@router.get("", response_model=BroadcastCampaignList)
async def list_broadcasts(current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    campaigns = await broadcast_service.list_campaigns(db, current_user.organization_id)
    return BroadcastCampaignList(items=[await _to_out(db, c) for c in campaigns], total=len(campaigns))


@router.get("/{broadcast_id}", response_model=BroadcastCampaignOut)
async def get_broadcast(broadcast_id: int, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign_or_404(db, broadcast_id, current_user.organization_id)
    return await _to_out(db, campaign)


@router.get("/{broadcast_id}/recipients", response_model=list[BroadcastRecipientOut])
async def get_broadcast_recipients(broadcast_id: int, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    await _get_campaign_or_404(db, broadcast_id, current_user.organization_id)  # 404 check
    return await broadcast_service.get_recipients(db, broadcast_id, current_user.organization_id)


@router.post("/{broadcast_id}/send", response_model=BroadcastCampaignOut)
@rate_limit("5/minute")  # bulk sends should be rare and deliberate
async def send_broadcast(broadcast_id: int, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign_or_404(db, broadcast_id, current_user.organization_id)
    if campaign.status not in (CampaignStatus.draft, CampaignStatus.scheduled):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot send from status '{campaign.status.value}'")

    customers = await broadcast_service.resolve_audience(
        db, organization_id=current_user.organization_id, audience_filter=campaign.audience_filter
    )
    await broadcast_service.build_recipients(db, campaign, customers)
    campaign = await broadcast_service.dispatch_campaign(db, campaign, approved_by=current_user.id)
    return await _to_out(db, campaign)


@router.post("/{broadcast_id}/schedule", response_model=BroadcastCampaignOut)
@rate_limit("10/minute")
async def schedule_broadcast(broadcast_id: int, payload: BroadcastCampaignScheduleRequest,
                              current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign_or_404(db, broadcast_id, current_user.organization_id)
    if campaign.status != CampaignStatus.draft:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Only draft campaigns can be scheduled (current: '{campaign.status.value}')")

    campaign.status = CampaignStatus.scheduled
    campaign.scheduled_at = payload.scheduled_at
    await db.commit()
    await db.refresh(campaign)
    # actual dispatch at scheduled_at should be a scheduled job calling dispatch_campaign() directly
    return await _to_out(db, campaign)