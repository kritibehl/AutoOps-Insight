from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4


@dataclass
class Incident:
    incident_id: str
    title: str
    severity: str
    status: str
    owner: str
    timeline: List[dict]


INCIDENTS: Dict[str, Incident] = {}


VALID_TRANSITIONS = {
    "new": ["triaged"],
    "triaged": ["assigned", "closed"],
    "assigned": ["mitigating", "closed"],
    "mitigating": ["resolved"],
    "resolved": ["closed"],
    "closed": [],
}


def create_incident(title: str, severity: str, owner: str = "unassigned") -> dict:
    incident = Incident(
        incident_id=f"inc_{uuid4().hex[:10]}",
        title=title,
        severity=severity,
        status="new",
        owner=owner,
        timeline=[],
    )
    incident.timeline.append(_event("created", "new", owner))
    INCIDENTS[incident.incident_id] = incident
    return asdict(incident)


def transition_incident(incident_id: str, new_status: str, actor: str, note: str = "") -> dict:
    incident = INCIDENTS[incident_id]
    allowed = VALID_TRANSITIONS.get(incident.status, [])

    if new_status not in allowed:
        return {
            "incident_id": incident_id,
            "transition_allowed": False,
            "from": incident.status,
            "to": new_status,
            "reason": "invalid_transition",
        }

    old = incident.status
    incident.status = new_status
    incident.timeline.append(_event("transition", new_status, actor, note, old))
    return asdict(incident)


def assign_incident(incident_id: str, owner: str, actor: str) -> dict:
    incident = INCIDENTS[incident_id]
    incident.owner = owner
    incident.timeline.append(_event("assigned", incident.status, actor, f"owner={owner}"))
    return asdict(incident)


def search_incidents(term: str) -> list[dict]:
    lower = term.lower()
    return [
        asdict(incident)
        for incident in INCIDENTS.values()
        if lower in f"{incident.title} {incident.severity} {incident.status} {incident.owner}".lower()
    ]


def _event(action: str, status: str, actor: str, note: str = "", previous_status: str = "") -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "status": status,
        "previous_status": previous_status,
        "actor": actor,
        "note": note,
    }
