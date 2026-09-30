import os
import joblib
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.training_data import TrainingData

# Path configured for app/scripts/ structure (points to root project /models directory)
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))
MODEL_PATH = os.path.join(MODEL_DIR, "intent_classifier.pkl")


def train_and_save_pipeline(texts: List[str], labels: List[str]) -> str:
    """Trains TF-IDF + LogisticRegression pipeline and exports artifact."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(class_weight="balanced", C=1.0)),
    ])
    pipeline.fit(texts, labels)

    joblib.dump(pipeline, MODEL_PATH)
    print(f"[AUTO-RETRAIN] Saved model artifact to: {MODEL_PATH}")
    return MODEL_PATH


async def run_async_retraining_job() -> Dict[str, Any]:
    """Async retraining pipeline for FastAPI background tasks."""
    async with AsyncSessionLocal() as db:
        query = (
            select(TrainingData)
            .where(TrainingData.verified.is_(True))
            .order_by(TrainingData.created_at.asc())
        )
        result = await db.execute(query)
        dataset: List[TrainingData] = result.scalars().all()

        if len(dataset) < 5:
            print(f"[AUTO-RETRAIN] Insufficient verified data ({len(dataset)} items). Skipping.")
            return {"status": "skipped", "reason": "insufficient_data", "count": len(dataset)}

        print(f"[AUTO-RETRAIN] Training model with {len(dataset)} verified samples (Async)...")
        texts = [data.text for data in dataset]
        labels = [data.category for data in dataset]

        path = train_and_save_pipeline(texts, labels)
        return {"status": "success", "artifact_path": path, "count": len(dataset)}


def run_sync_retraining_job() -> Dict[str, Any]:
    """Sync retraining pipeline for Standalone Scripts, Airflow, or Cron jobs."""
    sync_engine = create_engine(settings.SYNC_DATABASE_URL, pool_pre_ping=True)

    try:
        with Session(sync_engine) as db:
            query = (
                select(TrainingData)
                .where(TrainingData.verified.is_(True))
                .order_by(TrainingData.created_at.asc())
            )
            dataset = db.scalars(query).all()

            if len(dataset) < 5:
                print(f"[AUTO-RETRAIN] Insufficient verified data ({len(dataset)} items). Skipping.")
                return {"status": "skipped", "reason": "insufficient_data", "count": len(dataset)}

            print(f"[AUTO-RETRAIN] Training model with {len(dataset)} verified samples (Sync)...")
            texts = [data.text for data in dataset]
            labels = [data.category for data in dataset]

            path = train_and_save_pipeline(texts, labels)
            return {"status": "success", "artifact_path": path, "count": len(dataset)}
    finally:
        sync_engine.dispose()


if __name__ == "__main__":
    run_sync_retraining_job()