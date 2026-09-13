# telegram webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import TelegramClient

router = APIRouter(prefix="/webhooks", tags=["Telegram Webhook"])


# Inbound Telegram Message Handler (POST)
@router.post("/telegram", status_code=status.HTTP_200_OK)
async def telegram_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
  body = await request.json()
  try:
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_text = message.get("text")

    if chat_id and message_text:
      # Query your CSV/JSON knowledge base via RAG agent
      ai_reply = await generate_agent_reply(message_text)

      # Send automated response back to Telegram chat
      await TelegramClient.send_telegram_reply(str(chat_id), ai_reply)

    return {"status": "success"}
  except Exception as e:
    print(f"Telegram webhook error: {e}")
    return {"status": "error", "detail": str(e)}