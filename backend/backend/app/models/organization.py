from datetime import datetime
from sqlalchemy import String, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ai_settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    users = relationship("User", back_populates="organization")
    customers = relationship("Customer", back_populates="organization")