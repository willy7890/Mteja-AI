from sqlalchemy import select
from app.models.message import Message


async def build_conversation_context(
    conversation_id: int,
    db_session,
    max_messages: int = 15,
) -> list[dict]:
    result = await db_session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(max_messages)
    )
    messages = result.scalars().all()

    context = []
    for msg in messages:
        role = "assistant" if msg.sender_type == "agent" else "user"
        context.append({"role": role, "content": msg.content})

    return context