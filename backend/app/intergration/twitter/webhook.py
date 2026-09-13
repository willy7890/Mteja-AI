# twitter webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
import base64
import hashlib
import hmac
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import TwitterClient

router = APIRouter(prefix="/webhooks", tags=["Twitter Webhook"])


# 1. Twitter CRC Challenge Check (GET)
@router.get("/twitter", status_code=status.HTTP_200_OK)
async def twitter_crc_check(crc_token: str = Query(..., alias="crc_token")):
  consumer_secret = getattr(settings, "TWITTER_CONSUM_SECRET", "").encode()
  token_bytes = crc_token.encode()

  # Generate HMAC SHA-256 hash required by Twitter
  sha256_hash_digest = hmac.new(
      consumer_secret, token_bytes, hashlib.sha256
  ).digest()
  base64_digest = base64.b64encode(sha256_hash_digest).decode("utf-8")

  return {"response_token": f"sha256={base64_digest}"}


# 2. Inbound Twitter DM Handler (POST)
@router.post("/twitter", status_code=status.HTTP_200_OK)
async def twitter_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
  body = await request.json()
  try:
    direct_messages = body.get("direct_message_events", [])
    for event in direct_messages:
      message_create = event.get("message_create", {})
      sender_id = message_create.get("sender_id")
      recipient_id = message_create.get("target", {}).get("recipient_id")
      text = message_create.get("message_data", {}).get("text")

      # Prevent bot from replying to itself
      my_bot_id = getattr(settings, "TWITTER_BOT_USER_ID", "")
      if sender_id and text and sender_id != my_bot_id:
        # Query your CSV/JSON knowledge base via RAG agent
        ai_reply = await generate_agent_reply(text)

        # Send automated response back via Twitter DM
        await TwitterClient.send_twitter_reply(sender_id, ai_reply)

    return {"status": "success"}
  except Exception as e:
    print(f"Twitter webhook error: {e}")
    return {"status": "error", "detail": str(e)}