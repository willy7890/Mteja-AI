import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.media import MediaFile

# Configuration
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "customers"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
VOICE_CONTENT_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "audio/x-m4a",
    "audio/x-wav",
    "application/ogg",
    "audio/aac",
    "video/webm",
}
VOICE_EXTENSIONS = {".aac", ".mp3", ".m4a", ".ogg", ".wav", ".webm", ".mp4", ".mpeg"}
MAX_VOICE_FILE_SIZE = 25 * 1024 * 1024


class MediaService:

    @staticmethod
    def validate_voice(file: UploadFile) -> None:
        extension = os.path.splitext(file.filename or "")[1].lower()
        if file.content_type not in VOICE_CONTENT_TYPES or extension not in VOICE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported audio format. Use MP3, M4A, OGG, WAV, WEBM, or MPEG audio.",
            )

    @staticmethod
    def validate_voice_bytes(content: bytes, content_type: str | None) -> None:
        signatures = (
            content.startswith(b"ID3"),
            content[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"},
            content.startswith(b"RIFF") and content[8:12] == b"WAVE",
            content.startswith(b"OggS"),
            content.startswith(b"\x1a\x45\xdf\xa3"),
            len(content) > 12 and content[4:8] == b"ftyp",
        )
        if not any(signatures):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a recognized audio file",
            )

    @staticmethod
    async def save_voice(
        db: AsyncSession,
        file: UploadFile,
        customer_id: int,
        organization_id: int,
        conversation_id: int,
        message_id: int | None = None,
    ) -> MediaFile:
        MediaService.validate_voice(file)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty audio file is not allowed")
        if len(content) > MAX_VOICE_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Audio file exceeds the 25MB limit")
        MediaService.validate_voice_bytes(content, file.content_type)

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        extension = os.path.splitext(file.filename or "")[1].lower()
        stored_filename = f"{uuid.uuid4().hex}{extension}"
        file_path = UPLOAD_DIR / stored_filename
        file_path.write_bytes(content)
        media = MediaFile(
            customer_id=customer_id,
            organization_id=organization_id,
            conversation_id=conversation_id,
            message_id=message_id,
            filename=file.filename or stored_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_url=f"/uploads/customers/{stored_filename}",
            content_type=file.content_type or "application/octet-stream",
            file_size=len(content),
        )
        db.add(media)
        await db.flush()
        return media

    @staticmethod
    def validate_image(file: UploadFile) -> None:
        # Check content type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, JPEG and PNG images are allowed"
            )

        # Check extension
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file extension. Allowed: .jpg, .jpeg, .png"
            )

    @staticmethod
    async def save_image(
        db: AsyncSession,
        file: UploadFile,
        customer_id: int,
        organization_id: int,
        conversation_id: int | None = None,
        message_id: int | None = None,
    ) -> MediaFile:
        # Validate
        MediaService.validate_image(file)

        # Read file content to check size
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 5MB"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file is not allowed"
            )

        # Create upload directory if not exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        ext = os.path.splitext(file.filename or "")[1].lower()
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / stored_filename

        # Save file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Public URL (adjust according to your setup)
        file_url = f"/uploads/customers/{stored_filename}"

        media = MediaFile(
            customer_id=customer_id,
            organization_id=organization_id,
            conversation_id=conversation_id,
            message_id=message_id,
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_url=file_url,
            content_type=file.content_type,
            file_size=file_size,
        )

        db.add(media)
        await db.commit()
        await db.refresh(media)

        return media