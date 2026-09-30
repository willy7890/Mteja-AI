from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.database import Base


class TrainingData(Base):
    __tablename__ = "training_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Primary mapping: Maps to 'question' in DB.
    # Note: If your DB column is named 'query' or 'text', change 'question' below to match it
    # e.g., mapped_column("query", Text, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    @validates("question")
    def validate_question(self, key: str, question: str) -> str:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        return question.strip()

    # Optional alias: Allows using .query as a fallback property in code
    @hybrid_property
    def query(self) -> str:
        return self.question

    @query.setter
    def query(self, value: str) -> None:
        self.question = value