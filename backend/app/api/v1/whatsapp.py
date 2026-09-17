from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.whatsapp_window_service import WhatsAppWindowService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.get("/window-status/{conversation_id}")
async def get_window_status(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    
    return await WhatsAppWindowService.can_send_freeform_message(db, conversation_id)