from datetime import date, datetime
from typing import Optional, Any
from pydantic import BaseModel


class WebhookLogOut(BaseModel):
    id: int
    organization_id: Optional[int] = None
    channel: str
    direction: str
    event_type: Optional[str] = None
    signature_valid: Optional[bool] = None
    normalized_payload: Optional[dict[str, Any]] = None
    request_summary: Optional[dict[str, Any]] = None
    response_summary: Optional[dict[str, Any]] = None
    http_status_code: Optional[int] = None
    processing_status: str
    error_message: Optional[str] = None
    related_conversation_id: Optional[int] = None
    related_message_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookLogDetailOut(WebhookLogOut):
    raw_payload: Optional[dict[str, Any]] = None
    headers: Optional[dict[str, Any]] = None


class WebhookLogListResponse(BaseModel):
    items: list[WebhookLogOut]
    total: int
    page: int
    page_size: int


class WebhookLogStatsByChannel(BaseModel):
    channel: str
    total: int
    received: int
    processed: int
    failed: int
    rejected: int


class WebhookLogStatsResponse(BaseModel):
    organization_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    total: int
    processed: int
    failed: int
    rejected: int
    invalid_signature_count: int

    by_channel: list[WebhookLogStatsByChannel]

    generated_at: datetime