# MtejaAI — Demo Backend

A real FastAPI backend for the core agentic loop: message in → classify
(customer vs non-customer) → agent replies directly, or hands off to a
human. Demo it live via Swagger UI at `/docs`.

## Run it (do this before you present, not on stage)

```bash
cd mtejaai_backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open **http://127.0.0.1:8000/docs** — that's your live demo screen.

## Two modes — both work, be honest about which you're in

- **Mock mode (default, no setup needed):** deterministic logic, no
  internet required. Zero risk of failing on stage wifi. Every response
  includes `"mock_mode": true`.
- **Live mode:** set an API key first, then restart the server:

  ```bash
  export ANTHROPIC_API_KEY=your-key-here     # Windows: set ANTHROPIC_API_KEY=...
  uvicorn app.main:app --reload --port 8000
  ```

  Responses will show `"mock_mode": false` and the reply text is
  generated live by the model instead of the fallback rules.

**Recommendation for today:** demo in mock mode. It's deterministic
(same input → same output, no surprises in front of an audience) and
has zero dependency on venue wifi. If you have a key and want to show
the real model, test live mode fully beforehand — don't flip it on for
the first time on stage.

## Demo script — run these in `/docs`, in this order

1. **`POST /contacts`** — create a contact:
   ```json
   { "name": "Amina J.", "channel_id": "+255712345678" }
   ```
   Copy the returned `id`.

2. **`POST /contacts/{id}/messages`** — send an in-scope question:
   ```json
   { "channel": "sms", "text": "Hi, what time do you open tomorrow?" }
   ```
   → Agent replies directly, stage becomes `in_conversation`.

3. **Same endpoint, same contact** — send a pricing question:
   ```json
   { "channel": "sms", "text": "Can you give me a discount, the price is too high?" }
   ```
   → No reply. Stage becomes `escalated`. This is the safety behavior —
   point it out explicitly, it's the actual engineering, not a gap.

4. **`POST /contacts`** a second contact, then **`POST .../messages`**
   with informal chatter (e.g. `"eyy bro free leo lol"`) → classified
   `non_customer`, filtered, never reaches the agent.

5. **`GET /tasks`** — show the handoff task created by step 3. This is
   what a staff member would see and act on.

6. **`GET /dashboard/summary`** — total messages, leads, escalated,
   filtered counts. Also shows `mock_mode` so you can point to it as
   proof of which mode you're running.

## What this deliberately does NOT include (say this out loud, don't dodge it)

- Real SMS/email integration (Africa's Talking, Gmail API) — next
  integration step, not built for this demo
- Persistent database — in-memory, resets on restart. Swap for
  PostgreSQL + SQLAlchemy is already scoped in the project docs
- Multi-turn nuance beyond what's in the conversation history sent per
  request

Say plainly: "this demo proves the core decision logic — classify,
reply, or escalate — actually works. Wiring it to real SMS and a
persistent database is the next phase, already scoped."
