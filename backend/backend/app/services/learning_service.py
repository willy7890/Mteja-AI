from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.training_data import TrainingData


async def add_training_data(
    db: AsyncSession,
    question: str,
    category: Optional[str] = None,
    answer: Optional[str] = None,
    verified: bool = False,
) -> TrainingData:
    """Inserts a new training entry into the training_data table."""
    if not question or not question.strip():
        raise ValueError("Question is required for training data")

    entry = TrainingData(
        question=question.strip(),
        category=category,
        answer=answer.strip() if answer else None,
        verified=verified,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def verify_training_data(
    db: AsyncSession,
    training_data_id: int,
    verified_answer: Optional[str] = None,
) -> TrainingData:
    """Marks a training sample as verified and optionally updates the target answer."""
    entry = await db.get(TrainingData, training_data_id)
    if not entry:
        raise ValueError("Training data entry not found")

    entry.verified = True
    if verified_answer:
        entry.answer = verified_answer.strip()

    await db.commit()
    await db.refresh(entry)
    return entry