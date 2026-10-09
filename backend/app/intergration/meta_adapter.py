from datetime import datetime
import logging
from typing import Any
import uuid

import httpx

from app.core.config import settings
from app.intergration.base_adapter import ChannelAdapter

logger = logging.getLogger(__name__)


class MetaAdapter(ChannelAdapter):
    """Normalize Meta webhook events and send text replies through Graph API."""

    def __init__(self, channel_name: str):
        self.channel_name = channel_name

    @property
    def access_token(self) -> str:
        return getattr(settings, f"{self.channel_name.upper()}_ACCESS_TOKEN", "")

    @property
    def page_id(self) -> str:
        return getattr(settings, f"{self.channel_name.upper()}_PAGE_ID", "")

    async def send(self, to: str, content: str, **kwargs) -> dict:
        if self.channel_name == "whatsapp":
            object_id = kwargs.get("phone_number_id") or settings.WHATSAPP_PHONE_NUMBER_ID
            payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": content}}
            if settings.WHATSAPP_DRY_RUN:
                logger.warning("[WHATSAPP DRY RUN] to=%s: %s", to, content)
                return {"external_id": f"dry-run-{uuid.uuid4().hex[:12]}", "status": "sent", "error": None}
        else:
            object_id = kwargs.get("page_id") or self.page_id
            payload = {"recipient": {"id": to}, "message": {"text": content}}

        if not self.access_token or not object_id:
            return {"external_id": None, "status": "failed", "error": "Meta API credentials are not configured"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://graph.facebook.com/{settings.META_GRAPH_API_VERSION}/{object_id}/messages",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )
                data = response.json()
            if response.is_success:
                return {"external_id": data.get("messages", [{}])[0].get("id") or data.get("message_id"), "status": "sent", "error": None}
            return {"external_id": None, "status": "failed", "error": data.get("error", {}).get("message", str(data))}
        except Exception as exc:
            return {"external_id": None, "status": "failed", "error": str(exc)}

    def normalize_incoming(self, raw_payload: dict) -> dict:
        if self.channel_name == "whatsapp":
            return self._normalize_whatsapp(raw_payload)
        return self._normalize_messaging(raw_payload)

    def _normalize_whatsapp(self, payload: dict) -> dict:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    # Delivery/read receipts arrive as "statuses" with no messages
                    if value.get("statuses"):
                        return self._empty(payload, event="status")
                    continue
                message = messages[0]
                message_type = message.get("type")
                contacts = value.get("contacts", [])
                profile_name = contacts[0].get("profile", {}).get("name") if contacts else None
                return {
                    "external_id": str(message.get("id", "")),
                    "from": str(message.get("from", "")),
                    "sender_name": profile_name or str(message.get("from", "")),
                    "content": self._whatsapp_content(message) or f"[{message_type or 'unsupported'} message]",
                    "channel_metadata": {
                        "provider": "whatsapp",
                        "event": "message",
                        "type": message_type,
                        "phone_number_id": value.get("metadata", {}).get("phone_number_id"),
                        "raw": payload,
                    },
                    "timestamp": self._timestamp(message.get("timestamp")),
                }
        return self._empty(payload)

    @staticmethod
    def _whatsapp_content(message: dict) -> str:
        message_type = message.get("type")
        body = message.get(message_type, {}) if message_type else {}
        if message_type == "text":
            return body.get("body", "")
        if message_type == "interactive":
            reply = body.get("button_reply") or body.get("list_reply") or {}
            return reply.get("title", "")
        if message_type == "button":
            return body.get("text", "")
        if message_type in {"image", "video", "document"}:
            return body.get("caption", "")
        return ""

    def _normalize_messaging(self, payload: dict) -> dict:
        for entry in payload.get("entry", []):
            for event in entry.get("messaging", []):
                message = event.get("message", {})
                sender = event.get("sender", {})
                if not sender.get("id") or not message:
                    continue
                return {
                    "external_id": str(message.get("mid", "")),
                    "from": str(sender["id"]),
                    "content": message.get("text") or "[unsupported message]",
                    "channel_metadata": {"provider": self.channel_name, "raw": payload},
                    "timestamp": self._timestamp(event.get("timestamp")),
                }
        return self._empty(payload)

    @staticmethod
    def _timestamp(value: Any) -> str | None:
        if value is None:
            return None
        try:
            number = float(value)
            return datetime.utcfromtimestamp(number / 1000 if number > 10_000_000_000 else number).isoformat()
        except (TypeError, ValueError, OverflowError):
            return str(value)

    @staticmethod
    def _empty(payload: dict, event: str = "unsupported") -> dict:
        return {"external_id": "", "from": "", "content": "", "channel_metadata": {"event": event, "raw": payload}, "timestamp": None}