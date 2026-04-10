from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
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
    CREATE TABLE IF NOT EXISTS connector_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        connector_name TEXT NOT NULL UNIQUE,
        source_system TEXT NOT NULL,
        target_system TEXT NOT NULL,
        source_endpoint TEXT NOT NULL,
        target_endpoint TEXT NOT NULL,
        field_mapping_json TEXT NOT NULL,
        required_source_fields_json TEXT NOT NULL,
        required_target_fields_json TEXT NOT NULL,
        retry_limit INTEGER NOT NULL DEFAULT 3,
        retry_backoff_seconds REAL NOT NULL DEFAULT 0.5,
        is_enabled INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS connector_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        connector_name TEXT NOT NULL,
        source_system TEXT NOT NULL,
        target_system TEXT NOT NULL,
        status TEXT NOT NULL,
        records_in INTEGER NOT NULL DEFAULT 0,
        records_out INTEGER NOT NULL DEFAULT 0,
        attempts INTEGER NOT NULL DEFAULT 1,
        error_category TEXT,
        error_message TEXT,
        validation_passed INTEGER NOT NULL DEFAULT 0,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        input_payload_json TEXT,
        transformed_payload_json TEXT,
        output_payload_json TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def upsert_connector_config(
    connector_name: str,
    source_system: str,
    target_system: str,
    source_endpoint: str,
    target_endpoint: str,
    field_mapping: dict[str, str],
    required_source_fields: list[str],
    required_target_fields: list[str],
    retry_limit: int = 3,
    retry_backoff_seconds: float = 0.5,
    is_enabled: bool = True,
    db_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    cur = conn.cursor()

    now = utc_now_iso()
    existing = conn.execute(
        "SELECT id FROM connector_configs WHERE connector_name = ?",
        (connector_name,),
    ).fetchone()

    if existing:
        cur.execute("""
            UPDATE connector_configs
            SET source_system = ?, target_system = ?, source_endpoint = ?, target_endpoint = ?,
                field_mapping_json = ?, required_source_fields_json = ?, required_target_fields_json = ?,
                retry_limit = ?, retry_backoff_seconds = ?, is_enabled = ?, updated_at = ?
            WHERE connector_name = ?
        """, (
            source_system,
            target_system,
            source_endpoint,
            target_endpoint,
            json.dumps(field_mapping),
            json.dumps(required_source_fields),
            json.dumps(required_target_fields),
            retry_limit,
            retry_backoff_seconds,
            int(is_enabled),
            now,
            connector_name,
        ))
    else:
        cur.execute("""
            INSERT INTO connector_configs
            (connector_name, source_system, target_system, source_endpoint, target_endpoint,
             field_mapping_json, required_source_fields_json, required_target_fields_json,
             retry_limit, retry_backoff_seconds, is_enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            connector_name,
            source_system,
            target_system,
            source_endpoint,
            target_endpoint,
            json.dumps(field_mapping),
            json.dumps(required_source_fields),
            json.dumps(required_target_fields),
            retry_limit,
            retry_backoff_seconds,
            int(is_enabled),
            now,
            now,
        ))

    conn.commit()
    row = conn.execute(
        "SELECT * FROM connector_configs WHERE connector_name = ?",
        (connector_name,),
    ).fetchone()
    conn.close()
    return dict(row)


def list_connectors(db_path: str | Path = DB_PATH) -> list[dict[str, Any]]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM connector_configs ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _load_connector(connector_name: str, db_path: str | Path = DB_PATH) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM connector_configs WHERE connector_name = ? AND is_enabled = 1",
        (connector_name,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _validate_source(payload: list[dict[str, Any]], required_fields: list[str]) -> tuple[bool, list[str]]:
    errors = []
    for idx, row in enumerate(payload):
        for field in required_fields:
            if field not in row or row[field] in (None, ""):
                errors.append(f"row {idx}: missing source field '{field}'")
    return (len(errors) == 0, errors)


def _transform(payload: list[dict[str, Any]], field_mapping: dict[str, str]) -> list[dict[str, Any]]:
    transformed = []
    for row in payload:
        out = {}
        for source_field, target_field in field_mapping.items():
            out[target_field] = row.get(source_field)
        transformed.append(out)
    return transformed


def _validate_target(payload: list[dict[str, Any]], required_fields: list[str]) -> tuple[bool, list[str]]:
    errors = []
    for idx, row in enumerate(payload):
        for field in required_fields:
            if field not in row or row[field] in (None, ""):
                errors.append(f"row {idx}: missing target field '{field}'")
    return (len(errors) == 0, errors)


def _mock_target_send(
    transformed_payload: list[dict[str, Any]],
    fail_mode: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    if fail_mode == "rate_limit":
        return False, {"error_category": "quota_rate_limit", "message": "mock target rate limited request"}
    if fail_mode == "auth":
        return False, {"error_category": "auth_error", "message": "mock target rejected credentials"}
    if fail_mode == "schema":
        return False, {"error_category": "schema_mismatch", "message": "mock target rejected payload contract"}
    return True, {"accepted_records": len(transformed_payload), "status": "delivered"}


def run_connector(
    connector_name: str,
    source_payload: list[dict[str, Any]],
    fail_mode: str | None = None,
    db_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    ensure_tables(db_path)
    config = _load_connector(connector_name, db_path=db_path)
    if not config:
        return {"error": f"connector '{connector_name}' not found or disabled"}

    field_mapping = json.loads(config["field_mapping_json"])
    required_source_fields = json.loads(config["required_source_fields_json"])
    required_target_fields = json.loads(config["required_target_fields_json"])
    retry_limit = int(config["retry_limit"])
    retry_backoff_seconds = float(config["retry_backoff_seconds"])

    started_at = utc_now_iso()
    validation_passed = 0
    transformed_payload: list[dict[str, Any]] = []
    output_payload: dict[str, Any] | None = None
    status = "failed"
    error_category = None
    error_message = None
    attempts = 0

    src_ok, src_errors = _validate_source(source_payload, required_source_fields)
    if not src_ok:
        error_category = "source_validation_failed"
        error_message = "; ".join(src_errors)
    else:
        transformed_payload = _transform(source_payload, field_mapping)
        tgt_ok, tgt_errors = _validate_target(transformed_payload, required_target_fields)
        if not tgt_ok:
            error_category = "target_validation_failed"
            error_message = "; ".join(tgt_errors)
        else:
            validation_passed = 1
            for attempt in range(1, retry_limit + 1):
                attempts = attempt
                ok, result = _mock_target_send(transformed_payload, fail_mode=fail_mode)
                if ok:
                    status = "succeeded"
                    output_payload = result
                    error_category = None
                    error_message = None
                    break
                error_category = result.get("error_category", "delivery_failed")
                error_message = result.get("message", "connector delivery failed")
                if attempt < retry_limit:
                    time.sleep(retry_backoff_seconds * attempt)
            if status != "succeeded":
                output_payload = {"status": "failed"}

    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO connector_runs
        (connector_name, source_system, target_system, status, records_in, records_out, attempts,
         error_category, error_message, validation_passed, started_at, finished_at,
         input_payload_json, transformed_payload_json, output_payload_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        connector_name,
        config["source_system"],
        config["target_system"],
        status,
        len(source_payload),
        len(transformed_payload) if status == "succeeded" else 0,
        max(attempts, 1),
        error_category,
        error_message,
        validation_passed,
        started_at,
        utc_now_iso(),
        json.dumps(source_payload),
        json.dumps(transformed_payload),
        json.dumps(output_payload or {}),
        utc_now_iso(),
    ))
    conn.commit()
    row = conn.execute("SELECT * FROM connector_runs WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


def list_connector_runs(limit: int = 50, db_path: str | Path = DB_PATH) -> list[dict[str, Any]]:
    ensure_tables(db_path)
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM connector_runs ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def connector_analytics(db_path: str | Path = DB_PATH) -> dict[str, Any]:
    rows = list_connector_runs(limit=500, db_path=db_path)
    total = len(rows)
    success = sum(1 for r in rows if r["status"] == "succeeded")
    failed = total - success

    error_counts: dict[str, int] = {}
    for row in rows:
        cat = row.get("error_category")
        if cat:
            error_counts[cat] = error_counts.get(cat, 0) + 1

    avg_attempts = round(sum(int(r["attempts"]) for r in rows) / total, 2) if total else 0.0

    return {
        "total_runs": total,
        "success_runs": success,
        "failed_runs": failed,
        "success_rate": round(success / total, 2) if total else 0.0,
        "avg_attempts": avg_attempts,
        "error_category_counts": error_counts,
    }
