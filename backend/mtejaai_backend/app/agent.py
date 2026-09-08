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
from app import store

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are the backend logic for MtejaAI, an agentic customer-response system \
for a small Tanzanian service business (e.g. salon, clinic, shop).

Given an inbound message, the conversation so far, and (if relevant) a list of REAL products/services \
from the business's actual catalog, do TWO things and return ONLY strict JSON, no prose, no markdown fences:

1. Classify the message as "customer" (a genuine business inquiry) or "non_customer" \
(spam, personal/unrelated chat, wrong number, friend texting).
2. If "customer": decide if you (the agent) can answer directly, or must escalate to a human. \
You may answer directly ONLY for: opening hours, general availability, confirming a booking slot, \
simple FAQs, and PRODUCT/SERVICE QUESTIONS — when a product list is provided below, you may describe, \
compare, and recommend from ONLY those real items (never invent a product, price, or stock status that \
isn't in the provided list). You must ESCALATE (do not answer) for: discounts/price negotiation, \
complaints/refunds, anything ambiguous or emotionally charged, or a product question when NO product \
list is provided (meaning nothing matched — don't guess).

If a product list is provided and the customer mentioned a budget or asked "what can I get for X", \
recommend the best-fitting real item(s) from the list and mention its actual name and price. If an \
item has an image_url, mention that a photo is available.

Return JSON exactly in this shape:
{"classification": "customer" | "non_customer", "reason": "<5-8 words>", "escalate": true|false, \
"reply": "<agent's reply text if not escalating and is a customer, else empty string>", \
"escalate_reason": "<short reason if escalate true, else empty string>"}"""


def _extract_budget(text: str) -> float | None:
    """Very simple number extraction for a stated budget, e.g. 'I have 20000' or '20k'."""
    text = text.lower().replace(",", "")
    match = re.search(r"(\d+)\s*k\b", text)
    if match:
        return float(match.group(1)) * 1000
    match = re.search(r"\b(\d{4,})\b", text)
    if match:
        return float(match.group(1))
    return None


_PRODUCT_INTENT_WORDS = ["price", "cost", "how much", "product", "service", "package", "buy", "haircut", "budget", "afford", "recommend"]


def _build_product_context(latest_text: str) -> str:
    """Search the real catalog and format matches for the prompt — or return empty if nothing relevant."""
    lower = latest_text.lower()
    if not any(w in lower for w in _PRODUCT_INTENT_WORDS) and _extract_budget(latest_text) is None:
        return ""

    budget = _extract_budget(latest_text)
    keyword = _guess_keyword(latest_text)
    matches = store.search_products(max_price=budget, keyword=keyword)
    if not matches:
        return ""

    lines = [
        f"- {p['name']}: {p['details']} — TZS {p['price']:,.0f} ({'has photo' if p['image_url'] else 'no photo'})"
        for p in matches[:5]
    ]
    return "\n\nREAL PRODUCT CATALOG (only recommend from this list, never invent items):\n" + "\n".join(lines)


def _call_live(history_text: str, product_context: str) -> dict | None:
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
                "messages": [{"role": "user", "content": f"Conversation so far:\n{history_text}{product_context}\n\nRespond with the JSON only."}],
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


def _guess_keyword(text: str) -> str | None:
    """Match the message against real product names so a keyword-specific
    question (e.g. 'hair color') searches by that word, not just budget.
    Prefers the longest matching word — more specific words win over generic ones."""
    lower = text.lower()
    candidates = []
    for p in store.list_products():
        for word in p["name"].lower().split():
            word = word.strip("()")
            if len(word) > 3 and word in lower.split():
                candidates.append(word)
    if not candidates:
        return None
    return max(candidates, key=len)


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

    if any(w in lower for w in _PRICE_WORDS) and _extract_budget(latest_text) is None:
        return {
            "classification": "customer",
            "reason": "price negotiation requested",
            "escalate": True,
            "reply": "",
            "escalate_reason": "Pricing/discount request — agent is not authorized to negotiate",
            "mock_mode": True,
        }

    if any(w in lower for w in _PRODUCT_INTENT_WORDS) or _extract_budget(latest_text) is not None:
        budget = _extract_budget(latest_text)
        keyword = _guess_keyword(latest_text)
        matches = store.search_products(max_price=budget, keyword=keyword)
        if matches:
            # Specific keyword match → recommend the matching item itself (cheapest match).
            # Budget-only, no keyword → recommend the best item that fits the budget (priciest within it).
            best = matches[0] if keyword else matches[-1]
            photo_note = " We can also send you a photo." if best["image_url"] else ""
            reply = (
                f"Based on what you're looking for, I'd recommend our {best['name']} "
                f"— {best['details']} for TZS {best['price']:,.0f}.{photo_note}"
            )
            return {
                "classification": "customer",
                "reason": "product/budget inquiry, matched from catalog",
                "escalate": False,
                "reply": reply,
                "escalate_reason": "",
                "mock_mode": True,
            }
        return {
            "classification": "customer",
            "reason": "product inquiry, no matching item found",
            "escalate": True,
            "reply": "",
            "escalate_reason": "No catalog item matches this request — needs human input",
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
    product_context = _build_product_context(latest)

    live = _call_live(history_text, product_context)
    if live is not None:
        return live

    return _call_mock(latest)
