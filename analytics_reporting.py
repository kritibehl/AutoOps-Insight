from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("autoops.db")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_conn(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_reporting_tables(db_path: str | Path = DB_PATH) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporting_daily_summary (
        day TEXT PRIMARY KEY,
        total_events INTEGER NOT NULL,
        failure_events INTEGER NOT NULL,
        high_severity_events INTEGER NOT NULL,
        release_blocking_events INTEGER NOT NULL,
        avg_confidence REAL,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporting_weekly_summary (
        week_start TEXT PRIMARY KEY,
        total_events INTEGER NOT NULL,
        failure_events INTEGER NOT NULL,
        high_severity_events INTEGER NOT NULL,
        release_blocking_events INTEGER NOT NULL,
        avg_confidence REAL,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporting_pipeline_trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pipeline_name TEXT NOT NULL,
        day TEXT NOT NULL,
        total_events INTEGER NOT NULL,
        failure_events INTEGER NOT NULL,
        avg_confidence REAL,
        created_at TEXT NOT NULL,
        UNIQUE(pipeline_name, day)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporting_root_cause_counts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        probable_owner TEXT,
        failure_family TEXT,
        count INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(day, probable_owner, failure_family)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporting_deployment_regressions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_window TEXT NOT NULL,
        service_name TEXT,
        baseline_failure_rate REAL,
        candidate_failure_rate REAL,
        regression_delta REAL,
        regression_flag INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(deployment_window, service_name)
    )
    """)

    conn.commit()
    conn.close()


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _load_source_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    candidates = [
        "analyses",
        "incident_history",
        "analysis_history",
        "history",
        "incidents",
    ]
    for table in candidates:
        if _table_exists(conn, table):
            return conn.execute(f"SELECT * FROM {table} ORDER BY id ASC").fetchall()
    return []


def _safe_get(row: sqlite3.Row, *keys: str) -> Any:
    for key in keys:
        if key in row.keys():
            return row[key]
    return None


def _parse_payload(row: sqlite3.Row) -> dict[str, Any]:
    for key in ["after", "result_json", "result", "payload", "analysis_json", "data"]:
        if key in row.keys() and row[key]:
            try:
                value = row[key]
                if isinstance(value, str):
                    parsed = json.loads(value)
                elif isinstance(value, dict):
                    parsed = value
                else:
                    parsed = {}
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
    return {}


def normalize_event(row: sqlite3.Row) -> dict[str, Any]:
    payload = _parse_payload(row)

    created_at = (
        _safe_get(row, "timestamp", "created_at", "event_time")
        or payload.get("timestamp")
        or utc_now_iso()
    )
    day = str(created_at)[:10]

    severity = (
        _safe_get(row, "severity")
        or payload.get("severity")
        or payload.get("classification", {}).get("severity")
        or "unknown"
    )

    release_blocking = (
        _safe_get(row, "release_blocking")
        if _safe_get(row, "release_blocking") is not None
        else payload.get("release_blocking", False)
    )

    probable_owner = (
        _safe_get(row, "probable_owner")
        or payload.get("probable_owner")
        or "unknown"
    )

    failure_family = (
        _safe_get(row, "failure_family", "predicted_issue")
        or payload.get("failure_family")
        or payload.get("classification", {}).get("failure_family")
        or "unknown"
    )

    confidence = (
        _safe_get(row, "confidence")
        or payload.get("confidence")
        or payload.get("classification", {}).get("confidence")
    )
    try:
        confidence = float(confidence) if confidence is not None else None
    except Exception:
        confidence = None

    status = "failure"

    pipeline_name = (
        _safe_get(row, "filename")
        or payload.get("filename")
        or "default"
    )

    event_id = _safe_get(row, "id")
    message = (
        _safe_get(row, "summary", "message", "snippet", "log_line")
        or payload.get("message")
        or ""
    )

    return {
        "event_id": event_id,
        "created_at": str(created_at),
        "day": day,
        "severity": severity,
        "release_blocking": int(bool(release_blocking)),
        "probable_owner": probable_owner,
        "failure_family": failure_family,
        "confidence": confidence,
        "status": status,
        "pipeline_name": pipeline_name,
        "message": str(message),
    }


def rebuild_reporting_tables(db_path: str | Path = DB_PATH) -> dict[str, int]:
    ensure_reporting_tables(db_path)
    conn = get_conn(db_path)
    cur = conn.cursor()

    rows = _load_source_rows(conn)
    events = [normalize_event(r) for r in rows]

    cur.execute("DELETE FROM reporting_daily_summary")
    cur.execute("DELETE FROM reporting_weekly_summary")
    cur.execute("DELETE FROM reporting_pipeline_trends")
    cur.execute("DELETE FROM reporting_root_cause_counts")
    cur.execute("DELETE FROM reporting_deployment_regressions")

    by_day: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_pipeline_day: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    root_cause_counts: Counter = Counter()

    for e in events:
        by_day[e["day"]].append(e)
        by_pipeline_day[(e["pipeline_name"], e["day"])].append(e)
        root_cause_counts[(e["day"], e["probable_owner"], e["failure_family"])] += 1

    created_at = utc_now_iso()

    for day, items in by_day.items():
        total = len(items)
        failure_events = sum(1 for i in items if str(i["status"]).lower() != "success")
        high_severity = sum(1 for i in items if str(i["severity"]).lower() == "high")
        release_blocking = sum(int(i["release_blocking"]) for i in items)
        confs = [i["confidence"] for i in items if i["confidence"] is not None]
        avg_conf = sum(confs) / len(confs) if confs else None

        cur.execute("""
            INSERT INTO reporting_daily_summary
            (day, total_events, failure_events, high_severity_events, release_blocking_events, avg_confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (day, total, failure_events, high_severity, release_blocking, avg_conf, created_at))

    weekly_rollups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for day, items in by_day.items():
        dt = datetime.fromisoformat(day).date()
        week_start = (dt - timedelta(days=dt.weekday())).isoformat()
        weekly_rollups[week_start].extend(items)

    for week_start, items in weekly_rollups.items():
        total = len(items)
        failure_events = sum(1 for i in items if str(i["status"]).lower() != "success")
        high_severity = sum(1 for i in items if str(i["severity"]).lower() == "high")
        release_blocking = sum(int(i["release_blocking"]) for i in items)
        confs = [i["confidence"] for i in items if i["confidence"] is not None]
        avg_conf = sum(confs) / len(confs) if confs else None

        cur.execute("""
            INSERT INTO reporting_weekly_summary
            (week_start, total_events, failure_events, high_severity_events, release_blocking_events, avg_confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (week_start, total, failure_events, high_severity, release_blocking, avg_conf, created_at))

    for (pipeline_name, day), items in by_pipeline_day.items():
        total = len(items)
        failure_events = sum(1 for i in items if str(i["status"]).lower() != "success")
        confs = [i["confidence"] for i in items if i["confidence"] is not None]
        avg_conf = sum(confs) / len(confs) if confs else None

        cur.execute("""
            INSERT INTO reporting_pipeline_trends
            (pipeline_name, day, total_events, failure_events, avg_confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pipeline_name, day, total, failure_events, avg_conf, created_at))

    for (day, probable_owner, failure_family), count in root_cause_counts.items():
        cur.execute("""
            INSERT INTO reporting_root_cause_counts
            (day, probable_owner, failure_family, count, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (day, probable_owner, failure_family, count, created_at))

    ordered_days = sorted(by_day.keys())
    for i in range(1, len(ordered_days)):
        prev_day = ordered_days[i - 1]
        curr_day = ordered_days[i]

        prev_items = by_day[prev_day]
        curr_items = by_day[curr_day]

        prev_rate = sum(1 for x in prev_items if str(x["status"]).lower() != "success") / len(prev_items) if prev_items else 0.0
        curr_rate = sum(1 for x in curr_items if str(x["status"]).lower() != "success") / len(curr_items) if curr_items else 0.0
        delta = curr_rate - prev_rate

        cur.execute("""
            INSERT INTO reporting_deployment_regressions
            (deployment_window, service_name, baseline_failure_rate, candidate_failure_rate, regression_delta, regression_flag, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            curr_day,
            "all-services",
            prev_rate,
            curr_rate,
            delta,
            int(delta > 0.10),
            created_at,
        ))

    conn.commit()
    conn.close()

    return {
        "source_events": len(events),
        "daily_rows": len(by_day),
        "weekly_rows": len(weekly_rollups),
        "pipeline_rows": len(by_pipeline_day),
        "root_cause_rows": len(root_cause_counts),
        "regression_rows": max(len(ordered_days) - 1, 0),
    }


def fetch_table(table_name: str, limit: int = 100, db_path: str | Path = DB_PATH) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    allowed = {
        "reporting_daily_summary",
        "reporting_weekly_summary",
        "reporting_pipeline_trends",
        "reporting_root_cause_counts",
        "reporting_deployment_regressions",
    }
    if table_name not in allowed:
        conn.close()
        raise ValueError(f"unsupported table: {table_name}")

    rows = conn.execute(
        f"SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
