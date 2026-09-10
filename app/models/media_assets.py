
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base  

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    storage_path: Mapped[str] = mapped_column(String)
    mime_type: Mapped[str] = mapped_column(String)
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    
    organization = relationship("Organization")
    customer = relationship("Customer")
    conversation = relationship("Conversation", back_populates="media_assets")