def summarize_service_health(incident: dict) -> dict:
    severity = incident["severity"].lower()
    impact = incident["customer_impact"]

    risk = "low"
    if severity in {"high", "critical"}:
        risk = "high"
    elif severity == "medium":
        risk = "medium"

    return {
        "service": incident["service"],
        "health_status": "degraded" if risk in {"medium", "high"} else "watch",
        "risk_level": risk,
        "customer_impact_summary": f"{incident['service']} affected: {impact}",
    }
