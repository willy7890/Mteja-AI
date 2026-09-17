# deal SQLAlchemy model for MTEJA AI
# Defines table schema, relationships, and multi-tenant organization_id
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from app.core.database import Base


class Deal(Base):
  __tablename__ = "deals"

  id = Column(Integer, primary_key=True, index=True)
  organization_id = Column(
      Integer, ForeignKey("organizations.id"), nullable=False
  )
  customer_id = Column(ForeignKey("customers.id"), nullable=False)
  title = Column(String, nullable=False)
  value = Column(Float, default=0.0)
  stage = Column(
      String, default="lead"
  )  # lead, qualified, proposal, won, lost
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(
      DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
  )