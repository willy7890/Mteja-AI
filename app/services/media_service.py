import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media_assets import MediaAsset
from app.models.conversation import Conversation


ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  
UPLOAD_BASE_DIR = "uploads" 


class MediaValidationError(Exception):
    """Custom exception - router itaishika na kurudisha HTTP error sahihi"""
    pass


def validate_media(mime_type: str, size_bytes: int) -> None:
    if mime_type not in ALLOWED_MIME_TYPES:
        raise MediaValidationError("This file is not accepted. Use JPG or PNG.")
    if size_bytes > MAX_SIZE_BYTES:
        raise MediaValidationError(f"An image must not greater than {MAX_SIZE_BYTES // (1024*1024)}MB.")


def generate_storage_path(organization_id: int, mime_type: str) -> tuple[str, str]:
    """Inarudisha (reference_id, storage_path) - jina salama, si la mtumiaji"""
    reference_id = str(uuid.uuid4())
    ext = mime_type.split("/")[-1].replace("jpeg", "jpg")
    storage_path = f"org_{organization_id}/{reference_id}.{ext}"
    return reference_id, storage_path


def save_file_to_disk(contents: bytes, storage_path: str) -> None:
    full_path = os.path.join(UPLOAD_BASE_DIR, storage_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(contents)


async def create_media_asset(
    db: AsyncSession,
    *,
    contents: bytes,
    mime_type: str,
    conversation: Conversation,
): 
    size_bytes = len(contents)

    
    validate_media(mime_type, size_bytes)

    
    reference_id, storage_path = generate_storage_path(conversation.organization_id, mime_type)

    save_file_to_disk(contents, storage_path)


    asset = MediaAsset(
        reference_id=reference_id,
        organization_id=conversation.organization_id,
        customer_id=conversation.customer_id,
        conversation_id=conversation.id,
        storage_path=storage_path,
        mime_type=mime_type,
        size_bytes=size_bytes,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return asset


async def get_media_asset_for_org(
    db: AsyncSession, reference_id: str, organization_id: int):
    from sqlalchemy import select

    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.reference_id == reference_id,
            MediaAsset.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()