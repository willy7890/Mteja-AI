import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import Orchestrator
from app.api.dependencies import get_message_service
from app.core.config import settings
from app.core.database import get_db
from app.models.channel import ChannelIntegration
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.services.agent_service import handle_inbound_message
from app.services.message import MessageService
from app.services.telegram_service import format_telegram_reply


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

    if channel in {
        "telegram",
        "sms",
        "whatsapp",
        "facebook",
        "instagram",
    }:
        query = select(Customer).where(
            Customer.organization_id == organization_id,
            Customer.phone == identity,
        )

    elif channel == "email":
        query = select(Customer).where(
            Customer.organization_id == organization_id,
            Customer.email == identity,
        )

    else:
        return None

    result = await db.execute(query)

    return result.scalar_one_or_none()


def _verify_meta_signature(
    body: bytes,
    signature: str | None,
) -> None:
    if not settings.META_APP_SECRET:
        return

    if not signature or not signature.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature",
        )

    expected = hmac.new(
        settings.META_APP_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    received = signature.removeprefix("sha256=")

    if not hmac.compare_digest(received, expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature",
        )


def _verify_token(
    provider: str,
    supplied_token: str | None,
) -> str:
    expected = getattr(
        settings,
        f"{provider.upper()}_VERIFY_TOKEN",
        "",
    )

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Webhook verification token is not configured",
        )

    if not hmac.compare_digest(
        supplied_token or "",
        expected,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verification token",
        )

    return expected


async def _handle_meta_webhook(
    provider: str,
    organization_id: int,
    request: Request,
    db: AsyncSession,
    message_service: MessageService,
):
    body = await request.body()

    _verify_meta_signature(
        body,
        request.headers.get("x-hub-signature-256"),
    )

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        ) from exc

    adapter = message_service._get_adapter(provider)

    normalized = adapter.normalize_incoming(payload)

    if (
        not normalized.get("from")
        or not normalized.get("content")
    ):
        return {
            "ok": True,
            "message": "Ignored event",
        }

    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel=provider,
    )

    if not customer:
        return {
            "ok": True,
            "message": "Customer not found",
        }

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

    conversation_result = await db.execute(
        select(Conversation).where(
            Conversation.id == message.conversation_id,
            Conversation.organization_id == organization_id,
        )
    )

    conversation = conversation_result.scalar_one_or_none()

    if (
        not conversation
        or conversation.mode != "ai"
        or conversation.status != "open"
        or result.get("blocked")
    ):
        return {
            "ok": True,
            "message": "Conversation is owned by a human agent",
        }

    reply = await message_service.send(
        db=db,
        organization_id=organization_id,
        conversation_id=message.conversation_id,
        content=(
            result.get("response")
            or result.get("reply")
            or "Thanks for your message."
        ),
        channel=provider,
        sender_name=result.get(
            "agent",
            "mteja-ai",
        ),
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
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook verification request",
        )

    _verify_token(
        provider,
        verify_token,
    )

    return PlainTextResponse(challenge)


@router.get("/whatsapp/{organization_id}")
async def verify_whatsapp_webhook(
    organization_id: int,
    mode: str | None = Query(
        None,
        alias="hub.mode",
    ),
    verify_token: str | None = Query(
        None,
        alias="hub.verify_token",
    ),
    challenge: str | None = Query(
        None,
        alias="hub.challenge",
    ),
):
    return _meta_verification(
        "whatsapp",
        mode,
        verify_token,
        challenge,
    )


@router.post("/whatsapp/{organization_id}")
async def whatsapp_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    return await _handle_meta_webhook(
        "whatsapp",
        organization_id,
        request,
        db,
        message_service,
    )


@router.get("/facebook/{organization_id}")
async def verify_facebook_webhook(
    organization_id: int,
    mode: str | None = Query(
        None,
        alias="hub.mode",
    ),
    verify_token: str | None = Query(
        None,
        alias="hub.verify_token",
    ),
    challenge: str | None = Query(
        None,
        alias="hub.challenge",
    ),
):
    return _meta_verification(
        "facebook",
        mode,
        verify_token,
        challenge,
    )


