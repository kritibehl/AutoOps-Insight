import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


def render_markdown_report(summary: Dict[str, Any]) -> str:
    lines = []
    lines.append("# AutoOps Insight Report")
    lines.append("")
    lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Release Risk Summary")
    lines.append("")
    lines.append(f"- Release risk: **{summary['release_risk']}**")
    lines.append(f"- Total analyses: **{summary['total_analyses']}**")
    lines.append(f"- Release-blocking incidents: **{summary['release_blockers']}**")
    lines.append("")

    lines.append("## Top Failure Families")
    lines.append("")
    if summary["top_failure_families"]:
        for item in summary["top_failure_families"]:
            lines.append(f"- `{item['failure_family']}`: {item['total_count']}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Top Recurring Signatures")
    lines.append("")
    if summary["top_recurring_signatures"]:
        for item in summary["top_recurring_signatures"]:
            lines.append(
                f"- `{item['signature']}` | family={item['failure_family']} | severity={item['severity']} | "
                f"count={item['total_count']} | first_seen={item['first_seen']} | last_seen={item['last_seen']}"
            )
    else:
        lines.append("- No recurring signatures detected")
    lines.append("")

    lines.append("## Recent Analyses")
    lines.append("")
    if summary["recent_analyses"]:
        for item in summary["recent_analyses"]:
            lines.append(
                f"- id={item['id']} | created_at={item['created_at']} | "
                f"family={item['failure_family']} | severity={item['severity']} | "
                f"signature={item['signature']} | release_blocking={item['release_blocking']}"
            )
    else:
        lines.append("- None")
    lines.append("")

    if summary["release_risk"] in {"high", "critical"}:
        lines.append("## Operational Recommendation")
        lines.append("")
        lines.append("- Repeated failure signatures are present at levels that may indicate regression or release instability.")
        lines.append("- Investigate recurring signatures before promoting the current build or environment.")
        lines.append("")

    return "\n".join(lines)


def render_json_report(summary: Dict[str, Any]) -> str:
    return json.dumps(summary, indent=2)


def write_report_files(summary: Dict[str, Any], output_dir: str = "reports/generated") -> Dict[str, str]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = out_dir / "latest_report.md"
    json_path = out_dir / "latest_report.json"

    markdown_path.write_text(render_markdown_report(summary), encoding="utf-8")
    json_path.write_text(render_json_report(summary), encoding="utf-8")

    return {
        "markdown_path": str(markdown_path),
        "json_path": str(json_path),
    }
