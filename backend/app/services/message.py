from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message
from app.intergration.base_adapter import ChannelAdapter  # au app.integrations.base




class MessageService:
    """
    Channel-agnostic MessageService.
    
    - Haijui Telegram, Email, SMS, WhatsApp...
    - Inazungumza tu na ChannelAdapter kupitia interface.
    - Conversation history inapatikana independent of original channel.
    - Multi-tenant safe (organization_id).
    """

    def __init__(self, adapters: Dict[str, ChannelAdapter]):
        """
        adapters example:
        {
            "telegram": TelegramAdapter(),
            "email": EmailAdapter(),
            "sms": SmsAdapter(),
            "whatsapp": WhatsAppAdapter(),
        }
        """
        self.adapters = adapters

    # =========================================================
    # 1. INBOUND - Record message from any channel
    # =========================================================
    async def handle_incoming(
        self,
        db: AsyncSession,
        organization_id: int,
        channel: str,
        raw_payload: dict,
        customer_id: Optional[int] = None,
    ) -> Message:
        """
        Entry point ya kila ujumbe unaoingia (webhook).
        """
        adapter = self._get_adapter(channel)
        normalized = adapter.normalize_incoming(raw_payload)

        # 1. Find or create Conversation
        conversation = await self._get_or_create_conversation(
            db=db,
            organization_id=organization_id,
            external_participant_id=normalized["from"],
            channel=channel,
            customer_id=customer_id,
        )

        # 2. Create Message (single internal model)
        message = Message(
            conversation_id=conversation.id,
            content=normalized["content"],
            direction="inbound",
            channel=channel,
            status="delivered",  # inbound usually arrives delivered
            external_id=normalized.get("external_id"),
            sender_type="customer",
            sender_name=normalized.get("from", "Customer"),
            channel_metadata=normalized.get("channel_metadata", {}),
            created_at=self._parse_timestamp(normalized.get("timestamp")),
        )

        db.add(message)

        # 3. Update conversation
        conversation.last_customer_message_at = message.created_at
        conversation.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(message)

        # TODO: emit event "message.received" (for AI agents, notifications, etc.)
        return message

    # =========================================================
    # 2. OUTBOUND - Send message (same interface for all channels)
    # =========================================================
    async def send(
        self,
        db: AsyncSession,
        organization_id: int,
        conversation_id: int,
        content: str,
        channel: Optional[str] = None,
        sender_type: str = "agent",
        sender_name: str = "Agent",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Public interface ya kutuma ujumbe.
        Channel-agnostic.
        """
        # 1. Load conversation (multi-tenant safe)
        conversation = await self._get_conversation(
            db, organization_id, conversation_id
        )
        if not conversation:
            raise ValueError("Conversation not found or access denied")

        # 2. Decide channel
        target_channel = channel or conversation.channel
        if not target_channel:
            raise ValueError("No channel available for this conversation")

        adapter = self._get_adapter(target_channel)

        # 3. Create pending message first (single internal model)
        message = Message(
            conversation_id=conversation.id,
            content=content,
            direction="outbound",
            channel=target_channel,
            status="pending",
            sender_type=sender_type,
            sender_name=sender_name,
            channel_metadata=metadata or {},
        )
        db.add(message)
        await db.flush()  # get message.id

        # 4. Send via adapter (transport concern only)
        try:
            to = conversation.external_participant_id
            if not to:
                raise ValueError("Conversation has no external_participant_id")

            result = await adapter.send(
                to=to,
                content=content,
                **(metadata or {})
            )

            # 5. Update status
            if result.get("status") == "sent":
                message.status = "sent"
                message.external_id = result.get("external_id")
                message.sent_at = datetime.utcnow()
            else:
                message.status = "failed"
                message.error_info = {"error": result.get("error", "Unknown error")}

        except Exception as e:
            message.status = "failed"
            message.error_info = {"error": str(e)}

        # 6. Update conversation
        conversation.updated_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(message)
        return message

    # =========================================================
    # 3. HISTORY - Channel independent
    # =========================================================
    async def get_history(
        self,
        db: AsyncSession,
        organization_id: int,
        conversation_id: int,
        limit: int = 50,
        before: Optional[datetime] = None,
    ) -> List[Message]:
        """
        Retrieve conversation history independent of original channel.
        """
        query = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        if before:
            query = query.where(Message.created_at < before)

        result = await db.execute(query)
        messages = result.scalars().all()
        return list(reversed(messages))  # chronological order

    # =========================================================
    # Helpers
    # =========================================================
    def _get_adapter(self, channel: str) -> ChannelAdapter:
        adapter = self.adapters.get(channel)
        if not adapter:
            raise ValueError(f"No adapter registered for channel: {channel}")
        return adapter

    async def _get_conversation(
        self, db: AsyncSession, organization_id: int, conversation_id: int
    ) -> Optional[Conversation]:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_or_create_conversation(
        self,
        db: AsyncSession,
        organization_id: int,
        external_participant_id: str,
        channel: str,
        customer_id: Optional[int] = None,
    ) -> Conversation:
        # Try find existing by participant
        query = select(Conversation).where(
            Conversation.organization_id == organization_id,
            Conversation.external_participant_id == external_participant_id,
        )
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            return conversation

        # Create new
        if not customer_id:
            raise ValueError("customer_id is required when creating new conversation")

        conversation = Conversation(
            organization_id=organization_id,
            customer_id=customer_id,
            external_participant_id=external_participant_id,
            channel=channel,
            status="open",
            mode="ai",
            last_customer_message_at=datetime.now(),
        )
        db.add(conversation)
        await db.flush()
        return conversation

    def _parse_timestamp(self, value: Any) -> datetime:
        if value is None:
            return datetime.now()
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except Exception:
            return datetime.now()
        
        
