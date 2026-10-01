from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TrainingData(Base):
    __tablename__ = "training_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Context or category (e.g., 'customer_support', 'faqs', 'product_inquiry')
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Input data / prompt provided by user or dataset
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Expected completion / response
    completion: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Quality score or status (e.g., 'approved', 'pending', 'rejected')
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    
    # Optional foreign key if associated with a specific tenant or user
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (uncomment if User model exists and needed)
    # user = relationship("User", back_populates="training_data")