from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from incident_ops.service import (
    analytics_summary,
    ensure_tables,
    get_incident_detail,
    ingest_event,
    ingest_faultline_run,
    list_incidents,
    store_feedback,
    update_incident_status,
)

router = APIRouter(prefix="", tags=["incident-ops"])
ensure_tables()


class IncidentEventIn(BaseModel):
    source: str
    timestamp: str
    event_type: str
    payload: dict[str, Any]


class FaultlineRunIn(BaseModel):
    run_id: str
    status: str = "failed"
    timestamp: str | None = None
    summary: str | None = None
    explanation: str | None = None
    error: str | None = None
    timeline_url: str | None = None
    replay_url: str | None = None


class FeedbackIn(BaseModel):
    classification_correct: bool | None = None
    suggestion_useful: bool | None = None
    final_resolution: str | None = None
    notes: str | None = None


class StatusUpdateIn(BaseModel):
    status: str = Field(pattern="^(open|resolved)$")
    final_resolution: str | None = None


@router.post("/ingest/event")
def ingest_single_event(body: IncidentEventIn):
    return ingest_event(
        source=body.source,
        timestamp=body.timestamp,
        event_type=body.event_type,
        payload=body.payload,
    )


@router.post("/ingest/batch")
def ingest_batch(events: list[IncidentEventIn]):
    return {
        "items": [
            ingest_event(
                source=e.source,
                timestamp=e.timestamp,
                event_type=e.event_type,
                payload=e.payload,
            )
            for e in events
        ]
    }


@router.post("/faultline/ingest")
def ingest_faultline(body: FaultlineRunIn):
    return ingest_faultline_run(body.model_dump())


@router.get("/incident-inbox")
def incident_inbox(status: str | None = None, limit: int = 100):
    return {"items": list_incidents(status=status, limit=limit)}


@router.get("/incidents/{incident_id}")
def incident_detail(incident_id: int):
    return get_incident_detail(incident_id)


@router.post("/incidents/{incident_id}/status")
def incident_status_update(incident_id: int, body: StatusUpdateIn):
    return update_incident_status(
        incident_id=incident_id,
        status=body.status,
        final_resolution=body.final_resolution,
    )


@router.post("/incidents/{incident_id}/feedback")
def incident_feedback(incident_id: int, body: FeedbackIn):
    return store_feedback(
        incident_id=incident_id,
        classification_correct=body.classification_correct,
        suggestion_useful=body.suggestion_useful,
        final_resolution=body.final_resolution,
        notes=body.notes,
    )


@router.get("/incident-analytics")
def incident_analytics():
    return analytics_summary()
