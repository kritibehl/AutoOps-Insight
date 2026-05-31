import json
from pathlib import Path

INCIDENT = {
    "incident_id": "INC-PROD-901",
    "service": "checkout-api",
    "severity": "sev1",
    "customer_impact": "checkout requests delayed or failing for partner traffic",
    "timeline": [
        {"timestamp": "2026-05-16T14:00:00Z", "event": "release-204 deployed"},
        {"timestamp": "2026-05-16T14:07:00Z", "event": "p95 latency increased by 212%"},
        {"timestamp": "2026-05-16T14:09:00Z", "event": "retry budget exceeded"},
        {"timestamp": "2026-05-16T14:12:00Z", "event": "payment dependency timeout cluster detected"},
        {"timestamp": "2026-05-16T14:18:00Z", "event": "rollback review started"}
    ],
    "service_health_evidence": {
        "p95_latency_delta_pct": 212,
        "error_rate_delta_pct": 8.4,
        "retry_spike": True
    },
    "rollback_candidate": True,
    "corrective_actions": [
        "add dependency timeout regression coverage",
        "tighten retry-budget alerting",
        "document rollback criteria",
        "add deployment correlation review"
    ]
}

def build_postmortem(incident):
    return {
        "incident_id": incident["incident_id"],
        "service": incident["service"],
        "severity": incident["severity"],
        "customer_impact": incident["customer_impact"],
        "timeline": incident["timeline"],
        "service_health_evidence": incident["service_health_evidence"],
        "rollback_candidate": incident["rollback_candidate"],
        "what_happened": (
            "checkout-api degraded after release deployment, with latency, retry, "
            "and dependency-timeout signals indicating an operational regression."
        ),
        "contributing_factors": [
            "deployment correlated with latency spike",
            "retry budget exceeded shortly after rollout",
            "payment dependency timeout cluster appeared during incident window"
        ],
        "corrective_actions": incident["corrective_actions"],
        "blameless_note": (
            "This review focuses on system behavior, detection gaps, and process improvements, "
            "not individual fault."
        )
    }

def main():
    postmortem = build_postmortem(INCIDENT)
    Path("postmortem/postmortem_output.json").write_text(json.dumps(postmortem, indent=2))

    rows = "\n".join(
        f"| {item['timestamp']} | {item['event']} |"
        for item in postmortem["timeline"]
    )
    actions = "\n".join(f"- {a}" for a in postmortem["corrective_actions"])

    report = f"""# Blameless Postmortem

## Incident

{postmortem["incident_id"]}

## Service

{postmortem["service"]}

## Severity

{postmortem["severity"]}

## Customer impact

{postmortem["customer_impact"]}

## What happened

{postmortem["what_happened"]}

## Timeline

| Timestamp | Event |
|---|---|
{rows}

## Contributing factors

{chr(10).join(f"- {f}" for f in postmortem["contributing_factors"])}

## Corrective actions

{actions}

## Blameless note

{postmortem["blameless_note"]}
"""

    Path("postmortem/postmortem_template.md").write_text(report)
    print(json.dumps(postmortem, indent=2))

if __name__ == "__main__":
    main()
