from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MediaAssetBase(BaseModel):
    mime_type: str
    size_bytes: int


class MediaAssetCreate(MediaAssetBase):
   
    organization_id: int
    customer_id: int
    conversation_id: int
    storage_path: str
    reference_id: str


class MediaAssetResponse(BaseModel):
   
    model_config = ConfigDict(from_attributes=True)

    reference_id: str
    mime_type: str
    size_bytes: int
    created_at: datetime


class MediaUploadResponse(BaseModel):

    reference_id: str
    status: str = "uploaded"
    message: str 