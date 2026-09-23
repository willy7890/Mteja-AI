from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai.response_engine import AIResponseEngine

router = APIRouter(prefix="/ai", tags=["AI"])


class GenerateReplyRequest(BaseModel):
    message: str
    conversation_history: list[dict] | None = None
    conversation_id: int | None = None


@router.post("/generate-reply")
async def generate_reply(
    payload: GenerateReplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.conversation_id is not None:
        conversation = (await db.execute(select(Conversation).where(
            Conversation.id == payload.conversation_id,
            Conversation.organization_id == current_user.organization_id,
        ))).scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.current_handler != "ai" or conversation.status != "open":
            raise HTTPException(status_code=409, detail="Conversation is owned by a human agent")
    result = await AIResponseEngine.generate_reply(
        user_message=payload.message,
        conversation_history=payload.conversation_history,
    )
    return result