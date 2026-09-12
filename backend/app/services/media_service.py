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


class MediaService:

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