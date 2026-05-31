import json
from collections import defaultdict
from pathlib import Path

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def pct_change(previous, latest):
    if previous == 0:
        return None
    return round(((latest - previous) / previous) * 100, 1)


def analyze_trends(history):
    by_family = defaultdict(list)

    for row in history:
        by_family[row["incident_family"]].append(row)

    family_trends = []

    for family, rows in by_family.items():
        ordered = sorted(rows, key=lambda r: MONTH_ORDER.index(r["month"]))
        previous = ordered[-2]["count"]
        latest = ordered[-1]["count"]
        increase = pct_change(previous, latest)

        family_trends.append({
            "incident_family": family,
            "previous_month": ordered[-2]["month"],
            "latest_month": ordered[-1]["month"],
            "previous_count": previous,
            "latest_count": latest,
            "increase_pct": increase,
            "increase_label": f"+{increase}%" if increase is not None and increase >= 0 else f"{increase}%",
        })

    top = max(
        family_trends,
        key=lambda row: row["increase_pct"] if row["increase_pct"] is not None else -999
    )

    return {
        "top_incident_family": top["incident_family"],
        "top_incident": top["incident_family"],
        "previous_month": top["previous_month"],
        "latest_month": top["latest_month"],
        "previous_count": top["previous_count"],
        "latest_count": top["latest_count"],
        "increase_pct": top["increase_pct"],
        "increase": top["increase_label"],
        "trend_status": "investigate" if top["increase_pct"] and top["increase_pct"] >= 25 else "monitor",
        "recommended_action": (
            "review retry-budget policies and dependency-health monitoring"
            if top["incident_family"] == "retry_storm"
            else "review service-health trends and escalation triggers"
        ),
        "family_trends": family_trends,
    }


def build_report(summary):
    family_trends_json = json.dumps(summary["family_trends"], indent=2)

    return (
        "# Incident Trend Analytics\n\n"
        "## Top recurring incident family\n\n"
        f"{summary['top_incident_family']}\n\n"
        "## Trend\n\n"
        f"{summary['previous_count']} -> {summary['latest_count']} incidents\n\n"
        "## Increase\n\n"
        f"{summary['increase']}\n\n"
        "## Status\n\n"
        f"{summary['trend_status']}\n\n"
        "## Recommended action\n\n"
        f"{summary['recommended_action']}\n\n"
        "## All family trends\n\n"
        f"{family_trends_json}\n\n"
        "## Operational value\n\n"
        "This workflow identifies recurring incident families, month-over-month "
        "growth rates, risk signals, and recommended remediation actions for "
        "support and reliability workflows.\n"
    )


def main():
    history = json.loads(Path("incident_trends/incident_history.json").read_text())
    summary = analyze_trends(history)

    Path("incident_trends/incident_trend_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    Path("incident_trends/incident_trend_report.md").write_text(
        build_report(summary)
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
