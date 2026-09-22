from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.engines import process_chat_message
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation, HandlerType
from app.models.message import Message
from app.models.user import User
from app.schemas.conversation import (
    AssignRequest,
    ConversationResponse,
    EscalateRequest,
    HandoffRequest,
    HandoffStatusResponse,
    MessageCreate,
    MessageResponse,
    ReturnToAIRequest,
)
from app.services.handoff_service import (
    assign_agent,
    escalate_conversation,
    resolve_conversation,
    return_to_ai,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    current_handler: Optional[str] = Query(None),
    assigned_agent_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.organization_id == current_user.organization_id
        )
    )

    if status:
        query = query.where(Conversation.status == status)

    if channel:
        query = query.where(Conversation.channel == channel)

    if current_handler:
        query = query.where(
            Conversation.current_handler == current_handler
        )

    if assigned_agent_id is not None:
        query = query.where(
            Conversation.assigned_agent_id == assigned_agent_id
        )

    result = await db.execute(
        query.order_by(Conversation.created_at.desc())
    )

    return result.scalars().all()


@router.get("/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_owned_conversation(
        db,
        id,
        current_user.organization_id,
    )


@router.get("/{id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_owned_conversation(
        db,
        id,
        current_user.organization_id,
    )

    query = (
        select(Message)
        .where(Message.conversation_id == id)
        .order_by(Message.created_at.asc())
    )

    result = await db.execute(query)

    return result.scalars().all()


@router.post("/{id}/messages", response_model=MessageResponse)
async def send_message(
    id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_owned_conversation(
        db,
        id,
        current_user.organization_id,
    )

    user_msg = Message(
        conversation_id=conv.id,
        sender_type=payload.sender_type,
        content=payload.content,
    )

    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    if (
        payload.sender_type == "customer"
        and conv.current_handler == HandlerType.AI.value
    ):
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


@router.post("/{id}/takeover", response_model=ConversationResponse)
async def takeover_conversation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_owned_conversation(
        db,
        id,
        current_user.organization_id,
    )

    return await escalate_conversation(
        db,
        conv,
        reason="manual_takeover",
        triggered_by="agent",
        agent_id=current_user.id,
    )


@router.post("/{id}/escalate", response_model=ConversationResponse)
async def escalate(
    id: int,
    data: EscalateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_owned_conversation(
        db,
        id,
        current_user.organization_id,
    )

    return await escalate_conversation(
        db,
        conv,
        reason=data.reason,
        triggered_by="agent",
        agent_id=data.agent_id or current_user.id,
    )


@router.post(
    "/{id}/return-to-ai",
    response_model=ConversationResponse,
)
async def return_to_ai_endpoint(
    id: int,
    data: Optional[HandoffRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_owned_conversation(
        db,
        id,
        current_user.organization_id,
    )

    return await return_to_ai(
        db,
        conv,
        agent_id=current_user.id,
    )


@router.post("/{id}/resolve", response_model=ConversationResponse)
async def resolve(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_owned_conversation(
        db,
        id,
        current_user.organization_id,
    )

    return await resolve_conversation(
        db,
        conv,
        agent_id=current_user.id,
    )


async def _get_owned_conversation(
    db: AsyncSession,
    conversation_id: int,
    organization_id: int,
) -> Conversation:
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
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