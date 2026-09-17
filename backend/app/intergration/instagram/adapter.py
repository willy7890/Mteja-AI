# instagram API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import httpx
from app.core.config import settings


class InstagramClient:

  @staticmethod
  async def send_instagram_reply(recipient_id: str, text: str) -> bool:
    ig_page_id = getattr(
        settings, "INSTAGRAM_PAGE_ID", getattr(settings, "META_PAGE_ID", "")
    )
    token = getattr(settings, "META_ACCESS_TOKEN", "")

    if not ig_page_id or not token:
      print("Instagram/Meta credentials are not configured in settings.")
      return False

    url = f"https://graph.facebook.com/v17.0/{ig_page_id}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "access_token": token,
    }

    async with httpx.AsyncClient() as client:
      try:
        res = await client.post(url, json=payload)
        return res.status_code == 200
      except Exception as e:
        print(f"Failed to send Instagram reply: {e}")
        return False