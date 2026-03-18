from __future__ import annotations

import math
import sqlite3
from pathlib import Path
from typing import Any

try:
    from scipy.stats import ttest_ind, chi2_contingency
except Exception:
    ttest_ind = None
    chi2_contingency = None

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


def _load_rows(conn: sqlite3.Connection, limit: int) -> list[sqlite3.Row]:
    for table in ["analyses", "incident_history", "analysis_history", "history", "incidents"]:
        if _table_exists(conn, table):
            return conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return []


def _extract_metric(row: sqlite3.Row) -> float:
    for key in ["confidence"]:
        if key in row.keys() and row[key] is not None:
            try:
                return float(row[key])
            except Exception:
                pass
    return 0.0


def _extract_family(row: sqlite3.Row) -> str:
    for key in ["failure_family", "event_type", "root_cause"]:
        if key in row.keys() and row[key]:
            return str(row[key])
    return "unknown"


def welch_t_test(before: list[float], after: list[float]) -> dict[str, Any]:
    if len(before) < 2 or len(after) < 2:
        return {"error": "need at least 2 samples in each group"}

    if ttest_ind is not None:
        stat = ttest_ind(before, after, equal_var=False, nan_policy="omit")
        return {
            "before_mean": sum(before) / len(before),
            "after_mean": sum(after) / len(after),
            "delta": (sum(after) / len(after)) - (sum(before) / len(before)),
            "t_stat": float(stat.statistic),
            "p_value": float(stat.pvalue),
            "method": "scipy_welch_t_test",
        }

    m1 = sum(before) / len(before)
    m2 = sum(after) / len(after)
    v1 = sum((x - m1) ** 2 for x in before) / max(len(before) - 1, 1)
    v2 = sum((x - m2) ** 2 for x in after) / max(len(after) - 1, 1)
    denom = math.sqrt((v1 / len(before)) + (v2 / len(after))) if (v1 or v2) else 0.0
    t_stat = (m2 - m1) / denom if denom else 0.0

    return {
        "before_mean": m1,
        "after_mean": m2,
        "delta": m2 - m1,
        "t_stat": t_stat,
        "p_value": None,
        "method": "manual_welch_t_test",
    }


def chi_squared_test(before_counts: dict[str, int], after_counts: dict[str, int]) -> dict[str, Any]:
    cats = sorted(set(before_counts) | set(after_counts))
    if not cats:
        return {"error": "no categories found"}

    before_total = sum(before_counts.values())
    after_total = sum(after_counts.values())

    if before_total == 0 or after_total == 0:
        return {
            "error": "insufficient categorical data for chi-squared",
            "categories": cats,
            "before_total": before_total,
            "after_total": after_total,
            "method": "guard_empty_window",
        }

    contingency = [
        [before_counts.get(cat, 0) for cat in cats],
        [after_counts.get(cat, 0) for cat in cats],
    ]

    if chi2_contingency is not None:
        try:
            chi2, p_value, dof, expected = chi2_contingency(contingency)
            return {
                "chi2": float(chi2),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "categories": cats,
                "expected": expected.tolist(),
                "method": "scipy_chi_squared",
            }
        except ValueError as exc:
            return {
                "error": str(exc),
                "categories": cats,
                "contingency": contingency,
                "method": "scipy_chi_squared_guarded",
            }

    return {
        "chi2": None,
        "p_value": None,
        "degrees_of_freedom": max(len(cats) - 1, 1),
        "categories": cats,
        "expected": None,
        "method": "fallback_no_scipy",
    }


def compare_recent_windows(before_limit: int = 10, after_limit: int = 10, db_path: str | Path = DB_PATH) -> dict[str, Any]:
    conn = get_conn(db_path)

    after_rows = _load_rows(conn, after_limit)
    combined = _load_rows(conn, before_limit + after_limit)
    before_rows = combined[after_limit:after_limit + before_limit]

    before_metric = [_extract_metric(r) for r in before_rows]
    after_metric = [_extract_metric(r) for r in after_rows]

    before_counts: dict[str, int] = {}
    after_counts: dict[str, int] = {}

    for row in before_rows:
        fam = _extract_family(row)
        before_counts[fam] = before_counts.get(fam, 0) + 1

    for row in after_rows:
        fam = _extract_family(row)
        after_counts[fam] = after_counts.get(fam, 0) + 1

    conn.close()

    return {
        "welch_t_test": welch_t_test(before_metric, after_metric),
        "chi_squared": chi_squared_test(before_counts, after_counts),
        "sample_sizes": {"before": len(before_rows), "after": len(after_rows)},
    }
