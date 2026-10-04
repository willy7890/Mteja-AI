"""Tests for the Meta (WhatsApp) webhook: verification, signatures and inbound flow.

Run from the backend directory:  python -m pytest tests/test_meta_webhook.py
"""

import hashlib
import hmac
import json
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1 import webhooks
from app.core.config import settings
from app.core.database import Base, get_db
from app.intergration.meta_adapter import MetaAdapter
from app.models.conversation import Conversation
from app.models.customer import Customer
from app.models.escalation_log import EscalationLog
from app.models.message import Message

ORG_ID = 1
VERIFY_TOKEN = "test-verify-token"
APP_SECRET = "test-app-secret"
CUSTOMER_PHONE = "255712345678"


def whatsapp_text_payload(text: str, phone: str = CUSTOMER_PHONE) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WABA_ID",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "255700000000", "phone_number_id": "PHONE_ID"},
                    "contacts": [{"profile": {"name": "Asha"}, "wa_id": phone}],
                    "messages": [{
                        "from": phone,
                        "id": "wamid.TEST1",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": text},
                    }],
                },
            }],
        }],
    }


def whatsapp_status_payload() -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WABA_ID",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "255700000000", "phone_number_id": "PHONE_ID"},
                    "statuses": [{"id": "wamid.OUT1", "status": "delivered", "recipient_id": CUSTOMER_PHONE}],
                },
            }],
        }],
    }


def sign(body: bytes) -> str:
    return "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    tables = [
        Customer.__table__,
        Conversation.__table__,
        Message.__table__,
        EscalationLog.__table__,
    ]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=tables)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest.fixture
def sent_messages(monkeypatch):
    """Capture outbound Graph API sends instead of calling Meta."""
    sent = []

    async def fake_send(self, to, content, **kwargs):
        sent.append({"to": to, "content": content})
        return {"external_id": "wamid.OUT1", "status": "sent", "error": None}

    monkeypatch.setattr(MetaAdapter, "send", fake_send)
    return sent


@pytest.fixture
def agent_result(monkeypatch):
    """Replace the AI agent with a controllable stub."""
    result = {"status": "AI_REPLIED", "reply": "Habari Asha! Tunafungua saa 2 asubuhi."}

    async def fake_handle_inbound_message(**kwargs):
        return dict(result)

    monkeypatch.setattr(webhooks, "handle_inbound_message", fake_handle_inbound_message)
    return result


@pytest_asyncio.fixture
async def client(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_VERIFY_TOKEN", VERIFY_TOKEN)
    monkeypatch.setattr(settings, "META_APP_SECRET", APP_SECRET)

    app = FastAPI()
    app.include_router(webhooks.router, prefix="/api/v1")

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http


async def post_signed(client: AsyncClient, payload: dict):
    body = json.dumps(payload).encode()
    return await client.post(
        f"/api/v1/webhooks/whatsapp/{ORG_ID}",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sign(body)},
    )


# ---------------------------------------------------------------
# Verification handshake (GET)
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_verification_returns_challenge(client):
    response = await client.get(
        f"/api/v1/webhooks/whatsapp/{ORG_ID}",
        params={"hub.mode": "subscribe", "hub.verify_token": VERIFY_TOKEN, "hub.challenge": "12345"},
    )
    assert response.status_code == 200
    assert response.text == "12345"


@pytest.mark.asyncio
async def test_verification_rejects_wrong_token(client):
    response = await client.get(
        f"/api/v1/webhooks/whatsapp/{ORG_ID}",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "12345"},
    )
    assert response.status_code == 403


# ---------------------------------------------------------------
# Signature check (POST)
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_rejects_invalid_signature(client, sent_messages, agent_result):
    response = await client.post(
        f"/api/v1/webhooks/whatsapp/{ORG_ID}",
        content=json.dumps(whatsapp_text_payload("Hi")).encode(),
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": "sha256=bad"},
    )
    assert response.status_code == 403
    assert sent_messages == []


@pytest.mark.asyncio
async def test_rejects_missing_signature(client, sent_messages, agent_result):
    response = await client.post(f"/api/v1/webhooks/whatsapp/{ORG_ID}", json=whatsapp_text_payload("Hi"))
    assert response.status_code == 403
    assert sent_messages == []


# ---------------------------------------------------------------
# Inbound messages
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_new_sender_gets_customer_and_ai_reply(client, session_factory, sent_messages, agent_result):
    response = await post_signed(client, whatsapp_text_payload("Mnafungua saa ngapi?"))

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["reply_id"] is not None

    assert sent_messages == [{"to": CUSTOMER_PHONE, "content": agent_result["reply"]}]

    async with session_factory() as session:
        customer = (await session.execute(select(Customer))).scalar_one()
        assert customer.phone == CUSTOMER_PHONE
        assert customer.name == "Asha"
        assert customer.organization_id == ORG_ID

        conversation = (await session.execute(select(Conversation))).scalar_one()
        assert conversation.channel == "whatsapp"
        assert conversation.external_participant_id == CUSTOMER_PHONE

        messages = (await session.execute(select(Message).order_by(Message.id))).scalars().all()
        assert [(m.direction, m.content) for m in messages] == [
            ("inbound", "Mnafungua saa ngapi?"),
            ("outbound", agent_result["reply"]),
        ]


@pytest.mark.asyncio
async def test_returning_sender_reuses_customer_and_conversation(client, session_factory, sent_messages, agent_result):
    await post_signed(client, whatsapp_text_payload("Habari"))
    await post_signed(client, whatsapp_text_payload("Bei ya bidhaa?"))

    async with session_factory() as session:
        assert len((await session.execute(select(Customer))).scalars().all()) == 1
        assert len((await session.execute(select(Conversation))).scalars().all()) == 1
        assert len((await session.execute(select(Message))).scalars().all()) == 4
    assert len(sent_messages) == 2


@pytest.mark.asyncio
async def test_escalated_message_is_not_auto_replied(client, session_factory, sent_messages, agent_result):
    agent_result["status"] = "ESCALATED"

    response = await post_signed(client, whatsapp_text_payload("Nataka refund yangu!"))

    assert response.status_code == 200
    assert sent_messages == []
    async with session_factory() as session:
        messages = (await session.execute(select(Message))).scalars().all()
        assert [m.direction for m in messages] == ["inbound"]


@pytest.mark.asyncio
async def test_status_update_is_ignored(client, session_factory, sent_messages, agent_result):
    response = await post_signed(client, whatsapp_status_payload())

    assert response.status_code == 200
    assert response.json()["message"] == "Ignored event"
    assert sent_messages == []
    async with session_factory() as session:
        assert (await session.execute(select(Message))).scalars().all() == []
