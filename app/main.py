import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services import messaging_window
from app.core.config import settings
from app.core.database import engine, Base
from app.models.user import User
from app.models.organization import Organization
from app.models.customer import Customer
from app.models.telegram import TelegramLink, TelegramSession
from app.models import customer, organization, user, activity_log, conversation, message
from app.api.router import api_router
from app.routes.chat import router as chat_router
from app.api.v1 import webhooks
from app.services.telegram_service import build_telegram_app
from app.routes import media


logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

telegram_app = build_telegram_app() if settings.TELEGRAM_BOT_TOKEN else None
telegram_status = {"verified": False, "username": None, "polling": False}


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if telegram_app is None:
        logger.info("Telegram bot is not configured; skipping polling startup")
        return

    await telegram_app.initialize()
    bot = await telegram_app.bot.get_me()
    telegram_status.update(
        verified=True,
        username=bot.username,
    )
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    telegram_status["polling"] = True
    logger.info("Telegram bot started (polling) as @%s", bot.username)


@app.on_event("shutdown")
async def on_shutdown():
    telegram_status["polling"] = False
    if telegram_app is None:
        return

    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()
    logger.info("Telegram bot stopped")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "MTEJA AI API is running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "telegram": telegram_status,
    }


app.include_router(chat_router, tags=["chat"])

app.include_router(webhooks.router, prefix="/api/v1")


#app.include_router(messaging_window.router, prefix="/api/v1", tags=["messaging-window"])

app.include_router(media.router, prefix="/api/v1", tags=["media"])