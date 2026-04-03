from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
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


def ensure_tables(db_path: str | Path = DB_PATH) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS incident_inbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_key TEXT NOT NULL,
        failure_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        source TEXT NOT NULL,
        confidence REAL NOT NULL,
        suggested_cause TEXT NOT NULL,
        suggested_fix TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        replay_available INTEGER NOT NULL DEFAULT 0,
        runbook_link TEXT,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        event_count INTEGER NOT NULL DEFAULT 1,
        related_signature TEXT,
        final_resolution TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS incident_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER NOT NULL,
        source TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        fingerprint TEXT NOT NULL,
        replay_available INTEGER NOT NULL DEFAULT 0,
        metadata_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (incident_id) REFERENCES incident_inbox(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS incident_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER NOT NULL,
        classification_correct INTEGER,
        suggestion_useful INTEGER,
        final_resolution TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (incident_id) REFERENCES incident_inbox(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS incident_runbooks (
        failure_type TEXT PRIMARY KEY,
        suggested_fix TEXT NOT NULL,
        runbook_link TEXT NOT NULL,
        escalation_route TEXT NOT NULL,
        mitigation_sequence TEXT NOT NULL
    )
    """)

    conn.commit()

    seed_runbooks = {
        "timeout": {
            "suggested_fix": "check downstream latency, verify retry backoff, and review timeout budget",
            "runbook_link": "/incident/runbook/timeout",
            "escalation_route": "service-owner -> platform-networking",
            "mitigation_sequence": json.dumps([
                "inspect the exact timed-out operation",
                "compare before/after latency and retries",
                "de-rate traffic or fail over if needed",
                "evaluate rollback if change-window correlation is strong",
            ]),
        },
        "retry_storm": {
            "suggested_fix": "cap retries, restore backoff/jitter, and isolate the failing dependency",
            "runbook_link": "/incident/runbook/retry_storm",
            "escalation_route": "service-owner -> dependency owner",
            "mitigation_sequence": json.dumps([
                "confirm retry amplification",
                "reduce concurrency and retry volume",
                "stabilize the dependency before restoring traffic",
            ]),
        },
        "stale_write": {
            "suggested_fix": "verify fencing token checks and investigate lease expiry / concurrent commit paths",
            "runbook_link": "/incident/runbook/stale_write",
            "escalation_route": "service-owner -> storage/platform team",
            "mitigation_sequence": json.dumps([
                "check lease expiry timing",
                "validate fencing token rejection path",
                "replay the incident if supported",
            ]),
        },
        "dependency_latency": {
            "suggested_fix": "review upstream latency, queue depth, and fallback behavior",
            "runbook_link": "/incident/runbook/dependency_latency",
            "escalation_route": "service-owner -> dependency owner",
            "mitigation_sequence": json.dumps([
                "identify the slow dependency",
                "compare latency before and after change windows",
                "enable fallback or de-rate traffic",
            ]),
        },
        "dependency_failure": {
            "suggested_fix": "confirm dependency health and fail over to a known-good endpoint if available",
            "runbook_link": "/incident/runbook/dependency_failure",
            "escalation_route": "service-owner -> dependency owner",
            "mitigation_sequence": json.dumps([
                "verify dependency status",
                "check 5xx/timeout concentration",
                "reroute or fail over",
            ]),
        },
        "dns": {
            "suggested_fix": "verify resolver health and recent DNS/service-discovery changes",
            "runbook_link": "/incident/runbook/dns",
            "escalation_route": "service-owner -> platform-networking -> dns/platform team",
            "mitigation_sequence": json.dumps([
                "retry resolution from multiple hosts/regions",
                "check zone-specific impact",
                "rollback DNS/service-discovery change if correlation is strong",
            ]),
        },
    }

    for failure_type, info in seed_runbooks.items():
        cur.execute("""
        INSERT OR IGNORE INTO incident_runbooks
        (failure_type, suggested_fix, runbook_link, escalation_route, mitigation_sequence)
        VALUES (?, ?, ?, ?, ?)
        """, (
            failure_type,
            info["suggested_fix"],
            info["runbook_link"],
            info["escalation_route"],
            info["mitigation_sequence"],
        ))

    conn.commit()
    conn.close()


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _compact_text(payload: dict[str, Any]) -> str:
    fields = [
        str(payload.get("message", "")),
        str(payload.get("summary", "")),
        str(payload.get("error", "")),
        str(payload.get("status", "")),
        str(payload.get("source_detail", "")),
    ]
    return " ".join(f for f in fields if f).strip().lower()


def _severity_for_family(family: str) -> str:
    if family in {"stale_write", "retry_storm", "dependency_failure"}:
        return "high"
    if family in {"timeout", "dependency_latency", "dns"}:
        return "medium"
    return "low"


def _classify(payload: dict[str, Any], source: str, event_type: str) -> dict[str, Any]:
    text = _compact_text(payload)
    source_lower = source.lower()
    event_type_lower = event_type.lower()

    family = "dependency_failure"
    confidence = 0.68
    cause = "unexpected dependency or service-side failure"
    replay_available = 0

    patterns = [
        ("stale_write", [r"stale write", r"lease expiry", r"fencing token", r"concurrent commit"], 0.91,
         "concurrent commit after lease expiry or missing stale-write protection"),
        ("retry_storm", [r"retry storm", r"too many retries", r"retry burst", r"thundering herd"], 0.88,
         "retry amplification after dependency instability"),
        ("dependency_latency", [r"latency spike", r"slow dependency", r"upstream timeout", r"deadline exceeded"], 0.84,
         "dependency latency regression or upstream saturation"),
        ("timeout", [r"timeout", r"timed out", r"connect timeout", r"i/o timeout"], 0.82,
         "operation exceeded timeout threshold or dependency responded too slowly"),
        ("dns", [r"dns", r"no such host", r"name resolution", r"nxdomain", r"servfail"], 0.86,
         "resolver issue, DNS drift, or name-resolution failure"),
        ("dependency_failure", [r"connection refused", r"service unavailable", r"5xx", r"upstream failed"], 0.75,
         "dependency became unavailable or returned hard failures"),
    ]

    for candidate, regexes, score, guessed_cause in patterns:
        if any(re.search(rx, text) for rx in regexes):
            family = candidate
            confidence = score
            cause = guessed_cause
            break

    if "faultline" in source_lower or "faultline" in text:
        replay_available = 1
        confidence = max(confidence, 0.87)
        if family == "dependency_failure" and any(tok in text for tok in ["stale", "fencing", "lease"]):
            family = "stale_write"
            confidence = 0.91
            cause = "concurrent commit after lease expiry or stale write path in worker coordination"

    if "alert" in event_type_lower or payload.get("alert_name"):
        confidence = min(confidence + 0.04, 0.97)

    severity = _severity_for_family(family)
    related_signature = f"{family}:{_fingerprint(text or source + event_type)}"

    return {
        "failure_type": family,
        "severity": severity,
        "confidence": round(confidence, 2),
        "suggested_cause": cause,
        "replay_available": replay_available,
        "related_signature": related_signature,
    }


def _runbook_for(conn: sqlite3.Connection, failure_type: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM incident_runbooks WHERE failure_type = ?",
        (failure_type,),
    ).fetchone()
    if row:
        return dict(row)
    return {
        "suggested_fix": "inspect correlated changes, verify dependency health, and compare recent incidents",
        "runbook_link": f"/incident/runbook/{failure_type}",
        "escalation_route": "service-owner -> relevant platform owner",
        "mitigation_sequence": json.dumps([
            "confirm the failing dependency or operation",
            "compare nearby changes and repeat incidents",
            "contain impact and escalate with timestamps",
        ]),
    }


def _find_existing_open_incident(
    conn: sqlite3.Connection,
    incident_key: str,
    source: str,
    lookback_hours: int = 48,
) -> sqlite3.Row | None:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()
    return conn.execute("""
        SELECT * FROM incident_inbox
        WHERE incident_key = ?
          AND source = ?
          AND status = 'open'
          AND last_seen >= ?
        ORDER BY last_seen DESC
        LIMIT 1
    """, (incident_key, source, cutoff)).fetchone()


def ingest_event(
    source: str,
    timestamp: str,
    event_type: str,
    payload: dict[str, Any],
    db_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    cur = conn.cursor()

    classification = _classify(payload, source, event_type)
    runbook = _runbook_for(conn, classification["failure_type"])
    incident_key = classification["related_signature"]

    existing = _find_existing_open_incident(conn, incident_key, source)

    now = utc_now_iso()

    if existing:
        new_count = int(existing["event_count"]) + 1
        avg_conf = round((float(existing["confidence"]) + classification["confidence"]) / 2.0, 2)
        cur.execute("""
            UPDATE incident_inbox
            SET last_seen = ?, event_count = ?, confidence = ?, replay_available = MAX(replay_available, ?)
            WHERE id = ?
        """, (timestamp, new_count, avg_conf, classification["replay_available"], existing["id"]))
        incident_id = int(existing["id"])
    else:
        cur.execute("""
            INSERT INTO incident_inbox
            (incident_key, failure_type, severity, source, confidence, suggested_cause, suggested_fix,
             status, replay_available, runbook_link, first_seen, last_seen, event_count, related_signature,
             created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, 1, ?, ?)
        """, (
            incident_key,
            classification["failure_type"],
            classification["severity"],
            source,
            classification["confidence"],
            classification["suggested_cause"],
            runbook["suggested_fix"],
            classification["replay_available"],
            runbook["runbook_link"],
            timestamp,
            timestamp,
            classification["related_signature"],
            now,
        ))
        incident_id = int(cur.lastrowid)

    compact_text = _compact_text(payload) or f"{source}:{event_type}"
    cur.execute("""
        INSERT INTO incident_events
        (incident_id, source, timestamp, event_type, payload_json, fingerprint, replay_available, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_id,
        source,
        timestamp,
        event_type,
        json.dumps(payload),
        _fingerprint(compact_text),
        classification["replay_available"],
        json.dumps({
            "suggested_cause": classification["suggested_cause"],
            "runbook_link": runbook["runbook_link"],
            "escalation_route": runbook["escalation_route"],
        }),
        now,
    ))

    conn.commit()
    incident = conn.execute("SELECT * FROM incident_inbox WHERE id = ?", (incident_id,)).fetchone()
    conn.close()
    return dict(incident)


def ingest_faultline_run(payload: dict[str, Any], db_path: str | Path = DB_PATH) -> dict[str, Any]:
    run_id = str(payload.get("run_id", "faultline-run"))
    status = str(payload.get("status", "failed"))
    explanation = str(payload.get("explanation", "faultline run failed"))
    event_payload = {
        "message": explanation,
        "summary": payload.get("summary", explanation),
        "error": payload.get("error", explanation),
        "timeline_url": payload.get("timeline_url"),
        "replay_url": payload.get("replay_url"),
        "source_detail": f"faultline:{run_id}:{status}",
    }
    return ingest_event(
        source="Faultline",
        timestamp=payload.get("timestamp", utc_now_iso()),
        event_type="faultline_worker_event",
        payload=event_payload,
        db_path=db_path,
    )


def list_incidents(status: str | None = None, limit: int = 100, db_path: str | Path = DB_PATH) -> list[dict[str, Any]]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    if status:
        rows = conn.execute("""
            SELECT * FROM incident_inbox
            WHERE status = ?
            ORDER BY last_seen DESC
            LIMIT ?
        """, (status, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM incident_inbox
            ORDER BY last_seen DESC
            LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_incident_detail(incident_id: int, db_path: str | Path = DB_PATH) -> dict[str, Any]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    incident = conn.execute("SELECT * FROM incident_inbox WHERE id = ?", (incident_id,)).fetchone()
    if not incident:
        conn.close()
        return {"error": "incident not found"}

    incident_dict = dict(incident)
    events = conn.execute("""
        SELECT * FROM incident_events
        WHERE incident_id = ?
        ORDER BY timestamp DESC
    """, (incident_id,)).fetchall()

    related = conn.execute("""
        SELECT id, failure_type, severity, source, status, first_seen, last_seen
        FROM incident_inbox
        WHERE related_signature = ?
          AND id != ?
        ORDER BY last_seen DESC
        LIMIT 5
    """, (incident_dict["related_signature"], incident_id)).fetchall()

    feedback = conn.execute("""
        SELECT * FROM incident_feedback
        WHERE incident_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (incident_id,)).fetchall()

    runbook = _runbook_for(conn, incident_dict["failure_type"])
    conn.close()

    return {
        "incident": incident_dict,
        "events": [dict(r) for r in events],
        "related_incidents": [dict(r) for r in related],
        "feedback": [dict(r) for r in feedback],
        "runbook": {
            "suggested_fix": runbook["suggested_fix"],
            "runbook_link": runbook["runbook_link"],
            "escalation_route": runbook["escalation_route"],
            "mitigation_sequence": json.loads(runbook["mitigation_sequence"]),
        },
    }


def update_incident_status(incident_id: int, status: str, final_resolution: str | None = None, db_path: str | Path = DB_PATH) -> dict[str, Any]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
        UPDATE incident_inbox
        SET status = ?, final_resolution = COALESCE(?, final_resolution)
        WHERE id = ?
    """, (status, final_resolution, incident_id))
    conn.commit()
    row = conn.execute("SELECT * FROM incident_inbox WHERE id = ?", (incident_id,)).fetchone()
    conn.close()
    return dict(row) if row else {"error": "incident not found"}


def store_feedback(
    incident_id: int,
    classification_correct: bool | None,
    suggestion_useful: bool | None,
    final_resolution: str | None,
    notes: str | None,
    db_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO incident_feedback
        (incident_id, classification_correct, suggestion_useful, final_resolution, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        incident_id,
        None if classification_correct is None else int(classification_correct),
        None if suggestion_useful is None else int(suggestion_useful),
        final_resolution,
        notes,
        utc_now_iso(),
    ))
    if final_resolution:
        cur.execute("""
            UPDATE incident_inbox
            SET final_resolution = ?
            WHERE id = ?
        """, (final_resolution, incident_id))
    conn.commit()
    row = conn.execute("SELECT * FROM incident_feedback WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


def analytics_summary(db_path: str | Path = DB_PATH) -> dict[str, Any]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    incidents = conn.execute("SELECT * FROM incident_inbox ORDER BY last_seen DESC").fetchall()
    feedback = conn.execute("SELECT * FROM incident_feedback").fetchall()
    conn.close()

    failures = Counter(r["failure_type"] for r in incidents)
    repeat_incidents = sorted(
        [{"incident_id": r["id"], "failure_type": r["failure_type"], "event_count": r["event_count"], "source": r["source"]} for r in incidents if int(r["event_count"]) > 1],
        key=lambda x: x["event_count"],
        reverse=True,
    )[:10]

    by_day = Counter(r["last_seen"][:10] for r in incidents)
    resolved = sum(1 for r in incidents if r["status"] == "resolved")
    open_count = sum(1 for r in incidents if r["status"] == "open")
    total = len(incidents)
    resolution_rate = round((resolved / total), 2) if total else 0.0

    rule_hit_rate = 0.0
    useful_marks = [r for r in feedback if r["suggestion_useful"] is not None]
    if useful_marks:
        useful_true = sum(1 for r in useful_marks if int(r["suggestion_useful"]) == 1)
        rule_hit_rate = round(useful_true / len(useful_marks), 2)

    trends = []
    ordered_days = sorted(by_day.items(), key=lambda x: x[0])
    prev = None
    for day, count in ordered_days:
        delta_pct = None
        if prev is not None and prev > 0:
            delta_pct = round(((count - prev) / prev) * 100.0, 1)
        trends.append({"day": day, "count": count, "delta_pct": delta_pct})
        prev = count

    return {
        "top_failure_categories": failures.most_common(10),
        "repeat_incidents": repeat_incidents,
        "incidents_over_time": trends,
        "resolution_rate": resolution_rate,
        "open_incidents": open_count,
        "resolved_incidents": resolved,
        "rule_hit_rate": rule_hit_rate,
        "summary_cards": {
            "total_incidents": total,
            "repeat_incident_count": len(repeat_incidents),
            "open_incident_count": open_count,
        },
    }
