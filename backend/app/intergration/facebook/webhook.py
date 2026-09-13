# facebook webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import FacebookClient

router = APIRouter(prefix="/webhooks", tags=["Facebook Webhook"])


# 1. Facebook Webhook Verification (GET)
@router.get("/facebook", status_code=status.HTTP_200_OK)
async def verify_facebook_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
  verify_token = "mtejaai_secure_verify_token"  # Match this with your Meta app settings
  if mode and token:
    if mode == "subscribe" and token == verify_token:
      return int(challenge)
  return {"error": "Verification failed"}


# 2. Inbound Facebook Message Handler (POST)
@router.post("/facebook", status_code=status.HTTP_200_OK)
async def facebook_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
  body = await request.json()
  try:
    if body.get("object") == "page":
      for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
          sender_id = event.get("sender", {}).get("id")
          message_text = event.get("message", {}).get("text")

          if sender_id and message_text:
            # Query your CSV/JSON knowledge base via RAG agent
            ai_reply = await generate_agent_reply(message_text)

            # Send automated reply back to Facebook user
            await FacebookClient.send_facebook_reply(sender_id, ai_reply)

    return {"status": "success"}
  except Exception as e:
    print(f"Facebook webhook error: {e}")
    return {"status": "error", "detail": str(e)}