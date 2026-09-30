from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.broadcast import ChannelType, CampaignStatus, RecipientStatus


class BroadcastCampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    channels: list[ChannelType] = Field(min_length=1)
    audience_filter: dict = Field(default_factory=dict)

    template_id: str | None = None
    template_params: dict | None = None
    media_url: str | None = None  # promo image to send
    free_form_content: str | None = None

    @field_validator("free_form_content")
    @classmethod
    def require_content(cls, v, info):
        # need at least one of: template, text, or an image
        if not v and not info.data.get("template_id") and not info.data.get("media_url"):
            raise ValueError("Provide template_id, free_form_content, or media_url")
        return v


class BroadcastCampaignScheduleRequest(BaseModel):
    scheduled_at: datetime


class CampaignMetrics(BaseModel):
    total_recipients: int = 0
    pending: int = 0
    queued: int = 0
    sent: int = 0
    delivered: int = 0
    failed: int = 0
    skipped_no_consent: int = 0
    skipped_unavailable: int = 0
    skipped_rule_violation: int = 0


class BroadcastCampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    name: str
    description: str | None
    channels: list[str]
    audience_filter: dict
    template_id: str | None
    free_form_content: str | None
    media_url: str | None
    status: CampaignStatus
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    created_by: int
    approved_by: int | None
    created_at: datetime
    metrics: CampaignMetrics | None = None  # filled in by the service, not stored on the row


class BroadcastRecipientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    channel: ChannelType
    destination: str
    status: RecipientStatus
    used_template: str | None
    error_reason: str | None
    queued_at: datetime | None
    sent_at: datetime | None
    delivered_at: datetime | None


class BroadcastCampaignList(BaseModel):
    items: list[BroadcastCampaignOut]
    total: int