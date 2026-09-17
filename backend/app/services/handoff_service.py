from datetime import datetime, timezone
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, HandlerType, ConversationStatus
from app.models.escalation_log import EscalationLog


async def _get_conversation(
    db_session: AsyncSession, conversation: Union[Conversation, int]
) -> Conversation:
    if isinstance(conversation, int):
        conv = await db_session.get(Conversation, conversation)
        if not conv:
            raise ValueError("Conversation not found")
        return conv
    return conversation


async def escalate_conversation(
    db_session: AsyncSession,
    conversation: Union[Conversation, int],
    reason: str,
    triggered_by: str = "agent",
    agent_id: int | None = None,
) -> Conversation:
    """Escalates conversation to a Human Handler."""
    conv = await _get_conversation(db_session, conversation)

    conv.current_handler = HandlerType.HUMAN.value
    conv.status = ConversationStatus.ESCALATED.value
    conv.escalation_reason = reason
    conv.escalated_at = datetime.now(timezone.utc)
    if agent_id:
        conv.assigned_agent_id = agent_id

    log = EscalationLog(
        conversation_id=conv.id,
        triggered_by=triggered_by,
        triggered_by_user_id=agent_id,
        action="escalated",
        reason=reason,
    )
    db_session.add(log)
    await db_session.commit()
    await db_session.refresh(conv)
    return conv


async def assign_agent(
    db_session: AsyncSession,
    conversation: Union[Conversation, int],
    agent_id: int,
) -> Conversation:
    """Assigns an agent and ensures the handler is set to Human."""
    conv = await _get_conversation(db_session, conversation)

    conv.assigned_agent_id = agent_id
    conv.current_handler = HandlerType.HUMAN.value
    conv.status = ConversationStatus.ACTIVE.value

    log = EscalationLog(
        conversation_id=conv.id,
        triggered_by="agent",
        triggered_by_user_id=agent_id,
        action="assigned",
    )
    db_session.add(log)
    await db_session.commit()
    await db_session.refresh(conv)
    return conv


async def return_to_ai(
    db_session: AsyncSession,
    conversation: Union[Conversation, int],
    agent_id: int | None = None,
) -> Conversation:
    """Returns conversation control back to AI."""
    conv = await _get_conversation(db_session, conversation)

    conv.current_handler = HandlerType.AI.value
    conv.status = ConversationStatus.ACTIVE.value
    conv.assigned_agent_id = None
    conv.escalation_reason = None

    log = EscalationLog(
        conversation_id=conv.id,
        triggered_by="agent" if agent_id else "system",
        triggered_by_user_id=agent_id,
        action="returned_to_ai",
    )
    db_session.add(log)
    await db_session.commit()
    await db_session.refresh(conv)
    return conv


async def resolve_conversation(
    db_session: AsyncSession,
    conversation: Union[Conversation, int],
    agent_id: int | None = None,
) -> Conversation:
    """Resolves conversation and stamps resolved_at."""
    conv = await _get_conversation(db_session, conversation)

    conv.status = ConversationStatus.RESOLVED.value
    conv.resolved_at = datetime.now(timezone.utc)

    log = EscalationLog(
        conversation_id=conv.id,
        triggered_by="agent" if agent_id else "system",
        triggered_by_user_id=agent_id,
        action="resolved",
    )
    db_session.add(log)
    await db_session.commit()
    await db_session.refresh(conv)
    return conv