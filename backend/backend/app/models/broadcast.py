"""Broadcast campaign + per-recipient delivery tracking."""

import enum
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Integer, Enum as SAEnum, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChannelType(str, enum.Enum):
    whatsapp = "whatsapp"
    sms = "sms"
    email = "email"


class CampaignStatus(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    sending = "sending"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class RecipientStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    skipped_no_consent = "skipped_no_consent"
    skipped_unavailable = "skipped_unavailable"
    skipped_rule_violation = "skipped_rule_violation"


class BroadcastCampaign(Base):
    __tablename__ = "broadcast_campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    channels: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # e.g. ["whatsapp", "sms"]
    audience_filter: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    template_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    template_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    free_form_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)  # promo image/attachment

    status: Mapped[CampaignStatus] = mapped_column(SAEnum(CampaignStatus), default=CampaignStatus.draft, index=True)

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_broadcast_campaigns_org_status", "organization_id", "status"),)


class BroadcastRecipient(Base):
    __tablename__ = "broadcast_recipients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("broadcast_campaigns.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(nullable=False, index=True)  # denormalized for safe org-scoped queries

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    channel: Mapped[ChannelType] = mapped_column(SAEnum(ChannelType), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)  # phone/email used at send time

    used_template: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rendered_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[RecipientStatus] = mapped_column(SAEnum(RecipientStatus), default=RecipientStatus.pending, index=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("campaign_id", "customer_id", "channel", name="uq_campaign_customer_channel"),
        Index("ix_broadcast_recipients_campaign_status", "campaign_id", "status"),
    )