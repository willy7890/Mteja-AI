import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base

from app.models.user import User
from app.models.organization import Organization
from app.models.customer import Customer
from app.models.telegram import TelegramLink, TelegramSession
from app.models import (
    customer,
    organization,
    user,
    activity_log,
    conversation,
    message,
)

from app.api.router import api_router
from app.routes.chat import router as chat_router
from app.api.v1 import webhooks
from app.services.telegram_service import build_telegram_app


logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================
# TELEGRAM APPLICATION
# ============================================================

telegram_app = build_telegram_app()

telegram_status = {
    "verified": False,
    "username": None,
    "polling": False,
    "mode": "webhook",
    "error": None,
}


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def on_startup():

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")

    except Exception as exc:
        logger.exception(
            "Database initialization failed: %s",
            exc,
        )
        raise

    # --------------------------------------------------------
    # TELEGRAM
    # --------------------------------------------------------

    try:
        logger.info("Initializing Telegram bot in webhook mode...")

        await telegram_app.initialize()

        bot = await telegram_app.bot.get_me()

        telegram_status.update(
            verified=True,
            username=bot.username,
            polling=False,
            mode="webhook",
            error=None,
        )

        logger.info(
            "Telegram bot verified successfully as @%s",
            bot.username,
        )

        logger.info(
            "Telegram polling is DISABLED. Webhook mode is active."
        )

    except Exception as exc:

        telegram_status.update(
            verified=False,
            polling=False,
            mode="webhook",
            error=str(exc),
        )

        logger.exception(
            "Telegram initialization failed, but FastAPI will continue: %s",
            exc,
        )


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event("shutdown")
async def on_shutdown():

    telegram_status["polling"] = False

    # --------------------------------------------------------
    # TELEGRAM APPLICATION SHUTDOWN
    # --------------------------------------------------------

    try:
        await telegram_app.shutdown()

    except Exception as exc:
        logger.warning(
            "Telegram shutdown warning: %s",
            exc,
        )

    logger.info("Application shutdown complete")


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
# API ROUTES
# ============================================================

app.include_router(
    api_router,
    prefix="/api",
)


app.include_router(
    chat_router,
    tags=["chat"],
)


app.include_router(
    webhooks.router,
    prefix="/api/v1",
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {
        "message": "MTEJA AI API is running",
        "docs": "/docs",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "telegram": telegram_status,
    }