@router.post("/facebook/{organization_id}")
async def facebook_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    return await _handle_meta_webhook(
        "facebook",
        organization_id,
        request,
        db,
        message_service,
    )


@router.get("/instagram/{organization_id}")
async def verify_instagram_webhook(
    organization_id: int,
    mode: str | None = Query(
        None,
        alias="hub.mode",
    ),
    verify_token: str | None = Query(
        None,
        alias="hub.verify_token",
    ),
    challenge: str | None = Query(
        None,
        alias="hub.challenge",
    ),
):
    return _meta_verification(
        "instagram",
        mode,
        verify_token,
        challenge,
    )


@router.post("/instagram/{organization_id}")
async def instagram_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    return await _handle_meta_webhook(
        "instagram",
        organization_id,
        request,
        db,
        message_service,
    )


async def _find_telegram_integration_by_secret(
    db: AsyncSession,
    secret_token: str,
) -> ChannelIntegration | None:
    if not secret_token:
        return None

    result = await db.execute(
        select(ChannelIntegration).where(
            ChannelIntegration.channel_name == "telegram",
            ChannelIntegration.is_active.is_(True),
        )
    )

    integrations = result.scalars().all()

    for integration in integrations:
        if not integration.credentials_json:
            continue

        try:
            credentials = json.loads(
                integration.credentials_json
            )
        except (TypeError, ValueError):
            continue

        if not isinstance(credentials, dict):
            continue

        stored_secret = credentials.get("webhook_secret")

        if not stored_secret:
            continue

        if hmac.compare_digest(
            str(stored_secret),
            str(secret_token),
        ):
            return integration

    return None


async def _process_telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    secret_token = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if not secret_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing Telegram webhook secret",
        )

    integration = await _find_telegram_integration_by_secret(
        db=db,
        secret_token=secret_token,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram webhook secret",
        )

    organization_id = integration.organization_id

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        ) from exc

    adapter = await message_service._get_adapter_for_organization(
        db=db,
        organization_id=organization_id,
        channel="telegram",
    )

    normalized = adapter.normalize_incoming(payload)

    if (
        not normalized.get("from")
        or not normalized.get("content")
    ):
        return {
            "ok": True,
            "message": "Ignored Telegram event",
        }

    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel="telegram",
    )

    if not customer:
        metadata = normalized.get("channel_metadata") or {}
        customer = Customer(
            organization_id=organization_id,
            name=(
                metadata.get("from_first_name")
                or metadata.get("from_username")
                or "Telegram customer"
            ),
            phone=normalized["from"],
        )
        db.add(customer)
        await db.flush()

    message = await message_service.handle_incoming(
        db=db,
        organization_id=organization_id,
        channel="telegram",
        raw_payload=payload,
        customer_id=customer.id,
    )

    result = await handle_inbound_message(
        db=db,
        organization_id=organization_id,
        contact_id=str(message.conversation_id),
        message_text=normalized["content"],
    )

    conversation_result = await db.execute(
        select(Conversation).where(
            Conversation.id == message.conversation_id,
            Conversation.organization_id == organization_id,
        )
    )

    conversation = conversation_result.scalar_one_or_none()

    if (
        not conversation
        or conversation.current_handler != "ai"
        or conversation.status != "open"
        or result.get("status") == "ESCALATED"
    ):
        return {
            "ok": True,
            "message": "Conversation is owned by a human agent",
        }

    reply_text = result.get("reply") or "Thanks for your message."

    reply = await message_service.send(
        db=db,
        organization_id=organization_id,
        conversation_id=message.conversation_id,
        content=reply_text,
        channel="telegram",
        sender_name=result.get(
            "agent",
            "mteja-ai",
        ),
    )

    return {
        "ok": True,
        "organization_id": organization_id,
        "integration_id": integration.id,
        "message_id": message.id,
        "conversation_id": message.conversation_id,
        "reply_id": reply.external_id,
        "reply_status": reply.status,
    }


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    return await _process_telegram_webhook(
        request=request,
        db=db,
        message_service=message_service,
    )


