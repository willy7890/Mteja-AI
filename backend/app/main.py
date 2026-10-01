import asyncio
from contextlib import asynccontextmanager
import csv
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import joblib
import numpy as np
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.analytics import router as analytics_router
from app.api.broadcast import router as broadcast_router
from app.api.router import api_router
from app.api.webhook_logs import router as webhook_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.rate_limit import RateLimitMiddleware
from app.integrations.telegram.webhook import router as telegram_webhook_router
from app.models import (
    activity_log,
    broadcast,
    conversation,
    customer,
    escalation_log,
    lead,
    message,
    organization,
    training_data,
    user,
)
from app.routes.telegram import router as telegram_ws_router
from app.services.knowledge_service import kb_service

# Safely import LangChain components for local file loading
try:
    from langchain_community.document_loaders import (
        CSVLoader,
        DirectoryLoader,
        PyPDFLoader,
        TextLoader,
    )
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


# ============================================================
# GLOBAL ML ARTIFACTS
# ============================================================

model_vectorizer = None
model_X_vectors = None
model_y_answers = None


# ============================================================
# REQUEST / RESPONSE SCHEMAS
# ============================================================


class QueryRequest(BaseModel):
    question: str


class PredictionResponse(BaseModel):
    matched_answer: str
    confidence: float
    status: str


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "intent_classifier.pkl"
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "data" / "docs"


# ============================================================
# LOAD KNOWLEDGE BASE + ML MODEL IN BACKGROUND
# ============================================================


