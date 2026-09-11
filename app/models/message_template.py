# backend/app/models/message_template.py

from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))

    
    template_name: Mapped[str] = mapped_column(String)

    
    language_code: Mapped[str] = mapped_column(String, default="sw")

    
    category: Mapped[str] = mapped_column(String)

    
    is_approved: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization")