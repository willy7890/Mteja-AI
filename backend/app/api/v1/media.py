import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user  
from app.api.dependencies import get_message_service
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.media import MediaFile
from app.services.media_service import MediaService, UPLOAD_DIR
from app.services.voice_service import VoiceProcessingError, synthesize_speech, transcribe_audio, voice_http_error
from app.services.agent_service import generate_agent_reply
from app.services.message import MessageService
from app.core.config import settings
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


@router.post("/voice-note", status_code=status.HTTP_201_CREATED)
async def upload_voice_note(
    file: UploadFile = File(...),
    conversation_id: int = Form(...),
    include_voice_response: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
):
    conversation = await get_conversation_for_user(conversation_id, current_user, db)
    media = await MediaService.save_voice(
        db=db,
        file=file,
        customer_id=conversation.customer_id,
        organization_id=current_user.organization_id,
        conversation_id=conversation_id,
    )
    try:
        transcript = await transcribe_audio(media.file_path, media.filename)
        reply_text = await generate_agent_reply(transcript) if conversation.mode == "ai" else None
    except VoiceProcessingError as exc:
        await db.rollback()
        try:
            Path(media.file_path).unlink(missing_ok=True)
        except OSError:
            pass
        raise voice_http_error(exc) from exc

    message = Message(
        conversation_id=conversation_id,
        content=transcript,
        sender_type="customer",
        sender_name="Customer",
        direction="inbound",
        channel=conversation.channel,
        status="delivered",
        channel_metadata={"voice_media_id": media.id, "transcription_model": settings.VOICE_TRANSCRIPTION_MODEL},
    )
    db.add(message)
    await db.flush()
    media.message_id = message.id

    response_media = None
    response_message = None
    if reply_text:
        if conversation.channel in message_service.adapters and conversation.external_participant_id:
            response_message = await message_service.send(
                db=db,
                organization_id=current_user.organization_id,
                conversation_id=conversation_id,
                content=reply_text,
                channel=conversation.channel,
                sender_type="ai",
                sender_name="MtejaAI",
            )
        else:
            response_message = Message(
                conversation_id=conversation_id,
                content=reply_text,
                sender_type="ai",
                sender_name="MtejaAI",
                direction="outbound",
                channel=conversation.channel,
                status="sent",
            )
            db.add(response_message)
            await db.flush()
        if include_voice_response:
            output_name = f"{uuid.uuid4().hex}.mp3"
            output_path = UPLOAD_DIR / output_name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                await synthesize_speech(reply_text, str(output_path))
            except VoiceProcessingError as exc:
                await db.rollback()
                raise voice_http_error(exc) from exc
            response_media = MediaFile(
                customer_id=conversation.customer_id,
                organization_id=current_user.organization_id,
                conversation_id=conversation_id,
                message_id=response_message.id,
                filename=output_name,
                stored_filename=output_name,
                file_path=str(output_path),
                file_url=f"/uploads/customers/{output_name}",
                content_type="audio/mpeg",
                file_size=output_path.stat().st_size,
            )
            db.add(response_media)
    await db.commit()
    await db.refresh(message)
    if response_message:
        await db.refresh(response_message)
    if response_media:
        await db.refresh(response_media)
    return {
        "media": media,
        "transcript": transcript,
        "response": response_message,
        "response_audio": response_media,
    }


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
