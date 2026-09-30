from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.conversation import Conversation
from app.models.message import Message  

class WhatsAppWindowService:
    WINDOW_HOURS = 24

    @staticmethod
    def is_window_open(last_customer_message_at: datetime | None) -> bool:
       
        if not last_customer_message_at:
            return False

        now = datetime.now(timezone.utc)
        
        if last_customer_message_at.tzinfo is None:
            last_customer_message_at = last_customer_message_at.replace(tzinfo=timezone.utc)

        return now <= (last_customer_message_at + timedelta(hours=WhatsAppWindowService.WINDOW_HOURS))

    @staticmethod
    async def update_customer_message_time(
        db: AsyncSession,
        conversation_id: int,
        message_time: datetime | None = None
    ) -> Conversation:
    
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation.last_customer_message_at = message_time or datetime.now(timezone.utc)
        conversation.whatsapp_window_open = True

        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def can_send_freeform_message(
        db: AsyncSession,
        conversation_id: int
    ) -> dict:
       
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        is_open = WhatsAppWindowService.is_window_open(
            conversation.last_customer_message_at
        )

        conversation.whatsapp_window_open = is_open
        await db.commit()

        remaining_seconds = None
        if is_open and conversation.last_customer_message_at:
            expires_at = conversation.last_customer_message_at + timedelta(
                hours=WhatsAppWindowService.WINDOW_HOURS
            )
            remaining_seconds = int((expires_at - datetime.now(timezone.utc)).total_seconds())

        return {
            "conversation_id": conversation_id,
            "window_open": is_open,
            "last_customer_message_at": conversation.last_customer_message_at,
            "remaining_seconds": remaining_seconds,
            "can_send_freeform": is_open,
            "requires_template": not is_open,
        }

    @staticmethod
    async def enforce_window(
        db: AsyncSession,
        conversation_id: int,
        is_template: bool = False
    ) -> None:
      
        status_info = await WhatsAppWindowService.can_send_freeform_message(
            db, conversation_id
        )

        if not status_info["window_open"] and not is_template:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "24-hour messaging window has expired. You can only send approved WhatsApp templates.",
                    "window_open": False,
                    "requires_template": True,
                    "last_customer_message_at": status_info["last_customer_message_at"],
                }
            )