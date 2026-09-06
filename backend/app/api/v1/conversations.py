from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation
from app.models.customer import Customer
from app.models.message import Message
from app.models.user import User
from app.schemas.conversation import (
    AssignRequest,
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse,
)
from app.services.agent_service import generate_agent_reply

router = APIRouter(prefix="/conversations", tags=["Unified Inbox"])


@router.post(
    "/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  customer_result = await db.execute(
      select(Customer).where(
          Customer.id == data.customer_id,
          Customer.organization_id == current_user.organization_id,
      )
  )
  if customer_result.scalar_one_or_none() is None:
    raise HTTPException(status_code=404, detail="Customer not found")

  conversation = Conversation(
      organization_id=current_user.organization_id,
      customer_id=data.customer_id,
      channel=data.channel,
      status=data.status,
  )
  db.add(conversation)
  await db.commit()
  await db.refresh(conversation)
  return conversation


# 1. GET /api/v1/conversations (Multi-tenant + Filtering)
@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  query = select(Conversation).where(
      Conversation.organization_id == current_user.organization_id
  )

  if channel:
    query = query.where(Conversation.channel == channel)
  if status:
    query = query.where(Conversation.status == status)

  result = await db.execute(query.order_by(Conversation.created_at.desc()))
  return result.scalars().all()


# 2. GET /api/v1/conversations/{id}
@router.get("/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  query = select(Conversation).where(
      Conversation.id == id,
      Conversation.organization_id == current_user.organization_id,
  )
  result = await db.execute(query)
  conv = result.scalar_one_or_none()
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")
  return conv


# 3. POST /api/v1/conversations/{id}/messages
@router.post(
    "/{id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  conv_res = await db.execute(
      select(Conversation).where(
          Conversation.id == id,
          Conversation.organization_id == current_user.organization_id,
      )
  )
  conv = conv_res.scalar_one_or_none()
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")

  # 1. Save the incoming message
  message = Message(
      conversation_id=id, content=data.content, sender_type=data.sender_type
  )
  db.add(message)
  await db.commit()
  await db.refresh(message)

  # 2. Automatically trigger AI RAG agent response if in AI mode and message is from customer
  if conv.mode == "ai" and data.sender_type == "customer":
    ai_response_text = await generate_agent_reply(data.content)

    ai_message = Message(
        conversation_id=id, content=ai_response_text, sender_type="ai"
    )
    db.add(ai_message)
    await db.commit()

  return message


@router.patch("/{id}", response_model=ConversationResponse)
async def update_conversation(
    id: int,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  conv_res = await db.execute(
      select(Conversation).where(
          Conversation.id == id,
          Conversation.organization_id == current_user.organization_id,
      )
  )
  conv = conv_res.scalar_one_or_none()
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")

  if data.status:
    conv.status = data.status
  if data.assigned_to is not None:
    conv.assigned_to = data.assigned_to

  await db.commit()
  await db.refresh(conv)
  return conv


@router.post("/{id}/takeover", response_model=ConversationResponse)
async def takeover_conversation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  conv_res = await db.execute(
      select(Conversation).where(
          Conversation.id == id,
          Conversation.organization_id == current_user.organization_id,
      )
  )
  conv = conv_res.scalar_one_or_none()
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")

  conv.mode = "human"
  conv.assigned_to = current_user.id
  await db.commit()
  await db.refresh(conv)
  return conv


@router.post("/{id}/assign", response_model=ConversationResponse)
async def assign_conversation(
    id: int,
    data: AssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  conv_res = await db.execute(
      select(Conversation).where(
          Conversation.id == id,
          Conversation.organization_id == current_user.organization_id,
      )
  )
  conv = conv_res.scalar_one_or_none()
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")

  conv.assigned_to = data.agent_id
  await db.commit()
  await db.refresh(conv)
  return conv