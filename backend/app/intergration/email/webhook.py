# email webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import EmailClient

router = APIRouter(prefix="/webhooks", tags=["Email Webhook"])


class EmailWebhookPayload(BaseModel):
  sender_email: EmailStr
  subject: str
  message_body: str


@router.post("/email", status_code=status.HTTP_200_OK)
async def email_incoming_webhook(
    payload: EmailWebhookPayload, db: AsyncSession = Depends(get_db)
):
  try:
    # 1. Query your CSV/JSON knowledge base via RAG agent
    ai_reply = await generate_agent_reply(payload.message_body)

    # 2. Send the automated reply back to the customer via EmailClient
    success = EmailClient.send_email_reply(
        recipient=payload.sender_email,
        subject=payload.subject,
        reply_content=ai_reply,
    )

    if not success:
      raise HTTPException(
          status_code=500, detail="Failed to dispatch email reply."
      )

    return {
        "status": "success",
        "recipient": payload.sender_email,
        "reply": ai_reply,
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))