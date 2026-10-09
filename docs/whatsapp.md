# WhatsApp Bot — Developer Guide

How the WhatsApp channel works and how to develop on it without fighting Meta or webhook URLs.

| | |
|---|---|
| Business number | +255 628 736 818 (WhatsApp Business account "Mteja AI") |
| Meta app | "khamisi's bot" (in development mode) |
| Webhook endpoint | `GET/POST /api/v1/webhooks/whatsapp/{organization_id}` |
| Code | `backend/app/api/v1/webhooks.py`, `backend/app/intergration/meta_adapter.py` |
| Tests | `backend/tests/test_meta_webhook.py` |

## How a message flows

```
Customer's WhatsApp
   │
   ▼
Meta Cloud API ──POST (signed with X-Hub-Signature-256)──▶ /api/v1/webhooks/whatsapp/{org}
                                                              │ 1. check signature (META_APP_SECRET)
                                                              │ 2. MetaAdapter.normalize_incoming()
                                                              │ 3. find or create Customer by phone
                                                              │ 4. save Conversation + inbound Message
                                                              │ 5. handle_inbound_message(): classify → reply or escalate
                                                              ▼
Customer's WhatsApp ◀── Graph API /messages ◀── MessageService.send() → MetaAdapter.send()
```

Delivery/read receipts arrive at the same URL and are ignored.

## Two ways to work

Meta allows **one webhook URL per app**, so only one machine can receive the real WhatsApp messages at a time. Most of the time you don't need them.

### A. Simulator — everyone, every day (no Meta account needed)

The simulator posts realistic, correctly signed Meta payloads to your local backend, and dry-run mode logs the bot's replies instead of sending them.

```bash
cp backend/.env.example backend/.env      # fill SECRET_KEY; leave the Meta values empty
scripts/whatsapp-dev.sh --dry-run --no-tunnel
```

In another terminal:

```bash
python3 scripts/whatsapp_simulate.py "Mnafungua saa ngapi?"
python3 scripts/whatsapp_simulate.py "Habari" --from 255700000001 --name Juma
python3 scripts/whatsapp_simulate.py --button "Ndiyo"          # quick-reply button tap
python3 scripts/whatsapp_simulate.py --status delivered         # receipt (should be ignored)
tail -f backend/logs/backend.log                                # replies show as [WHATSAPP DRY RUN]
```

If `META_APP_SECRET` is set, the simulator signs with it exactly like Meta does, so signature checks are exercised too.

### B. Real WhatsApp — end-to-end tests on the shared number

Uses a free **ngrok static domain**, so the URL in Meta never changes. Whoever runs this receives the real messages.

One-time setup:

1. Create a free account at [ngrok.com](https://ngrok.com), install ngrok and run `ngrok config add-authtoken <token>`.
2. In the ngrok dashboard → **Domains**, claim your free static domain (e.g. `mteja-dev.ngrok-free.app`).
3. Fill `backend/.env`: `NGROK_DOMAIN`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `META_APP_SECRET`.
4. Run `scripts/whatsapp-dev.sh` and copy the printed **Meta callback** URL.
5. Meta app → **WhatsApp → Configuration → Webhook → Edit**: paste the callback URL and your verify token → **Verify and save** → subscribe to the **`messages`** field.

After that, just run `scripts/whatsapp-dev.sh` whenever you want to test with a real phone. Nothing changes in Meta.

While the app is unpublished, only phone numbers added as test recipients in **WhatsApp → API Setup** can message the bot.

## What `scripts/whatsapp-dev.sh` does

1. Starts Postgres in Docker (`mteja-ai-dev-postgres`) on the port in `DATABASE_URL`, and stops with a clear message if that port is taken.
2. Starts the backend on port 8001 (`BACKEND_PORT=... ` to change) and waits until `/health` responds.
3. Creates organization 1 on a fresh database (the `1` in the webhook URL).
4. Starts ngrok on `NGROK_DOMAIN` and checks that Meta's verification request works through it.
5. Ctrl+C stops the backend and ngrok; Postgres keeps running (`docker stop mteja-ai-dev-postgres`).

Options: `--dry-run`, `--no-tunnel`. Needs bash 5, Docker and `ss` (Linux or WSL).

## Python dependencies

There is no `requirements.txt` yet. This is what the backend currently needs to start:

```bash
python -m venv .venv
.venv/bin/pip install fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg aiosqlite pydantic-settings \
  httpx python-multipart email-validator "python-jose[cryptography]" passlib redis joblib numpy scikit-learn \
  langchain-core langchain-openai python-telegram-bot google-api-python-client google-auth pytest pytest-asyncio
```

Install `python-jose`, not `jose` — the `jose` package on PyPI is unrelated and breaks on Python 3.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Meta: "callback URL or verify token couldn't be validated" | Backend or tunnel not running, wrong URL, or the verify token in Meta differs from `WHATSAPP_VERIFY_TOKEN`. Use the token's **value**, not its name. |
| `403 Invalid webhook signature` | `META_APP_SECRET` doesn't match the Meta app (or the simulator's secret differs from the backend's). |
| Every message returns "owned by a human agent" and the bot never replies | The intent classifier model `backend/models/intent_classifier.pkl` is missing, so confidence falls back to 0.5 (< 0.65) and everything escalates. The model is produced by `app/scripts/auto_retrain.py`. |
| App crashes on start with `OpenAIError: Missing credentials` | `app/services/chat_service.py` needs `OPENAI_API_KEY` at import time. `whatsapp-dev.sh` sets a placeholder if it's missing. |
| `address already in use` for Postgres | Another Postgres uses that port. Change the port in `DATABASE_URL` (e.g. 5440). |
| Replies stop after a day | Temporary access tokens from API Setup expire after 24 hours. Generate a new one or use a system-user token. |

## Security

- Never commit `backend/.env` or paste access tokens/app secrets in chats or screenshots. If one leaks, regenerate it in Meta.
- Always set `META_APP_SECRET` when the backend is reachable from the internet; without it webhook signatures are not checked.
