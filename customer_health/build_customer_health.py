import json
from pathlib import Path

CUSTOMERS = [
    {"customer": "enterprise_alpha", "open_incidents": 3, "sla_breaches": 1, "escalations_previous": 5, "escalations_current": 7, "health": "at_risk"},
    {"customer": "enterprise_beta", "open_incidents": 2, "sla_breaches": 1, "escalations_previous": 3, "escalations_current": 4, "health": "at_risk"},
    {"customer": "enterprise_gamma", "open_incidents": 4, "sla_breaches": 0, "escalations_previous": 4, "escalations_current": 6, "health": "at_risk"},
    {"customer": "enterprise_delta", "open_incidents": 1, "sla_breaches": 1, "escalations_previous": 2, "escalations_current": 3, "health": "at_risk"},
    {"customer": "startup_echo", "open_incidents": 0, "sla_breaches": 0, "escalations_previous": 1, "escalations_current": 1, "health": "healthy"}
]

def build_customer_health(customers):
    at_risk = [c for c in customers if c["health"] == "at_risk"]
    prev = sum(c["escalations_previous"] for c in customers)
    current = sum(c["escalations_current"] for c in customers)
    growth = round(((current - prev) / prev) * 100, 1) if prev else 0

    return {
        "customers_at_risk": len(at_risk),
        "escalation_growth": f"+{growth}%",
        "open_incidents": sum(c["open_incidents"] for c in customers),
        "sla_breaches": sum(c["sla_breaches"] for c in customers),
        "top_risk_customers": [c["customer"] for c in at_risk],
        "recommended_action": "prioritize enterprise accounts with SLA breaches and growing escalations",
        "customer_health_status": "review_required"
    }

def main():
    summary = build_customer_health(CUSTOMERS)
    Path("customer_health/customer_health_summary.json").write_text(json.dumps(summary, indent=2))

    report = f"""# Customer Health Center

## Summary

- Customers at risk: {summary["customers_at_risk"]}
- Escalation growth: {summary["escalation_growth"]}
- Open incidents: {summary["open_incidents"]}
- SLA breaches: {summary["sla_breaches"]}

## Top risk customers

{chr(10).join(f"- {c}" for c in summary["top_risk_customers"])}

## Recommended action

{summary["recommended_action"]}

## Operational value

This workflow turns incident and escalation data into customer-health signals for support, FDE, TAM, and SRE operations review.
"""
    Path("customer_health/customer_health_report.md").write_text(report)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
