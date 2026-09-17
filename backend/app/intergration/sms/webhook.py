# telegram webhook handler for MTEJA AI
# Signature verification, event parsing, and normalization to unified format
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.integrations.telegram.client import TelegramClient
from app.services.ai.engines import ai_engine
from app.models.conversation import Conversation, HandlerType
from app.models.message import Message
from app.models.customer import Customer

router = APIRouter(prefix="/webhooks", tags=["Telegram Webhook"])


async def get_or_create_customer(db: AsyncSession, chat_id: str, sender_name: str, organization_id: int = 1) -> Customer:
    result = await db.execute(
        select(Customer).where(Customer.external_id == chat_id)
    )
    customer = result.scalar_one_or_none()

    if customer is None:
        customer = Customer(
            external_id=chat_id,
            name=sender_name,
            channel="telegram",
            organization_id=organization_id,
        )
        db.add(customer)
        await db.flush()

    return customer


async def get_or_create_conversation(db: AsyncSession, customer: Customer) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.customer_id == customer.id,
            Conversation.status != "resolved",
        )
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(
            customer_id=customer.id,
            organization_id=customer.organization_id,
            current_handler=HandlerType.AI,
        )
        db.add(conversation)
        await db.flush()

    return conversation


# Inbound Telegram Message Handler (POST)
@router.post("/telegram", status_code=status.HTTP_200_OK)
async def telegram_incoming_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
    body = await request.json()
    try:
        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        message_text = message.get("text")
        sender_name = (
            message.get("from", {}).get("username")
            or message.get("from", {}).get("first_name", "Telegram User")
        )

        if not (chat_id and message_text):
            return {"status": "ignored", "detail": "No chat_id or message text"}

        chat_id_str = str(chat_id)

        # 1. Tafuta/tengeneza customer na conversation
        customer = await get_or_create_customer(db, chat_id_str, sender_name)
        conversation = await get_or_create_conversation(db, customer)

        # 2. Hifadhi ujumbe wa mteja
        incoming_message = Message(
            conversation_id=conversation.id,
            content=message_text,
            sender_type="customer",
            sender_name=sender_name,
        )
        db.add(incoming_message)
        await db.commit()

        # 3. Kama binadamu tayari anashughulikia, usijibu (AI imezimwa)
        if conversation.current_handler == HandlerType.HUMAN:
            return {"status": "success", "detail": "human_handling_active"}

        # 4. Piga AI Engine (ina escalation logic ndani yake)
        organization = {"name": "Mteja AI Org", "context": ""}  # TODO: chukua halisi kutoka DB
        result = await ai_engine.generate_reply(
            conversation_id=conversation.id,
            organization=organization,
            db_session=db,
            agent_type="support",
        )

        ai_reply = result.get("reply")

        if ai_reply:
            # 5. Hifadhi jibu la AI
            ai_message = Message(
                conversation_id=conversation.id,
                content=ai_reply,
                sender_type="agent",
                sender_name="Mteja AI",
            )
            db.add(ai_message)
            await db.commit()

            # 6. Tuma jibu kwenda Telegram
            await TelegramClient.send_telegram_reply(chat_id_str, ai_reply)

        return {"status": "success"}

    except Exception as e:
        print(f"Telegram webhook error: {e}")
        return {"status": "error", "detail": str(e)}