import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("AUTOOPS_DB_PATH", "autoops.db"))

class SQLiteDB:
    def __init__(self):
        self._init()

    def _conn(self):
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    predicted_issue TEXT,
                    signature TEXT,
                    failure_family TEXT,
                    severity TEXT,
                    summary TEXT,
                    repo_name TEXT,
                    workflow_name TEXT,
                    run_id TEXT,
                    root_cause TEXT,
                    likely_trigger TEXT,
                    trigger_confidence REAL,
                    release_decision TEXT,
                    decision_confidence REAL
                )
                """
            )
            conn.commit()

    def insert_analysis(self, data):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO analyses (
                    predicted_issue,
                    signature,
                    failure_family,
                    severity,
                    summary,
                    repo_name,
                    workflow_name,
                    run_id,
                    root_cause,
                    likely_trigger,
                    trigger_confidence,
                    release_decision,
                    decision_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("predicted_issue"),
                    data.get("signature"),
                    data.get("failure_family"),
                    data.get("severity"),
                    data.get("summary"),
                    data.get("repo_name"),
                    data.get("workflow_name"),
                    data.get("run_id"),
                    data.get("root_cause"),
                    data.get("likely_trigger"),
                    data.get("trigger_confidence"),
                    data.get("release_decision"),
                    data.get("decision_confidence"),
                ),
            )
            conn.commit()

    def fetch_recent(self, limit=20):
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM analyses ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def fetch_by_signature(self, signature):
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM analyses WHERE signature = ? ORDER BY id DESC",
                (signature,),
            ).fetchall()
            return [dict(r) for r in rows]

    def fetch_recent_by_repo(self, repo_name, limit=50):
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM analyses WHERE repo_name = ? ORDER BY id DESC LIMIT ?",
                (repo_name, limit),
            ).fetchall()
            return [dict(r) for r in rows]

def get_db():
    return SQLiteDB()
