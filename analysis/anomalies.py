from typing import Any, Dict, List


def detect_anomalies(
    recent_items: List[Dict[str, Any]],
    recurring_items: List[Dict[str, Any]],
    signature_concentration: Dict[str, Any],
    family_trend: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    anomalies = []

    if signature_concentration.get("top_signature_share_pct", 0.0) >= 60.0 and signature_concentration.get("total_items", 0) >= 5:
        anomalies.append({
            "type": "recurring_signature_concentration",
            "severity": "high",
            "message": (
                f"Top signature {signature_concentration['top_signature']} accounts for "
                f"{signature_concentration['top_signature_share_pct']}% of recent analyses."
            ),
        })

    recurring_high = [item for item in recurring_items if item["total_count"] >= 3]
    for item in recurring_high:
        anomalies.append({
            "type": "repeated_signature",
            "severity": item["severity"],
            "message": (
                f"Signature {item['signature']} has recurred {item['total_count']} times "
                f"with severity {item['severity']}."
            ),
        })

    for family in family_trend:
        if family["recent_count"] >= 3 and family["delta"] >= 2:
            anomalies.append({
                "type": "family_spike",
                "severity": "medium",
                "message": (
                    f"Failure family {family['failure_family']} increased in the recent window "
                    f"(recent={family['recent_count']}, baseline={family['baseline_count']})."
                ),
            })

    blocker_count = sum(1 for item in recent_items if item.get("release_blocking"))
    if recent_items and blocker_count == len(recent_items) and len(recent_items) >= 3:
        anomalies.append({
            "type": "release_blocker_saturation",
            "severity": "high",
            "message": "All recent analyses are marked release-blocking.",
        })

    return anomalies
