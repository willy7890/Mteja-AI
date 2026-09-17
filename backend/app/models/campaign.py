# campaign SQLAlchemy model for MTEJA AI
# Defines table schema, relationships, and multi-tenant organization_id
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from app.core.database import Base


class Campaign(Base):
  __tablename__ = "campaigns"

  id = Column(Integer, primary_key=True, index=True)
  organization_id = Column(
      Integer, ForeignKey("organizations.id"), nullable=False
  )
  title = Column(String, nullable=False)
  message = Column(Text, nullable=False)
  channel = Column(String, nullable=False)  # "sms" or "email"
  status = Column(
      String, default="draft"
  )  # "draft", "scheduled", "sent", "failed"
  created_at = Column(DateTime, default=datetime.utcnow)
  sent_at = Column(DateTime, nullable=True)