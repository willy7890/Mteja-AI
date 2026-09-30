from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.ai_schemas import (
    GenerateReplyRequest,
    GenerateReplyResponse,
    TestPromptRequest,
    TestPromptResponse,
)
from app.services.ai.engine import ai_engine
from app.repositories.organization_repository import get_organization
from app.repositories.conversation_repository import get_recent_messages  # used inside engine

router = APIRouter(prefix="/api/v1/ai", tags=["AI Engine"])


@router.post(
    "/generate-reply",
    response_model=GenerateReplyResponse,
    summary="Generate an AI reply for a given conversation",
)
async def generate_reply(
    payload: GenerateReplyRequest,
    db: AsyncSession = Depends(get_db),
):
    organization = await get_organization(db, payload.organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    result = await ai_engine.generate_reply(
        conversation_id=payload.conversation_id,
        organization=organization,
        db_session=db,
        agent_type=payload.agent_type,
    )

    return GenerateReplyResponse(**result)


@router.post(
    "/test-prompt",
    response_model=TestPromptResponse,
    summary="Test a system prompt against sample messages (no DB involved)",
)
async def test_prompt(payload: TestPromptRequest):
    messages = [
        {"role": "user", "content": payload.system_prompt}
    ] + [msg.model_dump() for msg in payload.sample_messages]

    try:
        result = await ai_engine.provider.generate(
            messages, max_tokens=payload.max_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")

    return TestPromptResponse(**result)