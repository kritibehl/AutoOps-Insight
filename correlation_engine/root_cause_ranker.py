WEIGHTS = {
    "unsafe_response": 5,
    "tool_failure": 4,
    "latency_spike": 3,
    "missing_context": 3,
    "retrieval_failure": 3,
    "wrong_answer": 2,
    "dns_failure": 3,
    "service_unreachable": 4,
    "timeout": 3,
}

def rank_root_causes(events):
    scores = {}

    for event in events:
        issue = event.get("issue_family", "unknown")
        root_cause = event.get("root_cause", "unknown")
        recurrence = int(event.get("recurrence_total", 1) or 1)
        escalation = 2 if event.get("escalation_required") else 0

        score = WEIGHTS.get(issue, 1) + recurrence + escalation
        scores[root_cause] = scores.get(root_cause, 0) + score

    ranked = sorted(
        [{"root_cause": k, "score": v} for k, v in scores.items()],
        key=lambda x: x["score"],
        reverse=True,
    )

    return ranked
