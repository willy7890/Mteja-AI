from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.api.v1 import webhooks
from app.core.config import settings
from app.core.database import Base, engine
from app.core.rate_limit import RateLimitMiddleware
from app.api.analytics import router as analytics_router
from app.models import (
    activity_log,
    conversation,
    customer,
    media,
    message,
    organization,
    telegram,
    training_data,
    user,
)
from app.routes.chat import router as chat_router
from app.services.telegram_service import build_telegram_app

logger = logging.getLogger(__name__)

# Telegram Bot Instance & Status Tracker
telegram_app = build_telegram_app()
telegram_status = {
    "verified": False,
    "username": None,
    "polling": False,
    "mode": "polling",
    "error": None,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP HANDLERS ---
    # 1. Initialize Database Tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as exc:
        logger.exception("Database initialization failed: %s", exc)
        raise exc

    # 2. Initialize Telegram Bot Polling
    try:
        logger.info("Initializing Telegram bot in polling mode...")
        await telegram_app.initialize()
        bot = await telegram_app.bot.get_me()
        await telegram_app.start()
        await telegram_app.updater.start_polling()

        telegram_status.update(
            verified=True,
            username=bot.username,
            polling=True,
            mode="polling",
            error=None,
        )
        logger.info("Telegram bot started (polling) as @%s", bot.username)
    except Exception as exc:
        telegram_status.update(
            verified=False,
            polling=False,
            mode="polling",
            error=str(exc),
        )
        logger.exception(
            "Telegram initialization failed, but FastAPI will continue: %s",
            exc,
        )

    yield

    # --- SHUTDOWN HANDLERS ---
    telegram_status["polling"] = False
    try:
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()
        logger.info("Telegram bot stopped cleanly")
    except Exception as exc:
        logger.warning("Telegram shutdown warning: %s", exc)

    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Upload Directories Setup & Mounts
UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
os.makedirs("uploads/customers", exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_ROOT), name="uploads")

# Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# Application Routers
app.include_router(api_router, prefix="/api")
app.include_router(chat_router, tags=["chat"])
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(analytics_router)

@app.get("/")
async def root():
    return {
        "message": "MTEJA AI API is running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "telegram": telegram_status,
    }