from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import (
    SendMessageRequest,
    SendMessageResponse,
    MessageOut,
    ConversationOut,
)
from app.agents.orchestrator import Orchestrator

router = APIRouter(prefix="/api/v1", tags=["chat"])

orchestrator = Orchestrator()


@router.post("/messages/send", response_model=SendMessageResponse)
async def send_message(
    data: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Tafuta au Tengeneza Conversation
    if data.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == data.conversation_id,
                Conversation.organization_id == current_user.organization_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            organization_id=current_user.organization_id,
            customer_id=data.customer_id,
            status="open",
            mode="ai",  # Hakikisha field name inalingana na Model yako (mode/current_handler)
        )
        db.add(conversation)
        await db.flush()

    # 2. Hifadhi Ujumbe wa Mteja (Customer Message)
    user_message = Message(
        conversation_id=conversation.id,
        sender_type="customer",
        content=data.content,
    )
    db.add(user_message)
    await db.flush()

    # 3. Kama haiko kwenye Mode ya AI au imefungwa, hifadhi na usitishe AI Orchestrator
    is_ai_mode = getattr(conversation, "mode", None) == "ai" or getattr(conversation, "current_handler", None) == "ai"
    if not is_ai_mode or conversation.status != "open":
        await db.commit()
        await db.refresh(user_message)
        return SendMessageResponse(
            conversation_id=conversation.id,
            user_message=user_message,
            agent_response=None,
        )

    # 4. Tekeleza AI Orchestrator
    try:
        orch_result = await orchestrator.run(
            db=db,
            organization_id=current_user.organization_id,
            conversation_id=str(conversation.id),
            message=data.content,
        )
    except Exception as e:
        await db.commit()
        await db.refresh(user_message)
        raise HTTPException(
            status_code=500, detail=f"Hitilafu kwenye uchakataji wa AI: {str(e)}"
        )

    # 5. Kagua kama kulikuwa na Human Handoff wakati wa Orchestration
    await db.refresh(conversation)
    is_ai_mode = getattr(conversation, "mode", None) == "ai" or getattr(conversation, "current_handler", None) == "ai"
    if not is_ai_mode or conversation.status != "open":
        await db.commit()
        await db.refresh(user_message)
        return SendMessageResponse(
            conversation_id=conversation.id,
            user_message=user_message,
            agent_response=None,
        )

    # 6. Extract Jibu la Agent kwa Usalama
    reply_text = None
    if isinstance(orch_result, dict):
        res_payload = orch_result.get("result")
        if isinstance(res_payload, dict):
            reply_text = res_payload.get("message") or res_payload.get("content")
        elif isinstance(res_payload, str):
            reply_text = res_payload
        
        if not reply_text:
            reply_text = orch_result.get("message") or "Asante, ujumbe wako umepokelewa."

    agent_name = orch_result.get("agent", "MtejaAI Bot") if isinstance(orch_result, dict) else "MtejaAI Bot"

    # 7. Hifadhi Jibu la AI Agent
    agent_message = Message(
        conversation_id=conversation.id,
        sender_type="agent",
        sender_name=agent_name,
        content=reply_text,
    )
    db.add(agent_message)

    await db.commit()
    await db.refresh(user_message)
    await db.refresh(agent_message)

    return SendMessageResponse(
        conversation_id=conversation.id,
        user_message=user_message,
        agent_response=agent_message,
    )


@router.get("/conversations/me", response_model=List[ConversationOut])
async def list_my_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.organization_id == current_user.organization_id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/conversations/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageOut])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()