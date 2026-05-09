from collections import defaultdict
from datetime import datetime

def build_incident_graph(events):
    graph = defaultdict(list)

    for event in events:
        source = event.get("source", "unknown")
        issue = event.get("issue_family", "unknown")
        trace_id = event.get("trace_id", "missing_trace")
        action = event.get("action", "investigate")

        graph[trace_id].append({
            "source": source,
            "issue_family": issue,
            "action": action,
            "timestamp": event.get("timestamp"),
            "root_cause": event.get("root_cause", "unknown")
        })

    return dict(graph)


def summarize_graph(graph):
    summaries = []

    for trace_id, events in graph.items():
        issue_families = sorted(set(e["issue_family"] for e in events))
        sources = sorted(set(e["source"] for e in events))
        actions = sorted(set(e["action"] for e in events))

        summaries.append({
            "trace_id": trace_id,
            "sources": sources,
            "issue_families": issue_families,
            "actions": actions,
            "event_count": len(events),
            "has_escalation": any("escalate" in a for a in actions),
            "has_release_hold": any(a == "hold_release" for a in actions),
        })

    return summaries
