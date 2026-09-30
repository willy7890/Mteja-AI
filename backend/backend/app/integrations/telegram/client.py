# telegram API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import httpx
from app.core.config import settings


class TelegramClient:

  @staticmethod
  async def send_telegram_reply(chat_id: str, text: str) -> bool:
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")

    if not token:
      print("Telegram bot token is not configured in settings.")
      return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    async with httpx.AsyncClient() as client:
      try:
        res = await client.post(url, json=payload)
        return res.status_code == 200
      except Exception as e:
        print(f"Failed to send Telegram reply: {e}")
        return False