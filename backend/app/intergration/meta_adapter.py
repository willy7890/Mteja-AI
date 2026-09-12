from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings
from app.intergration.base_adapter import ChannelAdapter


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
        else:
            object_id = kwargs.get("page_id") or self.page_id
            payload = {"recipient": {"id": to}, "message": {"text": content}}

        if not self.access_token or not object_id:
            return {"external_id": None, "status": "failed", "error": "Meta API credentials are not configured"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://graph.facebook.com/v20.0/{object_id}/messages",
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
                    continue
                message = messages[0]
                message_type = message.get("type")
                content = message.get(message_type, {}).get("body", "") if message_type else ""
                return {
                    "external_id": str(message.get("id", "")),
                    "from": str(message.get("from", "")),
                    "content": content or f"[{message_type or 'unsupported'} message]",
                    "channel_metadata": {"provider": "whatsapp", "type": message_type, "raw": payload},
                    "timestamp": self._timestamp(message.get("timestamp")),
                }
        return self._empty(payload)

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
    def _empty(payload: dict) -> dict:
        return {"external_id": "", "from": "", "content": "", "channel_metadata": {"raw": payload}, "timestamp": None}