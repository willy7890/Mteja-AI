from __future__ import annotations

import time
import logging
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 60

STATUS_OPEN = "open"
STATUS_RESOLVED = "resolved"
STATUS_ESCALATED = "escalated"
MODE_AI = "ai"


class AnalyticsError(Exception):
    pass


class _TTLCache:
    def __init__(self):
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = CACHE_TTL_SECONDS):
        self._store[key] = (time.time() + ttl_seconds, value)


_overview_cache = _TTLCache()
_conversation_cache = _TTLCache()
_ai_performance_cache = _TTLCache()
_channel_cache = _TTLCache()
_response_time_cache = _TTLCache()


def _day_bounds(start_date: date, end_date: date) -> tuple[datetime, datetime]:
    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc)
    return start_dt, end_dt


def _first_response_subquery():
    return (
        select(
            Message.conversation_id.label("conversation_id"),
            func.min(Message.created_at).label("first_response_at"),
        )
        .where(Message.direction == "outbound")
        .group_by(Message.conversation_id)
        .subquery()
    )


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(
        self, *, organization_id: int, start_date: date, end_date: date
    ) -> dict:
        cache_key = f"overview:{organization_id}:{start_date}:{end_date}"
        cached = _overview_cache.get(cache_key)
        if cached is not None:
            return {**cached, "cached": True}

        start_dt, end_dt = _day_bounds(start_date, end_date)
        base_filter = (
            Conversation.organization_id == organization_id,
            Conversation.created_at >= start_dt,
            Conversation.created_at <= end_dt,
        )

        totals_result = await self.db.execute(
            select(
                func.count(),
                func.sum(
                    case(
                        (
                            (Conversation.status == STATUS_RESOLVED)
                            & (Conversation.mode == MODE_AI),
                            1,
                        ),
                        else_=0,
                    )
                ),
            ).where(*base_filter)
        )
        total_conversations, ai_resolved_conversations = totals_result.one()
        total_conversations = total_conversations or 0
        ai_resolved_conversations = ai_resolved_conversations or 0

        first_resp = _first_response_subquery()
        response_time_result = await self.db.execute(
            select(
                func.avg(
                    func.extract("epoch", first_resp.c.first_response_at - Conversation.created_at)
                ),
                func.avg(
                    case(
                        (
                            Conversation.status == STATUS_RESOLVED,
                            func.extract("epoch", Conversation.updated_at - Conversation.created_at),
                        ),
                        else_=None,
                    )
                ),
            )
            .select_from(Conversation)
            .outerjoin(first_resp, first_resp.c.conversation_id == Conversation.id)
            .where(*base_filter)
        )
        avg_first_response_seconds, avg_resolution_seconds = response_time_result.one()

        message_count_result = await self.db.execute(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(*base_filter)
        )
        total_messages = message_count_result.scalar_one() or 0

        channel_result = await self.db.execute(
            select(
                Conversation.channel,
                func.count(func.distinct(Conversation.id)),
                func.count(Message.id),
            )
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .where(*base_filter)
            .group_by(Conversation.channel)
        )
        channel_breakdown = [
            {"channel": channel, "conversation_count": conv_count, "message_count": msg_count or 0}
            for channel, conv_count, msg_count in channel_result.all()
        ]

        result = {
            "organization_id": organization_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "ai_resolved_conversations": ai_resolved_conversations,
            "ai_resolution_rate": (
                round(ai_resolved_conversations / total_conversations, 4) if total_conversations else 0.0
            ),
            "avg_first_response_seconds": (
                round(avg_first_response_seconds, 2) if avg_first_response_seconds is not None else None
            ),
            "avg_resolution_seconds": (
                round(avg_resolution_seconds, 2) if avg_resolution_seconds is not None else None
            ),
            "avg_messages_per_conversation": (
                round(total_messages / total_conversations, 2) if total_conversations else 0.0
            ),
            "channel_breakdown": channel_breakdown,
            "generated_at": datetime.now(timezone.utc),
            "cached": False,
        }

        _overview_cache.set(cache_key, result)
        return result

    async def get_conversation_analytics(
        self, *, organization_id: int, start_date: date, end_date: date
    ) -> dict:
        cache_key = f"conversations:{organization_id}:{start_date}:{end_date}"
        cached = _conversation_cache.get(cache_key)
        if cached is not None:
            return {**cached, "cached": True}

        start_dt, end_dt = _day_bounds(start_date, end_date)
        base_filter = (
            Conversation.organization_id == organization_id,
            Conversation.created_at >= start_dt,
            Conversation.created_at <= end_dt,
        )

        status_counts_result = await self.db.execute(
            select(
                func.count(),
                func.sum(
                    case(
                        ((Conversation.status == STATUS_RESOLVED) & (Conversation.mode == MODE_AI), 1),
                        else_=0,
                    )
                ),
                func.sum(case((Conversation.status == STATUS_ESCALATED, 1), else_=0)),
                func.sum(case((Conversation.status == STATUS_OPEN, 1), else_=0)),
            ).where(*base_filter)
        )
        total, ai_resolved, escalated, open_count = status_counts_result.one()
        total = total or 0
        ai_resolved = ai_resolved or 0
        escalated = escalated or 0
        open_count = open_count or 0

        first_resp = _first_response_subquery()
        response_time_result = await self.db.execute(
            select(
                func.avg(
                    func.extract("epoch", first_resp.c.first_response_at - Conversation.created_at)
                ),
                func.avg(
                    case(
                        (
                            Conversation.status == STATUS_RESOLVED,
                            func.extract("epoch", Conversation.updated_at - Conversation.created_at),
                        ),
                        else_=None,
                    )
                ),
            )
            .select_from(Conversation)
            .outerjoin(first_resp, first_resp.c.conversation_id == Conversation.id)
            .where(*base_filter)
        )
        avg_first_response_seconds, avg_resolution_seconds = response_time_result.one()

        daily_result = await self.db.execute(
            select(
                func.date(Conversation.created_at).label("bucket_date"),
                func.count(),
                func.sum(
                    case(
                        ((Conversation.status == STATUS_RESOLVED) & (Conversation.mode == MODE_AI), 1),
                        else_=0,
                    )
                ),
                func.sum(case((Conversation.status == STATUS_ESCALATED, 1), else_=0)),
            )
            .where(*base_filter)
            .group_by(func.date(Conversation.created_at))
            .order_by(func.date(Conversation.created_at))
        )
        daily_volume = [
            {
                "bucket_date": bucket_date,
                "conversation_count": conv_count or 0,
                "ai_resolved_count": ai_count or 0,
                "escalated_count": esc_count or 0,
            }
            for bucket_date, conv_count, ai_count, esc_count in daily_result.all()
        ]

        result = {
            "organization_id": organization_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_conversations": total,
            "ai_resolved_conversations": ai_resolved,
            "escalated_conversations": escalated,
            "open_conversations": open_count,
            "avg_first_response_seconds": (
                round(avg_first_response_seconds, 2) if avg_first_response_seconds is not None else None
            ),
            "avg_resolution_seconds": (
                round(avg_resolution_seconds, 2) if avg_resolution_seconds is not None else None
            ),
            "daily_volume": daily_volume,
            "generated_at": datetime.now(timezone.utc),
            "cached": False,
        }

        _conversation_cache.set(cache_key, result)
        return result

    async def get_ai_performance(
        self, *, organization_id: int, start_date: date, end_date: date
    ) -> dict:
        cache_key = f"ai_performance:{organization_id}:{start_date}:{end_date}"
        cached = _ai_performance_cache.get(cache_key)
        if cached is not None:
            return {**cached, "cached": True}

        start_dt, end_dt = _day_bounds(start_date, end_date)
        base_filter = (
            Conversation.organization_id == organization_id,
            Conversation.created_at >= start_dt,
            Conversation.created_at <= end_dt,
        )

        totals_result = await self.db.execute(
            select(
                func.count(),
                func.sum(
                    case(
                        ((Conversation.status == STATUS_RESOLVED) & (Conversation.mode == MODE_AI), 1),
                        else_=0,
                    )
                ),
                func.sum(case((Conversation.status == STATUS_ESCALATED, 1), else_=0)),
            ).where(*base_filter)
        )
        total, ai_resolved, escalated = totals_result.one()
        total = total or 0
        ai_resolved = ai_resolved or 0
        escalated = escalated or 0

        daily_result = await self.db.execute(
            select(
                func.date(Conversation.created_at).label("bucket_date"),
                func.count(),
                func.sum(
                    case(
                        ((Conversation.status == STATUS_RESOLVED) & (Conversation.mode == MODE_AI), 1),
                        else_=0,
                    )
                ),
                func.sum(case((Conversation.status == STATUS_ESCALATED, 1), else_=0)),
            )
            .where(*base_filter)
            .group_by(func.date(Conversation.created_at))
            .order_by(func.date(Conversation.created_at))
        )
        daily_trend = []
        for bucket_date, day_total, day_ai, day_escalated in daily_result.all():
            day_total = day_total or 0
            day_ai = day_ai or 0
            day_escalated = day_escalated or 0
            daily_trend.append({
                "bucket_date": bucket_date,
                "total_conversations": day_total,
                "ai_resolved_count": day_ai,
                "escalated_count": day_escalated,
                "ai_resolution_rate": round(day_ai / day_total, 4) if day_total else 0.0,
            })

        result = {
            "organization_id": organization_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_conversations": total,
            "ai_resolved_conversations": ai_resolved,
            "escalated_conversations": escalated,
            "ai_resolution_rate": round(ai_resolved / total, 4) if total else 0.0,
            "escalation_rate": round(escalated / total, 4) if total else 0.0,
            "daily_trend": daily_trend,
            "generated_at": datetime.now(timezone.utc),
            "cached": False,
        }

        _ai_performance_cache.set(cache_key, result)
        return result

    async def get_channel_analytics(
        self, *, organization_id: int, start_date: date, end_date: date
    ) -> dict:
        cache_key = f"channels:{organization_id}:{start_date}:{end_date}"
        cached = _channel_cache.get(cache_key)
        if cached is not None:
            return {**cached, "cached": True}

        start_dt, end_dt = _day_bounds(start_date, end_date)
        base_filter = (
            Conversation.organization_id == organization_id,
            Conversation.created_at >= start_dt,
            Conversation.created_at <= end_dt,
        )

        total_result = await self.db.execute(select(func.count()).where(*base_filter))
        total_conversations = total_result.scalar_one() or 0

        channel_result = await self.db.execute(
            select(
                Conversation.channel,
                func.count(func.distinct(Conversation.id)),
                func.count(Message.id),
                func.sum(
                    case(
                        ((Conversation.status == STATUS_RESOLVED) & (Conversation.mode == MODE_AI), 1),
                        else_=0,
                    )
                ),
            )
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .where(*base_filter)
            .group_by(Conversation.channel)
        )

        channels = []
        for channel, conv_count, msg_count, ai_count in channel_result.all():
            conv_count = conv_count or 0
            ai_count = ai_count or 0
            channels.append({
                "channel": channel,
                "conversation_count": conv_count,
                "message_count": msg_count or 0,
                "share_pct": round(conv_count / total_conversations * 100, 2) if total_conversations else 0.0,
                "ai_resolved_count": ai_count,
                "ai_resolution_rate": round(ai_count / conv_count, 4) if conv_count else 0.0,
            })

        result = {
            "organization_id": organization_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_conversations": total_conversations,
            "channels": channels,
            "generated_at": datetime.now(timezone.utc),
            "cached": False,
        }

        _channel_cache.set(cache_key, result)
        return result

    async def get_response_times(
        self, *, organization_id: int, start_date: date, end_date: date
    ) -> dict:
        cache_key = f"response_times:{organization_id}:{start_date}:{end_date}"
        cached = _response_time_cache.get(cache_key)
        if cached is not None:
            return {**cached, "cached": True}

        start_dt, end_dt = _day_bounds(start_date, end_date)
        base_filter = (
            Conversation.organization_id == organization_id,
            Conversation.created_at >= start_dt,
            Conversation.created_at <= end_dt,
        )

        first_resp = _first_response_subquery()

        overall_result = await self.db.execute(
            select(
                func.avg(
                    func.extract("epoch", first_resp.c.first_response_at - Conversation.created_at)
                ),
                func.avg(
                    case(
                        (
                            Conversation.status == STATUS_RESOLVED,
                            func.extract("epoch", Conversation.updated_at - Conversation.created_at),
                        ),
                        else_=None,
                    )
                ),
            )
            .select_from(Conversation)
            .outerjoin(first_resp, first_resp.c.conversation_id == Conversation.id)
            .where(*base_filter)
        )
        avg_first_response_seconds, avg_resolution_seconds = overall_result.one()

        by_channel_result = await self.db.execute(
            select(
                Conversation.channel,
                func.avg(
                    func.extract("epoch", first_resp.c.first_response_at - Conversation.created_at)
                ),
                func.avg(
                    case(
                        (
                            Conversation.status == STATUS_RESOLVED,
                            func.extract("epoch", Conversation.updated_at - Conversation.created_at),
                        ),
                        else_=None,
                    )
                ),
                func.count(func.distinct(Conversation.id)),
            )
            .select_from(Conversation)
            .outerjoin(first_resp, first_resp.c.conversation_id == Conversation.id)
            .where(*base_filter)
            .group_by(Conversation.channel)
        )
        by_channel = [
            {
                "channel": channel,
                "avg_first_response_seconds": round(avg_first, 2) if avg_first is not None else None,
                "avg_resolution_seconds": round(avg_resolution, 2) if avg_resolution is not None else None,
                "conversation_count": count or 0,
            }
            for channel, avg_first, avg_resolution, count in by_channel_result.all()
        ]

        result = {
            "organization_id": organization_id,
            "start_date": start_date,
            "end_date": end_date,
            "avg_first_response_seconds": (
                round(avg_first_response_seconds, 2) if avg_first_response_seconds is not None else None
            ),
            "avg_resolution_seconds": (
                round(avg_resolution_seconds, 2) if avg_resolution_seconds is not None else None
            ),
            "by_channel": by_channel,
            "generated_at": datetime.now(timezone.utc),
            "cached": False,
        }

        _response_time_cache.set(cache_key, result)
        return result