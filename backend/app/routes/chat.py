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
<<<<<<< HEAD
=======
    # 1. Pata au tengeneza Conversation
>>>>>>> origin/develop
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
<<<<<<< HEAD
            status="open",
            current_handler="ai",
=======
            channel=data.channel,
            mode="ai",
            status="open"
>>>>>>> origin/develop
        )
        db.add(conversation)
        await db.flush()

<<<<<<< HEAD
=======
    # 2. Hifadhi Message ya Mteja
>>>>>>> origin/develop
    user_message = Message(
        conversation_id=conversation.id,
        sender_type="customer",
        content=data.content,
    )
    db.add(user_message)
    await db.flush()

<<<<<<< HEAD
    # Only invoke AI orchestrator if the conversation is handled by AI
    if conversation.current_handler == "ai":
=======
    # 3. Kama haiko tayari kwa AI au imefungwa, Hifadhi na Rudisha bila jibu la Agent
    if conversation.mode != "ai" or conversation.status != "open":
        await db.commit()
        await db.refresh(user_message)
        return SendMessageResponse(
            conversation_id=conversation.id,
            user_message=user_message,
            agent_response=None,
        )

    # 4. Tekeleza Orchestrator
    try:
>>>>>>> origin/develop
        result = await orchestrator.run(
            db=db,
            organization_id=current_user.organization_id,
            conversation_id=str(conversation.id),
            message=data.content,
        )
<<<<<<< HEAD

        reply_text = result.get("result", {}).get("message") or str(result.get("result"))
        agent_message = Message(
            conversation_id=conversation.id,
            sender_type="ai",
            sender_name=result.get("agent", "system"),
            content=reply_text,
        )
        db.add(agent_message)
    else:
        agent_message = None
=======
    except Exception as e:
        # Ikitokea error kwenye AI, hifadhi angalau message ya user
        await db.commit()
        await db.refresh(user_message)
        raise HTTPException(
            status_code=500, detail=f"Orchestration processing error: {str(e)}"
        )

    # 5. Refresh Conversation kuangalia kama Human Takeover ilitokea
    await db.refresh(conversation)
    if conversation.mode != "ai" or conversation.status != "open":
        await db.commit()
        await db.refresh(user_message)
        return SendMessageResponse(
            conversation_id=conversation.id,
            user_message=user_message,
            agent_response=None,
        )

    # 6. Extract Reply Text kwa Ulinzi (Safe Parsing)
    reply_text = None
    if isinstance(result, dict):
        res_payload = result.get("result")
        if isinstance(res_payload, dict):
            reply_text = res_payload.get("message") or res_payload.get("content")
        elif isinstance(res_payload, str):
            reply_text = res_payload
        
        if not reply_text:
            reply_text = result.get("message") or "Asante kwa ujumbe wako."

    # 7. Hifadhi Jibu la AI Agent
    agent_message = Message(
        conversation_id=conversation.id,
        sender_type="agent",
        sender_name=result.get("agent", "MtejaAI Bot") if isinstance(result, dict) else "MtejaAI Bot",
        content=reply_text,
    )
    db.add(agent_message)
>>>>>>> origin/develop

    await db.commit()
    await db.refresh(user_message)
    if agent_message:
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
<<<<<<< HEAD
=======
    # Thititisha muundo wa conversation kwanza
>>>>>>> origin/develop
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