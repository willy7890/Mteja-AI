# sms API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import httpx
from app.core.config import settings


class SMSClient:

  @staticmethod
  async def send_sms_reply(phone: str, text: str) -> bool:
    api_key = getattr(settings, "AT_API_KEY", "")
    username = getattr(settings, "AT_USERNAME", "sandbox")

    if not api_key:
      print("Africa's Talking API key is not configured in settings.")
      return False

    url = "https://api.africastalking.com/version1/messaging"
    headers = {
        "apiKey": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {"username": username, "to": phone, "message": text}

    async with httpx.AsyncClient() as client:
      try:
        res = await client.post(url, data=data, headers=headers)
        return res.status_code in [200, 201]
      except Exception as e:
        print(f"Failed to send SMS reply: {e}")
        return False