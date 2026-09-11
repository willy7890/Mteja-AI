# # backend/app/routes/messaging_window.py

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.database import get_db
# from app.core.security import get_current_user  # adjust to your actual auth dependency
# from app.services.conversation_service import get_conversation_or_404
# from app.services.messaging_window import refresh_window_status

# router = APIRouter()


# @router.get("/conversations/{conversation_id}/messaging-window")
# async def get_messaging_window_status(
#     conversation_id: int,
#     current_user=Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     conversation = await get_conversation_or_404(
#         db, conversation_id, current_user.organization_id
#     )

#     status = await refresh_window_status(db, conversation)

#     return {
#         "conversation_id": conversation.id,
#         "messaging_window_status": status,
#         "last_customer_message_at": conversation.last_customer_message_at,
#     }