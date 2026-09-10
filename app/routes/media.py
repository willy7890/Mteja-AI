# backend/app/routers/media.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.media_service import (
    create_media_asset,
    get_media_asset_for_org,
    MediaValidationError,
)
from app.services.conversation_service import get_conversation_or_404  
from app.core.security import get_current_user  
from app.schemas.media_assets import MediaAssetResponse

router = APIRouter()


@router.post("/conversations/{conversation_id}/media", response_model=dict)
async def upload_media(
    conversation_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
   
    conversation = await get_conversation_or_404(
        db, conversation_id, current_user.organization_id
    )

   
    contents = await file.read()

    try:
        asset = await create_media_asset(
            db,
            contents=contents,
            mime_type=file.content_type,
            conversation=conversation,
        )
    except MediaValidationError as e:
       
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "reference_id": asset.reference_id,
        "status": "uploaded",
        "message": "uploaded succesfully",
    }


@router.get("/media/{reference_id}", response_model=MediaAssetResponse)
async def get_media(
    reference_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    asset = await get_media_asset_for_org(
        db, reference_id, current_user.organization_id
    )

    if asset is None:
        raise HTTPException(status_code=404, detail="Media not found")

    return asset