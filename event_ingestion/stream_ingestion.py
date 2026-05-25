from dataclasses import dataclass, asdict
from enum import Enum
from time import time
from uuid import uuid4
from typing import Dict, List, Optional


class EventStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"


@dataclass
class IncidentEvent:
    event_id: str
    source: str
    event_type: str
    payload: dict
    status: EventStatus
    attempts: int
    max_attempts: int
    created_at: float
    updated_at: float
    error: Optional[str] = None


EVENTS: Dict[str, IncidentEvent] = {}
STREAM: List[str] = []
DLQ: List[str] = []


def ingest_event(source: str, event_type: str, payload: dict, max_attempts: int = 3) -> dict:
    now = time()
    event = IncidentEvent(
        event_id=f"evt_{uuid4().hex[:12]}",
        source=source,
        event_type=event_type,
        payload=payload,
        status=EventStatus.PENDING,
        attempts=0,
        max_attempts=max_attempts,
        created_at=now,
        updated_at=now,
    )
    EVENTS[event.event_id] = event
    STREAM.append(event.event_id)
    return asdict(event)


def process_next_event() -> dict:
    if not STREAM:
        return {"status": "idle"}

    event_id = STREAM.pop(0)
    event = EVENTS[event_id]
    event.status = EventStatus.PROCESSING
    event.attempts += 1
    event.updated_at = time()

    try:
        if event.payload.get("force_failure"):
            raise RuntimeError("forced incident consumer failure")

        event.status = EventStatus.PROCESSED
        event.error = None

    except Exception as exc:
        event.error = str(exc)
        if event.attempts >= event.max_attempts:
            event.status = EventStatus.DEAD_LETTERED
            DLQ.append(event.event_id)
        else:
            event.status = EventStatus.FAILED
            STREAM.append(event.event_id)

    event.updated_at = time()
    return asdict(event)


def process_until_idle(limit: int = 20) -> dict:
    processed = []
    for _ in range(limit):
        result = process_next_event()
        processed.append(result)
        if result.get("status") == "idle":
            break
    return {"processed": processed, "dlq_depth": len(DLQ)}


def search_events(term: str) -> list[dict]:
    lower = term.lower()
    matches = []
    for event in EVENTS.values():
        blob = f"{event.source} {event.event_type} {event.payload}".lower()
        if lower in blob:
            matches.append(asdict(event))
    return matches


def list_dlq() -> list[dict]:
    return [asdict(EVENTS[event_id]) for event_id in DLQ if event_id in EVENTS]
