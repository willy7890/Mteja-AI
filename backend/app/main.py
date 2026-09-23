import os
import asyncio
import joblib
import numpy as np

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import RateLimitMiddleware

from app.models import (
    user,
    organization,
    customer,
    activity_log,
    conversation,
    message,
    lead,
    training_data,
    escalation_log,
    broadcast,
)

from app.api.router import api_router
from app.api.analytics import router as analytics_router
from app.api.broadcast import router as broadcast_router
from app.api.webhook_logs import router as webhook_router

from app.services.knowledge_service import kb_service

from app.integrations.telegram.webhook import router as telegram_webhook_router
from app.routes.telegram import router as telegram_ws_router


# Global ML artifacts
model_vectorizer = None
model_X_vectors = None
model_y_answers = None


class QueryRequest(BaseModel):
    question: str


class PredictionResponse(BaseModel):
    matched_answer: str
    confidence: float
    status: str


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "intent_classifier.pkl"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_vectorizer, model_X_vectors, model_y_answers

    # DB init
    database_error = None
    for attempt in range(1, 4):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database connection initialized successfully.")
            break
        except Exception as e:
            database_error = e
            if attempt == 3:
                print(f"❌ Database initialization failed: {e}")
                raise
            print(f"⚠️ Database connection attempt {attempt} failed; retrying...")
            await asyncio.sleep(attempt * 2)

    # Knowledge base
    try:
        async with AsyncSession(engine) as session:
            await kb_service.load_from_db(session)
        print(f"✅ Knowledge base loaded: {len(kb_service.documents)} documents")
    except Exception as e:
        print(f"⚠️ Failed to load knowledge base: {e}")

    # ML model
    if MODEL_PATH.exists():
        try:
            artifact = joblib.load(MODEL_PATH)
            model_vectorizer = artifact["vectorizer"]
            model_X_vectors = artifact["X_vectors"]
            model_y_answers = artifact["y_answers"]
            print(f"✅ Intent Classifier loaded successfully ({model_X_vectors.shape[0]} vectors).")
        except Exception as e:
            print(f"⚠️ Failed to load ML model artifact: {e}")
    else:
        print(f"⚠️ Model artifact not found at {MODEL_PATH}. ML predictions disabled.")

    print("🚀 MTEJA AI application startup complete.")
    yield
    print("🛑 MTEJA AI application shutting down...")


app = FastAPI(
    title=(
        settings.PROJECT_NAME
        if hasattr(settings, "PROJECT_NAME")
        else getattr(settings, "APP_NAME", "MTEJA AI API")
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mtejaai.signiai.co.tz",
        "https://www.mtejaai.signiai.co.tz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limit (enable when ready)
# app.add_middleware(RateLimitMiddleware)


# Routers
app.include_router(telegram_webhook_router)
app.include_router(telegram_ws_router)
app.include_router(api_router, prefix="/api")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(broadcast_router)
app.include_router(webhook_router)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "MTEJA AI API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse, tags=["ML Engine"])
async def predict_intent(payload: QueryRequest):
    if model_vectorizer is None or model_X_vectors is None or model_y_answers is None:
        raise HTTPException(status_code=503, detail="Intent classification model is not loaded.")

    clean_query = payload.question.lower().strip()
    if not clean_query:
        raise HTTPException(status_code=400, detail="Question payload cannot be empty.")

    query_vector = model_vectorizer.transform([clean_query])
    similarities = cosine_similarity(query_vector, model_X_vectors)[0]
    best_idx = int(np.argmax(similarities))
    confidence_score = float(similarities[best_idx]) * 100

    CONFIDENCE_THRESHOLD = 15.0

    if confidence_score >= CONFIDENCE_THRESHOLD:
        return PredictionResponse(
            matched_answer=model_y_answers[best_idx],
            confidence=round(confidence_score, 2),
            status="success",
        )

    return PredictionResponse(
        matched_answer="Samahani, sijaelewa swali lako. Tafadhali jaribu kuuliza kwa njia nyingine.",
        confidence=round(confidence_score, 2),
        status="fallback",
    )


# Static files
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
