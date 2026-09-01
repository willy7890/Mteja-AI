import base64
import hashlib
import hmac
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import generate_agent_reply
from app.services.client import (
    WhatsAppClient,
    FacebookClient,
    InstagramClient,
    TelegramClient,
    SMSClient,
    TikTokClient,
    TwitterClient,
)

router = APIRouter(tags=["Multi-Channel Webhooks"])


# ==========================================
# 1. WHATSAPP WEBHOOKS
# ==========================================
@router.get("/whatsapp", status_code=status.HTTP_200_OK)
async def verify_whatsapp(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
  if mode == "subscribe" and token == "mtejaai_secure_verify_token":
    return int(challenge)
  return {"error": "Verification failed"}


@router.post("/whatsapp", status_code=status.HTTP_200_OK)
async def whatsapp_webhook(request: Request):
  body = await request.json()
  try:
    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    messages = changes.get("value", {}).get("messages", [])

    if messages:
      msg = messages[0]
      phone = msg.get("from")
      text = msg.get("text", {}).get("body")
      if phone and text:
        reply = await generate_agent_reply(text)
        await WhatsAppClient.send_whatsapp_reply(phone, reply)
  except Exception as e:
    print(f"WhatsApp webhook error: {e}")
  return {"status": "success"}


# ==========================================
# 2. FACEBOOK & INSTAGRAM WEBHOOKS
# ==========================================
@router.get("/meta", status_code=status.HTTP_200_OK)
async def verify_meta(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
  if mode == "subscribe" and token == "mtejaai_secure_verify_token":
    return int(challenge)
  return {"error": "Verification failed"}


@router.post("/facebook", status_code=status.HTTP_200_OK)
async def facebook_webhook(request: Request):
  body = await request.json()
  try:
    for entry in body.get("entry", []):
      for event in entry.get("messaging", []):
        sender_id = event.get("sender", {}).get("id")
        text = event.get("message", {}).get("text")
        if sender_id and text:
          reply = await generate_agent_reply(text)
          await FacebookClient.send_facebook_reply(sender_id, reply)
  except Exception as e:
    print(f"Facebook webhook error: {e}")
  return {"status": "success"}


@router.post("/instagram", status_code=status.HTTP_200_OK)
async def instagram_webhook(request: Request):
  body = await request.json()
  try:
    for entry in body.get("entry", []):
      for event in entry.get("messaging", []):
        sender_id = event.get("sender", {}).get("id")
        text = event.get("message", {}).get("text")
        if sender_id and text:
          reply = await generate_agent_reply(text)
          await InstagramClient.send_instagram_reply(sender_id, reply)
  except Exception as e:
    print(f"Instagram webhook error: {e}")
  return {"status": "success"}


# ==========================================
# 3. TELEGRAM WEBHOOK
# ==========================================
@router.post("/telegram", status_code=status.HTTP_200_OK)
async def telegram_webhook(request: Request):
  body = await request.json()
  try:
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    if chat_id and text:
      reply = await generate_agent_reply(text)
      await TelegramClient.send_telegram_reply(str(chat_id), reply)
  except Exception as e:
    print(f"Telegram webhook error: {e}")
  return {"status": "success"}


# ==========================================
# 4. SMS (AFRICA'S TALKING) WEBHOOK
# ==========================================
@router.post("/sms", status_code=status.HTTP_200_OK)
async def sms_webhook(request: Request):
  try:
    form_data = await request.form()
    phone = form_data.get("from")
    text = form_data.get("text")
    if phone and text:
      reply = await generate_agent_reply(text)
      await SMSClient.send_sms_reply(phone, reply)
  except Exception as e:
    print(f"SMS webhook error: {e}")
  return {"status": "success"}


# ==========================================
# 5. TIKTOK WEBHOOK
# ==========================================
@router.post("/tiktok", status_code=status.HTTP_200_OK)
async def tiktok_webhook(request: Request):
  body = await request.json()
  try:
    event = body.get("data", {})
    sender_id = event.get("sender_id")
    text = event.get("content", {}).get("text")
    if sender_id and text:
      reply = await generate_agent_reply(text)
      await TikTokClient.send_tiktok_reply(sender_id, reply)
  except Exception as e:
    print(f"TikTok webhook error: {e}")
  return {"status": "success"}


# ==========================================
# 6. TWITTER / X WEBHOOK
# ==========================================
@router.get("/twitter", status_code=status.HTTP_200_OK)
async def twitter_crc(crc_token: str = Query(..., alias="crc_token")):
  # Handle Twitter CRC verification handshake
  return {"response_token": f"sha256=verified"}


@router.post("/twitter", status_code=status.HTTP_200_OK)
async def twitter_webhook(request: Request):
  body = await request.json()
  try:
    for event in body.get("direct_message_events", []):
      message_create = event.get("message_create", {})
      sender_id = message_create.get("sender_id")
      text = message_create.get("message_data", {}).get("text")
      if sender_id and text:
        reply = await generate_agent_reply(text)
        await TwitterClient.send_twitter_reply(sender_id, reply)
  except Exception as e:
    print(f"Twitter webhook error: {e}")
  return {"status": "success"}