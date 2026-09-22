from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_logs import WebhookLog

logger = logging.getLogger(__name__)

SENSITIVE_KEYS = {
    "access_token", "token", "api_key", "apikey", "secret",
    "authorization", "password", "client_secret", "refresh_token",
}


class WebhookLogError(Exception):
    pass


class WebhookLogNotFoundError(WebhookLogError):
    pass


def mask_sensitive(data: Any) -> Any:
    """
    Recursively redacts known sensitive keys from a dict/list structure
    before it's persisted. Applied to headers and, defensively, to the
    raw payload — most provider webhook bodies don't carry secrets, but
    some include re-auth or verify tokens in query params/body.
    """
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_KEYS:
                masked[key] = "***REDACTED***"
            else:
                masked[key] = mask_sensitive(value)
        return masked
    if isinstance(data, list):
        return [mask_sensitive(item) for item in data]
    return data


class WebhookLogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_inbound_log(
        self,
        *,
        channel: str,
        raw_payload: dict | None,
        headers: dict | None = None,
        organization_id: int | None = None,
        event_type: str | None = None,
    ) -> WebhookLog:
        log = WebhookLog(
            organization_id=organization_id,
            channel=channel,
            direction="inbound",
            event_type=event_type,
            raw_payload=mask_sensitive(raw_payload) if raw_payload is not None else None,
            headers=mask_sensitive(headers) if headers is not None else None,
            processing_status="received",
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def mark_signature_verified(self, log_id: int, *, valid: bool) -> None:
        log = await self.db.get(WebhookLog, log_id)
        if log is None:
            return
        log.signature_valid = valid
        if not valid:
            log.processing_status = "rejected"
            log.error_message = "signature_verification_failed"
        await self.db.commit()

    async def mark_processed(
        self,
        log_id: int,
        *,
        status: str,
        normalized_payload: dict | None = None,
        organization_id: int | None = None,
        event_type: str | None = None,
        error_message: str | None = None,
        related_conversation_id: int | None = None,
        related_message_id: int | None = None,
    ) -> None:
        log = await self.db.get(WebhookLog, log_id)
        if log is None:
            return
        log.processing_status = status
        if normalized_payload is not None:
            log.normalized_payload = normalized_payload
        if organization_id is not None:
            log.organization_id = organization_id
        if event_type is not None:
            log.event_type = event_type
        if error_message is not None:
            log.error_message = error_message
        if related_conversation_id is not None:
            log.related_conversation_id = related_conversation_id
        if related_message_id is not None:
            log.related_message_id = related_message_id
        await self.db.commit()

    async def log_outbound_call(
        self,
        *,
        channel: str,
        organization_id: int | None,
        request_summary: dict | None,
        response_summary: dict | None,
        http_status_code: int | None,
        processing_status: str = "processed",
        error_message: str | None = None,
        event_type: str | None = None,
    ) -> WebhookLog:
        log = WebhookLog(
            organization_id=organization_id,
            channel=channel,
            direction="outbound",
            event_type=event_type,
            request_summary=mask_sensitive(request_summary) if request_summary else None,
            response_summary=mask_sensitive(response_summary) if response_summary else None,
            http_status_code=http_status_code,
            processing_status=processing_status,
            error_message=error_message,
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_log_by_id(self, *, organization_id: int, log_id: int) -> WebhookLog:
        result = await self.db.execute(
            select(WebhookLog).where(
                WebhookLog.id == log_id,
                WebhookLog.organization_id == organization_id,
            )
        )
        log = result.scalar_one_or_none()
        if log is None:
            raise WebhookLogNotFoundError(f"Webhook log {log_id} not found")
        return log

    async def list_logs(
        self,
        *,
        organization_id: int,
        page: int = 1,
        page_size: int = 50,
        channel: str | None = None,
        direction: str | None = None,
        processing_status: str | None = None,
        event_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[WebhookLog], int]:
        base_query = select(WebhookLog).where(WebhookLog.organization_id == organization_id)

        if channel:
            base_query = base_query.where(WebhookLog.channel == channel)
        if direction:
            base_query = base_query.where(WebhookLog.direction == direction)
        if processing_status:
            base_query = base_query.where(WebhookLog.processing_status == processing_status)
        if event_type:
            base_query = base_query.where(WebhookLog.event_type == event_type)
        if start_date:
            base_query = base_query.where(
                WebhookLog.created_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
            )
        if end_date:
            base_query = base_query.where(
                WebhookLog.created_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc)
            )

        count_result = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total = count_result.scalar_one()

        result = await self.db.execute(
            base_query.order_by(WebhookLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()
        return items, total

    async def get_stats(
        self,
        *,
        organization_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        base_filter = [WebhookLog.organization_id == organization_id]
        if start_date:
            base_filter.append(
                WebhookLog.created_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
            )
        if end_date:
            base_filter.append(
                WebhookLog.created_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc)
            )

        totals_result = await self.db.execute(
            select(
                func.count(),
                func.sum(case((WebhookLog.processing_status == "processed", 1), else_=0)),
                func.sum(case((WebhookLog.processing_status == "failed", 1), else_=0)),
                func.sum(case((WebhookLog.processing_status == "rejected", 1), else_=0)),
                func.sum(case((WebhookLog.signature_valid.is_(False), 1), else_=0)),
            ).where(*base_filter)
        )
        total, processed, failed, rejected, invalid_sig = totals_result.one()

        channel_result = await self.db.execute(
            select(
                WebhookLog.channel,
                func.count(),
                func.sum(case((WebhookLog.processing_status == "received", 1), else_=0)),
                func.sum(case((WebhookLog.processing_status == "processed", 1), else_=0)),
                func.sum(case((WebhookLog.processing_status == "failed", 1), else_=0)),
                func.sum(case((WebhookLog.processing_status == "rejected", 1), else_=0)),
            )
            .where(*base_filter)
            .group_by(WebhookLog.channel)
        )
        by_channel = [
            {
                "channel": channel,
                "total": total_c or 0,
                "received": received or 0,
                "processed": processed_c or 0,
                "failed": failed_c or 0,
                "rejected": rejected_c or 0,
            }
            for channel, total_c, received, processed_c, failed_c, rejected_c in channel_result.all()
        ]

        return {
            "organization_id": organization_id,
            "start_date": start_date,
            "end_date": end_date,
            "total": total or 0,
            "processed": processed or 0,
            "failed": failed or 0,
            "rejected": rejected or 0,
            "invalid_signature_count": invalid_sig or 0,
            "by_channel": by_channel,
            "generated_at": datetime.now(timezone.utc),
        }


# --------------------------------------------------------------------------
# Fail-safe wrappers — call these from existing webhook handlers.
# Logging must never block message acknowledgement, so every function here
# swallows its own exceptions and only logs them via the standard logger.
# --------------------------------------------------------------------------

async def log_inbound_safe(
    db: AsyncSession,
    *,
    channel: str,
    raw_payload: dict | None,
    headers: dict | None = None,
    organization_id: int | None = None,
    event_type: str | None = None,
) -> Optional[int]:
    try:
        service = WebhookLogService(db)
        log = await service.create_inbound_log(
            channel=channel,
            raw_payload=raw_payload,
            headers=headers,
            organization_id=organization_id,
            event_type=event_type,
        )
        return log.id
    except Exception:  # noqa: BLE001
        logger.exception("Failed to persist inbound webhook log for channel=%s", channel)
        return None


async def mark_signature_verified_safe(db: AsyncSession, log_id: int | None, *, valid: bool) -> None:
    if log_id is None:
        return
    try:
        await WebhookLogService(db).mark_signature_verified(log_id, valid=valid)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to update signature verification for webhook log %s", log_id)


async def mark_processed_safe(
    db: AsyncSession,
    log_id: int | None,
    *,
    status: str,
    normalized_payload: dict | None = None,
    organization_id: int | None = None,
    event_type: str | None = None,
    error_message: str | None = None,
    related_conversation_id: int | None = None,
    related_message_id: int | None = None,
) -> None:
    if log_id is None:
        return
    try:
        await WebhookLogService(db).mark_processed(
            log_id,
            status=status,
            normalized_payload=normalized_payload,
            organization_id=organization_id,
            event_type=event_type,
            error_message=error_message,
            related_conversation_id=related_conversation_id,
            related_message_id=related_message_id,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to update processing result for webhook log %s", log_id)


async def log_outbound_safe(
    db: AsyncSession,
    *,
    channel: str,
    organization_id: int | None,
    request_summary: dict | None,
    response_summary: dict | None,
    http_status_code: int | None,
    processing_status: str = "processed",
    error_message: str | None = None,
    event_type: str | None = None,
) -> None:
    try:
        await WebhookLogService(db).log_outbound_call(
            channel=channel,
            organization_id=organization_id,
            request_summary=request_summary,
            response_summary=response_summary,
            http_status_code=http_status_code,
            processing_status=processing_status,
            error_message=error_message,
            event_type=event_type,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to persist outbound webhook log for channel=%s", channel)