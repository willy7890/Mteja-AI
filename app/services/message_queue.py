"""
Sends outbound messages. No real provider wired up yet (no Twilio).
Swap the _send_* functions below with real API calls later —
nothing else in the app needs to change.
"""

import logging
import uuid
from typing import Optional, Dict, Any

from app.models.broadcast import ChannelType

logger = logging.getLogger(__name__)


class MessageDispatchError(Exception):
    pass


def _fake_provider_id() -> str:
    # stand-in for a real provider message id (Twilio SID etc.)
    return f"local-{uuid.uuid4().hex[:12]}"


def _send_whatsapp(*, destination: str, template_id: Optional[str],
                    template_params: Optional[Dict[str, Any]],
                    content: Optional[str], media_url: Optional[str]) -> str:
    # TODO: call real WhatsApp Business API here.
    # media_url = image to send as a WhatsApp media message.
    logger.info("WHATSAPP -> %s | template=%s content=%r media=%s",
                destination, template_id, content, media_url)
    return _fake_provider_id()


def _send_sms(*, destination: str, content: Optional[str]) -> str:
    # TODO: call real SMS API here. SMS can't carry images — text only.
    logger.info("SMS -> %s | content=%r", destination, content)
    return _fake_provider_id()


def _send_email(*, destination: str, template_id: Optional[str],
                 template_params: Optional[Dict[str, Any]],
                 content: Optional[str], media_url: Optional[str]) -> str:
    # TODO: call real email API here. media_url = image attached/embedded.
    logger.info("EMAIL -> %s | template=%s content=%r media=%s",
                destination, template_id, content, media_url)
    return _fake_provider_id()


def enqueue_outbound_message(
    *,
    channel: ChannelType,
    destination: str,
    template_id: Optional[str] = None,
    template_params: Optional[Dict[str, Any]] = None,
    content: Optional[str] = None,
    media_url: Optional[str] = None,
) -> str:
    """Send one message. Returns provider message id, raises on failure."""
    try:
        if channel == ChannelType.whatsapp:
            return _send_whatsapp(
                destination=destination, template_id=template_id,
                template_params=template_params, content=content, media_url=media_url,
            )
        if channel == ChannelType.sms:
            return _send_sms(destination=destination, content=content)
        if channel == ChannelType.email:
            return _send_email(
                destination=destination, template_id=template_id,
                template_params=template_params, content=content, media_url=media_url,
            )
    except Exception as exc:  # noqa: BLE001 - normalize any provider error
        raise MessageDispatchError(str(exc)) from exc

    raise MessageDispatchError(f"Unsupported channel: {channel}")