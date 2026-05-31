import json
from collections import Counter, defaultdict
from pathlib import Path

def analyze_runbook_quality(steps):
    total = len(steps)
    resolved = sum(1 for s in steps if s["resolved"])
    escalated = sum(1 for s in steps if s["escalated"])

    by_runbook = defaultdict(list)
    for step in steps:
        by_runbook[step["runbook"]].append(step)

    runbook_summaries = []
    for runbook, items in by_runbook.items():
        resolved_count = sum(1 for i in items if i["resolved"])
        unresolved_steps = [i["step"] for i in items if not i["resolved"]]
        runbook_summaries.append({
            "runbook": runbook,
            "steps_observed": len(items),
            "resolved_steps": resolved_count,
            "success_rate": round(resolved_count / len(items), 2),
            "unresolved_steps": unresolved_steps,
            "recommended_update": (
                "add clearer rollback/dependency-owner guidance"
                if unresolved_steps
                else "no update needed"
            )
        })

    return {
        "total_steps_reviewed": total,
        "resolved_steps": resolved,
        "unresolved_steps": total - resolved,
        "escalation_triggers": escalated,
        "overall_success_rate": round(resolved / total, 2) if total else 0,
        "runbook_summaries": runbook_summaries
    }

def main():
    steps = json.loads(Path("runbook_quality/unresolved_steps.json").read_text())
    summary = analyze_runbook_quality(steps)

    Path("runbook_quality/runbook_quality_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    report = f"""# Runbook Gap Report

## Summary

- Total steps reviewed: {summary["total_steps_reviewed"]}
- Resolved steps: {summary["resolved_steps"]}
- Unresolved steps: {summary["unresolved_steps"]}
- Escalation triggers: {summary["escalation_triggers"]}
- Overall success rate: {summary["overall_success_rate"]}

## Runbook summaries

{json.dumps(summary["runbook_summaries"], indent=2)}

## Operational value

This workflow tracks repeated incident patterns, unresolved diagnostic steps, escalation triggers, and recommended runbook updates.
"""

    Path("runbook_quality/runbook_gap_report.md").write_text(report)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
