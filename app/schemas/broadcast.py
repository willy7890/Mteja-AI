from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.broadcast import ChannelType, BroadcastStatus, RecipientStatus


class AudienceFilter(BaseModel):
    segment_id: Optional[str] = None
    tags: Optional[list[str]] = None
    saved_query_id: Optional[str] = None
    customer_ids: Optional[list[int]] = None

    @field_validator("customer_ids")
    @classmethod
    def _cap_explicit_list(cls, v):
        if v is not None and len(v) > 5000:
            raise ValueError("customer_ids list too large for a single campaign (max 5000)")
        return v


class BroadcastCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    message_body: str = Field(..., min_length=1, max_length=4096)
    channels: list[ChannelType] = Field(..., min_length=1)
    whatsapp_template_id: Optional[str] = None
    audience: AudienceFilter
    scheduled_at: Optional[datetime] = None

    @field_validator("channels")
    @classmethod
    def _dedupe_channels(cls, v):
        seen, out = set(), []
        for c in v:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out

    @field_validator("whatsapp_template_id")
    @classmethod
    def _template_required_for_whatsapp(cls, v, info):
        channels = info.data.get("channels") or []
        if ChannelType.WHATSAPP in channels and not v:
            pass
        return v


class BroadcastScheduleRequest(BaseModel):
    scheduled_at: datetime

    @field_validator("scheduled_at")
    @classmethod
    def _must_be_future(cls, v: datetime) -> datetime:
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.utcnow()
        if v <= now:
            raise ValueError("scheduled_at must be in the future")
        return v


class BroadcastRecipientOut(BaseModel):
    id: int
    customer_id: int
    channel: ChannelType
    status: RecipientStatus
    error_reason: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BroadcastCampaignOut(BaseModel):
    id: int
    organization_id: int
    name: str
    message_body: str
    channels: list[str]
    status: BroadcastStatus
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: int
    approved_by: Optional[int] = None

    total_recipients: int
    total_sent: int
    total_delivered: int
    total_failed: int
    total_skipped: int

    created_at: datetime

    class Config:
        from_attributes = True


class BroadcastListResponse(BaseModel):
    items: list[BroadcastCampaignOut]
    total: int
    page: int
    page_size: int


class BroadcastRecipientListResponse(BaseModel):
    items: list[BroadcastRecipientOut]
    total: int
    page: int
    page_size: int