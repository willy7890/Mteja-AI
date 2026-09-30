from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/telegram", tags=["Telegram"])


class TelegramWebhookPayload(BaseModel):
    update_id: int
    message: dict | None = None


@router.get("/health")
async def telegram_health():
    return {"status": "ok", "service": "telegram"}


@router.post("/webhook")
async def telegram_webhook(payload: TelegramWebhookPayload):
    if payload.message is None:
        raise HTTPException(status_code=400, detail="No message payload received")

    return {"status": "received", "update_id": payload.update_id}
