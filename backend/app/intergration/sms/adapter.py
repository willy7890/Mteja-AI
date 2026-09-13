import httpx
from typing import Optional, Any
from app.intergration.base_adapter import ChannelAdapter
from app.core.config import settings


class SmsAdapter(ChannelAdapter):
    

    channel_name = "sms"

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        from_number: Optional[str] = None,
    ):
        self.provider = provider or settings.SMS_PROVIDER or "africastalking"
        self.api_key = api_key or settings.SMS_API_KEY
        self.api_secret = api_secret or settings.SMS_API_SECRET
        self.from_number = from_number or settings.SMS_FROM

    
    async def send(self, to: str, content: str, **kwargs):
        to = self._clean_phone_number(to)

        try:
            if self.provider == "africastalking":
                return await self._send_africastalking(to, content)
            elif self.provider == "twilio":
                return await self._send_twilio(to, content)
            else:
                return {
                    "external_id": None,
                    "status": "failed",
                    "error": f"Unsupported SMS provider: {self.provider}",
                }
        except Exception as e:
            return {
                "external_id": None,
                "status": "failed",
                "error": str(e),
            }

    async def _send_africastalking(self, to: str, content: str) -> dict:
      
        url = "https://api.africastalking.com/version1/messaging"
        headers = {
            "ApiKey": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "username": self.api_secret or "sandbox",  # username ya Africa's Talking
            "to": to,
            "message": content,
            "from": self.from_number or "",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=data, headers=headers)
            result = response.json()

        
        recipients = result.get("SMSMessageData", {}).get("Recipients", [])
        if recipients and recipients[0].get("statusCode") in [100, 101, 102]:
            return {
                "external_id": recipients[0].get("messageId"),
                "status": "sent",
                "error": None,
            }
        else:
            error_msg = recipients[0].get("status") if recipients else str(result)
            return {
                "external_id": None,
                "status": "failed",
                "error": error_msg,
            }

    async def _send_twilio(self, to: str, content: str) -> dict:
       
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.api_key}/Messages.json"
        auth = (self.api_key, self.api_secret)
        data = {
            "From": self.from_number,
            "To": to,
            "Body": content,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=data, auth=auth)
            result = response.json()

        if response.status_code in (200, 201):
            return {
                "external_id": result.get("sid"),
                "status": "sent",
                "error": None,
            }
        else:
            return {
                "external_id": None,
                "status": "failed",
                "error": result.get("message") or str(result),
            }

    def normalize_incoming(self, raw_payload: dict) -> dict:
      
       
        if "from" in raw_payload and "text" in raw_payload:
            return {
                "external_id": raw_payload.get("id") or raw_payload.get("messageId") or "",
                "from": self._clean_phone_number(raw_payload.get("from", "")),
                "content": raw_payload.get("text") or raw_payload.get("message") or "",
                "channel_metadata": {
                    "to": raw_payload.get("to"),
                    "date": raw_payload.get("date"),
                    "provider": "africastalking",
                    "raw": raw_payload,
                },
                "timestamp": raw_payload.get("date"),
            }

        if "From" in raw_payload and "Body" in raw_payload:
            return {
                "external_id": raw_payload.get("MessageSid") or raw_payload.get("SmsSid") or "",
                "from": self._clean_phone_number(raw_payload.get("From", "")),
                "content": raw_payload.get("Body") or "",
                "channel_metadata": {
                    "to": raw_payload.get("To"),
                    "account_sid": raw_payload.get("AccountSid"),
                    "provider": "twilio",
                    "raw": raw_payload,
                },
                "timestamp": None,
            }

        
        return {
            "external_id": str(raw_payload.get("id") or raw_payload.get("message_id") or ""),
            "from": self._clean_phone_number(
                raw_payload.get("from") or raw_payload.get("From") or ""
            ),
            "content": (
                raw_payload.get("text")
                or raw_payload.get("Body")
                or raw_payload.get("message")
                or ""
            ),
            "channel_metadata": {
                "provider": "unknown",
                "raw": raw_payload,
            },
            "timestamp": None,
        }
        
    def _clean_phone_number(self, phone: str):
        
        if not phone:
            return ""
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "+255" + phone[1:] 
        if not phone.startswith("+"):
            phone = "+" + phone
        return phone