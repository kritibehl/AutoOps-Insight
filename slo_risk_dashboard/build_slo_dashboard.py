import json
from pathlib import Path

INCIDENTS = [
    {
        "incident_id": "INC-1001",
        "service": "checkout-api",
        "status": "open",
        "sla_breached": True,
        "p95_latency_ms": 4200,
        "issue_family": "retry_storm",
        "customer_impact": "high",
        "escalation_age_hours": 18
    },
    {
        "incident_id": "INC-1002",
        "service": "payment-api",
        "status": "open",
        "sla_breached": False,
        "p95_latency_ms": 3100,
        "issue_family": "dependency_timeout",
        "customer_impact": "medium",
        "escalation_age_hours": 7
    },
    {
        "incident_id": "INC-1003",
        "service": "checkout-api",
        "status": "resolved",
        "sla_breached": True,
        "p95_latency_ms": 3900,
        "issue_family": "retry_storm",
        "customer_impact": "medium",
        "escalation_age_hours": 11
    },
    {
        "incident_id": "INC-1004",
        "service": "search-api",
        "status": "open",
        "sla_breached": False,
        "p95_latency_ms": 700,
        "issue_family": "latency_spike",
        "customer_impact": "low",
        "escalation_age_hours": 2
    }
]


def build_slo_risk_dashboard(incidents):
    open_incidents = [i for i in incidents if i["status"] == "open"]
    sla_breaches = [i for i in incidents if i["sla_breached"]]

    family_counts = {}
    for incident in incidents:
        family = incident["issue_family"]
        family_counts[family] = family_counts.get(family, 0) + 1

    repeated_issue_family = max(family_counts, key=family_counts.get)

    max_escalation_age = max(i["escalation_age_hours"] for i in open_incidents)
    highest_p95 = max(i["p95_latency_ms"] for i in incidents)

    risk_level = (
        "high"
        if len(sla_breaches) >= 2 or max_escalation_age >= 12
        else "medium"
    )

    return {
        "open_incidents": len(open_incidents),
        "sla_breaches": len(sla_breaches),
        "p95_latency_ms": highest_p95,
        "repeated_issue_family": repeated_issue_family,
        "customer_impact": "high" if any(i["customer_impact"] == "high" for i in incidents) else "medium",
        "max_escalation_age_hours": max_escalation_age,
        "risk_level": risk_level,
        "recommended_action": "prioritize breached SLA incidents and retry_storm remediation",
        "dashboard_tiles": [
            "open_incidents",
            "sla_breaches",
            "p95_latency",
            "repeated_issue_family",
            "customer_impact",
            "escalation_aging"
        ]
    }


def main():
    dashboard = build_slo_risk_dashboard(INCIDENTS)

    Path("slo_risk_dashboard/slo_risk_summary.json").write_text(
        json.dumps(dashboard, indent=2)
    )

    ageing = {
        "max_escalation_age_hours": dashboard["max_escalation_age_hours"],
        "risk_level": dashboard["risk_level"],
        "recommended_action": dashboard["recommended_action"],
    }

    Path("slo_risk_dashboard/escalation_ageing_report.json").write_text(
        json.dumps(ageing, indent=2)
    )

    report = f"""# SLA / SLO Risk Dashboard

## Summary

- Open incidents: {dashboard["open_incidents"]}
- SLA breaches: {dashboard["sla_breaches"]}
- Highest p95 latency ms: {dashboard["p95_latency_ms"]}
- Repeated issue family: {dashboard["repeated_issue_family"]}
- Customer impact: {dashboard["customer_impact"]}
- Max escalation age hours: {dashboard["max_escalation_age_hours"]}
- Risk level: {dashboard["risk_level"]}

## Recommended action

{dashboard["recommended_action"]}

## Dashboard tiles

{chr(10).join(f"- {tile}" for tile in dashboard["dashboard_tiles"])}

## Operational value

This dashboard summarizes incident risk, SLA/SLO breach pressure, repeated issue families, customer impact, latency health, and escalation aging for support and SRE review.
"""

    Path("slo_risk_dashboard/slo_dashboard_report.md").write_text(report)
    print(json.dumps(dashboard, indent=2))


if __name__ == "__main__":
    main()
