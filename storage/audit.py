from datetime import datetime

_AUDIT_EVENTS = []


def init_audit_db():
    return True


def record_audit_event(event: dict):
    event = dict(event)
    event["created_at"] = datetime.utcnow().isoformat()
    _AUDIT_EVENTS.append(event)
    return event


def get_recent_audit_events(limit: int = 20):
    return list(reversed(_AUDIT_EVENTS))[:limit]
