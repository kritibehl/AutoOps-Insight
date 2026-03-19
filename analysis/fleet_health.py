from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path("autoops.db")


def _conn(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def fleet_summary(db_path: str | Path = DB_PATH) -> dict[str, Any]:
    conn = _conn(db_path)
    rows = conn.execute(
        """
        SELECT id, created_at, filename, failure_family, probable_owner, severity, release_blocking, signature
        FROM analyses
        ORDER BY created_at ASC
        """
    ).fetchall()

    recurring_sources = Counter()
    noisy_services = Counter()
    blast_radius = Counter()
    recurrence_by_subsystem = Counter()
    mttr_like_windows = defaultdict(list)
    signature_timestamps = defaultdict(list)

    for row in rows:
        source = row["filename"] or "unknown-source"
        owner = row["probable_owner"] or "unknown-owner"
        family = row["failure_family"] or "unknown-family"
        sig = row["signature"] or f"{owner}:{family}"

        recurring_sources[source] += 1
        noisy_services[owner] += 1
        recurrence_by_subsystem[f"{owner}:{family}"] += 1
        if row["release_blocking"]:
            blast_radius[owner] += 1

        try:
            signature_timestamps[sig].append(datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")))
        except Exception:
            pass

    for sig, ts_list in signature_timestamps.items():
        if len(ts_list) >= 2:
            span_minutes = (max(ts_list) - min(ts_list)).total_seconds() / 60.0
            mttr_like_windows["signature_recurrence_window_minutes"].append(span_minutes)

    mttr_like = None
    spans = mttr_like_windows["signature_recurrence_window_minutes"]
    if spans:
        mttr_like = sum(spans) / len(spans)

    conn.close()
    return {
        "top_recurring_incident_sources": recurring_sources.most_common(10),
        "noisy_service_ranking": noisy_services.most_common(10),
        "highest_blast_radius_regressions": blast_radius.most_common(10),
        "incident_recurrence_by_subsystem": recurrence_by_subsystem.most_common(10),
        "mttr_style_metrics": {
            "signature_recurrence_window_minutes_avg": mttr_like,
            "note": "approximated from repeated incident signature windows, not closed-loop ticket resolution",
        },
        "totals": {
            "analysis_rows": sum(recurring_sources.values()),
            "unique_sources": len(recurring_sources),
            "unique_services": len(noisy_services),
        },
    }
