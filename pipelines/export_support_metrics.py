import json
import sqlite3
from pathlib import Path

DB_PATH = Path("autoops.db")
OUT = Path("artifacts/analytics/support_metrics.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row

    total = conn.execute("SELECT COUNT(*) AS c FROM support_incidents").fetchone()["c"]

    top_issue_family = [
        dict(r) for r in conn.execute(
            """
            SELECT issue_family, COUNT(*) AS count
            FROM support_incidents
            GROUP BY issue_family
            ORDER BY count DESC
            """
        )
    ]

    source_counts = [
        dict(r) for r in conn.execute(
            """
            SELECT source, COUNT(*) AS count
            FROM support_incidents
            GROUP BY source
            ORDER BY count DESC
            """
        )
    ]

    action_counts = [
        dict(r) for r in conn.execute(
            """
            SELECT action, COUNT(*) AS count
            FROM support_incidents
            GROUP BY action
            ORDER BY count DESC
            """
        )
    ]

    recurring_blockers = [
        dict(r) for r in conn.execute(
            """
            SELECT signature, issue_family, MAX(recurrence_total) AS recurrence_total
            FROM support_incidents
            GROUP BY signature, issue_family
            HAVING recurrence_total >= 3
            ORDER BY recurrence_total DESC
            LIMIT 20
            """
        )
    ]

    escalations = conn.execute(
        "SELECT COUNT(*) AS c FROM support_incidents WHERE escalation_required = 1"
    ).fetchone()["c"]

payload = {
    "total_support_incidents": total,
    "top_issue_family": top_issue_family,
    "source_counts": source_counts,
    "action_counts": action_counts,
    "recurring_customer_blockers": recurring_blockers,
    "escalation_count": escalations,
}

OUT.write_text(json.dumps(payload, indent=2))
print(json.dumps(payload, indent=2))
