import sqlite3
from datetime import datetime

DB_PATH = "autoops.db"

def init_audit_table():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS incident_audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor TEXT,
        action TEXT,
        incident_id TEXT,
        old_state TEXT,
        new_state TEXT,
        reason TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

def write_audit_log(
    actor,
    action,
    incident_id,
    old_state,
    new_state,
    reason
):
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    INSERT INTO incident_audit_logs (
        actor,
        action,
        incident_id,
        old_state,
        new_state,
        reason,
        timestamp
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        actor,
        action,
        incident_id,
        old_state,
        new_state,
        reason,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

