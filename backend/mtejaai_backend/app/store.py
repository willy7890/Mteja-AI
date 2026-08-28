"""
In-memory store — deliberate choice for a same-day live demo: zero setup,
zero DB connection risk on stage. Swap for PostgreSQL + SQLAlchemy
(already scoped in the project docs) once past the demo.
"""
from datetime import datetime
from itertools import count

contacts: dict[int, dict] = {}
messages: dict[int, dict] = {}
tasks: dict[int, dict] = {}
products: dict[int, dict] = {}

_contact_ids = count(1)
_message_ids = count(1)
_task_ids = count(1)
_product_ids = count(1)


def create_contact(name: str, channel_id: str) -> dict:
    for c in contacts.values():
        if c["channel_id"] == channel_id:
            return c
    cid = next(_contact_ids)
    contact = {
        "id": cid,
        "name": name,
        "channel_id": channel_id,
        "stage": "new",
        "created_at": datetime.utcnow(),
    }
    contacts[cid] = contact
    return contact


def get_contact(contact_id: int) -> dict | None:
    return contacts.get(contact_id)


def list_contacts() -> list[dict]:
    return list(contacts.values())


def add_message(contact_id: int, channel: str, direction: str, text: str) -> dict:
    mid = next(_message_ids)
    msg = {
        "id": mid,
        "contact_id": contact_id,
        "channel": channel,
        "direction": direction,
        "text": text,
        "created_at": datetime.utcnow(),
    }
    messages[mid] = msg
    return msg


def get_history(contact_id: int) -> list[dict]:
    return [m for m in messages.values() if m["contact_id"] == contact_id]


def set_stage(contact_id: int, stage: str) -> None:
    if contact_id in contacts:
        contacts[contact_id]["stage"] = stage


def create_task(contact_id: int, reason: str) -> dict:
    tid = next(_task_ids)
    task = {
        "id": tid,
        "contact_id": contact_id,
        "reason": reason,
        "status": "open",
        "created_at": datetime.utcnow(),
    }
    tasks[tid] = task
    return task


def list_tasks() -> list[dict]:
    return list(tasks.values())


def create_product(name: str, details: str, price: float, quantity: int, image_url: str | None) -> dict:
    pid = next(_product_ids)
    product = {
        "id": pid, "name": name, "details": details,
        "price": price, "quantity": quantity, "image_url": image_url,
    }
    products[pid] = product
    return product


def list_products() -> list[dict]:
    return list(products.values())


def search_products(max_price: float | None = None, keyword: str | None = None) -> list[dict]:
    """Real filtered query against the product catalog — in-stock only."""
    results = [p for p in products.values() if p["quantity"] > 0]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    if keyword:
        import re
        pattern = re.compile(r"\b" + re.escape(keyword.lower()) + r"\b")
        results = [p for p in results if pattern.search(p["name"].lower()) or pattern.search(p["details"].lower())]
    return sorted(results, key=lambda p: p["price"])


def seed_demo_products() -> None:
    if products:
        return
    create_product("Basic Haircut", "Wash, cut, and style. 30 minutes.", 15000, 999, None)
    create_product("Premium Haircut + Beard Trim", "Full grooming package, 50 minutes.", 30000, 999, None)
    create_product("Kids Haircut", "For children under 12. 20 minutes.", 8000, 999, None)
    create_product("Hair Color (Full)", "Full color treatment, includes wash and style.", 55000, 12, None)
    create_product("Deluxe Spa Package", "Haircut, massage, and facial. 2 hours.", 90000, 5, None)
