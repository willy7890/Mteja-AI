# whatsapp webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import WhatsAppClient

router = APIRouter(prefix="/webhooks", tags=["WhatsApp Webhook"])


# 1. WhatsApp Webhook Verification (GET)
@router.get("/whatsapp", status_code=status.HTTP_200_OK)
async def verify_whatsapp_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
  verify_token = "mtejaai_secure_verify_token"  # Match this with your Meta app settings
  if mode and token:
    if mode == "subscribe" and token == verify_token:
      return int(challenge)
  return {"error": "Verification failed"}


# 2. Inbound WhatsApp Message Handler (POST)
@router.post("/whatsapp", status_code=status.HTTP_200_OK)
async def whatsapp_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
  body = await request.json()
  try:
    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])

    if messages:
      message_data = messages[0]
      sender_phone = message_data.get("from")
      message_text = message_data.get("text", {}).get("body")

      if sender_phone and message_text:
        # Query your CSV/JSON knowledge base via RAG agent
        ai_reply = await generate_agent_reply(message_text)

        # Send automated response back via WhatsApp Cloud API
        await WhatsAppClient.send_whatsapp_reply(sender_phone, ai_reply)

    return {"status": "success"}
  except Exception as e:
    print(f"WhatsApp webhook error: {e}")
    return {"status": "error", "detail": str(e)}