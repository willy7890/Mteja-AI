import hashlib
import hmac

from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.dependencies import get_message_service
from app.services.message import MessageService
from app.models.customer import Customer
from app.agents.orchestrator import Orchestrator
from app.services.telegram_service import format_telegram_reply
from app.core.config import settings


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
orchestrator = Orchestrator()



async def find_customer_by_identity(
    db: AsyncSession,
    organization_id: int,
    identity: str,
    channel: str,
):

   
    if not identity:
        return None

    
    if channel == "telegram":
    
        query = select(Customer).where(
            Customer.organization_id == organization_id,
            Customer.phone == identity,
        )
    elif channel == "sms":
        query = select(Customer).where(
            Customer.organization_id == organization_id,
            Customer.phone == identity,
        )
    elif channel == "email":
        query = select(Customer).where(
            Customer.organization_id == organization_id,
            Customer.email == identity,
        )
    elif channel in {"whatsapp", "facebook", "instagram"}:
        query = select(Customer).where(
            Customer.organization_id == organization_id,
            Customer.phone == identity,
        )
    else:
        return None

    result = await db.execute(query)
    return result.scalar_one_or_none()


def _verify_meta_signature(body: bytes, signature: str | None) -> None:
    if not settings.META_APP_SECRET:
        return
    if not signature or not signature.startswith("sha256="):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook signature")
    expected = hmac.new(settings.META_APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature.removeprefix("sha256="), expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook signature")


def _verify_token(provider: str, supplied_token: str | None) -> str:
    expected = getattr(settings, f"{provider.upper()}_VERIFY_TOKEN", "")
    if not expected or not hmac.compare_digest(supplied_token or "", expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid verification token")
    return expected


async def _handle_meta_webhook(
    provider: str,
    organization_id: int,
    request: Request,
    db: AsyncSession,
    message_service: MessageService,
):
    body = await request.body()
    _verify_meta_signature(body, request.headers.get("x-hub-signature-256"))
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    normalized = message_service._get_adapter(provider).normalize_incoming(payload)
    if not normalized.get("from") or not normalized.get("content"):
        return {"ok": True, "message": "Ignored event"}

    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel=provider,
    )
    if not customer:
        return {"ok": True, "message": "Customer not found"}

    message = await message_service.handle_incoming(
        db=db,
        organization_id=organization_id,
        channel=provider,
        raw_payload=payload,
        customer_id=customer.id,
    )
    result = await orchestrator.run(
        db=db,
        organization_id=organization_id,
        conversation_id=str(message.conversation_id),
        message=normalized["content"],
    )
    reply = await message_service.send(
        db=db,
        organization_id=organization_id,
        conversation_id=message.conversation_id,
        content=result.get("response") or result.get("reply") or "Thanks for your message.",
        channel=provider,
        sender_name=result.get("agent", "mteja-ai"),
    )
    return {
        "ok": True,
        "message_id": message.id,
        "conversation_id": message.conversation_id,
        "reply_id": reply.external_id,
        "reply_status": reply.status,
    }


def _meta_verification(
    provider: str,
    mode: str | None,
    verify_token: str | None,
    challenge: str | None,
):
    if mode != "subscribe" or not challenge:
        raise HTTPException(status_code=400, detail="Invalid webhook verification request")
    _verify_token(provider, verify_token)
    return PlainTextResponse(challenge)


@router.get("/whatsapp/{organization_id}")
async def verify_whatsapp_webhook(
    organization_id: int,
    mode: str | None = Query(None, alias="hub.mode"),
    verify_token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
):
    return _meta_verification("whatsapp", mode, verify_token, challenge)


@router.post("/whatsapp/{organization_id}")
async def whatsapp_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(get_message_service),
):
    return await _handle_meta_webhook("whatsapp", organization_id, request, db, message_service)


@router.get("/facebook/{organization_id}")
async def verify_facebook_webhook(
    organization_id: int,
    mode: str | None = Query(None, alias="hub.mode"),
    verify_token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
):
    return _meta_verification("facebook", mode, verify_token, challenge)


@router.post("/facebook/{organization_id}")
async def facebook_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(get_message_service),
):
    return await _handle_meta_webhook("facebook", organization_id, request, db, message_service)


@router.get("/instagram/{organization_id}")
async def verify_instagram_webhook(
    organization_id: int,
    mode: str | None = Query(None, alias="hub.mode"),
    verify_token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
):
    return _meta_verification("instagram", mode, verify_token, challenge)


@router.post("/instagram/{organization_id}")
async def instagram_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(get_message_service),
):
    return await _handle_meta_webhook("instagram", organization_id, request, db, message_service)


@router.post("/telegram/{organization_id}")
async def telegram_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(get_message_service),
):
    
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    
    adapter = message_service._get_adapter("telegram")
    normalized = adapter.normalize_incoming(payload)

    if not normalized.get("from") or not normalized.get("content"):
        
        return {"ok": True, "message": "Ignored"}

    
    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel="telegram",
    )

    if not customer:
        
        print(f"[Telegram] Unknown customer: {normalized['from']}")
        return {"ok": True, "message": "Customer not found"}

    
    message = await message_service.handle_incoming(
        db=db,
        organization_id=organization_id,
        channel="telegram",
        raw_payload=payload,
        customer_id=customer.id,
    )

    result = await orchestrator.run(
        db=db,
        organization_id=organization_id,
        conversation_id=str(message.conversation_id),
        message=normalized["content"],
    )
    reply_text = format_telegram_reply(result)
    reply = await message_service.send(
        db=db,
        organization_id=organization_id,
        conversation_id=message.conversation_id,
        content=reply_text,
        channel="telegram",
        sender_name=result.get("agent", "mteja-ai"),
    )

    return {
        "ok": True,
        "message_id": message.id,
        "conversation_id": message.conversation_id,
        "reply_id": reply.external_id,
        "reply_status": reply.status,
    }


@router.post("/email/{organization_id}")
async def email_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(get_message_service),
):
    try:
       
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    adapter = message_service._get_adapter("email")
    normalized = adapter.normalize_incoming(payload)

    if not normalized.get("from"):
        return {"ok": True, "message": "Ignored - no sender"}

    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel="email",
    )

    if not customer:
        print(f"[Email] Unknown customer: {normalized['from']}")
        return {"ok": True, "message": "Customer not found"}

    message = await message_service.handle_incoming(
        db=db,
        organization_id=organization_id,
        channel="email",
        raw_payload=payload,
        customer_id=customer.id,
    )

    return {
        "ok": True,
        "message_id": message.id,
        "conversation_id": message.conversation_id,
    }



@router.post("/sms/{organization_id}")
async def sms_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(get_message_service),
):
    
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    adapter = message_service._get_adapter("sms")
    normalized = adapter.normalize_incoming(payload)

    if not normalized.get("from") or not normalized.get("content"):
        return {"ok": True, "message": "Ignored"}

    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel="sms",
    )

    if not customer:
        print(f"[SMS] Unknown customer: {normalized['from']}")
        return {"ok": True, "message": "Customer not found"}

    message = await message_service.handle_incoming(
        db=db,
        organization_id=organization_id,
        channel="sms",
        raw_payload=payload,
        customer_id=customer.id,
    )

    return {
        "ok": True,
        "message_id": message.id,
        "conversation_id": message.conversation_id,
    }