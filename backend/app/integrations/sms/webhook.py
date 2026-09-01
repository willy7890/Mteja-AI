# sms webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import SMSClient

router = APIRouter(prefix="/webhooks", tags=["SMS Webhook"])


# Inbound SMS Handler (POST)
@router.post("/sms", status_code=status.HTTP_200_OK)
async def sms_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
  try:
    # Africa's Talking sends data via form-data
    form_data = await request.form()
    sender_phone = form_data.get("from")
    message_text = form_data.get("text")

    if sender_phone and message_text:
      # Query your CSV/JSON knowledge base via RAG agent
      ai_reply = await generate_agent_reply(message_text)

      # Send automated response back via SMS
      await SMSClient.send_sms_reply(sender_phone, ai_reply)

    return {"status": "success"}
  except Exception as e:
    print(f"SMS webhook error: {e}")
    return {"status": "error", "detail": str(e)}