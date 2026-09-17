# telegram API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import httpx
from datetime import datetime
from typing import Any, Optional
from app.intergration.base_adapter import ChannelAdapter  # badilisha path kama ni tofauti
from app.core.config import settings  # assume una settings


class TelegramAdapter(ChannelAdapter):
    

    channel_name = "telegram"

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send(self, to: str, content: str, **kwargs) -> dict:
       
        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": to,
            "text": content,
            "parse_mode": kwargs.get("parse_mode", "HTML"),
        }

        
        if "reply_to_message_id" in kwargs:
            payload["reply_to_message_id"] = kwargs["reply_to_message_id"]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                data = response.json()

            if data.get("ok"):
                result = data["result"]
                return {
                    "external_id": str(result["message_id"]),
                    "status": "sent",
                    "error": None,
                }
            else:
                return {
                    "external_id": None,
                    "status": "failed",
                    "error": data.get("description", "Unknown Telegram error"),
                }

        except Exception as e:
            return {
                "external_id": None,
                "status": "failed",
                "error": str(e),
            }

   
    def normalize_incoming(self, raw_payload: dict) -> dict:
       
        message = raw_payload.get("message") or raw_payload.get("edited_message")

        if not message:
            
            return {
                "external_id": str(raw_payload.get("update_id", "")),
                "from": "",
                "content": "",
                "channel_metadata": {"raw": raw_payload},
                "timestamp": None,
            }

        chat = message.get("chat", {})
        from_user = message.get("from", {})
        text = message.get("text") or message.get("caption") or ""

        
        chat_id = str(chat.get("id", ""))

        
        channel_metadata = {
            "telegram_message_id": message.get("message_id"),
            "chat_type": chat.get("type"),               # private | group | supergroup
            "from_user_id": from_user.get("id"),
            "from_username": from_user.get("username"),
            "from_first_name": from_user.get("first_name"),
            "from_last_name": from_user.get("last_name"),
            "is_bot": from_user.get("is_bot", False),
            "date": message.get("date"),
            "reply_to_message_id": (
                message.get("reply_to_message", {}).get("message_id")
                if message.get("reply_to_message") else None
            ),
            "has_media": bool(
                message.get("photo")
                or message.get("document")
                or message.get("video")
                or message.get("audio")
                or message.get("voice")
            ),
        }

        
        timestamp = None
        if message.get("date"):
            try:
                timestamp = datetime.utcfromtimestamp(message["date"]).isoformat()
            except Exception:
                timestamp = None

        return {
            "external_id": str(message.get("message_id", "")),
            "from": chat_id,                    # hii ndiyo external_participant_id
            "content": text,
            "channel_metadata": channel_metadata,
            "timestamp": timestamp,
        }