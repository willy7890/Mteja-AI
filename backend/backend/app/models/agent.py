# agent SQLAlchemy model for MTEJA AI
# Defines table schema, relationships, and multi-tenant organization_id
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from app.core.database import Base


class AgentConfiguration(Base):
  __tablename__ = "agent_configurations"

  id = Column(Integer, primary_key=True, index=True)
  organization_id = Column(
      Integer, ForeignKey("organizations.id"), nullable=False, unique=True
  )
  agent_name = Column(String, default="MtejaAI Assistant")
  system_prompt = Column(
      Text,
      default=(
          "You are MtejaAI, an AI customer support assistant. Use ONLY the"
          " provided knowledge base context to answer."
      ),
  )
  model_name = Column(String, default="gpt-4o")
  temperature = Column(Integer, default=0.3)  # stored as float or int
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(
      DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
  )