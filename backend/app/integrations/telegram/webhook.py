import logging
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import settings
from app.core.database import get_db
from app.services.chat_service import get_trained_rag_response

# Anzisha logger
logger = logging.getLogger("telegram_webhook")

router = APIRouter()

TELEGRAM_BOT_TOKEN = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


async def send_telegram_message(chat_id: str, text: str):
    """Tuma jibu kwenda Telegram API."""
    if not text or not TELEGRAM_BOT_TOKEN:
        return

    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }
            await client.post(TELEGRAM_API_URL, json=payload, timeout=10.0)
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")


async def process_telegram_update(data: dict, db: AsyncSession):
    """Soma JSON kutoka Telegram na uipitishe kwenye RAG/LLM."""
    try:
        # Safely extract message object
        message = data.get("message") or data.get("edited_message") or {}
        
        # Kama sio message ya kawaida (k.m. channel post au inline query), puuzia bila kutoa warning
        if not message:
            return

        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))
        incoming_text = message.get("text", "").strip()

        if not chat_id:
            return

        # Kama mtumiaji ametuma picha/sticker au faili bila text
        if not incoming_text:
            await send_telegram_message(
                chat_id, 
                "Samahani, kwa sasa naweza kusoma na kujibu ujumbe wa maandishi (text) pekee."
            )
            return

        # Kagua /start command
        if incoming_text == "/start":
            await send_telegram_message(
                chat_id, 
                "Habari! Karibu Mteja AI. Nawezaje kukusaidia leo?"
            )
            return

        # Pata jibu kupitia RAG + LLM kutoka kwenye Trained Data
        ai_reply = await get_trained_rag_response(
            db_session=db,
            user_id=chat_id,
            user_query=incoming_text,
            chat_history_list=[]
        )

        # Tuma jibu kwa mtumiaji
        await send_telegram_message(chat_id, ai_reply)

    except Exception as e:
        logger.error(f"Error processing Telegram background task: {e}")


@router.post("/telegram/webhook", tags=["Telegram Integration"])
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint inayopokea updates zote kutoka Telegram bila kutoa Yellow Warning."""
    try:
        # Tumia request.json() badala ya Pydantic strict schema ili kuzuia 422 errors
        data = await request.json()
        
        # Ongeza mchakato kwenye background task
        background_tasks.add_task(process_telegram_update, data, db)

        return {"status": "ok"}
    except Exception as e:
        logger.warning(f"Telegram webhook raw payload error: {e}")
        return {"status": "ok"} # Telegram inataka '200 OK' siku zote ili isiendelee kuretry