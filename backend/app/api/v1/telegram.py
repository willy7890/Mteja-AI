import json
import secrets
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import get_current_user
from app.models.channel import ChannelIntegration
from app.models.user import User

router = APIRouter(prefix="/telegram", tags=["Telegram"])


def _parse_credentials(integration: ChannelIntegration) -> dict:
    try:
        credentials = json.loads(integration.credentials_json or "{}")
    except (json.JSONDecodeError, TypeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Invalid Telegram integration credentials",
        ) from exc

    if not isinstance(credentials, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid Telegram integration credentials",
        )

    return credentials


def _get_telegram_token(integration: ChannelIntegration) -> str:
    credentials = _parse_credentials(integration)
    token = credentials.get("bot_token") or settings.TELEGRAM_BOT_TOKEN

    if not token:
        raise HTTPException(
            status_code=503,
            detail="Telegram bot token is missing",
        )

    return str(token).strip()


def _get_or_create_webhook_secret(integration: ChannelIntegration) -> str:
    credentials = _parse_credentials(integration)
    webhook_secret = credentials.get("webhook_secret")

    if webhook_secret:
        return str(webhook_secret)

    webhook_secret = secrets.token_urlsafe(32)
    credentials["webhook_secret"] = webhook_secret
    integration.credentials_json = json.dumps(credentials, separators=(",", ":"))

    return webhook_secret


def _telegram_api_url(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


_RETRYABLE_TELEGRAM_EXCEPTIONS = (
    httpx.ConnectTimeout,
    httpx.ConnectError,
    httpx.ReadTimeout,
)

_telegram_client: httpx.AsyncClient | None = None


def _get_telegram_client() -> httpx.AsyncClient:
    global _telegram_client
    if _telegram_client is None or _telegram_client.is_closed:
        _telegram_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=20.0, read=20.0, write=20.0, pool=20.0),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=120.0,
            ),
            http2=True,
        )
    return _telegram_client


@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(_RETRYABLE_TELEGRAM_EXCEPTIONS),
    reraise=True,
)
async def _post_to_telegram(url: str, payload: dict[str, Any]) -> httpx.Response:
    client = _get_telegram_client()
    response = await client.post(url, json=payload)
    response.raise_for_status()
    return response


async def _telegram_request(
    token: str,
    method: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        response = await _post_to_telegram(
            _telegram_api_url(token, method),
            payload or {},
        )
        data = response.json()
    except httpx.ConnectTimeout as exc:
        raise HTTPException(
            status_code=503,
            detail="Cannot reach api.telegram.org from the backend",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Telegram API is unavailable",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Telegram returned an invalid response",
        ) from exc

    if not data.get("ok"):
        raise HTTPException(
            status_code=502,
            detail=data.get("description", "Telegram API request failed"),
        )

    return data


async def _get_telegram_integration(db, organization_id: int) -> ChannelIntegration:
    result = await db.execute(
        select(ChannelIntegration)
        .where(
            ChannelIntegration.organization_id == organization_id,
            ChannelIntegration.channel_name == "telegram",
        )
        .order_by(ChannelIntegration.id.desc())
    )
    integration = result.scalars().first()

    if not integration:
        raise HTTPException(
            status_code=404,
            detail="Telegram integration has not been created for this organization",
        )

    return integration


@router.get("/status")
async def telegram_status(
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as db:
        integration = await _get_telegram_integration(
            db, current_user.organization_id
        )
        token = _get_telegram_token(integration)

        try:
            bot_result = await _telegram_request(token, "getMe")
            webhook_result = await _telegram_request(token, "getWebhookInfo")
        except HTTPException as exc:
            return {
                "connected": False,
                "integration_id": integration.id,
                "organization_id": current_user.organization_id,
                "channel": "telegram",
                "error": exc.detail,
                "webhook": {"configured": False},
            }

    bot = bot_result["result"]
    webhook = webhook_result["result"]

    return {
        "connected": integration.is_active and bool(webhook.get("url")),
        "integration_id": integration.id,
        "organization_id": current_user.organization_id,
        "channel": "telegram",
        "bot": {
            "id": bot.get("id"),
            "username": bot.get("username"),
            "name": bot.get("first_name"),
        },
        "webhook": {
            "configured": bool(webhook.get("url")),
            "url": webhook.get("url"),
            "pending_updates": webhook.get("pending_update_count", 0),
            "last_error": webhook.get("last_error_message"),
        },
    }


@router.post("/connect")
async def connect_telegram(
    current_user: User = Depends(get_current_user),
):
    webhook_url = settings.TELEGRAM_WEBHOOK_URL

    if not webhook_url:
        raise HTTPException(
            status_code=503,
            detail="TELEGRAM_WEBHOOK_URL is not configured on the server",
        )

    if not webhook_url.startswith("https://"):
        raise HTTPException(
            status_code=400,
            detail="TELEGRAM_WEBHOOK_URL must use HTTPS",
        )

    async with AsyncSessionLocal() as db:
        integration = await _get_telegram_integration(
            db, current_user.organization_id
        )
        token = _get_telegram_token(integration)

        bot_result = await _telegram_request(token, "getMe")
        bot = bot_result["result"]

        webhook_secret = _get_or_create_webhook_secret(integration)

        result = await _telegram_request(
            token,
            "setWebhook",
            {
                "url": webhook_url,
                "secret_token": webhook_secret,
                "drop_pending_updates": False,
            },
        )

        integration.is_active = True
        await db.commit()

    return {
        "connected": True,
        "integration_id": integration.id,
        "organization_id": current_user.organization_id,
        "bot": {
            "id": bot.get("id"),
            "username": bot.get("username"),
            "name": bot.get("first_name"),
        },
        "webhook": {
            "url": webhook_url,
            "configured": True,
        },
        "message": result.get("description", "Telegram connected"),
    }


@router.post("/disconnect")
async def disconnect_telegram(
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as db:
        integration = await _get_telegram_integration(
            db, current_user.organization_id
        )
        token = _get_telegram_token(integration)

        result = await _telegram_request(
            token,
            "deleteWebhook",
            {"drop_pending_updates": False},
        )

        integration.is_active = False
        await db.commit()

    return {
        "connected": False,
        "integration_id": integration.id,
        "organization_id": current_user.organization_id,
        "message": result.get("description", "Telegram disconnected"),
    }