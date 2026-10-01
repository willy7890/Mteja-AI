import httpx
import logging
from fastapi import APIRouter, Request, Response, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.chat_service import get_trained_rag_response

logger = logging.getLogger("whatsapp_webhook")

router = APIRouter()

WHATSAPP_TOKEN = getattr(settings, "WHATSAPP_ACCESS_TOKEN", "")
PHONE_NUMBER_ID = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "")
VERIFY_TOKEN = getattr(settings, "WHATSAPP_VERIFY_TOKEN", "mteja_ai_secret_token")

WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"


async def send_whatsapp_message(phone_number: str, text: str):
    """Inatuma ujumbe wa maandishi kwenda WhatsApp API."""
    if not text or not WHATSAPP_TOKEN:
        return

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(WHATSAPP_API_URL, json=payload, headers=headers, timeout=10.0)
            if res.status_code != 200:
                logger.error(f"WhatsApp API Error: {res.text}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")


async def process_whatsapp_update(data: dict, db: AsyncSession):
    """Worker inayosoma ujumbe wa WhatsApp na kuvuta jibu kutoka RAG/LLM."""
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return  # Sio message event (labda ni status notification kama 'delivered')

        message = messages[0]
        sender_phone = message.get("from")  # Namba ya simu ya mteja
        message_type = message.get("type")

        # Kusoma text pekee
        if message_type == "text":
            incoming_text = message.get("text", {}).get("body", "").strip()

            # Pata jibu kutoka kwenye RAG + LLM Engine
            ai_reply = await get_trained_rag_response(
                db_session=db,
                user_id=sender_phone,
                user_query=incoming_text,
                chat_history_list=[]
            )

            # Tuma jibu kwa mteja WhatsApp
            await send_whatsapp_message(sender_phone, ai_reply)

        else:
            await send_whatsapp_message(
                sender_phone, 
                "Samahani, kwa sasa naweza kujibu ujumbe wa maandishi (text) pekee."
            )

    except Exception as e:
        logger.error(f"Error processing WhatsApp update: {e}")


# ------------------------------------------------------------------
# 1. VERIFICATION ENDPOINT (Meta inatumia hii ku-verify Webhook)
# ------------------------------------------------------------------
@router.get("/whatsapp/webhook", tags=["WhatsApp Integration"])
async def verify_whatsapp_webhook(request: Request):
    """Endpoint ya Meta kudhibitisha Webhook URL yako."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("WhatsApp Webhook verified successfully!")
            return Response(content=challenge, status_code=200)
        else:
            return Response(content="Verification failed", status_code=403)
            
    return Response(content="Bad Request", status_code=400)


# ------------------------------------------------------------------
# 2. MESSAGE RECEIVER ENDPOINT
# ------------------------------------------------------------------
@router.post("/whatsapp/webhook", tags=["WhatsApp Integration"])
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint inayopokea messages zote za WhatsApp."""
    try:
        data = await request.json()
        background_tasks.add_task(process_whatsapp_update, data, db)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Invalid WhatsApp payload: {e}")
        return {"status": "ok"}  # Lazima urudishe 200 OK kwa Meta