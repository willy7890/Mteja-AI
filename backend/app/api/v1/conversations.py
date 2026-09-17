from datetime import datetime, timezone
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
  HandoffRequest,
  HandoffStatusResponse,
    MessageCreate,
    MessageResponse,
  ReturnToAIRequest,
)
from app.services.agent_service import generate_agent_reply, requires_human_handoff
from app.services.audit_service import notify_agent, record_activity

router = APIRouter(tags=["Unified Inbox"])


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
      conversation_id=id,
      content=data.content,
      sender_type=data.sender_type,
      sender_name=(
        data.sender_name
        or (
          current_user.full_name
          if data.sender_type in {"agent", "human"}
          else (conv.customer.name if data.sender_type == "customer" else data.sender_type)
        )
      ),
  )
  db.add(message)
  await db.commit()
  await db.refresh(message)

  # 2. Automatically trigger AI RAG agent response if in AI mode and message is from customer
  if conv.mode == "ai" and data.sender_type == "customer":
    if requires_human_handoff(data.content):
      previous_mode = conv.mode
      conv.mode = "human"
      metadata = dict(conv.metadata_ or {})
      metadata["handoff"] = {
        "reason": "AI policy or confidence threshold",
        "previous_mode": previous_mode,
        "trigger": "ai",
        "handed_off_at": datetime.now(timezone.utc).isoformat(),
      }
      conv.metadata_ = metadata
      await record_activity(
        db,
        organization_id=current_user.organization_id,
        user_id=None,
        conversation_id=conv.id,
        actor="ai",
        action_type="handoff",
        description="AI escalated conversation to a human agent",
        details={"previous_mode": previous_mode},
      )
      await db.commit()
      await db.refresh(message)
      return message

    ai_response_text = await generate_agent_reply(data.content)

    # Handoff may happen while generation is in flight; re-check ownership
    # before writing any AI reply.
    await db.refresh(conv)
    if conv.mode != "ai" or conv.status != "open":
      return message

    ai_message = Message(
      conversation_id=id,
      content=ai_response_text,
      sender_type="ai",
      sender_name="MtejaAI",
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

  if data.assigned_to is not None:
    agent_result = await db.execute(select(User).where(
        User.id == data.assigned_to,
        User.organization_id == current_user.organization_id,
        User.role.in_(["agent", "admin", "owner"]),
    ))
    if agent_result.scalar_one_or_none() is None:
      raise HTTPException(status_code=404, detail="Assigned agent not found")
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
  data: HandoffRequest | None = None,
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

  if conv.status != "open":
    raise HTTPException(status_code=409, detail="Conversation is not active")
  assigned_agent_id = data.agent_id if data and data.agent_id is not None else current_user.id
  agent_result = await db.execute(select(User).where(
      User.id == assigned_agent_id,
      User.organization_id == current_user.organization_id,
      User.role.in_( ["agent", "admin", "owner"]),
  ))
  if agent_result.scalar_one_or_none() is None:
    raise HTTPException(status_code=404, detail="Assigned agent not found")
  previous_mode = conv.mode
  conv.mode = "human"
  conv.assigned_to = assigned_agent_id
  reason = data.reason if data else "Manual takeover"
  metadata = dict(conv.metadata_ or {})
  metadata["handoff"] = {
      "reason": reason,
      "previous_mode": previous_mode,
      "handed_off_at": datetime.now(timezone.utc).isoformat(),
  }
  conv.metadata_ = metadata
  await record_activity(
      db,
      organization_id=current_user.organization_id,
      user_id=current_user.id,
      conversation_id=conv.id,
      actor="human",
      action_type="handoff",
      description=reason,
      details={"previous_mode": previous_mode, "assigned_to": conv.assigned_to},
  )
  await db.commit()
  await db.refresh(conv)
  await notify_agent({
      "event": "conversation_handoff",
      "conversation_id": conv.id,
      "organization_id": current_user.organization_id,
      "assigned_to": conv.assigned_to,
      "reason": reason,
  })
  return conv


@router.post("/{id}/handoff", response_model=ConversationResponse)
async def handoff_conversation(
    id: int,
    data: HandoffRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  return await takeover_conversation(id, data, current_user, db)


@router.get("/{id}/handoff-status", response_model=HandoffStatusResponse)
async def handoff_status(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  result = await db.execute(select(Conversation).where(
      Conversation.id == id,
      Conversation.organization_id == current_user.organization_id,
  ))
  conv = result.scalar_one_or_none()
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")
  handoff = (conv.metadata_ or {}).get("handoff", {})
  return HandoffStatusResponse(
      conversation_id=conv.id,
      mode=conv.mode,
      status=conv.status,
      assigned_to=conv.assigned_to,
      handoff_reason=handoff.get("reason"),
      handed_off_at=handoff.get("handed_off_at"),
  )


@router.post("/{id}/return-to-ai", response_model=ConversationResponse)
async def return_to_ai(
    id: int,
    data: ReturnToAIRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
  result = await db.execute(select(Conversation).where(
      Conversation.id == id,
      Conversation.organization_id == current_user.organization_id,
  ))
  conv = result.scalar_one_or_none()
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")
  previous_mode = conv.mode
  conv.mode = "ai"
  metadata = dict(conv.metadata_ or {})
  metadata["handoff"] = {"reason": data.reason, "previous_mode": previous_mode}
  conv.metadata_ = metadata
  await record_activity(
      db,
      organization_id=current_user.organization_id,
      user_id=current_user.id,
      conversation_id=conv.id,
      actor="human",
      action_type="handoff_return",
      description=data.reason,
      details={"previous_mode": previous_mode},
  )
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

  agent_result = await db.execute(select(User).where(
      User.id == data.agent_id,
      User.organization_id == current_user.organization_id,
      User.role.in_(["agent", "admin", "owner"]),
  ))
  if agent_result.scalar_one_or_none() is None:
    raise HTTPException(status_code=404, detail="Assigned agent not found")
  conv.assigned_to = data.agent_id
  await db.commit()
  await db.refresh(conv)
  return conv