from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai.response_engine import AIResponseEngine

router = APIRouter(prefix="/ai", tags=["AI"])


class GenerateReplyRequest(BaseModel):
    message: str
    conversation_history: list[dict] | None = None


@router.post("/generate-reply")
async def generate_reply(payload: GenerateReplyRequest):
    result = await AIResponseEngine.generate_reply(
        user_message=payload.message,
        conversation_history=payload.conversation_history,
    )
    return result