import json
from collections import Counter, defaultdict
from pathlib import Path

def summarize_patterns(incidents):
    family_counts = Counter(i["failure_family"] for i in incidents)
    blocker_counts = Counter(i["customer_blocker"] for i in incidents)

    by_family = defaultdict(list)
    for incident in incidents:
        by_family[incident["failure_family"]].append(incident)

    reusable_patterns = []
    for family, items in by_family.items():
        reusable_patterns.append({
            "failure_family": family,
            "count": len(items),
            "common_symptoms": sorted({i["symptom"] for i in items}),
            "customer_blockers": sorted({i["customer_blocker"] for i in items}),
            "recommended_operational_actions": sorted({i["recommended_action"] for i in items}),
        })

    top_family = family_counts.most_common(1)[0][0] if family_counts else None

    return {
        "total_incidents_reviewed": len(incidents),
        "top_failure_family": top_family,
        "failure_family_distribution": dict(family_counts),
        "customer_blocker_distribution": dict(blocker_counts),
        "reusable_incident_patterns": reusable_patterns,
    }

def main():
    incidents = json.loads(Path("genai_incidents/recurring_genai_failures.json").read_text())
    summary = summarize_patterns(incidents)

    Path("field_patterns/recurring_rag_failure_patterns.json").write_text(
        json.dumps(summary, indent=2)
    )

    report = f"""# Field Pattern Summary

## Total incidents reviewed

{summary["total_incidents_reviewed"]}

## Top recurring failure family

{summary["top_failure_family"]}

## Failure family distribution

{json.dumps(summary["failure_family_distribution"], indent=2)}

## Customer blocker distribution

{json.dumps(summary["customer_blocker_distribution"], indent=2)}

## Reusable incident patterns

{json.dumps(summary["reusable_incident_patterns"], indent=2)}

## Operational interpretation

AutoOps converts recurring GenAI field incidents into reusable issue patterns, customer blocker summaries, and engineering-facing recommendations.
"""

    Path("field_patterns/field_pattern_summary.md").write_text(report)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
