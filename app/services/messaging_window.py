# backend/app/services/messaging_window.py

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.activity_log import ActivityLog


WINDOW_DURATION = timedelta(hours=24)


class MessagingWindowClosedError(Exception):
    pass


def is_window_open(conversation: Conversation) -> bool:
    if conversation.last_customer_message_at is None:
        return False

    elapsed = datetime.utcnow() - conversation.last_customer_message_at
    return elapsed < WINDOW_DURATION


async def record_customer_message(db: AsyncSession, conversation: Conversation) -> None:
    conversation.last_customer_message_at = datetime.utcnow()
    conversation.messaging_window_status = "open"

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)


async def refresh_window_status(db: AsyncSession, conversation: Conversation) -> str:
    status = "open" if is_window_open(conversation) else "closed"

    if conversation.messaging_window_status != status:
        conversation.messaging_window_status = status
        db.add(conversation)
        await db.commit()

        log_entry = ActivityLog(
            organization_id=conversation.organization_id,
            conversation_id=conversation.id,
            action=f"messaging_window_{status}",
            details=f"24-hour messaging window is now {status}",
        )
        db.add(log_entry)
        await db.commit()

    return status


async def assert_can_send_free_form(db: AsyncSession, conversation: Conversation) -> None:
    status = await refresh_window_status(db, conversation)

    if status == "closed":
        raise MessagingWindowClosedError(
            "24-hour messaging window imefungwa. Tumia approved template."
        )