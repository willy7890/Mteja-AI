from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.engines import process_chat_message
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation, HandlerType, ConversationStatus
from app.models.message import Message
from app.models.user import User
from app.schemas.conversation import (
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    EscalateRequest,
    HandoffRequest,
)
from app.agents.engines import process_chat_message
from app.services.handoff_service import (
    assign_agent,
    escalate_conversation,
    resolve_conversation,
    return_to_ai,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


# ----------------------------------------------------------------------
# 1. READ ROUTES (List & History)
# ----------------------------------------------------------------------
@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    status: Optional[str] = Query(None),
    current_handler: Optional[str] = Query(None),
    assigned_agent_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists conversations for the user's organization with optional filters."""
    query = select(Conversation).where(
        Conversation.organization_id == current_user.organization_id
    )
    if status:
        query = query.where(Conversation.status == status)
    if current_handler:
        query = query.where(Conversation.current_handler == current_handler)
    if assigned_agent_id is not None:
        query = query.where(Conversation.assigned_agent_id == assigned_agent_id)

    result = await db.execute(query.order_by(Conversation.created_at.desc()))
    return result.scalars().all()


@router.get("/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves single conversation details."""
    return await _get_owned_conversation(db, id, current_user.organization_id)


@router.get("/{id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves message history for a conversation."""
    await _get_owned_conversation(db, id, current_user.organization_id)
    query = (
        select(Message)
        .where(Message.conversation_id == id)
        .order_by(Message.created_at.asc())
    )
    result = await db.execute(query)
    return result.scalars().all()


# ----------------------------------------------------------------------
# 2. MESSAGING ROUTE (Unified Entry Point)
# ----------------------------------------------------------------------
@router.post("/{id}/messages", response_model=MessageResponse)
async def send_message(
    id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Single entry point for sending a message.

    - If current_handler is AI: Runs intent engine and appends AI response.
    - If current_handler is HUMAN: Stores human agent response directly.
    """
    conv = await _get_owned_conversation(db, id, current_user.organization_id)

    # Record incoming message
    user_msg = Message(
        conversation_id=conv.id,
        sender_type=payload.sender_type,  # "customer" or "agent"
        content=payload.content,
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    # If incoming from customer and AI is active, run through engine
    if payload.sender_type == "customer" and conv.current_handler == HandlerType.AI.value:
        engine_result = await process_chat_message(
            db=db,
            conversation=conv,
            user_message=payload.content,
        )

        if engine_result.get("message"):
            ai_msg = Message(
                conversation_id=conv.id,
                sender_type="ai",
                content=engine_result["message"],
            )
            db.add(ai_msg)
            await db.commit()

    return user_msg


# ----------------------------------------------------------------------
# 3. TAKEOVER & HANDOFF ROUTES
# ----------------------------------------------------------------------
@router.post("/{id}/takeover", response_model=ConversationResponse)
async def takeover_conversation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Human agent manually takes over conversation control."""
    conv = await _get_owned_conversation(db, id, current_user.organization_id)
    return await escalate_conversation(
        db, conv, reason="manual_takeover", triggered_by="agent", agent_id=current_user.id
    )


@router.post("/{id}/escalate", response_model=ConversationResponse)
async def escalate(
    id: int,
    data: EscalateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Escalates conversation with explicit reason."""
    conv = await _get_owned_conversation(db, id, current_user.organization_id)
    return await escalate_conversation(
        db, conv, reason=data.reason, triggered_by="agent", agent_id=data.agent_id or current_user.id
    )


@router.post("/{id}/return-to-ai", response_model=ConversationResponse)
async def return_to_ai_endpoint(
    id: int,
    data: HandoffRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns conversation control back to AI."""
    conv = await _get_owned_conversation(db, id, current_user.organization_id)
    agent_id = data.agent_id if data and data.agent_id is not None else current_user.id
    return await return_to_ai(db, conv, agent_id=agent_id)


@router.post("/{id}/resolve", response_model=ConversationResponse)
async def resolve(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marks conversation as resolved."""
    conv = await _get_owned_conversation(db, id, current_user.organization_id)
    return await resolve_conversation(db, conv, agent_id=current_user.id)


# ----------------------------------------------------------------------
# HELPER
# ----------------------------------------------------------------------
async def _get_owned_conversation(
    db: AsyncSession, conversation_id: int, organization_id: int
) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == organization_id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return conv
