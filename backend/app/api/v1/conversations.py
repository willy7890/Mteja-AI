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
<<<<<<< HEAD
    MessageCreate,
    MessageResponse,
    EscalateRequest,
)
from app.agents.engines import process_chat_message
from app.services.handoff_service import (
    assign_agent,
    escalate_conversation,
    resolve_conversation,
    return_to_ai,
)
=======
    ConversationUpdate,
  HandoffRequest,
  HandoffStatusResponse,
    MessageCreate,
    MessageResponse,
  ReturnToAIRequest,
)
from app.services.agent_service import generate_agent_reply, requires_human_handoff
from app.services.audit_service import notify_agent, record_activity
>>>>>>> origin/develop

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
<<<<<<< HEAD
    """Retrieves message history for a conversation."""
    await _get_owned_conversation(db, id, current_user.organization_id)
    query = (
        select(Message)
        .where(Message.conversation_id == id)
        .order_by(Message.created_at.asc())
=======
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
>>>>>>> origin/develop
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
<<<<<<< HEAD
    """Escalates conversation with explicit reason."""
    conv = await _get_owned_conversation(db, id, current_user.organization_id)
    return await escalate_conversation(
        db, conv, reason=data.reason, triggered_by="agent", agent_id=data.agent_id or current_user.id
    )
=======
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
>>>>>>> origin/develop


@router.post("/{id}/return-to-ai", response_model=ConversationResponse)
async def return_to_ai_endpoint(
    id: int,
  data: HandoffRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
<<<<<<< HEAD
    """Returns conversation control back to AI."""
    conv = await _get_owned_conversation(db, id, current_user.organization_id)
    return await return_to_ai(db, conv, agent_id=current_user.id)


@router.post("/{id}/resolve", response_model=ConversationResponse)
async def resolve(
=======
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
>>>>>>> origin/develop
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/develop
