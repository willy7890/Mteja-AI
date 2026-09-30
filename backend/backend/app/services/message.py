from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.intergration.base_adapter import ChannelAdapter
from app.intergration.telegram.adapter import TelegramAdapter
from app.models.channel import ChannelIntegration
from app.models.conversation import Conversation
from app.models.message import Message


class MessageService:
    """
    Handles incoming and outgoing messages.

    Supports organization-aware channel integrations,
    including Telegram bots for different organizations.
    """

    def __init__(self, adapters: Dict[str, ChannelAdapter]):
        self.adapters = adapters

    # =========================================================
    # INCOMING MESSAGE
    # =========================================================

    async def handle_incoming(
        self,
        db: AsyncSession,
        organization_id: int,
        channel: str,
        raw_payload: dict,
        customer_id: Optional[int] = None,
    ) -> Message:

        adapter = await self._get_adapter_for_organization(
            db=db,
            organization_id=organization_id,
            channel=channel,
        )

        normalized = adapter.normalize_incoming(raw_payload)

        external_participant_id = normalized.get("from")

        if not external_participant_id:
            raise ValueError(
                "Incoming message has no external participant ID"
            )

        conversation = await self._get_or_create_conversation(
            db=db,
            organization_id=organization_id,
            external_participant_id=external_participant_id,
            channel=channel,
            customer_id=customer_id,
        )

        content = normalized.get("content", "")

        if not content or not str(content).strip():
            raise ValueError(
                "Incoming message content cannot be empty"
            )

        message = Message(
            conversation_id=conversation.id,
            content=str(content).strip(),
            sender_type="customer",
            sender_name=normalized.get(
                "sender_name",
                normalized.get("from", "Customer"),
            ),
            direction="inbound",
            channel=channel,
            created_at=self._parse_timestamp(
                normalized.get("timestamp")
            ),
        )

        db.add(message)

        conversation.last_customer_message_at = (
            message.created_at
        )

        conversation.updated_at = self._utc_now()

        await db.commit()
        await db.refresh(message)

        return message

    # =========================================================
    # OUTGOING MESSAGE
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

        if not content or not content.strip():
            raise ValueError(
                "Message content cannot be empty"
            )

        conversation = await self._get_conversation(
            db=db,
            organization_id=organization_id,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found or access denied"
            )

        target_channel = (
            channel or conversation.channel
        )

        if not target_channel:
            raise ValueError(
                "No channel available for this conversation"
            )

        adapter = await self._get_adapter_for_organization(
            db=db,
            organization_id=organization_id,
            channel=target_channel,
        )

        message = Message(
            conversation_id=conversation.id,
            content=content.strip(),
            sender_type=sender_type,
            sender_name=sender_name,
            direction="outbound",
            channel=target_channel,
            created_at=self._utc_now(),
        )

        db.add(message)

        await db.flush()

        try:
            recipient = conversation.external_participant_id

            if not recipient:
                raise ValueError(
                    "Conversation has no external_participant_id"
                )

            result = await adapter.send(
                to=recipient,
                content=content.strip(),
                **(metadata or {}),
            )

            if not result:
                raise ValueError(
                    "Channel adapter returned an empty response"
                )

        except Exception:
            await db.rollback()
            raise

        conversation.updated_at = self._utc_now()

        await db.commit()
        await db.refresh(message)

        return message

    # =========================================================
    # GET MESSAGE HISTORY
    # =========================================================

    async def get_history(
        self,
        db: AsyncSession,
        organization_id: int,
        conversation_id: int,
        limit: int = 50,
        before: Optional[datetime] = None,
    ) -> List[Message]:

        conversation = await self._get_conversation(
            db=db,
            organization_id=organization_id,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found or access denied"
            )

        if limit < 1:
            limit = 50

        if limit > 200:
            limit = 200

        query = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(
                Message.created_at.desc()
            )
            .limit(limit)
        )

        if before:
            query = query.where(
                Message.created_at < before
            )

        result = await db.execute(query)

        messages = result.scalars().all()

        return list(reversed(messages))

    # =========================================================
    # ORGANIZATION-AWARE ADAPTER
    # =========================================================

    async def _get_adapter_for_organization(
        self,
        db: AsyncSession,
        organization_id: int,
        channel: str,
    ) -> ChannelAdapter:

        if channel == "telegram":

            result = await db.execute(
                select(ChannelIntegration)
                .where(
                    ChannelIntegration.organization_id
                    == organization_id,
                    ChannelIntegration.channel_name
                    == "telegram",
                    ChannelIntegration.is_active.is_(True),
                )
                .order_by(
                    ChannelIntegration.id.desc()
                )
            )

            integration = result.scalars().first()

            if not integration:
                raise ValueError(
                    "Active Telegram integration "
                    "not found for this organization"
                )

            if not integration.credentials_json:
                raise ValueError(
                    "Telegram credentials are missing"
                )

            try:
                credentials = json.loads(
                    integration.credentials_json
                )

            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "Invalid Telegram integration credentials"
                ) from exc

            if not isinstance(credentials, dict):
                raise ValueError(
                    "Invalid Telegram credentials format"
                )

            bot_token = credentials.get("bot_token")

            if not bot_token:
                raise ValueError(
                    "Telegram bot token is missing"
                )

            return TelegramAdapter(
                bot_token=str(bot_token).strip()
            )

        return self._get_adapter(channel)

    # =========================================================
    # DEFAULT ADAPTER
    # =========================================================

    def _get_adapter(
        self,
        channel: str,
    ) -> ChannelAdapter:

        adapter = self.adapters.get(channel)

        if not adapter:
            raise ValueError(
                f"No adapter registered for channel: {channel}"
            )

        return adapter

    # =========================================================
    # GET CONVERSATION
    # =========================================================

    async def _get_conversation(
        self,
        db: AsyncSession,
        organization_id: int,
        conversation_id: int,
    ) -> Optional[Conversation]:

        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id,
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET OR CREATE CONVERSATION
    # =========================================================

    async def _get_or_create_conversation(
        self,
        db: AsyncSession,
        organization_id: int,
        external_participant_id: str,
        channel: str,
        customer_id: Optional[int] = None,
    ) -> Conversation:

        query = select(Conversation).where(
            Conversation.organization_id == organization_id,
            Conversation.channel == channel,
            Conversation.external_participant_id
            == external_participant_id,
        )

        result = await db.execute(query)

        conversation = result.scalar_one_or_none()

        if conversation:
            return conversation

        if not customer_id:
            raise ValueError(
                "customer_id is required "
                "when creating a new conversation"
            )

        conversation = Conversation(
            organization_id=organization_id,
            customer_id=customer_id,
            external_participant_id=(
                external_participant_id
            ),
            channel=channel,
            status="open",
            current_handler="ai",
            last_customer_message_at=self._utc_now(),
            updated_at=self._utc_now(),
        )

        db.add(conversation)

        await db.flush()

        return conversation

    # =========================================================
    # TIMESTAMP PARSER
    # =========================================================

    def _parse_timestamp(
        self,
        value: Any,
    ) -> datetime:

        if value is None:
            return self._utc_now()

        if isinstance(value, datetime):

            if value.tzinfo is None:
                return value.replace(
                    tzinfo=timezone.utc
                )

            return value

        try:
            parsed_datetime = datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    "+00:00",
                )
            )

            if parsed_datetime.tzinfo is None:
                parsed_datetime = parsed_datetime.replace(
                    tzinfo=timezone.utc
                )

            return parsed_datetime

        except (TypeError, ValueError):
            return self._utc_now()

    # =========================================================
    # UTC DATETIME HELPER
    # =========================================================

    def _utc_now(self) -> datetime:
        return datetime.now(timezone.utc)