"""
Channel compliance rules.

This is the piece that keeps a broadcast from turning into a provider
violation or spam complaint. Each channel has different constraints on
*when* and *how* you're allowed to message someone outbound; this module
is the single place that encodes them, so the send path can't accidentally
skip a check.

Extend as your providers' policies evolve — these are deliberately
conservative defaults, not the full Meta/carrier spec.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from app.models.broadcast import ChannelType

SMS_MAX_SEGMENT_CHARS = 160  # GSM-7 single-segment limit
SMS_MAX_CONCAT_SEGMENTS = 3  # refuse to send messages that would split into more than this
WHATSAPP_SESSION_WINDOW_HOURS = 24  # Meta's customer-service window for free-form messages


@dataclass
class RuleViolation:
    reason: str


class ChannelRuleResult:
    def __init__(self, allowed: bool, requires_template: bool = False, violation: Optional[str] = None):
        self.allowed = allowed
        self.requires_template = requires_template
        self.violation = violation


def check_whatsapp(
    *,
    has_template: bool,
    free_form_content: Optional[str],
    last_customer_message_at: Optional[datetime],
) -> ChannelRuleResult:
    """
    WhatsApp Business rule: outside a 24h customer-service session window,
    only pre-approved template messages may be sent. Free-form marketing
    text sent outside the window is a provider policy violation and risks
    the business's WhatsApp access.
    """
    session_open = (
        last_customer_message_at is not None
        and datetime.utcnow() - last_customer_message_at <= timedelta(hours=WHATSAPP_SESSION_WINDOW_HOURS)
    )

    if session_open:
        # Either path is fine inside an open session.
        if has_template or free_form_content:
            return ChannelRuleResult(allowed=True, requires_template=False)
        return ChannelRuleResult(allowed=False, violation="No content or template provided")

    # Outside the session window: template is mandatory.
    if has_template:
        return ChannelRuleResult(allowed=True, requires_template=True)

    return ChannelRuleResult(
        allowed=False,
        requires_template=True,
        violation="Outside 24h session window: WhatsApp requires an approved template",
    )


def check_sms(*, content: Optional[str]) -> ChannelRuleResult:
    if not content:
        return ChannelRuleResult(allowed=False, violation="No content provided for SMS")

    segments = -(-len(content) // SMS_MAX_SEGMENT_CHARS)  # ceil division
    if segments > SMS_MAX_CONCAT_SEGMENTS:
        return ChannelRuleResult(
            allowed=False,
            violation=(
                f"Content requires {segments} SMS segments, exceeds limit of "
                f"{SMS_MAX_CONCAT_SEGMENTS}"
            ),
        )

    # Placeholder: plug in a real STOP/opt-out keyword and sender-ID check here.
    return ChannelRuleResult(allowed=True)


def check_email(*, content: Optional[str], has_template: bool) -> ChannelRuleResult:
    if not content and not has_template:
        return ChannelRuleResult(allowed=False, violation="No content or template provided for email")
    return ChannelRuleResult(allowed=True)


def enforce_channel_rules(
    channel: ChannelType,
    *,
    has_template: bool,
    free_form_content: Optional[str],
    last_customer_message_at: Optional[datetime] = None,
) -> ChannelRuleResult:
    if channel == ChannelType.whatsapp:
        return check_whatsapp(
            has_template=has_template,
            free_form_content=free_form_content,
            last_customer_message_at=last_customer_message_at,
        )
    if channel == ChannelType.sms:
        return check_sms(content=free_form_content)
    if channel == ChannelType.email:
        return check_email(content=free_form_content, has_template=has_template)

    return ChannelRuleResult(allowed=False, violation=f"Unsupported channel: {channel}")