@router.post("/telegram/{organization_id}")
async def telegram_webhook_with_organization(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    return await _process_telegram_webhook(
        request=request,
        db=db,
        message_service=message_service,
    )


@router.post("/email/{organization_id}")
async def email_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    try:
        content_type = request.headers.get(
            "content-type",
            "",
        )

        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid email webhook payload",
        ) from exc

    adapter = message_service._get_adapter("email")

    normalized = adapter.normalize_incoming(payload)

    if (
        not normalized.get("from")
        or not normalized.get("content")
    ):
        return {
            "ok": True,
            "message": "Ignored email event",
        }

    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel="email",
    )

    if not customer:
        return {
            "ok": True,
            "message": "Customer not found",
        }

    message = await message_service.handle_incoming(
        db=db,
        organization_id=organization_id,
        channel="email",
        raw_payload=payload,
        customer_id=customer.id,
    )

    result = await orchestrator.run(
        db=db,
        organization_id=organization_id,
        conversation_id=str(message.conversation_id),
        message=normalized["content"],
    )

    conversation_result = await db.execute(
        select(Conversation).where(
            Conversation.id == message.conversation_id,
            Conversation.organization_id == organization_id,
        )
    )

    conversation = conversation_result.scalar_one_or_none()

    if (
        not conversation
        or conversation.mode != "ai"
        or conversation.status != "open"
        or result.get("blocked")
    ):
        return {
            "ok": True,
            "message": "Conversation is owned by a human agent",
        }

    reply = await message_service.send(
        db=db,
        organization_id=organization_id,
        conversation_id=message.conversation_id,
        content=(
            result.get("response")
            or result.get("reply")
            or "Thanks for your message."
        ),
        channel="email",
        sender_name=result.get(
            "agent",
            "mteja-ai",
        ),
    )

    return {
        "ok": True,
        "message_id": message.id,
        "conversation_id": message.conversation_id,
        "reply_id": reply.external_id,
        "reply_status": reply.status,
    }


@router.post("/sms/{organization_id}")
async def sms_webhook(
    organization_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(
        get_message_service
    ),
):
    try:
        content_type = request.headers.get(
            "content-type",
            "",
        )

        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid SMS webhook payload",
        ) from exc

    adapter = message_service._get_adapter("sms")

    normalized = adapter.normalize_incoming(payload)

    if (
        not normalized.get("from")
        or not normalized.get("content")
    ):
        return {
            "ok": True,
            "message": "Ignored SMS event",
        }

    customer = await find_customer_by_identity(
        db=db,
        organization_id=organization_id,
        identity=normalized["from"],
        channel="sms",
    )

    if not customer:
        return {
            "ok": True,
            "message": "Customer not found",
        }

    message = await message_service.handle_incoming(
        db=db,
        organization_id=organization_id,
        channel="sms",
        raw_payload=payload,
        customer_id=customer.id,
    )

    result = await orchestrator.run(
        db=db,
        organization_id=organization_id,
        conversation_id=str(message.conversation_id),
        message=normalized["content"],
    )

    conversation_result = await db.execute(
        select(Conversation).where(
            Conversation.id == message.conversation_id,
            Conversation.organization_id == organization_id,
        )
    )

    conversation = conversation_result.scalar_one_or_none()

    if (
        not conversation
        or conversation.mode != "ai"
        or conversation.status != "open"
        or result.get("blocked")
    ):
        return {
            "ok": True,
            "message": "Conversation is owned by a human agent",
        }

    reply = await message_service.send(
        db=db,
        organization_id=organization_id,
        conversation_id=message.conversation_id,
        content=(
            result.get("response")
            or result.get("reply")
            or "Thanks for your message."
        ),
        channel="sms",
        sender_name=result.get(
            "agent",
            "mteja-ai",
        ),
    )

    return {
        "ok": True,
        "message_id": message.id,
        "conversation_id": message.conversation_id,
        "reply_id": reply.external_id,
        "reply_status": reply.status,
    }