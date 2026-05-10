VALID_TRANSITIONS = {
    "new": ["triaged"],
    "triaged": ["escalated", "resolved"],
    "escalated": ["resolved"],
    "resolved": ["reopened"],
    "reopened": ["triaged", "resolved"],
}

def next_status(current_status: str, severity: str) -> str:
    if current_status == "new":
        return "triaged"
    if current_status == "triaged" and severity.lower() in {"high", "critical"}:
        return "escalated"
    if current_status == "triaged":
        return "resolved"
    return current_status

def is_valid_transition(old_status: str, new_status: str) -> bool:
    return new_status in VALID_TRANSITIONS.get(old_status, [])
