from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broadcast import (
    BroadcastCampaign,
    BroadcastRecipient,
    ChannelType,
    BroadcastStatus,
    RecipientStatus,
)
from app.models.activity_log import ActivityLog
from app.schemas.broadcast import BroadcastCreateRequest

logger = logging.getLogger(__name__)


class BroadcastError(Exception):
    pass


class CrossTenantAudienceError(BroadcastError):
    pass


class RateLimitedError(BroadcastError):
    pass


class CampaignNotFoundError(BroadcastError):
    pass


class CampaignNotSendableError(BroadcastError):
    pass


class CampaignNotScheduleableError(BroadcastError):
    pass


@dataclass
class CustomerRecord:
    id: int
    organization_id: int
    whatsapp_opt_in: bool
    sms_opt_in: bool
    email_opt_in: bool
    has_open_whatsapp_session: bool
    phone: str | None
    email: str | None


class AudienceResolver(Protocol):
    async def resolve(self, organization_id: int, audience_filter: dict) -> list[CustomerRecord]:
        ...


class QueueClient(Protocol):
    async def queue(
        self,
        *,
        channel: ChannelType,
        customer: CustomerRecord,
        message_body: str,
        template_id: str | None,
        use_template: bool,
    ) -> str:
        ...


SMS_MAX_LEN = 459


def _consent_field(channel: ChannelType, customer: CustomerRecord) -> bool:
    return {
        ChannelType.WHATSAPP: customer.whatsapp_opt_in,
        ChannelType.SMS: customer.sms_opt_in,
        ChannelType.EMAIL: customer.email_opt_in,
    }[channel]


def _channel_contactable(channel: ChannelType, customer: CustomerRecord) -> bool:
    if channel in (ChannelType.WHATSAPP, ChannelType.SMS):
        return bool(customer.phone)
    if channel == ChannelType.EMAIL:
        return bool(customer.email)
    return False


def check_channel_compliance(
    channel: ChannelType,
    message_body: str,
    whatsapp_template_id: str | None,
    customer: CustomerRecord,
) -> tuple[bool, str | None, bool]:
    if channel == ChannelType.WHATSAPP:
        if not customer.has_open_whatsapp_session:
            if not whatsapp_template_id:
                return False, "whatsapp_template_required_outside_session_window", True
            return True, None, True
        return True, None, False

    if channel == ChannelType.SMS:
        if len(message_body) > SMS_MAX_LEN:
            return False, f"sms_body_exceeds_{SMS_MAX_LEN}_chars", False
        return True, None, False

    if channel == ChannelType.EMAIL:
        return True, None, False

    return False, "unsupported_channel", False


