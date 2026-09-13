# backend/app/services/learning_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.training_data import TrainingData # Model yako ya kuhifadhia data mpya

class LearningService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_new_interaction(self, question: str, predicted_category: str, is_human_verified: bool = False):
        """Hifadhi swali jipya la mteja kwa ajili ya retraining ya baadaye."""
        new_entry = TrainingData(
            question=question.strip().lower(),
            category=predicted_category,
            verified=is_human_verified # True kama lilijibiwa na Human Agent
        )
        self.db.add(new_entry)
        await self.db.commit()