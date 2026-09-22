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

# Import all models so Alembic and SQLAlchemy Base metadata
# capture the complete database schema.
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

from app.integrations.telegram.webhook import (
    router as telegram_webhook_router,
)

from app.routes.telegram import (
    router as telegram_ws_router,
)


# ============================================================
# GLOBAL ML ARTIFACTS
# ============================================================

model_vectorizer = None
model_X_vectors = None
model_y_answers = None


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class QueryRequest(BaseModel):
    question: str


class PredictionResponse(BaseModel):
    matched_answer: str
    confidence: float
    status: str


# ============================================================
# PROJECT PATHS
# ============================================================

# backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# backend/models/intent_classifier.pkl
MODEL_PATH = BASE_DIR / "models" / "intent_classifier.pkl"

# backend/static/
STATIC_DIR = BASE_DIR / "static"


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_vectorizer
    global model_X_vectors
    global model_y_answers

    # --------------------------------------------------------
    # 1. Initialize database metadata
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # 2. Load Knowledge Base
    # --------------------------------------------------------
    try:
        async with AsyncSession(engine) as session:
            await kb_service.load_from_db(session)

        print(
            f"✅ Knowledge base loaded: "
            f"{len(kb_service.documents)} documents"
        )

    except Exception as e:
        print(f"⚠️ Failed to load knowledge base: {e}")

    # --------------------------------------------------------
    # 3. Load ML Model
    # --------------------------------------------------------
    if MODEL_PATH.exists():
        try:
            artifact = joblib.load(MODEL_PATH)

            model_vectorizer = artifact["vectorizer"]
            model_X_vectors = artifact["X_vectors"]
            model_y_answers = artifact["y_answers"]

            print(
                "✅ Intent Classifier loaded successfully "
                f"({model_X_vectors.shape[0]} vectors)."
            )

        except Exception as e:
            print(
                f"⚠️ Failed to load ML model artifact: {e}"
            )

    else:
        print(
            "⚠️ Model artifact not found at "
            f"{MODEL_PATH}. ML predictions disabled."
        )

    # --------------------------------------------------------
    # Application is ready
    # --------------------------------------------------------
    print("🚀 MTEJA AI application startup complete.")

    yield

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------
    print("🛑 MTEJA AI application shutting down...")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=(
        settings.PROJECT_NAME
        if hasattr(settings, "PROJECT_NAME")
        else getattr(
            settings,
            "APP_NAME",
            "MTEJA AI API",
        )
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# RATE LIMIT MIDDLEWARE
# ============================================================

# Enable this when RateLimitMiddleware configuration is ready.
#
# app.add_middleware(RateLimitMiddleware)


# ============================================================
# API ROUTERS
# ============================================================

# Telegram webhook
app.include_router(
    telegram_webhook_router
)

# Telegram WebSocket / frontend routes
app.include_router(
    telegram_ws_router
)

# Main API
app.include_router(
    api_router,
    prefix="/api",
)

# Analytics
app.include_router(
    analytics_router,
    prefix="/api/v1",
)

# Broadcast
app.include_router(
    broadcast_router
)

# Webhook logs
app.include_router(
    webhook_router
)


# ============================================================
# HEALTH / ROOT ENDPOINTS
# ============================================================

@app.get(
    "/",
    tags=["Health"],
)
async def root():
    return {
        "message": "MTEJA AI API is running",
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Health"],
)
async def health():
    return {
        "status": "ok"
    }


# ============================================================
# ML PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["ML Engine"],
)
async def predict_intent(
    payload: QueryRequest,
):
    # --------------------------------------------------------
    # Check ML model
    # --------------------------------------------------------
    if (
        model_vectorizer is None
        or model_X_vectors is None
        or model_y_answers is None
    ):
        raise HTTPException(
            status_code=503,
            detail="Intent classification model is not loaded.",
        )

    # --------------------------------------------------------
    # Clean input
    # --------------------------------------------------------
    clean_query = payload.question.lower().strip()

    if not clean_query:
        raise HTTPException(
            status_code=400,
            detail="Question payload cannot be empty.",
        )

    # --------------------------------------------------------
    # Vectorize query
    # --------------------------------------------------------
    query_vector = model_vectorizer.transform(
        [clean_query]
    )

    # --------------------------------------------------------
    # Calculate cosine similarity
    # --------------------------------------------------------
    similarities = cosine_similarity(
        query_vector,
        model_X_vectors,
    )[0]

    # --------------------------------------------------------
    # Find best match
    # --------------------------------------------------------
    best_idx = int(
        np.argmax(similarities)
    )

    confidence_score = (
        float(similarities[best_idx]) * 100
    )

    # --------------------------------------------------------
    # Confidence threshold
    # --------------------------------------------------------
    CONFIDENCE_THRESHOLD = 15.0

    if confidence_score >= CONFIDENCE_THRESHOLD:
        return PredictionResponse(
            matched_answer=model_y_answers[best_idx],
            confidence=round(
                confidence_score,
                2,
            ),
            status="success",
        )

    # --------------------------------------------------------
    # Fallback response
    # --------------------------------------------------------
    return PredictionResponse(
        matched_answer=(
            "Samahani, sijaelewa swali lako. "
            "Tafadhali jaribu kuuliza kwa njia nyingine."
        ),
        confidence=round(
            confidence_score,
            2,
        ),
        status="fallback",
    )


# ============================================================
# STATIC FILES
# ============================================================

# Make sure backend/static exists.
STATIC_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static",
)


# ============================================================
# END OF APPLICATION
# ============================================================