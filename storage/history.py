from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from analysis.release.change_point import detect_change_point
from analysis.release.clustering import cluster_by_signature
from analysis.release.confidence import calibrate_confidence
from analysis.release.decision_engine import decide_release
from analysis.release.prediction import recurrence_prediction
from analysis.release.root_cause import classify_root_cause
from analysis.release.runbooks import get_runbook
from storage.db.client import get_db

DB_PATH = Path(os.getenv("AUTOOPS_DB_PATH", "autoops.db"))


@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    db = get_db()
    if db.__class__.__name__ == "PostgresClient":
        return

    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                signature TEXT,
                failure_family TEXT,
                severity TEXT,
                summary TEXT
            )
            """
        )


def get_signature_stats(signature: str):
    db = get_db()

    if db.__class__.__name__ == "PostgresClient":
        rows = db.fetch_by_signature(signature)
        total_count = len(rows)
        first_seen = rows[-1]["created_at"] if rows else None
        last_seen = rows[0]["created_at"] if rows else None
        return {
            "total_count": total_count,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "is_recurring": total_count > 1,
            "recent_occurrences": rows[:5],
        }

    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS total_count
            FROM analyses
            WHERE signature = ?
            """,
            (signature,),
        ).fetchone()

    total_count = int(row["total_count"]) if row else 0
    return {
        "total_count": total_count,
        "first_seen": None,
        "last_seen": None,
        "is_recurring": total_count > 1,
        "recent_occurrences": [],
    }


def record_analysis(
    result: Dict[str, Any],
    filename: Optional[str] = None,
    repo_name: Optional[str] = None,
    workflow_name: Optional[str] = None,
    run_id: Optional[str] = None,
    raw_text: Optional[str] = None,
):
    db = get_db()

    if db.__class__.__name__ == "PostgresClient":
        stats = get_signature_stats(result["signature"])
        prior_total = int(stats["total_count"])
        recurrence_score = recurrence_prediction(prior_total + 1)
        recent_same_repo = db.fetch_recent_by_repo(repo_name, limit=20) if repo_name else []
        baseline_count = len(recent_same_repo[:10])
        recent_count = len([r for r in recent_same_repo[:5] if r.get("failure_family") == result["failure_family"]]) + 1
        change_point_flag = detect_change_point(recent_count=recent_count, baseline_count=baseline_count)
        root_cause = classify_root_cause(raw_text or result["summary"], result["failure_family"])
        runbook, runbook_confidence = get_runbook(result["failure_family"])

        calibrated = calibrate_confidence(
            rule_confidence=float(result.get("confidence", 0.70)),
            ml_confidence=float(result.get("ml_fallback_confidence", 0.0)) if result.get("ml_fallback_confidence") is not None else None,
        )

        release_decision, decision_confidence = decide_release(
            failure_family=result["failure_family"],
            severity=result["severity"],
            recurrence_score=recurrence_score,
            change_point_flag=change_point_flag,
            ambiguous_classification=calibrated["ambiguous_classification"],
        )

        data = {
            "signature": result["signature"],
            "failure_family": result["failure_family"],
            "severity": result["severity"],
            "summary": result["summary"],
            "repo_name": repo_name or filename,
            "workflow_name": workflow_name,
            "run_id": run_id,
            "root_cause": root_cause,
            "runbook": runbook,
            "runbook_confidence": runbook_confidence,
            "release_decision": release_decision,
            "decision_confidence": decision_confidence,
            "change_point_flag": change_point_flag,
            "recurrence_score": recurrence_score,
        }
        db.insert_analysis(data)
        return {
            **data,
            **calibrated,
        }

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO analyses (
                signature,
                failure_family,
                severity,
                summary
            ) VALUES (?, ?, ?, ?)
            """,
            (
                result["signature"],
                result["failure_family"],
                result["severity"],
                result["summary"],
            ),
        )
    return result


def get_recent_analyses(limit: int = 20):
    db = get_db()

    if db.__class__.__name__ == "PostgresClient":
        return db.fetch_recent(limit)

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, signature, failure_family, severity, summary
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_top_recurring_signatures(limit: int = 10):
    rows = get_recent_analyses(limit=200)
    clusters = cluster_by_signature(rows)
    return clusters[:limit]


def get_analysis_by_id(analysis_id: int):
    rows = get_recent_analyses(limit=500)
    for row in rows:
        if row.get("id") == analysis_id:
            return row
    return None


def get_report_summary():
    items = get_recent_analyses(limit=50)
    recurring = get_top_recurring_signatures(limit=10)

    release_risk = "low"
    if any(x.get("release_decision") == "rollback_review" for x in items):
        release_risk = "high"
    elif any(x.get("release_decision") == "hold" for x in items):
        release_risk = "medium"

    return {
        "total_analyses": len(items),
        "release_blockers": len([x for x in items if x.get("release_decision") in {"hold", "rollback_review"}]),
        "release_risk": release_risk,
        "top_failure_families": {},
        "top_recurring_signatures": recurring,
        "recent_analyses": items,
        "recent_failure_family_distribution": {},
        "recent_signature_concentration": {},
        "window_comparison": {},
        "recent_family_trend": {},
        "anomalies": [],
    }


def get_all_analyses(limit: int = 1000):
    return get_recent_analyses(limit=limit)


def get_audit_event_by_id(audit_id: int):
    return None
