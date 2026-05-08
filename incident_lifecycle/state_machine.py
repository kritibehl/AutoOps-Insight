VALID_STATES = {
    "new": ["triaged", "suppressed"],
    "triaged": ["acknowledged", "escalated", "resolved"],
    "acknowledged": ["resolved", "escalated"],
    "escalated": ["resolved"],
    "suppressed": ["reopened"],
    "resolved": ["reopened"],
    "reopened": ["triaged", "resolved"]
}

def is_valid_transition(old_state, new_state):
    return new_state in VALID_STATES.get(old_state, [])
