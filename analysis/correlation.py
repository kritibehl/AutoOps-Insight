from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("autoops.db")


def _conn(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def correlate_incident(
    incident_id: int | None = None,
    signature: str | None = None,
    db_path: str | Path = DB_PATH,
    window_minutes: int = 30,
) -> dict[str, Any]:
    conn = _conn(db_path)

    incident = None
    if incident_id is not None:
        incident = conn.execute("SELECT * FROM analyses WHERE id = ?", (incident_id,)).fetchone()
    elif signature:
        incident = conn.execute(
            "SELECT * FROM analyses WHERE signature = ? ORDER BY created_at DESC LIMIT 1",
            (signature,),
        ).fetchone()

    if incident is None:
        conn.close()
        return {"error": "incident not found"}

    created_at = incident["created_at"]
    ts = _parse_dt(created_at)
    if ts is None:
        conn.close()
        return {"error": "incident has invalid timestamp"}

    start = (ts - timedelta(minutes=window_minutes)).isoformat()
    end = (ts + timedelta(minutes=window_minutes)).isoformat()

    nearby_analyses = conn.execute(
        """
        SELECT id, created_at, filename, failure_family, severity, probable_owner, release_blocking, confidence, signature
        FROM analyses
        WHERE created_at BETWEEN ? AND ?
        ORDER BY created_at ASC
        """,
        (start, end),
    ).fetchall()

    audit_events = []
    audit_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
    ).fetchone()
    if audit_exists:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(audit_log)").fetchall()}
        ts_col = "timestamp" if "timestamp" in cols else ("created_at" if "created_at" in cols else None)
        if ts_col:
            audit_events = conn.execute(
                f"SELECT * FROM audit_log WHERE {ts_col} BETWEEN ? AND ? ORDER BY {ts_col} ASC",
                (start, end),
            ).fetchall()

    family_counts = Counter(row["failure_family"] for row in nearby_analyses)
    owner_counts = Counter((row["probable_owner"] or "unknown") for row in nearby_analyses)
    burst_size = len(nearby_analyses)
    blocking_count = sum(int(row["release_blocking"]) for row in nearby_analyses)

    deployment_related = []
    for row in audit_events:
        row_dict = dict(row)
        summary = json.dumps(row_dict).lower()
        if any(term in summary for term in ["deploy", "release", "rollout", "rule_update"]):
            deployment_related.append(row_dict)

    correlation_signals = []
    if deployment_related:
        correlation_signals.append("deployment_or_change_event_near_incident")
    if burst_size >= 3:
        correlation_signals.append("multi_event_burst_detected")
    if blocking_count >= 1:
        correlation_signals.append("release_blocking_incidents_present")
    if len(family_counts) == 1 and burst_size >= 2:
        correlation_signals.append("single_failure_family_cluster")

    summary = {
        "incident": dict(incident),
        "window": {"start": start, "end": end, "minutes": window_minutes},
        "nearby_analysis_count": burst_size,
        "family_counts": dict(family_counts),
        "probable_owner_counts": dict(owner_counts),
        "blocking_count": blocking_count,
        "change_events_nearby": deployment_related,
        "correlation_signals": correlation_signals,
        "assessment": {
            "rollback_suspected_useful": bool(deployment_related and burst_size >= 1),
            "blast_radius_hint": "broad" if len(owner_counts) > 1 or burst_size >= 5 else "localized",
        },
    }
    conn.close()
    return summary
