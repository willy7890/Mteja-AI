import os
import joblib
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine, Base
#from app.core.middleware import RateLimitMiddleware  # Impoti middleware

# Import all models to ensure Alembic and Base metadata capture full database schemas
from app.models import (user,organization,customer,activity_log,conversation,message,lead,training_data,escalation_log,broadcast,)
from app.api.router import api_router
from app.api.analytics import router as analytics_router  # Impoti analytics_router
from app.api.broadcast import router as broadcast_router
from app.api.webhook_logs import router as webhook_router
from app.services.knowledge_service import kb_service
from app.intergration.telegram.webhook import router as telegram_webhook_router
from fastapi.staticfiles import StaticFiles

# Global variables for ML Artifacts
model_vectorizer = None
model_X_vectors = None
model_y_answers = None


# Pydantic Schemas for /predict
class QueryRequest(BaseModel):
    question: str


class PredictionResponse(BaseModel):
    matched_answer: str
    confidence: float
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_vectorizer, model_X_vectors, model_y_answers

    # 1. Initialize DB tables synchronously inside async context
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Pre-load Knowledge Base documents into memory
    async with AsyncSession(engine) as session:
        await kb_service.load_from_db(session)
    print(f"✅ Knowledge base loaded: {len(kb_service.documents)} documents")

    # 3. Load Vector Search ML Artifact (intent_classifier.pkl)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "models", "intent_classifier.pkl")

    if os.path.exists(model_path):
        try:
            artifact = joblib.load(model_path)
            model_vectorizer = artifact["vectorizer"]
            model_X_vectors = artifact["X_vectors"]
            model_y_answers = artifact["y_answers"]
            print(
                f"✅ Intent Classifier loaded successfully ({model_X_vectors.shape[0]} vectors)."
            )
        except Exception as e:
            print(f"⚠️ Failed to load ML model artifact: {e}")
    else:
        print(f"⚠️ Model artifact not found at {model_path}. ML predictions disabled.")

    yield


# Application Initialization
app = FastAPI(
    title=settings.PROJECT_NAME
    if hasattr(settings, "PROJECT_NAME")
    else getattr(settings, "APP_NAME", "MTEJA AI API"),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#app.add_middleware(RateLimitMiddleware)

# Primary API & Webhook Routers
app.include_router(telegram_webhook_router)
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
    if model_vectorizer is None or model_X_vectors is None:
        raise HTTPException(
            status_code=503,
            detail="Intent classification model is not loaded.",
        )

    clean_query = payload.question.lower().strip()
    if not clean_query:
        raise HTTPException(
            status_code=400, detail="Question payload cannot be empty."
        )

    # Transform input and calculate Cosine Similarity against all stored vectors
    query_vector = model_vectorizer.transform([clean_query])
    similarities = cosine_similarity(query_vector, model_X_vectors)[0]

    best_idx = int(np.argmax(similarities))
    confidence_score = float(similarities[best_idx]) * 100

    CONFIDENCE_THRESHOLD = 15.0  # Fallback boundary percentage

    if confidence_score >= CONFIDENCE_THRESHOLD:
        return PredictionResponse(
            matched_answer=model_y_answers[best_idx],
            confidence=round(confidence_score, 2),
            status="success",
        )
    else:
        return PredictionResponse(
            matched_answer="Samahani, sijaelewa swali lako. Tafadhali jaribu kuuliza kwa njia nyingine.",
            confidence=round(confidence_score, 2),
            status="fallback",
        )
        
        
        

app.mount("/static", StaticFiles(directory="static"), name="static")