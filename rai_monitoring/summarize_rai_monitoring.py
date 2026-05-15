import json
from collections import Counter
from pathlib import Path

def summarize_events(events):
    risk_counter = Counter()
    total_regressions = 0

    for event in events:
        total_regressions += event.get("safety_regressions", 0)
        for category in event.get("risk_categories", []):
            risk_counter[category] += 1

    release_blocks = sum(1 for e in events if e.get("release_decision") == "block")
    human_review_escalations = sum(
        1 for e in events if e.get("release_decision") == "block" or e.get("false_allows", 0) > 0
    )
    false_allow_incidents = sum(1 for e in events if e.get("false_allows", 0) > 0)

    return {
        "total_safety_events": len(events),
        "release_blocks": release_blocks,
        "human_review_escalations": human_review_escalations,
        "false_allow_incidents": false_allow_incidents,
        "risk_category_distribution": dict(risk_counter),
        "top_recurring_risk_families": [
            {"risk_family": k, "count": v}
            for k, v in risk_counter.most_common()
        ],
        "average_safety_regressions_per_run": round(total_regressions / len(events), 2) if events else 0,
    }

def main():
    events = json.loads(Path("rai_monitoring/safety_events.json").read_text())
    metrics = summarize_events(events)

    Path("rai_monitoring/rai_monitoring_metrics.json").write_text(json.dumps(metrics, indent=2))
    Path("ai_safety_incidents/safety_monitoring_metrics.json").write_text(json.dumps(metrics, indent=2))

    top_risk = metrics["top_recurring_risk_families"][0]["risk_family"] if metrics["top_recurring_risk_families"] else "none"

    report = f"""# Responsible AI Monitoring Summary

- Safety events observed: {metrics["total_safety_events"]}
- Release blocks: {metrics["release_blocks"]}
- Human-review escalations: {metrics["human_review_escalations"]}
- Most common risk family: {top_risk}
- False-allow incidents: {metrics["false_allow_incidents"]}
- Average safety regressions per run: {metrics["average_safety_regressions_per_run"]}

## Risk category distribution

{json.dumps(metrics["risk_category_distribution"], indent=2)}

## Operational interpretation

AutoOps treats safety-regression findings as operational incidents, exposing monitoring metrics for release blocks, false allows, human-review routing, and recurring risk families.
"""

    Path("rai_monitoring/rai_risk_trend_report.md").write_text(report)
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
