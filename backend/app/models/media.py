from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    
    # Ownership
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    # File info
    filename = Column(String(255), nullable=False)          
    stored_filename = Column(String(255), nullable=False, unique=True)  
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)          
    content_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)          

    created_at = Column(DateTime(timezone=True), server_default=func.now())