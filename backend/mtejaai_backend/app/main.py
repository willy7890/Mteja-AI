from fastapi import FastAPI, HTTPException
from app import store, agent
from app.schemas import (
    ContactCreate, Contact, MessageIn, Message, MessageResponse,
    ClassifyResult, Task, DashboardSummary,
)

app = FastAPI(
    title="MtejaAI",
    description=(
        "Agentic customer-response platform demo backend.\n\n"
        "Core loop: a customer message comes in \u2192 gets classified "
        "(customer vs non-customer) \u2192 the agent replies directly for "
        "in-scope questions, or hands off to a human for pricing/complaints.\n\n"
        "Try it: POST /contacts to create a contact, then POST "
        "/contacts/{id}/messages to send them a message and watch the "
        "classification + reply happen live."
    ),
    version="0.1.0-demo",
)


@app.post("/contacts", response_model=Contact, tags=["Contacts"])
def create_contact(payload: ContactCreate):
    """Create (or fetch, if the channel_id already exists) a contact."""
    return store.create_contact(payload.name, payload.channel_id)


@app.get("/contacts", response_model=list[Contact], tags=["Contacts"])
def list_contacts():
    return store.list_contacts()


@app.get("/contacts/{contact_id}", response_model=Contact, tags=["Contacts"])
def get_contact(contact_id: int):
    contact = store.get_contact(contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    return contact


@app.get("/contacts/{contact_id}/timeline", response_model=list[Message], tags=["Contacts"])
def get_timeline(contact_id: int):
    if not store.get_contact(contact_id):
        raise HTTPException(404, "Contact not found")
    return store.get_history(contact_id)


@app.post("/contacts/{contact_id}/messages", response_model=MessageResponse, tags=["Messaging"])
def send_message(contact_id: int, payload: MessageIn):
    """
    The core demo endpoint. Send a message as if it came from the
    customer over SMS/email — this triggers classification, and either
    an agent reply or a human handoff, live.
    """
    contact = store.get_contact(contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")

    inbound = store.add_message(contact_id, payload.channel, "in", payload.text)

    history = [
        {"direction": m["direction"], "text": m["text"]}
        for m in store.get_history(contact_id)
    ]
    result = agent.classify_and_respond(history)

    outbound = None
    if result["classification"] == "non_customer":
        store.set_stage(contact_id, "filtered")
    elif result["escalate"]:
        store.set_stage(contact_id, "escalated")
        store.create_task(contact_id, result.get("escalate_reason") or "Escalated by agent")
    else:
        store.set_stage(contact_id, "in_conversation")
        outbound = store.add_message(contact_id, payload.channel, "out", result.get("reply") or "")

    return MessageResponse(
        contact=store.get_contact(contact_id),
        inbound_message=inbound,
        classification=ClassifyResult(**result),
        outbound_message=outbound,
    )


@app.get("/tasks", response_model=list[Task], tags=["Handoff"])
def list_tasks():
    """Messages the agent escalated to a human — this is the safety valve."""
    return store.list_tasks()


@app.get("/dashboard/summary", response_model=DashboardSummary, tags=["Dashboard"])
def dashboard_summary():
    all_contacts = store.list_contacts()
    return DashboardSummary(
        total_messages=len(store.messages),
        total_leads=sum(1 for c in all_contacts if c["stage"] in ("new", "in_conversation", "escalated")),
        escalated=sum(1 for c in all_contacts if c["stage"] == "escalated"),
        filtered=sum(1 for c in all_contacts if c["stage"] == "filtered"),
        mock_mode=agent.ANTHROPIC_API_KEY is None,
    )


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "mode": "live" if agent.ANTHROPIC_API_KEY else "mock"}
