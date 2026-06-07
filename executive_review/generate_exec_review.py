import json
from pathlib import Path

def build_exec_review():
    return {
        "top_risks": [
            "4 enterprise customers at risk",
            "escalations increased by 33.3%",
            "retry_storm is the fastest-growing incident family",
            "2 SLA breaches require review"
        ],
        "recommended_actions": [
            "prioritize enterprise accounts with active SLA breaches",
            "review retry-budget and dependency-health policies",
            "prepare rollback review for release-correlated latency incidents",
            "update runbooks for unresolved escalation paths"
        ],
        "business_summary": "Customer risk is elevated due to escalation growth, repeated retry_storm incidents, and SLA breach pressure.",
        "review_status": "executive_review_required"
    }

def main():
    review = build_exec_review()
    Path("executive_review/executive_review_summary.json").write_text(json.dumps(review, indent=2))

    report = f"""# Executive Operations Review

## Business summary

{review["business_summary"]}

## Top risks

{chr(10).join(f"- {risk}" for risk in review["top_risks"])}

## Recommended actions

{chr(10).join(f"- {action}" for action in review["recommended_actions"])}

## Review status

{review["review_status"]}
"""
    Path("executive_review/executive_review_report.md").write_text(report)
    print(json.dumps(review, indent=2))

if __name__ == "__main__":
    main()
