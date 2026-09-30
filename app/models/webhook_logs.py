from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    Index,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)

    channel = Column(String(50), nullable=False, index=True)
    direction = Column(String(10), nullable=False, index=True)
    event_type = Column(String(100), nullable=True, index=True)

    signature_valid = Column(Boolean, nullable=True)

    raw_payload = Column(JSON, nullable=True)
    normalized_payload = Column(JSON, nullable=True)
    headers = Column(JSON, nullable=True)

    request_summary = Column(JSON, nullable=True)
    response_summary = Column(JSON, nullable=True)
    http_status_code = Column(Integer, nullable=True)

    processing_status = Column(String(30), nullable=False, default="received", index=True)
    error_message = Column(Text, nullable=True)

    related_conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    related_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization")

    __table_args__ = (
        Index("ix_webhook_logs_org_channel_created", "organization_id", "channel", "created_at"),
        Index("ix_webhook_logs_status_created", "processing_status", "created_at"),
    )