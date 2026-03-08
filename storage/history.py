import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from analysis.anomalies import detect_anomalies
from analysis.trends import (
    compute_failure_family_distribution,
    compute_signature_concentration,
    compute_window_comparison,
    compute_failure_family_window_trend,
)

DB_PATH = os.getenv("AUTOOPS_DB_PATH", "autoops.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            filename TEXT,
            predicted_issue TEXT NOT NULL,
            failure_family TEXT NOT NULL,
            severity TEXT NOT NULL,
            signature TEXT NOT NULL,
            summary TEXT NOT NULL,
            likely_cause TEXT,
            first_remediation_step TEXT,
            next_debugging_action TEXT,
            probable_owner TEXT,
            release_blocking INTEGER NOT NULL,
            confidence REAL NOT NULL,
            evidence_json TEXT NOT NULL
        )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_signature ON analyses(signature)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_failure_family ON analyses(failure_family)")
        conn.commit()


def record_analysis(result: Dict[str, Any], filename: Optional[str] = None):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO analyses (
            created_at,
            filename,
            predicted_issue,
            failure_family,
            severity,
            signature,
            summary,
            likely_cause,
            first_remediation_step,
            next_debugging_action,
            probable_owner,
            release_blocking,
            confidence,
            evidence_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at,
            filename,
            result["predicted_issue"],
            result["failure_family"],
            result["severity"],
            result["signature"],
            result["summary"],
            result.get("likely_cause"),
            result.get("first_remediation_step"),
            result.get("next_debugging_action"),
            result.get("probable_owner"),
            int(bool(result.get("release_blocking", False))),
            float(result["confidence"]),
            json.dumps(result.get("evidence", [])),
        ))
        conn.commit()


def get_signature_stats(signature: str) -> Dict[str, Any]:
    with get_conn() as conn:
        count_row = conn.execute("""
            SELECT COUNT(*) AS total_count,
                   MIN(created_at) AS first_seen,
                   MAX(created_at) AS last_seen
            FROM analyses
            WHERE signature = ?
        """, (signature,)).fetchone()

        recent_rows = conn.execute("""
            SELECT id, created_at, filename, failure_family, severity, confidence
            FROM analyses
            WHERE signature = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (signature,)).fetchall()

    total_count = int(count_row["total_count"]) if count_row and count_row["total_count"] is not None else 0
    first_seen = count_row["first_seen"] if count_row else None
    last_seen = count_row["last_seen"] if count_row else None

    return {
        "total_count": total_count,
        "first_seen": first_seen,
        "last_seen": last_seen,
        "is_recurring": total_count > 1,
        "recent_occurrences": [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "filename": row["filename"],
                "failure_family": row["failure_family"],
                "severity": row["severity"],
                "confidence": row["confidence"],
            }
            for row in recent_rows
        ],
    }


def get_top_recurring_signatures(limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                signature,
                failure_family,
                severity,
                COUNT(*) AS total_count,
                MIN(created_at) AS first_seen,
                MAX(created_at) AS last_seen
            FROM analyses
            GROUP BY signature, failure_family, severity
            HAVING COUNT(*) > 1
            ORDER BY total_count DESC, last_seen DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        {
            "signature": row["signature"],
            "failure_family": row["failure_family"],
            "severity": row["severity"],
            "total_count": row["total_count"],
            "first_seen": row["first_seen"],
            "last_seen": row["last_seen"],
        }
        for row in rows
    ]


def get_recent_analyses(limit: int = 20):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                id,
                created_at,
                filename,
                predicted_issue,
                failure_family,
                severity,
                signature,
                confidence,
                release_blocking
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "filename": row["filename"],
            "predicted_issue": row["predicted_issue"],
            "failure_family": row["failure_family"],
            "severity": row["severity"],
            "signature": row["signature"],
            "confidence": row["confidence"],
            "release_blocking": bool(row["release_blocking"]),
        }
        for row in rows
    ]


def get_analysis_by_id(analysis_id: int):
    with get_conn() as conn:
        row = conn.execute("""
            SELECT *
            FROM analyses
            WHERE id = ?
        """, (analysis_id,)).fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "filename": row["filename"],
        "predicted_issue": row["predicted_issue"],
        "failure_family": row["failure_family"],
        "severity": row["severity"],
        "signature": row["signature"],
        "summary": row["summary"],
        "likely_cause": row["likely_cause"],
        "first_remediation_step": row["first_remediation_step"],
        "next_debugging_action": row["next_debugging_action"],
        "probable_owner": row["probable_owner"],
        "release_blocking": bool(row["release_blocking"]),
        "confidence": row["confidence"],
        "evidence": json.loads(row["evidence_json"]),
    }


def get_failure_family_counts(limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                failure_family,
                COUNT(*) AS total_count
            FROM analyses
            GROUP BY failure_family
            ORDER BY total_count DESC, failure_family ASC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        {
            "failure_family": row["failure_family"],
            "total_count": row["total_count"],
        }
        for row in rows
    ]


def get_release_blocker_count():
    with get_conn() as conn:
        row = conn.execute("""
            SELECT COUNT(*) AS total_count
            FROM analyses
            WHERE release_blocking = 1
        """).fetchone()

    return int(row["total_count"]) if row and row["total_count"] is not None else 0


def get_total_analysis_count():
    with get_conn() as conn:
        row = conn.execute("""
            SELECT COUNT(*) AS total_count
            FROM analyses
        """).fetchone()

    return int(row["total_count"]) if row and row["total_count"] is not None else 0


def get_report_summary():
    total_analyses = get_total_analysis_count()
    release_blockers = get_release_blocker_count()
    recurring = get_top_recurring_signatures(limit=10)
    family_counts = get_failure_family_counts(limit=10)
    recent = get_recent_analyses(limit=20)

    recent_window = recent[:5]
    family_distribution = compute_failure_family_distribution(recent_window)
    signature_concentration = compute_signature_concentration(recent_window)
    window_comparison = compute_window_comparison(recent, recent_window_size=5, baseline_window_size=10)
    family_trend = compute_failure_family_window_trend(recent, recent_window_size=5, baseline_window_size=10)
    anomalies = detect_anomalies(recent_window, recurring, signature_concentration, family_trend)

    release_risk = "low"
    if release_blockers > 0:
        release_risk = "medium"
    if any(item["total_count"] >= 3 for item in recurring):
        release_risk = "high"
    if any(item["severity"] == "critical" and item["total_count"] >= 2 for item in recurring):
        release_risk = "critical"
    if any(a["severity"] == "high" for a in anomalies) and total_analyses >= 3:
        release_risk = "high"

    return {
        "total_analyses": total_analyses,
        "release_blockers": release_blockers,
        "release_risk": release_risk,
        "top_failure_families": family_counts,
        "top_recurring_signatures": recurring,
        "recent_analyses": recent,
        "recent_failure_family_distribution": family_distribution,
        "recent_signature_concentration": signature_concentration,
        "window_comparison": window_comparison,
        "recent_family_trend": family_trend,
        "anomalies": anomalies,
    }
