

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column,String,Text,DateTime,ForeignKey,Enum as SAEnum,Integer,JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base  


def gen_uuid() -> str:
    return str(uuid.uuid4())


class ChannelType(str, enum.Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"


class BroadcastStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecipientStatus(str, enum.Enum):
    PENDING = "pending"
    SKIPPED_NO_CONSENT = "skipped_no_consent"
    SKIPPED_CHANNEL_UNAVAILABLE = "skipped_channel_unavailable"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    REJECTED_BY_PROVIDER = "rejected_by_provider"


class BroadcastCampaign(Base):
    __tablename__ = "broadcast_campaigns"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    message_body = Column(Text, nullable=False)

    # Which channels this campaign attempts, in priority order, e.g. ["whatsapp", "sms"]
    channels = Column(JSON, nullable=False, default=list)

    # WhatsApp template reference, required if "whatsapp" is in channels and
    # the recipient is outside the free-form session window.
    whatsapp_template_id = Column(String(255), nullable=True)

    # Audience definition — a serialized filter (segment id, tags, saved query, etc.)
    audience_filter = Column(JSON, nullable=False, default=dict)

    status = Column(SAEnum(BroadcastStatus), nullable=False, default=BroadcastStatus.DRAFT, index=True)

    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)

    # Aggregate counters, updated as recipient states change
    total_recipients = Column(Integer, nullable=False, default=0)
    total_sent = Column(Integer, nullable=False, default=0)
    total_delivered = Column(Integer, nullable=False, default=0)
    total_failed = Column(Integer, nullable=False, default=0)
    total_skipped = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    recipients = relationship(
        "BroadcastRecipient", back_populates="campaign", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_broadcast_org_status", "org_id", "status"),
    )


class BroadcastRecipient(Base):
    __tablename__ = "broadcast_recipients"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("broadcast_campaigns.id"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=False), nullable=False, index=True)  # denormalized for tenant-safety on queries

    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id"), nullable=False)
    channel = Column(SAEnum(ChannelType), nullable=False)

    status = Column(SAEnum(RecipientStatus), nullable=False, default=RecipientStatus.PENDING, index=True)
    provider_message_id = Column(String(255), nullable=True)
    error_reason = Column(Text, nullable=True)

    queued_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    campaign = relationship("BroadcastCampaign", back_populates="recipients")

    __table_args__ = (
        Index("ix_recipient_campaign_status", "campaign_id", "status"),
        Index("ix_recipient_org", "org_id"),
    )
