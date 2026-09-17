# twitter API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import httpx
from app.core.config import settings


class TwitterClient:

  @staticmethod
  async def send_twitter_reply(recipient_id: str, text: str) -> bool:
    bearer_token = getattr(settings, "TWITTER_BEARER_TOKEN", "")

    if not bearer_token:
      print("Twitter Bearer Token is not configured in settings.")
      return False

    url = f"https://api.twitter.com/2/dm_conversations/with/{recipient_id}/messages"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}

    async with httpx.AsyncClient() as client:
      try:
        res = await client.post(url, json=payload, headers=headers)
        return res.status_code in [200, 201]
      except Exception as e:
        print(f"Failed to send Twitter DM reply: {e}")
        return False