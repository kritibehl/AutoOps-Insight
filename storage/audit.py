from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from storage.history import get_conn


def init_audit_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            rule_id TEXT,
            actor TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            change_summary TEXT NOT NULL,
            before_json TEXT,
            after_json TEXT
        )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
        conn.commit()


def record_audit_event(
    event_type: str,
    actor: str,
    change_summary: str,
    rule_id: Optional[str] = None,
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None,
):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO audit_log (
            event_type, rule_id, actor, timestamp, change_summary, before_json, after_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_type,
            rule_id,
            actor,
            datetime.now(timezone.utc).isoformat(),
            change_summary,
            json.dumps(before) if before is not None else None,
            json.dumps(after) if after is not None else None,
        ))
        conn.commit()


def get_recent_audit_events(limit: int = 20) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("""
        SELECT id, event_type, rule_id, actor, timestamp, change_summary, before_json, after_json
        FROM audit_log
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,)).fetchall()

    return [
        {
            "id": row["id"],
            "event_type": row["event_type"],
            "rule_id": row["rule_id"],
            "actor": row["actor"],
            "timestamp": row["timestamp"],
            "change_summary": row["change_summary"],
            "before": json.loads(row["before_json"]) if row["before_json"] else None,
            "after": json.loads(row["after_json"]) if row["after_json"] else None,
        }
        for row in rows
    ]
