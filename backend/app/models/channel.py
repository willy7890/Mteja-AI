# channel SQLAlchemy model for MTEJA AI
# Defines table schema, relationships, and multi-tenant organization_id
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey
from app.core.database import Base


class ChannelIntegration(Base):
  __tablename__ = "channel_integrations"

  id = Column(Integer, primary_key=True, index=True)
  organization_id = Column(
      Integer, ForeignKey("organizations.id"), nullable=False
  )
  channel_name = Column(
      String, nullable=False
  )  # whatsapp, facebook, instagram, telegram, sms, email, tiktok, twitter
  is_active = Column(Boolean, default=True)
  credentials_json = Column(
      String, nullable=True
  )  # encrypted tokens or account identifiers
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(
      DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
  )