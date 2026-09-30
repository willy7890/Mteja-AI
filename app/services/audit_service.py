import json
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog
from app.core.redis import get_redis


async def record_activity(
    db: AsyncSession,
    *,
    organization_id: int,
    actor: str,
    action_type: str,
    description: str,
    user_id: int | None = None,
    conversation_id: int | str | None = None,
    details: dict | None = None,
) -> ActivityLog:
    entry = ActivityLog(
        organization_id=organization_id,
        user_id=user_id,
        conversation_id=str(conversation_id) if conversation_id is not None else None,
        actor=actor,
        action_type=action_type,
        description=description,
        details=json.dumps(details, default=str) if details else None,
    )
    db.add(entry)
    return entry


async def notify_agent(event: dict) -> None:
    try:
        redis = await asyncio.wait_for(get_redis(), timeout=0.2)
        await asyncio.wait_for(redis.publish("mteja:agent-events", json.dumps(event, default=str)), timeout=0.2)
    except Exception:
        return