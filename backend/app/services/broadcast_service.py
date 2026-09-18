"""
Broadcast core logic: create campaign -> resolve audience -> split by
channel -> check consent/rules -> queue -> track status -> aggregate.

Async throughout (AsyncSession) to match the rest of the app.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broadcast import BroadcastCampaign, BroadcastRecipient, CampaignStatus, RecipientStatus, ChannelType
from app.models.customer import Customer
from app.services.audit_service import record_activity
from app.services.channel_rules import enforce_channel_rules
from app.services.message_queue import enqueue_outbound_message


class BroadcastError(Exception):
    pass


async def create_campaign(db: AsyncSession, *, organization_id: int, created_by: int, payload) -> BroadcastCampaign:
    campaign = BroadcastCampaign(
        organization_id=organization_id,
        name=payload.name,
        description=payload.description,
        channels=[c.value for c in payload.channels],
        audience_filter=payload.audience_filter,
        template_id=payload.template_id,
        template_params=payload.template_params,
        free_form_content=payload.free_form_content,
        media_url=payload.media_url,
        status=CampaignStatus.draft,
        created_by=created_by,
    )
    db.add(campaign)
    await record_activity(db, organization_id=organization_id, user_id=created_by, actor="admin",
                           action_type="campaign_created", description=f"Broadcast '{campaign.name}' created")
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def get_campaign(db: AsyncSession, campaign_id: int, organization_id: int) -> BroadcastCampaign | None:
    # always scoped to organization_id - never trust campaign_id alone
    result = await db.execute(
        select(BroadcastCampaign).where(
            BroadcastCampaign.id == campaign_id,
            BroadcastCampaign.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()


async def list_campaigns(db: AsyncSession, organization_id: int) -> list[BroadcastCampaign]:
    result = await db.execute(
        select(BroadcastCampaign)
        .where(BroadcastCampaign.organization_id == organization_id)
        .order_by(BroadcastCampaign.created_at.desc())
    )
    return list(result.scalars().all())


async def resolve_audience(db: AsyncSession, *, organization_id: int, audience_filter: dict) -> list[Customer]:
    """
    Turn the audience filter into a real customer list.
    CRITICAL: always scoped to organization_id - this is what stops a
    broadcast from reaching another org's customers.

    NOTE: Customer currently has no `tags` and no opt-in/consent field,
    so those filters aren't supported yet - every customer in the org
    is considered part of the audience. Add a consent column when ready;
    _has_channel_consent() below is the only place that needs to change.
    """
    result = await db.execute(select(Customer).where(Customer.organization_id == organization_id))
    return list(result.scalars().all())


def _select_destination(customer: Customer, channel: ChannelType) -> str | None:
    if channel in (ChannelType.whatsapp, ChannelType.sms):
        return customer.phone
    if channel == ChannelType.email:
        return customer.email
    return None


def _has_channel_consent(customer: Customer, channel: ChannelType) -> bool:
    # placeholder - no consent field on Customer yet, so everyone passes.
    # once a consent column/table exists, replace this with a real check.
    return True


async def build_recipients(db: AsyncSession, campaign: BroadcastCampaign, customers: list[Customer]) -> list[BroadcastRecipient]:
    """
    For each customer: pick the first channel (in campaign order) they
    have both a destination and consent for, run the compliance check,
    and record the outcome. Skips are recorded, not dropped, so metrics
    stay honest.
    """
    channels = [ChannelType(c) for c in campaign.channels]
    recipients = []

    for customer in customers:
        chosen_channel, destination = None, None
        skip_status = RecipientStatus.skipped_unavailable

        for channel in channels:
            dest = _select_destination(customer, channel)
            if not dest:
                continue
            if not _has_channel_consent(customer, channel):
                skip_status = RecipientStatus.skipped_no_consent
                continue
            chosen_channel, destination = channel, dest
            break

        if not chosen_channel:
            recipients.append(BroadcastRecipient(
                campaign_id=campaign.id, organization_id=campaign.organization_id,
                customer_id=customer.id, channel=channels[0], destination="", status=skip_status,
            ))
            continue

        rule = enforce_channel_rules(
            chosen_channel,
            has_template=bool(campaign.template_id),
            free_form_content=campaign.free_form_content,
            last_customer_message_at=None,  # no such field on Customer yet
        )

        recipient = BroadcastRecipient(
            campaign_id=campaign.id, organization_id=campaign.organization_id,
            customer_id=customer.id, channel=chosen_channel, destination=destination,
        )

        if not rule.allowed:
            recipient.status = RecipientStatus.skipped_rule_violation
            recipient.error_reason = rule.violation
        else:
            recipient.status = RecipientStatus.pending
            recipient.used_template = campaign.template_id if rule.requires_template else None
            recipient.rendered_content = None if rule.requires_template else campaign.free_form_content
            recipient.media_url = campaign.media_url

        recipients.append(recipient)

    db.add_all(recipients)
    await db.commit()
    return recipients


async def dispatch_campaign(db: AsyncSession, campaign: BroadcastCampaign, *, approved_by: int) -> BroadcastCampaign:
    """Queue every pending recipient, then finalize the campaign status."""
    campaign.status = CampaignStatus.sending
    campaign.approved_by = approved_by
    campaign.started_at = datetime.utcnow()
    await record_activity(db, organization_id=campaign.organization_id, user_id=approved_by, actor="admin",
                           action_type="campaign_send_started", description=f"Broadcast '{campaign.name}' send started")
    await db.commit()

    result = await db.execute(
        select(BroadcastRecipient).where(
            BroadcastRecipient.campaign_id == campaign.id,
            BroadcastRecipient.status == RecipientStatus.pending,
        )
    )
    pending = list(result.scalars().all())

    for recipient in pending:
        try:
            provider_message_id = enqueue_outbound_message(
                channel=recipient.channel, destination=recipient.destination,
                template_id=recipient.used_template, template_params=campaign.template_params,
                content=recipient.rendered_content, media_url=recipient.media_url,
            )
            recipient.status = RecipientStatus.queued
            recipient.provider_message_id = provider_message_id
            recipient.queued_at = datetime.utcnow()
        except Exception as exc:  # one bad recipient shouldn't stop the batch
            recipient.status = RecipientStatus.failed
            recipient.error_reason = str(exc)
            recipient.failed_at = datetime.utcnow()

    await db.commit()
    await _finalize_campaign_status(db, campaign)
    return campaign


async def _finalize_campaign_status(db: AsyncSession, campaign: BroadcastCampaign) -> None:
    """Mark the campaign completed once no recipient is still pending/queued."""
    result = await db.execute(select(BroadcastRecipient.status).where(BroadcastRecipient.campaign_id == campaign.id))
    statuses = {row[0] for row in result.all()}
    if statuses & {RecipientStatus.pending, RecipientStatus.queued}:
        return

    campaign.status = CampaignStatus.completed
    campaign.completed_at = datetime.utcnow()
    await record_activity(db, organization_id=campaign.organization_id, user_id=campaign.approved_by, actor="system",
                           action_type="campaign_completed", description=f"Broadcast '{campaign.name}' completed")
    await db.commit()


async def update_recipient_status(db: AsyncSession, recipient: BroadcastRecipient, *,
                                   status: RecipientStatus, error_reason: str | None = None) -> None:
    """Call this from provider delivery-receipt webhooks."""
    recipient.status = status
    recipient.error_reason = error_reason
    now = datetime.utcnow()
    if status == RecipientStatus.sent:
        recipient.sent_at = now
    elif status == RecipientStatus.delivered:
        recipient.delivered_at = now
    elif status == RecipientStatus.failed:
        recipient.failed_at = now
    await db.commit()

    campaign = await db.get(BroadcastCampaign, recipient.campaign_id)
    await _finalize_campaign_status(db, campaign)


async def get_recipients(db: AsyncSession, campaign_id: int, organization_id: int) -> list[BroadcastRecipient]:
    result = await db.execute(
        select(BroadcastRecipient).where(
            BroadcastRecipient.campaign_id == campaign_id,
            BroadcastRecipient.organization_id == organization_id,
        )
    )
    return list(result.scalars().all())


async def aggregate_metrics(db: AsyncSession, campaign_id: int) -> dict:
    result = await db.execute(select(BroadcastRecipient.status).where(BroadcastRecipient.campaign_id == campaign_id))
    counts = {s.value: 0 for s in RecipientStatus}
    total = 0
    for row in result.all():
        counts[row[0].value] += 1
        total += 1
    counts["total_recipients"] = total
    return counts