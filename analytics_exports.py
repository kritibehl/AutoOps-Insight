from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("autoops.db")


def export_powerbi_bundle(db_path: str | Path = DB_PATH, out_dir: str | Path = "bi_exports") -> dict:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    tables = [
        "reporting_daily_summary",
        "reporting_weekly_summary",
        "reporting_pipeline_trends",
        "reporting_root_cause_counts",
        "reporting_deployment_regressions",
    ]

    exported_files = []

    for table in tables:
        found = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()
        if not found:
            continue

        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        output_file = out_path / f"{table}.csv"

        with output_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if rows:
                writer.writerow(rows[0].keys())
                for row in rows:
                    writer.writerow([row[k] for k in row.keys()])
            else:
                writer.writerow(["no_rows"])

        exported_files.append(str(output_file))

    readme = out_path / "POWERBI_DASHBOARD_PLAN.md"
    readme.write_text(
        """# Power BI Dashboard Plan

## Pages
1. CI Failure Trends Over Time
2. Flaky / Failure Category Distribution
3. Root Cause Category Counts
4. Deployment Regression Spikes
5. Release Risk by Service / Pipeline

## Visuals
- Line chart: daily failure_events
- Stacked column: failure_family by day
- Heatmap: pipeline_name vs day
- KPI cards: release_blocking_events, regression_flag count
- Table: highest regression_delta windows

## Notes
Import the CSVs in Power BI and create relationships on day / week_start / pipeline_name as needed.
""",
        encoding="utf-8",
    )

    conn.close()
    return {"exported_files": exported_files, "dashboard_plan": str(readme)}
