from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user  
from app.models.user import User
from app.models.conversation import Conversation
from app.services.media_service import MediaService
from app.schemas.media import MediaFileResponse

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/upload", response_model=MediaFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_customer_picture(
    file: UploadFile = File(...),
    conversation_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

 
    media = await MediaService.save_image(
        db=db,
        file=file,
        customer_id=conversation.customer_id,
        organization_id=current_user.organization_id,
        conversation_id=conversation_id,
    )

    return media