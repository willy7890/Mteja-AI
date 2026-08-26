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

_contact_ids = count(1)
_message_ids = count(1)
_task_ids = count(1)


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
