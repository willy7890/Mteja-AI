#!/usr/bin/env python3
"""Send a fake (but correctly signed) WhatsApp webhook to a local MtejaAI backend.

Lets you develop the WhatsApp bot without Meta, a tunnel or a real phone.
Pair it with WHATSAPP_DRY_RUN=true so the bot's replies are logged, not sent.

Examples:
    python scripts/whatsapp_simulate.py "Mnafungua saa ngapi?"
    python scripts/whatsapp_simulate.py "Habari" --from 255700000001 --name Juma
    python scripts/whatsapp_simulate.py --button "Ndiyo"
    python scripts/whatsapp_simulate.py --status delivered

Uses only the Python standard library.
"""

import argparse
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[1] / "backend" / ".env"


def read_env(path: Path) -> dict:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def build_payload(args) -> dict:
    value = {
        "messaging_product": "whatsapp",
        "metadata": {"display_phone_number": "255000000000", "phone_number_id": "SIMULATED_PHONE_ID"},
    }

    if args.status:
        value["statuses"] = [{
            "id": f"wamid.SIM{uuid.uuid4().hex[:16]}",
            "status": args.status,
            "timestamp": str(int(time.time())),
            "recipient_id": args.sender,
        }]
    else:
        message = {
            "from": args.sender,
            "id": f"wamid.SIM{uuid.uuid4().hex[:16]}",
            "timestamp": str(int(time.time())),
        }
        if args.button:
            message["type"] = "interactive"
            message["interactive"] = {
                "type": "button_reply",
                "button_reply": {"id": "sim-button", "title": args.button},
            }
        else:
            message["type"] = "text"
            message["text"] = {"body": args.text}
        value["contacts"] = [{"profile": {"name": args.name}, "wa_id": args.sender}]
        value["messages"] = [message]

    return {
        "object": "whatsapp_business_account",
        "entry": [{"id": "SIMULATED_WABA_ID", "changes": [{"field": "messages", "value": value}]}],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate an inbound WhatsApp webhook from Meta.")
    parser.add_argument("text", nargs="?", default="Habari, mnafungua saa ngapi?", help="message text")
    parser.add_argument("--from", dest="sender", default="255700000000", help="customer phone (no +)")
    parser.add_argument("--name", default="Test Customer", help="customer WhatsApp profile name")
    parser.add_argument("--button", help="simulate a quick-reply button tap with this title")
    parser.add_argument("--status", choices=["sent", "delivered", "read", "failed"], help="send a status receipt instead of a message")
    parser.add_argument("--url", default="http://localhost:8001", help="backend base URL")
    parser.add_argument("--org", default="1", help="organization id in the webhook path")
    args = parser.parse_args()

    env = read_env(ENV_FILE)
    # Same precedence as the backend: real environment variables win over backend/.env
    secret = os.environ.get("META_APP_SECRET", env.get("META_APP_SECRET", ""))
    if secret.startswith("<"):
        secret = ""

    body = json.dumps(build_payload(args)).encode()
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["X-Hub-Signature-256"] = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    else:
        print("! META_APP_SECRET is not set in backend/.env; sending without a signature")

    url = f"{args.url.rstrip('/')}/api/v1/webhooks/whatsapp/{args.org}"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            print(f"{response.status} {response.read().decode()}")
            return 0
    except urllib.error.HTTPError as exc:
        print(f"{exc.code} {exc.read().decode()}")
    except urllib.error.URLError as exc:
        print(f"Could not reach {url}: {exc.reason}. Is the backend running?")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
