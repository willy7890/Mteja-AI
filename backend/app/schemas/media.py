from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MediaFileResponse(BaseModel):
    id: int
    filename: str
    file_url: str
    content_type: str
    file_size: int
    conversation_id: int | None = None
    message_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
