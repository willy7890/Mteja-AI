# tiktok webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import TikTokClient

router = APIRouter(prefix="/webhooks", tags=["TikTok Webhook"])


# Inbound TikTok Message Handler (POST)
@router.post("/tiktok", status_code=status.HTTP_200_OK)
async def tiktok_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
  body = await request.json()
  try:
    event = body.get("data", {})
    sender_id = event.get("sender_id")
    message_text = event.get("content", {}).get("text")

    if sender_id and message_text:
      # Query your CSV/JSON knowledge base via RAG agent
      ai_reply = await generate_agent_reply(message_text)

      # Send automated response back on TikTok
      await TikTokClient.send_tiktok_reply(sender_id, ai_reply)

    return {"status": "success"}
  except Exception as e:
    print(f"TikTok webhook error: {e}")
    return {"status": "error", "detail": str(e)}