async def load_local_documents() -> int:
    """Reads local documents (CSV, TXT, PDF) from data/docs directory into Knowledge Base."""
    if not DOCS_DIR.exists():
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        return 0

    documents = []

    if LANGCHAIN_AVAILABLE:
        try:
            # 1. Load CSV Files
            for csv_file in DOCS_DIR.glob("**/*.csv"):
                try:
                    loader = CSVLoader(
                        file_path=str(csv_file), encoding="utf-8"
                    )
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"⚠️ Error loading CSV {csv_file.name}: {e}")

            # 2. Load TXT Files
            for txt_file in DOCS_DIR.glob("**/*.txt"):
                try:
                    loader = TextLoader(str(txt_file), encoding="utf-8")
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"⚠️ Error loading TXT {txt_file.name}: {e}")

            # 3. Load PDF Files
            for pdf_file in DOCS_DIR.glob("**/*.pdf"):
                try:
                    loader = PyPDFLoader(str(pdf_file))
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"⚠️ Error loading PDF {pdf_file.name}: {e}")

            if not documents:
                return 0

            # Split large text documents into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500, chunk_overlap=50
            )
            chunks = text_splitter.split_documents(documents)

            # Append chunks to kb_service
            if hasattr(kb_service, "documents"):
                kb_service.documents.extend(chunks)
            elif hasattr(kb_service, "add_documents"):
                await kb_service.add_documents(chunks)

            return len(chunks)

        except Exception as e:
            print(f"⚠️ Error processing local documents with LangChain: {e}")
            return 0
    else:
        # Fallback manual CSV loader if LangChain is not installed
        try:
            raw_docs = []
            for csv_file in DOCS_DIR.glob("**/*.csv"):
                with open(csv_file, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        content = "\n".join(
                            [f"{k}: {v}" for k, v in row.items() if v]
                        )
                        raw_docs.append(content)

            if hasattr(kb_service, "documents"):
                kb_service.documents.extend(raw_docs)

            return len(raw_docs)
        except Exception as e:
            print(f"⚠️ Manual fallback CSV loader failed: {e}")
            return 0


async def _load_kb_and_model():
    """Heavy work runs AFTER the server has started.

    Knowledge Base and ML model are loaded in the background so FastAPI does
    not have to wait for them before becoming ready.
    """

    global model_vectorizer
    global model_X_vectors
    global model_y_answers

    # --------------------------------------------------------
    # KNOWLEDGE BASE (Database + Local Files)
    # --------------------------------------------------------

    db_docs_count = 0
    file_docs_count = 0

    try:
        # 1. Load Knowledge Base from PostgreSQL Database
        async with AsyncSession(engine) as session:
            await kb_service.load_from_db(session)
            db_docs_count = (
                len(kb_service.documents)
                if hasattr(kb_service, "documents")
                else 0
            )

        # 2. Load Knowledge Base from Local Files (data/docs/*.csv, *.txt, *.pdf)
        file_docs_count = await load_local_documents()

        total_docs = db_docs_count + file_docs_count
        print(
            f"✅ Knowledge base loaded successfully: "
            f"{total_docs} documents/chunks "
            f"({db_docs_count} from DB, {file_docs_count} from files)."
        )

    except Exception as e:
        print(f"⚠️ Failed to load knowledge base: {e}")

    # --------------------------------------------------------
    # ML MODEL
    # --------------------------------------------------------

    if MODEL_PATH.exists():
        try:
            artifact = joblib.load(MODEL_PATH)

            model_vectorizer = artifact["vectorizer"]
            model_X_vectors = artifact["X_vectors"]
            model_y_answers = artifact["y_answers"]

            print(
                f"✅ Intent Classifier loaded "
                f"({model_X_vectors.shape[0]} vectors)."
            )

        except Exception as e:
            print(f"⚠️ Failed to load ML model: {e}")

    else:
        print(f"⚠️ Model not found at {MODEL_PATH}")


# ============================================================
# FASTAPI LIFESPAN
# ============================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    for attempt in range(1, 4):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            print("✅ Database connection initialized successfully.")
            break

        except Exception as e:
            if attempt == 3:
                print(f"❌ Database initialization failed: {e}")
                raise

            print(f"⚠️ DB attempt {attempt} failed; retrying...")
            await asyncio.sleep(attempt * 2)

    # ========================================================
    # START HEAVY LOADING IN BACKGROUND
    # ========================================================

    asyncio.create_task(_load_kb_and_model())

    print(
        "🚀 MTEJA AI application startup complete "
        "(KB/model loading in background)."
    )

    # ========================================================
    # SERVER IS READY
    # ========================================================

    yield

    # ========================================================
    # SHUTDOWN
    # ========================================================

    print("🛑 MTEJA AI application shutting down...")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

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


# ============================================================
# CORS
# ============================================================

DEFAULT_FRONTEND_URL = "https://mtejaai.signiai.co.tz"


def build_cors_origins() -> list[str]:
    """Combine origins from the CORS_ORIGINS env var with the frontend URL and

    local development URLs, without duplicates.
    """

    origins = {
        origin.strip().rstrip("/")
        for origin in (getattr(settings, "CORS_ORIGINS", "") or "").split(",")
        if origin.strip()
    }

    frontend_url = (
        getattr(settings, "FRONTEND_URL", "") or DEFAULT_FRONTEND_URL
    ).rstrip("/")

    origins.add(frontend_url)
    origins.add(DEFAULT_FRONTEND_URL)
    origins.add("http://localhost:5173")

    return sorted(origins)


app.add_middleware(
    CORSMiddleware,
    allow_origins=build_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# RATE LIMIT
# ============================================================

# Enable when ready
# app.add_middleware(RateLimitMiddleware)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(telegram_webhook_router)
app.include_router(telegram_ws_router)
app.include_router(api_router, prefix="/api")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(broadcast_router)
app.include_router(webhook_router)


# ============================================================
# ROOT & HEALTH
# ============================================================


@app.get("/", tags=["Health"])
async def root():
    kb_count = (
        len(kb_service.documents) if hasattr(kb_service, "documents") else 0
    )
    return {
        "message": "MTEJA AI API is running",
        "docs": "/docs",
        "knowledge_base_documents": kb_count,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.post(
    "/predict", response_model=PredictionResponse, tags=["ML Engine"]
)
async def predict_intent(payload: QueryRequest):
    if (
        model_vectorizer is None
        or model_X_vectors is None
        or model_y_answers is None
    ):
        raise HTTPException(
            status_code=503,
            detail="Intent classification model is not loaded.",
        )

    clean_query = payload.question.lower().strip()

    if not clean_query:
        raise HTTPException(
            status_code=400, detail="Question payload cannot be empty."
        )

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
        matched_answer=(
            "Samahani, sijaelewa swali lako. Tafadhali jaribu kuuliza kwa njia"
            " nyingine."
        ),
        confidence=round(confidence_score, 2),
        status="fallback",
    )


# Static files mount
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")