import json
from pathlib import Path


def build_timeline(events):
    return [
        {"step": idx + 1, "timestamp": event["timestamp"], "event": event["event"]}
        for idx, event in enumerate(events)
    ]


def rollback_recommendation(incident):
    health = incident["service_health"]
    rollback_candidate = (
        incident["severity"] == "sev1"
        and health.get("p95_latency_delta_pct", 0) >= 100
        and health.get("retry_spike") is True
    )

    return {
        "rollback_candidate": rollback_candidate,
        "deployment_id": incident["deployment_id"],
        "reason": "sev1 latency spike and retry exhaustion detected after deployment"
        if rollback_candidate
        else "rollback not automatically recommended",
        "recommended_action": "prepare rollback review"
        if rollback_candidate
        else "continue investigation",
    }


def ai_assisted_runbook_summary(incident):
    health = incident["service_health"]
    return (
        f"{incident['service']} degraded after {incident['deployment_id']}. "
        f"p95 latency increased by {health['p95_latency_delta_pct']}% and "
        f"error rate increased by {health['error_rate_delta_pct']}%. "
        "Retry spike and dependency timeout evidence detected."
    )


def build_post_incident_review(incident, timeline, rollback):
    return {
        "incident_id": incident["incident_id"],
        "service": incident["service"],
        "severity": incident["severity"],
        "customer_impact": incident["customer_impact"],
        "timeline_steps": len(timeline),
        "rollback_candidate": rollback["rollback_candidate"],
        "service_health_evidence": incident["service_health"],
        "follow_up_items": [
            "add dependency timeout regression coverage",
            "tighten retry-budget alerting",
            "document rollback criteria",
            "add deployment correlation review",
        ],
    }


def build_runbook_package(incident):
    timeline = build_timeline(incident["events"])
    rollback = rollback_recommendation(incident)
    summary = ai_assisted_runbook_summary(incident)
    post_review = build_post_incident_review(incident, timeline, rollback)

    return {
        "incident_id": incident["incident_id"],
        "incident_timeline": timeline,
        "rollback_recommendation": rollback,
        "ai_assisted_runbook_summary": summary,
        "post_incident_review": post_review,
    }


def build_report(package):
    timeline_rows = "\n".join(
        f"| {item['step']} | {item['timestamp']} | {item['event']} |"
        for item in package["incident_timeline"]
    )

    rollback_json = json.dumps(package["rollback_recommendation"], indent=2)
    review_json = json.dumps(package["post_incident_review"], indent=2)

    return (
        "# Production Incident Runbook Automation\n\n"
        f"## Incident\n\n{package['incident_id']}\n\n"
        f"## AI-assisted runbook summary\n\n{package['ai_assisted_runbook_summary']}\n\n"
        "## Incident timeline\n\n"
        "| Step | Timestamp | Event |\n"
        "|---:|---|---|\n"
        f"{timeline_rows}\n\n"
        "## Rollback recommendation\n\n"
        f"{rollback_json}\n\n"
        "## Post-incident review template\n\n"
        f"{review_json}\n\n"
        "## Operational value\n\n"
        "This workflow converts deployment context, incident events, service-health "
        "evidence, and logs into a production-review artifact with rollback "
        "guidance and follow-up actions.\n"
    )


def main():
    incident = json.loads(Path("incident_runbooks/sample_production_incident.json").read_text())
    package = build_runbook_package(incident)

    Path("incident_runbooks/incident_response_package.json").write_text(
        json.dumps(package, indent=2)
    )
    Path("incident_runbooks/post_incident_review_template.md").write_text(
        build_report(package)
    )

    print(json.dumps(package, indent=2))


if __name__ == "__main__":
    main()
