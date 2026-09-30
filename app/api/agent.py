from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.agent_service import handle_inbound_message
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["agent"])

class TestMessageRequest(BaseModel):
    organization_id: int
    contact_id: str
    message: str

@router.post("/test-classifier")
async def test_classifier(req: TestMessageRequest, db: AsyncSession = Depends(get_db)):
    result = await handle_inbound_message(
        db=db,
        organization_id=req.organization_id,
        contact_id=req.contact_id,
        message_text=req.message
    )
    return result