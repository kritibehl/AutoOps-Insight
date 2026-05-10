from datetime import datetime

def normalize_support_incident(payload: dict) -> dict:
    required = ["service", "severity", "issue_type", "symptom", "customer_impact", "source"]
    missing = [k for k in required if not payload.get(k)]

    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    return {
        "incident_id": payload.get("incident_id") or f"SUP-{int(datetime.utcnow().timestamp())}",
        "service": payload["service"],
        "severity": payload["severity"],
        "issue_type": payload["issue_type"],
        "symptom": payload["symptom"],
        "customer_impact": payload["customer_impact"],
        "source": payload["source"],
        "created_at": datetime.utcnow().isoformat(),
        "status": "new",
    }
