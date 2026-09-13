# instagram webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import InstagramClient

router = APIRouter(prefix="/webhooks", tags=["Instagram Webhook"])


# 1. Instagram Webhook Verification (GET)
@router.get("/instagram", status_code=status.HTTP_200_OK)
async def verify_instagram_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
  verify_token = "mtejaai_secure_verify_token"  # Match this with your Meta app settings
  if mode and token:
    if mode == "subscribe" and token == verify_token:
      return int(challenge)
  return {"error": "Verification failed"}


# 2. Inbound Instagram DM Handler (POST)
@router.post("/instagram", status_code=status.HTTP_200_OK)
async def instagram_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
  body = await request.json()
  try:
    if body.get("object") == "instagram":
      for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
          sender_id = event.get("sender", {}).get("id")
          message_text = event.get("message", {}).get("text")

          if sender_id and message_text:
            # Query your CSV/JSON knowledge base via RAG agent
            ai_reply = await generate_agent_reply(message_text)

            # Send automated reply back to Instagram user
            await InstagramClient.send_instagram_reply(sender_id, ai_reply)

    return {"status": "success"}
  except Exception as e:
    print(f"Instagram webhook error: {e}")
    return {"status": "error", "detail": str(e)}