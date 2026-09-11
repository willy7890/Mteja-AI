from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MediaFileResponse(BaseModel):
    id: int
    filename: str
    file_url: str
    content_type: str
    file_size: int
    conversation_id: Optional[int] = None
    message_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True