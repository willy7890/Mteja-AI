"""
backend/app/services/outbound.py

Bridges BroadcastService to the project's existing, approved outbound
tools (tools/marketing_tools.py) so broadcast sends go through the SAME
tool layer as agent-initiated sends — same approval list, same logging,
same provider clients. Broadcasts should never call WhatsApp/SMS/email
providers directly.

I don't have the exact function signatures in tools/marketing_tools.py,
so the calls below are named by convention (send_whatsapp_template,
send_whatsapp_freeform, send_sms, send_email). Rename/adjust the imports
to match what actually exists there — tell me the real signatures and
I'll wire this precisely.
"""

from __future__ import annotations

import logging

from app.models.broadcast import ChannelType
from app.services.broadcast import QueueClient, CustomerRecord

# Adjust these imports to the real function names in tools/marketing_tools.py
from app.tools.marketing_tools import (
    send_whatsapp_template,
    send_whatsapp_freeform,
    send_sms,
    send_email,
)

logger = logging.getLogger(__name__)


class ToolOutboundError(Exception):
    """Raised when the underlying tool call fails or returns no message id."""


class ToolQueueClient(QueueClient):
    """
    Implements the QueueClient protocol expected by BroadcastService.
    Each method call is per-recipient — BroadcastService handles looping,
    consent checks, and compliance checks before this is ever invoked, so
    this class assumes the send is already validated and just needs to
    happen.
    """

    async def queue(
        self,
        *,
        channel: ChannelType,
        customer: CustomerRecord,
        message_body: str,
        template_id: str | None,
        use_template: bool,
    ) -> str:
        if channel == ChannelType.WHATSAPP:
            return await self._send_whatsapp(customer, message_body, template_id, use_template)
        if channel == ChannelType.SMS:
            return await self._send_sms(customer, message_body)
        if channel == ChannelType.EMAIL:
            return await self._send_email(customer, message_body)

        raise ToolOutboundError(f"Unsupported channel: {channel}")

    async def _send_whatsapp(
        self, customer: CustomerRecord, message_body: str, template_id: str | None, use_template: bool
    ) -> str:
        if not customer.phone:
            raise ToolOutboundError(f"Customer {customer.id} has no phone on file")

        try:
            if use_template:
                if not template_id:
                    raise ToolOutboundError("Template required but none provided")
                result = await send_whatsapp_template(
                    to=customer.phone,
                    template_id=template_id,
                    # Pass campaign message_body as a variable payload if your
                    # template supports one merge field; adjust to your template schema.
                    variables={"body": message_body},
                )
            else:
                result = await send_whatsapp_freeform(to=customer.phone, body=message_body)
        except Exception as exc:  # noqa: BLE001
            logger.exception("WhatsApp send failed for customer %s", customer.id)
            raise ToolOutboundError(str(exc)) from exc

        message_id = self._extract_message_id(result)
        if not message_id:
            raise ToolOutboundError("WhatsApp tool returned no message id")
        return message_id

    async def _send_sms(self, customer: CustomerRecord, message_body: str) -> str:
        if not customer.phone:
            raise ToolOutboundError(f"Customer {customer.id} has no phone on file")

        try:
            result = await send_sms(to=customer.phone, body=message_body)
        except Exception as exc:  # noqa: BLE001
            logger.exception("SMS send failed for customer %s", customer.id)
            raise ToolOutboundError(str(exc)) from exc

        message_id = self._extract_message_id(result)
        if not message_id:
            raise ToolOutboundError("SMS tool returned no message id")
        return message_id

    async def _send_email(self, customer: CustomerRecord, message_body: str) -> str:
        if not customer.email:
            raise ToolOutboundError(f"Customer {customer.id} has no email on file")

        try:
            result = await send_email(
                to=customer.email,
                subject="Update",  # consider adding a subject field to BroadcastCampaign
                body=message_body,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Email send failed for customer %s", customer.id)
            raise ToolOutboundError(str(exc)) from exc

        message_id = self._extract_message_id(result)
        if not message_id:
            raise ToolOutboundError("Email tool returned no message id")
        return message_id

    @staticmethod
    def _extract_message_id(result) -> str | None:
        """
        Normalizes whatever tools/marketing_tools.py returns (dict, dataclass,
        or plain string id) into a plain string message id.
        """
        if isinstance(result, str):
            return result
        if isinstance(result, dict):
            return result.get("message_id") or result.get("id")
        return getattr(result, "message_id", None) or getattr(result, "id", None)