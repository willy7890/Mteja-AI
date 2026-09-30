import httpx
from app.core.config import settings


class WhatsAppClient:

  @staticmethod
  async def send_whatsapp_reply(phone: str, text: str) -> bool:
    phone_number_id = getattr(settings, "WA_PHONE_NUMBER_ID", "")
    access_token = getattr(settings, "WA_ACCESS_TOKEN", "")

    if not phone_number_id or not access_token:
      print("WhatsApp phone number ID or access token is not configured.")
      return False

    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient() as client:
      try:
        res = await client.post(url, json=payload, headers=headers)
        return res.status_code == 200
      except Exception as e:
        print(f"Failed to send WhatsApp reply: {e}")
        return False