from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class TrainingData(Base):
    __tablename__ = "training_data"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500), nullable=False)
    category = Column(String(100), nullable=True)
    answer = Column(Text, nullable=False)