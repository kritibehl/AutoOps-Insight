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

    lines.append("## Recent Failure Family Distribution")
    lines.append("")
    if summary["recent_failure_family_distribution"]:
        for item in summary["recent_failure_family_distribution"]:
            lines.append(
                f"- `{item['failure_family']}`: count={item['count']} | share={item['percentage']}%"
            )
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Recent Signature Concentration")
    lines.append("")
    sig = summary["recent_signature_concentration"]
    lines.append(f"- Total recent items: {sig['total_items']}")
    lines.append(f"- Unique signatures: {sig['unique_signatures']}")
    lines.append(f"- Top signature: {sig['top_signature']}")
    lines.append(f"- Top signature count: {sig['top_signature_count']}")
    lines.append(f"- Top signature share: {sig['top_signature_share_pct']}%")
    lines.append("")

    lines.append("## Window Comparison")
    lines.append("")
    wc = summary["window_comparison"]
    lines.append(f"- Recent window size: {wc['recent_window_size']}")
    lines.append(f"- Baseline window size: {wc['baseline_window_size']}")
    lines.append(f"- Recent release-blocker rate: {wc['recent_release_blocker_rate']}%")
    lines.append(f"- Baseline release-blocker rate: {wc['baseline_release_blocker_rate']}%")
    lines.append(f"- Delta: {wc['release_blocker_delta_pct_points']} percentage points")
    lines.append("")

    lines.append("## Recent Family Trend")
    lines.append("")
    if summary["recent_family_trend"]:
        for item in summary["recent_family_trend"]:
            lines.append(
                f"- `{item['failure_family']}`: recent={item['recent_count']} | "
                f"baseline={item['baseline_count']} | delta={item['delta']}"
            )
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Detected Anomalies")
    lines.append("")
    if summary["anomalies"]:
        for item in summary["anomalies"]:
            lines.append(
                f"- [{item['severity']}] {item['type']}: {item['message']}"
            )
    else:
        lines.append("- No anomaly heuristics triggered")
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
        lines.append("- Repeated failure signatures or concentrated release-blocking patterns indicate elevated release risk.")
        lines.append("- Review recurring signatures, failure-family spikes, and recent blocker concentration before promotion.")
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
