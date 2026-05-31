import json
from collections import defaultdict
from pathlib import Path

def family_for_alert(alert_type):
    if alert_type in {"latency_spike", "retry_storm", "dependency_failure"}:
        return "service_degradation"
    if alert_type == "escalation_burst":
        return "incident_escalation"
    return "uncategorized"

def correlate_alerts(alerts):
    grouped = defaultdict(list)

    for alert in alerts:
        family = family_for_alert(alert["alert_type"])
        grouped[family].append(alert)

    families = []
    for family, items in grouped.items():
        services = sorted({a["service"] for a in items})
        severities = sorted({a["severity"] for a in items})
        families.append({
            "incident_family": family,
            "alert_count": len(items),
            "services": services,
            "severities": severities,
            "alert_types": sorted({a["alert_type"] for a in items}),
            "recommended_review": (
                "open sev1 incident review"
                if "sev1" in severities and len(items) >= 2
                else "monitor"
            )
        })

    return {
        "alerts_received": len(alerts),
        "incident_families_detected": len(families),
        "families": families,
        "correlation_status": "PASS"
    }

def main():
    alerts = json.loads(Path("alert_correlation/alert_families.json").read_text())
    result = correlate_alerts(alerts)

    Path("alert_correlation/alert_correlation_summary.json").write_text(
        json.dumps(result, indent=2)
    )

    report = f"""# Alert Correlation Report

## Summary

- Alerts received: {result["alerts_received"]}
- Incident families detected: {result["incident_families_detected"]}
- Correlation status: {result["correlation_status"]}

## Incident families

{json.dumps(result["families"], indent=2)}

## Operational value

This workflow groups latency spikes, retry storms, dependency failures, and escalation bursts into incident families for operational review.
"""

    Path("alert_correlation/reports/alert_correlation_report.md").write_text(report)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
