from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user  
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.media import MediaFile
from app.services.media_service import MediaService
from app.schemas.media import MediaFileResponse

router = APIRouter(prefix="/media", tags=["Media"])


async def get_conversation_for_user(conversation_id: int, current_user: User, db: AsyncSession):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.post("/upload", response_model=MediaFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_customer_picture(
    file: UploadFile = File(...),
    conversation_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    conversation = await get_conversation_for_user(conversation_id, current_user, db)

 
    media = await MediaService.save_image(
        db=db,
        file=file,
        customer_id=conversation.customer_id,
        organization_id=current_user.organization_id,
        conversation_id=conversation_id,
    )

    return media


@router.get("", response_model=list[MediaFileResponse])
async def list_conversation_media(
    conversation_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_conversation_for_user(conversation_id, current_user, db)
    result = await db.execute(
        select(MediaFile)
        .where(
            MediaFile.conversation_id == conversation_id,
            MediaFile.organization_id == current_user.organization_id,
        )
        .order_by(MediaFile.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{media_id}", response_model=MediaFileResponse)
async def get_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MediaFile).where(
            MediaFile.id == media_id,
            MediaFile.organization_id == current_user.organization_id,
        )
    )
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")
    return media


@router.post("/{media_id}/attach", response_model=MediaFileResponse)
async def attach_media_to_message(
    media_id: int,
    message_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    media_result = await db.execute(
        select(MediaFile).where(
            MediaFile.id == media_id,
            MediaFile.organization_id == current_user.organization_id,
        )
    )
    media = media_result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")

    message_result = await db.execute(
        select(Message).join(Conversation).where(
            Message.id == message_id,
            Message.conversation_id == media.conversation_id,
            Conversation.organization_id == current_user.organization_id,
        )
    )
    if message_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    media.message_id = message_id
    await db.commit()
    await db.refresh(media)
    return media


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MediaFile).where(
            MediaFile.id == media_id,
            MediaFile.organization_id == current_user.organization_id,
        )
    )
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")

    try:
        import os
        os.remove(media.file_path)
    except FileNotFoundError:
        pass
    await db.delete(media)
    await db.commit()
