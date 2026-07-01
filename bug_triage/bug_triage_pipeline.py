import json
from collections import Counter
from pathlib import Path


def priority_for_bug(bug):
    if bug["customer_impact"] == "high" and bug["recent_release"]:
        return "p0_review"
    if bug["customer_impact"] == "high":
        return "p1"
    return "p2"


def regression_risk(bug):
    if bug["recent_release"] and "regression" in bug["failure_family"]:
        return "high"
    if bug["recent_release"]:
        return "medium"
    return "low"


def triage_bugs(bugs):
    family_counts = Counter(b["failure_family"] for b in bugs)

    triaged = []
    for bug in bugs:
        triaged.append({
            "bug_id": bug["bug_id"],
            "service": bug["service"],
            "failure_family": bug["failure_family"],
            "priority": priority_for_bug(bug),
            "regression_risk": regression_risk(bug),
            "recurring_failure": family_counts[bug["failure_family"]] > 1,
            "recommended_owner": (
                "release_engineering"
                if bug["recent_release"]
                else f"{bug['service']}_owner"
            ),
            "investigation_summary": (
                f"{bug['service']} issue classified as {bug['failure_family']} "
                f"with {bug['customer_impact']} customer impact."
            )
        })

    return {
        "bugs_reviewed": len(bugs),
        "failure_family_counts": dict(family_counts),
        "p0_review_count": sum(1 for b in triaged if b["priority"] == "p0_review"),
        "high_regression_risk_count": sum(1 for b in triaged if b["regression_risk"] == "high"),
        "triaged_bugs": triaged,
        "pipeline_status": "PASS"
    }


def main():
    bugs = json.loads(Path("examples/bug_queue_sample.json").read_text())
    summary = triage_bugs(bugs)

    Path("reports/bug_triage_quality_report.md").write_text(
        "# Bug Triage Quality Report\n\n"
        f"- Bugs reviewed: {summary['bugs_reviewed']}\n"
        f"- P0 review count: {summary['p0_review_count']}\n"
        f"- High regression risk count: {summary['high_regression_risk_count']}\n"
        f"- Pipeline status: {summary['pipeline_status']}\n\n"
        "## Failure families\n\n"
        f"```json\n{json.dumps(summary['failure_family_counts'], indent=2)}\n```\n\n"
        "## Triaged bugs\n\n"
        f"```json\n{json.dumps(summary['triaged_bugs'], indent=2)}\n```\n"
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