class BroadcastService:
    def __init__(self, db: AsyncSession, audience_resolver: AudienceResolver, queue_client: QueueClient):
        self.db = db
        self.audience_resolver = audience_resolver
        self.queue_client = queue_client

    async def create_campaign(
        self,
        *,
        organization_id: int,
        created_by: int,
        payload: BroadcastCreateRequest,
    ) -> BroadcastCampaign:
        campaign = BroadcastCampaign(
            organization_id=organization_id,
            name=payload.name,
            message_body=payload.message_body,
            channels=[c.value for c in payload.channels],
            whatsapp_template_id=payload.whatsapp_template_id,
            audience_filter=payload.audience.model_dump(exclude_none=True),
            status=BroadcastStatus.SCHEDULED if payload.scheduled_at else BroadcastStatus.DRAFT,
            scheduled_at=payload.scheduled_at,
            created_by=created_by,
        )
        self.db.add(campaign)
        await self.db.flush()

        await self._log(
            organization_id=organization_id,
            actor_id=created_by,
            campaign_id=campaign.id,
            event="broadcast_campaign_created",
            details={"name": payload.name, "channels": campaign.channels},
        )

        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def get_campaign_by_id(self, *, organization_id: int, campaign_id: int) -> BroadcastCampaign:
        result = await self.db.execute(
            select(BroadcastCampaign).where(
                BroadcastCampaign.id == campaign_id,
                BroadcastCampaign.organization_id == organization_id,
            )
        )
        campaign = result.scalar_one_or_none()
        if campaign is None:
            raise CampaignNotFoundError(f"Broadcast campaign {campaign_id} not found")
        return campaign

    async def send_campaign(self, *, organization_id: int, campaign_id: int) -> BroadcastCampaign:
        campaign = await self.get_campaign_by_id(organization_id=organization_id, campaign_id=campaign_id)

        if campaign.status not in (BroadcastStatus.DRAFT, BroadcastStatus.SCHEDULED):
            raise CampaignNotSendableError(
                f"Campaign {campaign_id} is in status '{campaign.status.value}' and cannot be sent "
                f"(only draft or scheduled campaigns can be launched)"
            )

        await self.resolve_and_stage_recipients(campaign)
        await self.db.refresh(campaign)
        return campaign

    async def schedule_campaign(
        self, *, organization_id: int, campaign_id: int, scheduled_at: datetime
    ) -> BroadcastCampaign:
        campaign = await self.get_campaign_by_id(organization_id=organization_id, campaign_id=campaign_id)

        if campaign.status != BroadcastStatus.DRAFT:
            raise CampaignNotScheduleableError(
                f"Campaign {campaign_id} is in status '{campaign.status.value}' — "
                f"only draft campaigns can be scheduled"
            )

        campaign.scheduled_at = scheduled_at
        campaign.status = BroadcastStatus.SCHEDULED

        await self._log(
            organization_id=organization_id,
            actor_id=campaign.created_by,
            campaign_id=campaign.id,
            event="broadcast_campaign_scheduled",
            details={"scheduled_at": scheduled_at.isoformat()},
        )

        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def resolve_and_stage_recipients(self, campaign: BroadcastCampaign) -> int:
        customers = await self.audience_resolver.resolve(campaign.organization_id, campaign.audience_filter)

        for c in customers:
            if c.organization_id != campaign.organization_id:
                raise CrossTenantAudienceError(
                    f"Resolver returned customer {c.id} outside org {campaign.organization_id}"
                )

        channels = [ChannelType(c) for c in campaign.channels]

        queued_count = 0
        skipped_count = 0
        failed_count = 0

        for customer in customers:
            chosen_channel = next(
                (ch for ch in channels if _channel_contactable(ch, customer)), None
            )
            if chosen_channel is None:
                skipped_count += 1
                await self._add_recipient(
                    campaign, customer, channel=channels[0],
                    status=RecipientStatus.SKIPPED_CHANNEL_UNAVAILABLE,
                )
                continue

            if not _consent_field(chosen_channel, customer):
                skipped_count += 1
                await self._add_recipient(
                    campaign, customer, channel=chosen_channel,
                    status=RecipientStatus.SKIPPED_NO_CONSENT,
                )
                continue

            allowed, reason, use_template = check_channel_compliance(
                chosen_channel, campaign.message_body, campaign.whatsapp_template_id, customer
            )
            if not allowed:
                failed_count += 1
                await self._add_recipient(
                    campaign, customer, channel=chosen_channel,
                    status=RecipientStatus.FAILED, error_reason=reason,
                )
                continue

            recipient = await self._add_recipient(
                campaign, customer, channel=chosen_channel, status=RecipientStatus.PENDING,
            )

            try:
                provider_message_id = await self.queue_client.queue(
                    channel=chosen_channel,
                    customer=customer,
                    message_body=campaign.message_body,
                    template_id=campaign.whatsapp_template_id,
                    use_template=use_template,
                )
                recipient.status = RecipientStatus.QUEUED
                recipient.provider_message_id = provider_message_id
                recipient.queued_at = datetime.now(timezone.utc)
                queued_count += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to queue broadcast recipient %s", customer.id)
                recipient.status = RecipientStatus.FAILED
                recipient.error_reason = str(exc)[:500]
                failed_count += 1

        campaign.total_recipients = len(customers)
        campaign.total_skipped = skipped_count
        campaign.total_failed = failed_count
        campaign.status = BroadcastStatus.SENDING if queued_count else BroadcastStatus.FAILED
        campaign.started_at = datetime.now(timezone.utc)

        await self._log(
            organization_id=campaign.organization_id,
            actor_id=campaign.created_by,
            campaign_id=campaign.id,
            event="broadcast_campaign_staged",
            details={
                "queued": queued_count, "skipped": skipped_count, "failed": failed_count,
            },
        )

        await self.db.commit()
        return queued_count

    async def _add_recipient(
        self,
        campaign: BroadcastCampaign,
        customer: CustomerRecord,
        *,
        channel: ChannelType,
        status: RecipientStatus,
        error_reason: str | None = None,
    ) -> BroadcastRecipient:
        recipient = BroadcastRecipient(
            campaign_id=campaign.id,
            organization_id=campaign.organization_id,
            customer_id=customer.id,
            channel=channel,
            status=status,
            error_reason=error_reason,
        )
        self.db.add(recipient)
        await self.db.flush()
        return recipient

    async def _log(
        self, *, organization_id: int, actor_id: int, campaign_id: int, event: str, details: dict
    ) -> None:
        self.db.add(
            ActivityLog(
                organization_id=organization_id,
                actor_id=actor_id,
                event_type=event,
                metadata={"campaign_id": campaign_id, **details},
            )
        )

    async def list_campaigns(
        self, *, organization_id: int, page: int = 1, page_size: int = 20
    ) -> tuple[list[BroadcastCampaign], int]:
        base_query = select(BroadcastCampaign).where(BroadcastCampaign.organization_id == organization_id)

        count_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            base_query.order_by(BroadcastCampaign.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()
        return items, total

    async def list_recipients(
        self,
        *,
        organization_id: int,
        campaign_id: int,
        page: int = 1,
        page_size: int = 50,
        status_filter: RecipientStatus | None = None,
    ) -> tuple[list[BroadcastRecipient], int]:
        await self.get_campaign_by_id(organization_id=organization_id, campaign_id=campaign_id)

        base_query = select(BroadcastRecipient).where(BroadcastRecipient.campaign_id == campaign_id)
        if status_filter is not None:
            base_query = base_query.where(BroadcastRecipient.status == status_filter)

        count_result = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total = count_result.scalar_one()

        result = await self.db.execute(
            base_query.order_by(BroadcastRecipient.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()
        return items, total