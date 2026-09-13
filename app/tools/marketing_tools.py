from __future__ import annotations
import aiosmtplib
import uuid
from email.message import EmailMessage
import logging
from typing import Any
from app.tools.base_tool import BaseTool


from typing import Any
 
import httpx
 
from app.core.config import settings 
 
logger = logging.getLogger(__name__)
 
GRAPH_API_BASE = "https://graph.facebook.com"

AT_SMS_URL = "https://api.africastalking.com/version1/messaging"
SMS_MAX_LEN = 459 
 
 

class GetCampaignIdeasTool(BaseTool):
    name = "get_campaign_ideas"
    description = "Generates marketing campaign ideas"

    async def run(self, **kwargs) -> Any:
        product = kwargs.get("product", "")
        audience = kwargs.get("audience", "")

        return {
            "ideas": [
                f"Facebook Ads campaign for {product}",
                f"Email campaign targeting {audience}",
                f"Content marketing about {product}"
            ]
        }


class CreateMarketingMessageTool(BaseTool):
    name = "create_marketing_message"
    description = "Creates a marketing message"

    async def run(self, **kwargs) -> Any:
        product = kwargs.get("product", "")
        tone = kwargs.get("tone", "professional")

        return {
            "message": f"A {tone} marketing message about {product} has been created."
        }


MARKETING_TOOLS = [
    GetCampaignIdeasTool(),
    CreateMarketingMessageTool(),
]

 
class WhatsAppSendError(Exception):
    """Raised when the WhatsApp Cloud API rejects or fails to send a message."""
 
 
def _normalize_phone(phone: str) -> str:
    """
    WhatsApp Cloud API expects E.164 without a leading '+' (e.g. '2557XXXXXXXX').
    Adjust this if your stored phone format is already Cloud-API-ready.
    """
    return phone.lstrip("+").replace(" ", "").replace("-", "")
 
 
def _build_template_components(variables: dict[str, Any] | None) -> list[dict]:
    """
    Converts a simple {"body": "..."} / {"1": "...", "2": "..."} style dict
    into the Cloud API's `components` structure for a body with positional
    variables. Adjust this mapping to match how your approved templates are
    actually parameterized (header/body/button variables, ordering, etc.).
    """
    if not variables:
        return []
 
    parameters = [
        {"type": "text", "text": str(value)}
        for value in variables.values()
    ]
    return [
        {
            "type": "body",
            "parameters": parameters,
        }
    ]
 
 
async def send_whatsapp_template(
    *,
    to: str,
    template_id: str,
    variables: dict[str, Any] | None = None,
    language_code: str = "en_US",
) -> dict:
    """
    Sends an approved WhatsApp template message.
 
    Args:
        to: recipient phone number (any reasonable format; normalized internally)
        template_id: the template's `name` as registered in WhatsApp Manager
                     (Cloud API identifies templates by name + language, not a numeric id —
                     if your BroadcastCampaign stores a different kind of id, adjust the
                     lookup that resolves it to a template name before calling this)
        variables: values to fill the template's body placeholders, in order
        language_code: template's approved language, e.g. "en_US", "sw"
 
    Returns:
        {"message_id": "<wamid...>"} on success.
 
    Raises:
        WhatsAppSendError on any non-2xx response or malformed payload.
    """
    url = f"{GRAPH_API_BASE}/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": _normalize_phone(to),
        "type": "template",
        "template": {
            "name": template_id,
            "language": {"code": language_code},
            "components": _build_template_components(variables),
        },
    }
 
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as exc:
            logger.exception("WhatsApp Cloud API request failed for %s", to)
            raise WhatsAppSendError(f"Network error calling WhatsApp API: {exc}") from exc
 
    if response.status_code >= 400:
        logger.error(
            "WhatsApp template send failed (status=%s) for %s: %s",
            response.status_code, to, response.text,
        )
        raise WhatsAppSendError(
            f"WhatsApp API returned {response.status_code}: {response.text}"
        )
 
    data = response.json()
    try:
        message_id = data["messages"][0]["id"]
    except (KeyError, IndexError, TypeError) as exc:
        raise WhatsAppSendError(f"Unexpected WhatsApp API response shape: {data}") from exc
 
    return {"message_id": message_id}
 
 
 
 
def _normalize_phone(phone: str) -> str:
    return phone.lstrip("+").replace(" ", "").replace("-", "")
 
 
