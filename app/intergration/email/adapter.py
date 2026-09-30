import httpx
from datetime import datetime
from typing import Optional, Any
from email.utils import parseaddr
from app.intergration.base_adapter import ChannelAdapter
from app.core.config import settings


class EmailAdapter(ChannelAdapter):
  

    channel_name = "email"

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
       
        self.api_key = api_key or getattr(settings, "EMAIL_API_KEY", None)
        self.from_email = from_email or getattr(settings, "EMAIL_FROM", "noreply@example.com")
        self.from_name = from_name or getattr(settings, "EMAIL_FROM_NAME", "Mteja AI")
        self.provider = getattr(settings, "EMAIL_PROVIDER", "resend")  # resend | sendgrid | mailgun

   
    async def send(self, to: str, content: str, **kwargs) -> dict:
       
        subject = kwargs.get("subject", "Message from Mteja AI")
        html_content = kwargs.get("html", None)
        reply_to = kwargs.get("reply_to", None)

        try:
            if self.provider == "resend":
                return await self._send_with_resend(to, subject, content, html_content, reply_to)
            elif self.provider == "sendgrid":
                return await self._send_with_sendgrid(to, subject, content, html_content, reply_to)
            else:
                return {
                    "external_id": None,
                    "status": "failed",
                    "error": f"Unsupported email provider: {self.provider}",
                }
        except Exception as e:
            return {
                "external_id": None,
                "status": "failed",
                "error": str(e),
            }

    async def _send_with_resend(
        self, to: str, subject: str, text: str, html: Optional[str], reply_to: Optional[str]
    ):
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [to],
            "subject": subject,
            "text": text,
        }
        if html:
            payload["html"] = html
        if reply_to:
            payload["reply_to"] = reply_to

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()

        if response.status_code in (200, 201):
            return {
                "external_id": data.get("id"),
                "status": "sent",
                "error": None,
            }
        else:
            return {
                "external_id": None,
                "status": "failed",
                "error": data.get("message") or str(data),
            }

    async def _send_with_sendgrid(
        self, to: str, subject: str, text: str, html: Optional[str], reply_to: Optional[str]
    ):
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        content = []
        if text:
            content.append({"type": "text/plain", "value": text})
        if html:
            content.append({"type": "text/html", "value": html})

        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": self.from_email, "name": self.from_name},
            "subject": subject,
            "content": content,
        }
        if reply_to:
            payload["reply_to"] = {"email": reply_to}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code in (200, 202):
            # SendGrid returns message id in headers sometimes
            external_id = response.headers.get("X-Message-Id")
            return {
                "external_id": external_id,
                "status": "sent",
                "error": None,
            }
        else:
            return {
                "external_id": None,
                "status": "failed",
                "error": response.text,
            }

    
    def normalize_incoming(self, raw_payload: dict):
       
        
        if "data" in raw_payload and "from" in raw_payload.get("data", {}):
            data = raw_payload["data"]
            from_email = data.get("from")
            if isinstance(from_email, str):
                from_email = parseaddr(from_email)[1]

            return {
                "external_id": data.get("email_id") or data.get("id") or str(raw_payload.get("id", "")),
                "from": from_email or "",
                "content": data.get("text") or data.get("html") or data.get("body") or "",
                "channel_metadata": {
                    "subject": data.get("subject"),
                    "to": data.get("to"),
                    "cc": data.get("cc"),
                    "reply_to": data.get("reply_to"),
                    "provider": "resend",
                    "raw": data,
                },
                "timestamp": data.get("created_at"),
            }

        
        if "from" in raw_payload and ("text" in raw_payload or "html" in raw_payload):
            from_email = parseaddr(raw_payload.get("from", ""))[1]

            return {
                "external_id": raw_payload.get("headers", {}).get("Message-ID") or raw_payload.get("message_id"),
                "from": from_email,
                "content": raw_payload.get("text") or raw_payload.get("html") or "",
                "channel_metadata": {
                    "subject": raw_payload.get("subject"),
                    "to": raw_payload.get("to"),
                    "cc": raw_payload.get("cc"),
                    "provider": "sendgrid",
                    "raw": raw_payload,
                },
                "timestamp": None,
            }

       
        from_email = raw_payload.get("from") or raw_payload.get("sender") or ""
        if isinstance(from_email, str):
            from_email = parseaddr(from_email)[1]

        return {
            "external_id": str(raw_payload.get("id") or raw_payload.get("message_id") or ""),
            "from": from_email,
            "content": raw_payload.get("text") or raw_payload.get("body") or raw_payload.get("html") or "",
            "channel_metadata": {
                "subject": raw_payload.get("subject"),
                "provider": "unknown",
                "raw": raw_payload,
            },
            "timestamp": raw_payload.get("timestamp") or raw_payload.get("date"),
        }