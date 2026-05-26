import json
from pathlib import Path

def build_timeline(events):
    return [
        {
            "step": idx + 1,
            "timestamp": event["timestamp"],
            "event": event["event"],
        }
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
        "reason": (
            "sev1 incident with latency spike, retry budget exhaustion, and timeout cluster after deployment"
            if rollback_candidate
            else "rollback not automatically recommended"
        ),
        "recommended_action": "prepare rollback review" if rollback_candidate else "continue investigation",
    }

def ai_assisted_runbook_summary(incident):
    service = incident["service"]
    deployment = incident["deployment_id"]
    health = incident["service_health"]

    return (
        f"{service} is degraded after {deployment}. p95 latency increased by "
        f"{health['p95_latency_delta_pct']}% and error rate increased by "
        f"{health['error_rate_delta_pct']}%, with retry spike and payment dependency timeout evidence. "
        "Operators should inspect dependency saturation, compare against the deployment, and prepare rollback review."
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
            "add dependency timeout regression check",
            "tighten retry-budget alerting",
            "document rollback criteria for checkout-api",
            "add service-owner review for high-latency deployment patterns"
        ]
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

def main():
    incident = json.loads(Path("incident_runbooks/sample_production_incident.json").read_text())
    package = build_runbook_package(incident)

    Path("incident_runbooks/incident_response_package.json").write_text(
        json.dumps(package, indent=2)
    )

    timeline_rows = "\n".join(
        f"| {item['step']} | {item['timestamp']} | {item['event']} |"
        for item in package["incident_timeline"]
    )

    report = f"""# Production Incident Runbook Automation

## Incident

{package["incident_id"]}

## AI-assisted runbook summary

{package["ai_assisted_runbook_summary"]}

## Incident timeline

| Step | Timestamp | Event |
|---:|---|---|
{timeline_rows}

## Rollback recommendation

```json
{json.dumps(package["rollback_recommendation"], indent=2)}
Post-incident review template
{json.dumps(package["post_incident_review"], indent=2)}
Operational value

This runbook package converts incident events, service-health evidence, logs, and deployment context into a production-review artifact with timeline, rollback recommendation, post-incident summary, and follow-up actions.
"""

Path("incident_runbooks/post_incident_review_template.md").write_text(report)
print(json.dumps(package, indent=2))

if name == "main":
main()
