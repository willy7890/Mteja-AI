"""
Core agentic logic: classify an inbound message, then either let the
agent reply or hand off to a human.

Two modes:
- LIVE: if ANTHROPIC_API_KEY is set, calls the real model.
- MOCK: deterministic keyword-based fallback, used automatically if no
  key is set or the API call fails (e.g. no internet on stage). This is
  intentional — a demo should never go blank because of wifi.

The response always reports which mode ran (`mock_mode`), so nothing is
presented as "AI" that wasn't.
"""
import json
import os
import re
import httpx

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are the backend logic for MtejaAI, an agentic customer-response system \
for a small Tanzanian service business (e.g. salon, clinic, shop).

Given an inbound message and the conversation so far, do TWO things and return ONLY strict JSON, \
no prose, no markdown fences:

1. Classify the message as "customer" (a genuine business inquiry) or "non_customer" \
(spam, personal/unrelated chat, wrong number, friend texting).
2. If "customer": decide if you (the agent) can answer directly, or must escalate to a human. \
You may answer directly ONLY for: opening hours, general availability, confirming a booking slot, \
simple FAQs. You must ESCALATE (do not answer) for: discounts/price negotiation, complaints/refunds, \
anything ambiguous or emotionally charged.

Return JSON exactly in this shape:
{"classification": "customer" | "non_customer", "reason": "<5-8 words>", "escalate": true|false, \
"reply": "<agent's reply text if not escalating and is a customer, else empty string>", \
"escalate_reason": "<short reason if escalate true, else empty string>"}"""


def _call_live(history_text: str) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None
    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 400,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": f"Conversation so far:\n{history_text}\n\nRespond with the JSON only."}],
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        text = next((b["text"] for b in data.get("content", []) if b.get("type") == "text"), "")
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        parsed = json.loads(match.group(0))
        parsed["mock_mode"] = False
        return parsed
    except Exception:
        return None


# --- Offline fallback: simple, deterministic, transparent ---

_PRICE_WORDS = ["price", "discount", "cheap", "expensive", "cost", "negotiate", "bei", "punguza"]
_COMPLAINT_WORDS = ["refund", "complain", "terrible", "bad service", "money back", "angry", "disappointed"]
_GREETING_WORDS = ["hour", "open", "close", "available", "book", "appointment", "time", "wapi", "saa"]
_NON_CUSTOMER_HINTS = ["lol", "😂", "bro", "free", "eyy", "vipi", "mzee"]


def _call_mock(latest_text: str) -> dict:
    lower = latest_text.lower()

    if any(w in lower for w in _NON_CUSTOMER_HINTS) and not any(w in lower for w in _GREETING_WORDS):
        return {
            "classification": "non_customer",
            "reason": "informal tone, no business intent",
            "escalate": False,
            "reply": "",
            "escalate_reason": "",
            "mock_mode": True,
        }

    if any(w in lower for w in _COMPLAINT_WORDS):
        return {
            "classification": "customer",
            "reason": "complaint detected",
            "escalate": True,
            "reply": "",
            "escalate_reason": "Complaint — needs human judgment, not automated reply",
            "mock_mode": True,
        }

    if any(w in lower for w in _PRICE_WORDS):
        return {
            "classification": "customer",
            "reason": "price negotiation requested",
            "escalate": True,
            "reply": "",
            "escalate_reason": "Pricing/discount request — agent is not authorized to negotiate",
            "mock_mode": True,
        }

    if any(w in lower for w in _GREETING_WORDS):
        return {
            "classification": "customer",
            "reason": "asking about hours/availability",
            "escalate": False,
            "reply": "Hi! We're open Mon-Sat, 9am-6pm. Happy to book you in — what day works best?",
            "escalate_reason": "",
            "mock_mode": True,
        }

    return {
        "classification": "customer",
        "reason": "general inquiry",
        "escalate": True,
        "reply": "",
        "escalate_reason": "Message doesn't match a known FAQ pattern — routed to a human to be safe",
        "mock_mode": True,
    }


def classify_and_respond(history: list[dict]) -> dict:
    """history: list of {"direction": "in"|"out", "text": str}, oldest first."""
    latest = history[-1]["text"]
    history_text = "\n".join(
        f"{'CUSTOMER' if h['direction'] == 'in' else 'AGENT'}: {h['text']}" for h in history
    )

    live = _call_live(history_text)
    if live is not None:
        return live

    return _call_mock(latest)
