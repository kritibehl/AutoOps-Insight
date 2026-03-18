from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("autoops.db")


def get_conn(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _load_rows(conn: sqlite3.Connection) -> tuple[str | None, list[sqlite3.Row]]:
    for table in ["analyses", "incident_history", "analysis_history", "history", "incidents"]:
        if _table_exists(conn, table):
            return table, conn.execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()
    return None, []


def validate_data_quality(db_path: str | Path = DB_PATH) -> dict[str, Any]:
    conn = get_conn(db_path)
    table, rows = _load_rows(conn)

    if not table:
        conn.close()
        return {"error": "no source history table found"}

    actual_cols = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    required_cols = {"id"}
    missing_cols = sorted(required_cols - actual_cols)

    missing_required = 0
    duplicates = 0
    stale_rows = 0
    outlier_flags = 0
    seen = set()
    now = datetime.now(timezone.utc)

    for row in rows:
        row_id = row["id"] if "id" in row.keys() else None
        if row_id is None:
            missing_required += 1

        signature = tuple((k, row[k]) for k in row.keys() if k in {"id", "timestamp", "created_at", "event_type", "failure_family"})
        if signature in seen:
            duplicates += 1
        seen.add(signature)

        timestamp = None
        for key in ["timestamp", "created_at", "event_time"]:
            if key in row.keys() and row[key]:
                timestamp = str(row[key])
                break

        if timestamp:
            try:
                ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if now - ts > timedelta(days=7):
                    stale_rows += 1
            except Exception:
                stale_rows += 1

        if "confidence" in row.keys() and row["confidence"] is not None:
            try:
                c = float(row["confidence"])
                if c < 0.0 or c > 1.0:
                    outlier_flags += 1
            except Exception:
                outlier_flags += 1

    conn.close()

    return {
        "table": table,
        "rows_checked": len(rows),
        "missing_required": missing_required,
        "duplicates": duplicates,
        "stale_rows": stale_rows,
        "outlier_flags": outlier_flags,
        "schema_issues": {"missing_columns": missing_cols},
        "anomaly_summary": {
            "has_issues": bool(missing_required or duplicates or stale_rows or outlier_flags or missing_cols)
        },
    }
