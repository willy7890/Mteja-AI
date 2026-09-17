from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from app.core.database import Base


class Lead(Base):
  __tablename__ = "leads"

  id = Column(Integer, primary_key=True, index=True)
  organization_id = Column(
      Integer, ForeignKey("organizations.id"), nullable=False
  )
  name = Column(String, nullable=False)
  phone = Column(String, nullable=True)
  email = Column(String, nullable=True)
  source = Column(
      String, default="website"
  )  # whatsapp, facebook, instagram, sms, email, telegram
  status = Column(
      String, default="new"
  )  # new, contacted, qualified, converted, lost
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(
      DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
  )