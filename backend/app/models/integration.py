from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey
from app.core.database import Base


class Integration(Base):
  __tablename__ = "integrations"

  id = Column(Integer, primary_key=True, index=True)
  organization_id = Column(
      Integer, ForeignKey("organizations.id"), nullable=False
  )
  service_name = Column(
      String, nullable=False
  )  # e.g., "gmail", "whatsapp", "mailchimp"
  is_connected = Column(Boolean, default=False)
  config_data = Column(
      String, nullable=True
  )  # JSON string containing tokens or metadata
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(
      DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
  )