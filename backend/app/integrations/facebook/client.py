# facebook API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import httpx
from app.core.config import settings


class FacebookClient:

  @staticmethod
  async def send_facebook_reply(recipient_id: str, text: str) -> bool:
    page_id = getattr(settings, "META_PAGE_ID", "")
    token = getattr(settings, "META_ACCESS_TOKEN", "")

    if not page_id or not token:
      print("Meta/Facebook page credentials are not configured in settings.")
      return False

    url = f"https://graph.facebook.com/v17.0/{page_id}/messages"
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
        print(f"Failed to send Facebook reply: {e}")
        return False