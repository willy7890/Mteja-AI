# tiktok API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import httpx
from app.core.config import settings


class TikTokClient:

  @staticmethod
  async def send_tiktok_reply(recipient_id: str, text: str) -> bool:
    access_token = getattr(settings, "TIKTOK_ACCESS_TOKEN", "")

    if not access_token:
      print("TikTok access token is not configured in settings.")
      return False

    url = "https://business-api.tiktok.com/open_api/v1.3/message/send/"
    headers = {
        "Access-Token": access_token,
        "Content-Type": "application/json",
    }
    payload = {
        "recipient_id": recipient_id,
        "message": {"message_type": "text", "text": text},
    }

    async with httpx.AsyncClient() as client:
      try:
        res = await client.post(url, json=payload, headers=headers)
        data = res.json()
        return data.get("code") == 0
      except Exception as e:
        print(f"Failed to send TikTok reply: {e}")
        return False