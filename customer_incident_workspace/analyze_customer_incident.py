import json
from pathlib import Path


def analyze_customer_incident(payload):
    signals = payload["signals"]

    deployment_regression = (
        signals.get("release_id_matched") is True
        and signals.get("p95_latency_delta_pct", 0) >= 100
    )

    severity = "sev2" if deployment_regression else "sev3"

    evidence = [
        f"p95 +{signals['p95_latency_delta_pct']}%",
        f"error_rate +{signals['error_rate_delta_pct']}%",
    ]

    if signals.get("release_id_matched"):
        evidence.append("release_id matched")

    if signals.get("retry_spike"):
        evidence.append("retry spike detected")

    suspected_cause = (
        "deployment_regression"
        if deployment_regression
        else "service_degradation_under_review"
    )

    recommended_action = (
        "rollback_candidate"
        if deployment_regression
        else "continue_triage"
    )

    return {
        "customer": payload["customer"],
        "service": payload["service"],
        "issue": payload["issue"],
        "severity": severity,
        "suspected_cause": suspected_cause,
        "evidence": evidence,
        "recommended_action": recommended_action,
        "customer_safe_summary": (
            f"{payload['service']} is showing elevated latency after {payload['release_id']}. "
            "The incident is under engineering review and rollback readiness is being evaluated."
        ),
        "engineering_follow_up": [
            "compare release-204 diff against latency spike window",
            "review retry budget and dependency saturation",
            "prepare rollback review if customer impact persists"
        ],
        "workspace_status": "ready_for_support_review"
    }


def main():
    payload = json.loads(
        Path("customer_incident_workspace/sample_customer_incident.json").read_text()
    )
    summary = analyze_customer_incident(payload)

    Path("customer_incident_workspace/customer_incident_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    report = f"""# Customer Incident Workspace

## Customer

{summary["customer"]}

## Service

{summary["service"]}

## Issue

{summary["issue"]}

## Severity

{summary["severity"]}

## Suspected cause

{summary["suspected_cause"]}

## Evidence

{chr(10).join(f"- {item}" for item in summary["evidence"])}

## Recommended action

{summary["recommended_action"]}

## Customer-safe summary

{summary["customer_safe_summary"]}

## Engineering follow-up

{chr(10).join(f"- {item}" for item in summary["engineering_follow_up"])}

## Operational value

This workspace converts customer-facing incident symptoms into support-ready severity, evidence, suspected cause, recommended action, customer-safe language, and engineering follow-up.
"""

    Path("customer_incident_workspace/customer_incident_report.md").write_text(report)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
