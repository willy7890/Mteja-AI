import os
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Database Connection (Adjust connection string)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "app" / "data" / "mteja_ai_tanzania_dataset.csv"
MODEL_PATH = PROJECT_ROOT / "app" / "ml_models" / "mteja_category_classifier.pkl"
DATABASE_URL = os.getenv("DATABASE_URL", "")

def retrain_model():
    # 1. Load Original Dataset
    df_base = pd.read_csv(DATASET_PATH)
    text_column = "question" if "question" in df_base.columns else "customer"

    # 2. Fetch New Interactions from Database
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        df_new = pd.read_sql(
            "SELECT question, category FROM training_data WHERE verified = TRUE",
            engine,
        )
    else:
        df_new = pd.DataFrame(columns=["question", "category"])

    # 3. Combine Old and New Data (Adaptive Learning)
    df_combined = pd.concat(
        [df_base[[text_column, "category"]].rename(columns={text_column: "question"}), df_new],
        ignore_index=True,
    )
    df_combined = df_combined.dropna().drop_duplicates(subset=['question'])

    X = df_combined['question'].astype(str).str.lower().str.strip()
    y = df_combined['category']

    # 4. Train Updated Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
        ('classifier', MultinomialNB(alpha=0.1))
    ])
    
    print(f"Retraining model with {len(df_combined)} total examples...")
    pipeline.fit(X, y)

    # 5. Overwrite the Trained Artifact
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model updated successfully: {MODEL_PATH}")

if __name__ == "__main__":
    retrain_model()