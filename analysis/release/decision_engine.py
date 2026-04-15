from __future__ import annotations

def decide_release(
    failure_family: str,
    severity: str,
    recurrence_score: float,
    change_point_flag: bool,
    ambiguous_classification: bool = False,
) -> tuple[str, float]:
    sev = severity.lower()

    if ambiguous_classification:
        return "investigate", 0.79

    if failure_family in {"dns_failure", "service_unreachable", "tls_handshake"}:
        return "rollback_review", 0.91 if change_point_flag else 0.86

    if change_point_flag and recurrence_score >= 0.70:
        return "rollback_review", 0.90

    if sev in {"critical", "high"} and recurrence_score >= 0.55:
        return "hold", 0.87

    if sev == "high":
        return "investigate", 0.78

    return "ship", 0.74
