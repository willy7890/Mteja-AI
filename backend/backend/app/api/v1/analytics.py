from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation, ConversationStatus, HandlerType
from app.models.message import Message
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_analytics_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Generates real-time conversation analytics using standard DB fields."""
    base_filter = [Conversation.organization_id == current_user.organization_id]
    
    if start_date:
        base_filter.append(Conversation.created_at >= start_date)
    if end_date:
        base_filter.append(Conversation.created_at <= end_date)

    # 1. Total count of conversations
    total_query = select(func.count(Conversation.id)).where(*base_filter)
    total_conversations = (await db.execute(total_query)).scalar() or 0

    # 2. Count by Current Handler (AI vs Human)
    ai_handler_query = select(func.count(Conversation.id)).where(
        *base_filter,
        Conversation.current_handler == HandlerType.AI.value
    )
    ai_handled_count = (await db.execute(ai_handler_query)).scalar() or 0

    human_handler_query = select(func.count(Conversation.id)).where(
        *base_filter,
        Conversation.current_handler == HandlerType.HUMAN.value
    )
    human_handled_count = (await db.execute(human_handler_query)).scalar() or 0

    # 3. Count by Conversation Status Enum (Active, Escalated, Resolved, Open)
    active_query = select(func.count(Conversation.id)).where(
        *base_filter,
        Conversation.status == ConversationStatus.ACTIVE.value
    )
    active_count = (await db.execute(active_query)).scalar() or 0

    escalated_query = select(func.count(Conversation.id)).where(
        *base_filter,
        Conversation.status == ConversationStatus.ESCALATED.value
    )
    escalated_count = (await db.execute(escalated_query)).scalar() or 0

    resolved_query = select(func.count(Conversation.id)).where(
        *base_filter,
        Conversation.status == ConversationStatus.RESOLVED.value
    )
    resolved_count = (await db.execute(resolved_query)).scalar() or 0

    # 4. Total messages metrics
    total_messages_query = (
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(*base_filter)
    )
    total_messages = (await db.execute(total_messages_query)).scalar() or 0

    # Calculate Rates
    escalation_rate = (
        round((escalated_count / total_conversations) * 100, 2)
        if total_conversations > 0
        else 0.0
    )
    resolution_rate = (
        round((resolved_count / total_conversations) * 100, 2)
        if total_conversations > 0
        else 0.0
    )

    return {
        "total_conversations": total_conversations,
        "handlers": {
            "ai": ai_handled_count,
            "human": human_handled_count,
        },
        "statuses": {
            "active": active_count,
            "escalated": escalated_count,
            "resolved": resolved_count,
        },
        "rates": {
            "escalation_rate_pct": escalation_rate,
            "resolution_rate_pct": resolution_rate,
        },
        "total_messages": total_messages,
    }