async def send_whatsapp_freeform(*, to: str, body: str) -> dict:
    """
    Sends a free-form text WhatsApp message.
 
    Args:
        to: recipient phone number (normalized internally)
        body: plain text message content (Cloud API limit: 4096 chars)
 
    Returns:
        {"message_id": "<wamid...>"} on success.
 
    Raises:
        WhatsAppSendError on any non-2xx response, or if the API reports the
        session window is closed (error code 131047 / "re-engagement message").
    """
    if len(body) > 4096:
        raise WhatsAppSendError(f"Message body exceeds 4096 char limit ({len(body)} chars)")
 
    url = f"{GRAPH_API_BASE}/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": _normalize_phone(to),
        "type": "text",
        "text": {"body": body},
    }
 
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as exc:
            logger.exception("WhatsApp Cloud API request failed for %s", to)
            raise WhatsAppSendError(f"Network error calling WhatsApp API: {exc}") from exc
 
    if response.status_code >= 400:
        error_body = response.text
        logger.error(
            "WhatsApp freeform send failed (status=%s) for %s: %s",
            response.status_code, to, error_body,
        )
        # Error code 131047 = "Re-engagement message" — session window closed.
        # Surface this distinctly so callers can tell "should've used a template"
        # apart from a generic provider failure.
        if "131047" in error_body:
            raise WhatsAppSendError(
                "Session window closed — must use send_whatsapp_template instead"
            )
        raise WhatsAppSendError(
            f"WhatsApp API returned {response.status_code}: {error_body}"
        )
 
    data = response.json()
    try:
        message_id = data["messages"][0]["id"]
    except (KeyError, IndexError, TypeError) as exc:
        raise WhatsAppSendError(f"Unexpected WhatsApp API response shape: {data}") from exc
 
    return {"message_id": message_id}
 
 
 

 
class SmsSendError(Exception):
    """Raised when the SMS gateway rejects or fails to send a message."""
 
 
def _normalize_phone(phone: str) -> str:
    """
    Africa's Talking expects E.164 with a leading '+' (e.g. '+2557XXXXXXXX').
    Adjust if your stored phone format needs different handling
    (e.g. numbers stored without a country code).
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = f"+{phone}"
    return phone
 
 
async def send_sms(*, to: str, body: str) -> dict:
    """
    Sends a single SMS via Africa's Talking.
 
    Args:
        to: recipient phone number (normalized internally)
        body: message text
 
    Returns:
        {"message_id": "<messageId from AT>"} on success.
 
    Raises:
        SmsSendError if the body exceeds the length ceiling, the request
        fails, or Africa's Talking reports a non-Success status for the recipient.
    """
    if len(body) > SMS_MAX_LEN:
        raise SmsSendError(f"SMS body exceeds {SMS_MAX_LEN} char limit ({len(body)} chars)")
 
    headers = {
        "apiKey": settings.AT_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "username": settings.AT_USERNAME,
        "to": _normalize_phone(to),
        "message": body,
    }
    sender_id = getattr(settings, "AT_SENDER_ID", None)
    if sender_id:
        data["from"] = sender_id
 
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(AT_SMS_URL, data=data, headers=headers)
        except httpx.RequestError as exc:
            logger.exception("Africa's Talking request failed for %s", to)
            raise SmsSendError(f"Network error calling SMS gateway: {exc}") from exc
 
    if response.status_code >= 400:
        logger.error(
            "SMS send failed (status=%s) for %s: %s",
            response.status_code, to, response.text,
        )
        raise SmsSendError(f"SMS gateway returned {response.status_code}: {response.text}")
 
    payload = response.json()
    try:
        recipients = payload["SMSMessageData"]["Recipients"]
    except (KeyError, TypeError) as exc:
        raise SmsSendError(f"Unexpected SMS gateway response shape: {payload}") from exc
 
    if not recipients:
        raise SmsSendError(f"SMS gateway returned no recipients: {payload}")
 
    recipient_result = recipients[0]
    status_text = recipient_result.get("status", "")
    if status_text.lower() != "success":
        raise SmsSendError(
            f"SMS gateway rejected message for {to}: {status_text} "
            f"(cost={recipient_result.get('cost')}, statusCode={recipient_result.get('statusCode')})"
        )
 
    message_id = recipient_result.get("messageId")
    if not message_id:
        raise SmsSendError(f"SMS gateway returned success but no messageId: {payload}")
 
    return {"message_id": message_id}
 
 
 
class EmailSendError(Exception):
    """Raised when the SMTP send fails."""
 
 
async def send_email(*, to: str, subject: str, body: str, html_body: str | None = None) -> dict:
    """
    Sends an email via SMTP.
 
    Args:
        to: recipient email address
        subject: email subject line
        body: plain-text body (used as-is, or as the fallback part if html_body is given)
        html_body: optional HTML version of the body
 
    Returns:
        {"message_id": "<generated Message-ID>"} on success.
        Note: unlike WhatsApp/SMS gateways, SMTP does not hand back a
        provider-assigned id synchronously — the Message-ID header set
        here is generated client-side so BroadcastRecipient still has
        something to store. If you move to a provider HTTP API later,
        swap this for the id it actually returns.
 
    Raises:
        EmailSendError if the SMTP handshake or send fails.
    """
    message_id = f"<{uuid.uuid4()}@{settings.SMTP_FROM_EMAIL.split('@')[-1]}>"
 
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg["Message-ID"] = message_id
    msg.set_content(body)
 
    if html_body:
        msg.add_alternative(html_body, subtype="html")
 
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=getattr(settings, "SMTP_USE_TLS", True),
        )
    except aiosmtplib.SMTPException as exc:
        logger.exception("SMTP send failed for %s", to)
        raise EmailSendError(f"SMTP error sending to {to}: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 — connection/timeout errors, etc.
        logger.exception("Unexpected error sending email to %s", to)
        raise EmailSendError(f"Failed to send email to {to}: {exc}") from exc
 
    return {"message_id": message_id}
 