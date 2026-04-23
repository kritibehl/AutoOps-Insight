from __future__ import annotations

from storage.db.client import get_db

def init_db():
    get_db()

def get_signature_stats(signature: str):
    rows = get_db().fetch_by_signature(signature)
    total_count = len(rows)
    return {
        "total_count": total_count,
        "first_seen": rows[-1]["created_at"] if rows else None,
        "last_seen": rows[0]["created_at"] if rows else None,
        "is_recurring": total_count > 1,
        "recent_occurrences": rows[:5],
    }

def _infer_root_cause(failure_family: str) -> str:
    mapping = {
        "dns_failure": "service_discovery_or_dns_misconfiguration",
        "timeout": "dependency_latency_or_unresponsive_service",
        "latency_spike": "latency_regression_after_change",
        "service_unreachable": "dependency_unreachable",
    }
    return mapping.get(failure_family, "unknown_or_mixed_failure")

def _infer_trigger(failure_family: str) -> tuple[str, float]:
    if failure_family == "dns_failure":
        return "config_change", 0.70
    if failure_family in {"timeout", "latency_spike"}:
        return "deployment_change", 0.66
    if failure_family == "service_unreachable":
        return "dependency_change", 0.68
    return "unknown", 0.40

def _release_decision(failure_family: str, recurrence_total: int) -> tuple[str, float, list[str]]:
    reasons = []
    if recurrence_total >= 3:
        reasons.append("high recurrence")
    if failure_family in {"timeout", "latency_spike"}:
        reasons.append("latency regression")
    if failure_family in {"dns_failure", "service_unreachable"}:
        reasons.append("dependency instability")
    if not reasons:
        reasons.append("operator review required")

    if failure_family in {"dns_failure", "service_unreachable"}:
        return "hold_release", 0.91 if recurrence_total >= 3 else 0.82, reasons
    if failure_family in {"timeout", "latency_spike"}:
        return "hold_release", 0.84 if recurrence_total >= 2 else 0.78, reasons
    return "investigate", 0.60, reasons

def record_analysis(result, filename=None, repo_name=None, workflow_name=None, run_id=None, raw_text=None):
    prior = get_signature_stats(result["signature"])
    recurrence_total = prior["total_count"] + 1
    root_cause = _infer_root_cause(result["failure_family"])
    likely_trigger, trigger_confidence = _infer_trigger(result["failure_family"])
    release_decision, decision_confidence, decision_reason = _release_decision(
        result["failure_family"], recurrence_total
    )

    data = {
        "predicted_issue": result.get("predicted_issue", result["failure_family"]),
        "signature": result["signature"],
        "failure_family": result["failure_family"],
        "severity": result["severity"],
        "summary": result["summary"],
        "repo_name": repo_name or filename,
        "workflow_name": workflow_name,
        "run_id": run_id,
        "root_cause": root_cause,
        "likely_trigger": likely_trigger,
        "trigger_confidence": trigger_confidence,
        "release_decision": release_decision,
        "decision_confidence": decision_confidence,
    }

    get_db().insert_analysis(data)

    return {
        **data,
        "incident_type": result["failure_family"],
        "recurrence_total": recurrence_total,
        "confidence": result.get("confidence", 0.8),
        "decision_reason": decision_reason,
        "action": release_decision,
    }

def get_recent_analyses(limit: int = 20):
    return get_db().fetch_recent(limit)

def get_top_recurring_signatures(limit: int = 10):
    rows = get_recent_analyses(limit=500)
    counts = {}
    first = {}
    for row in rows:
        sig = row["signature"]
        counts[sig] = counts.get(sig, 0) + 1
        first.setdefault(sig, row)
    items = []
    for sig, count in counts.items():
        row = first[sig]
        items.append({
            "signature": sig,
            "count": count,
            "failure_family": row["failure_family"],
            "repo_name": row.get("repo_name"),
        })
    return sorted(items, key=lambda x: x["count"], reverse=True)[:limit]

def get_analysis_by_id(analysis_id: int):
    rows = get_recent_analyses(limit=500)
    for row in rows:
        if row.get("id") == analysis_id:
            return row
    return None

def get_report_summary():
    rows = get_recent_analyses(limit=100)
    top_failures = {}
    noisy = {}
    for row in rows:
        fam = row.get("failure_family", "unknown")
        repo = row.get("repo_name", "unknown")
        top_failures[fam] = top_failures.get(fam, 0) + 1
        noisy[repo] = noisy.get(repo, 0) + 1

    return {
        "total_analyses": len(rows),
        "top_failures": sorted(
            [{"failure_family": k, "count": v} for k, v in top_failures.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:10],
        "noisy_services": sorted(
            [{"service": k, "count": v} for k, v in noisy.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:10],
        "top_recurring_signatures": get_top_recurring_signatures(limit=10),
        "release_risk": "medium" if rows else "low",
    }

def get_audit_event_by_id(audit_id: int):
    return None
