from datetime import datetime, timezone

WINDOW_MINUTES = 90

SEVERITY_SCORE = {
    "low": 1,
    "medium": 2,
    "high": 4,
    "critical": 6,
}

def parse_ts(ts: str):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def correlate_deployments_to_incidents(deployments, incidents, window_minutes=WINDOW_MINUTES):
    correlations = []

    for deploy in deployments:
        deployed_at = parse_ts(deploy["deployed_at"])
        affected = []

        for incident in incidents:
            if incident["service"] != deploy["service"]:
                continue

            created_at = parse_ts(incident["created_at"])
            delta_minutes = (created_at - deployed_at).total_seconds() / 60

            if 0 <= delta_minutes <= window_minutes:
                affected.append({
                    **incident,
                    "minutes_after_deploy": round(delta_minutes, 2),
                })

        severity_points = sum(SEVERITY_SCORE.get(i["severity"], 1) for i in affected)
        incident_spike = len(affected)

        rollback_candidate = incident_spike >= 2 or severity_points >= 6
        release_risk = "high" if severity_points >= 8 else "medium" if severity_points >= 4 else "low"

        correlations.append({
            "deployment_id": deploy["deployment_id"],
            "service": deploy["service"],
            "version": deploy["version"],
            "deployed_at": deploy["deployed_at"],
            "owner": deploy["owner"],
            "change_type": deploy["change_type"],
            "incident_spike": incident_spike,
            "severity_points": severity_points,
            "affected_service": deploy["service"],
            "rollback_candidate": rollback_candidate,
            "release_risk": release_risk,
            "release_risk_attribution": (
                f"{incident_spike} incidents within {window_minutes} minutes after deployment "
                f"for {deploy['service']}."
            ),
            "related_incidents": affected,
        })

    return correlations

def summarize_release_risk(correlations):
    rollback_candidates = [c for c in correlations if c["rollback_candidate"]]

    return {
        "deployments_analyzed": len(correlations),
        "rollback_candidates": len(rollback_candidates),
        "highest_risk_services": [
            {
                "service": c["service"],
                "deployment_id": c["deployment_id"],
                "release_risk": c["release_risk"],
                "incident_spike": c["incident_spike"],
                "rollback_candidate": c["rollback_candidate"],
            }
            for c in correlations
            if c["release_risk"] in {"medium", "high"}
        ],
        "recommended_actions": [
            "review rollback criteria for high-risk deployments",
            "compare deploy timestamp with incident spike",
            "notify service owner for affected service",
            "hold release if post-deploy incident spike exceeds threshold",
        ],
    }
