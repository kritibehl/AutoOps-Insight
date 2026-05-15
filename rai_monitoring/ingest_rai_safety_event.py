import json
from pathlib import Path

REQUIRED_FIELDS = [
    "evaluation_run_id",
    "source_service",
    "release_decision",
    "safety_regressions",
    "false_allows",
    "risk_categories",
    "recommended_mitigation",
]

def validate_event(event: dict):
    missing = [field for field in REQUIRED_FIELDS if field not in event]
    errors = []

    if missing:
        errors.extend([f"missing_required_field:{field}" for field in missing])

    if not isinstance(event.get("risk_categories", []), list):
        errors.append("invalid_field:risk_categories_must_be_list")

    return errors

def severity_for_event(event: dict):
    if event.get("release_decision") == "block" or event.get("false_allows", 0) > 0:
        return "sev1"
    if event.get("safety_regressions", 0) >= 3:
        return "sev2"
    return "sev3"

def normalize_rai_event(event: dict):
    errors = validate_event(event)
    if errors:
        return {
            "valid": False,
            "validation_errors": errors,
            "normalized_event": None,
        }

    normalized = {
        "incident_id": f"RAI-{event['evaluation_run_id']}",
        "incident_type": "responsible_ai_safety_regression",
        "severity": severity_for_event(event),
        "release_impact": "blocked" if event["release_decision"] == "block" else "review",
        "review_required": event.get("false_allows", 0) > 0 or event["release_decision"] == "block",
        "risk_family": "safety_regression",
        "source_service": event["source_service"],
        "source_run_id": event["evaluation_run_id"],
        "recommended_action": event["recommended_mitigation"],
        "owner": "ai_safety_review_queue",
        "human_review_required": True,
        "status": "open",
        "safety_regressions": event["safety_regressions"],
        "false_allows": event["false_allows"],
        "risk_categories": event["risk_categories"],
    }

    return {
        "valid": True,
        "validation_errors": [],
        "normalized_event": normalized,
    }

def main():
    event = json.loads(Path("rai_monitoring/sample_rai_safety_event.json").read_text())
    result = normalize_rai_event(event)

    out = Path("ai_safety_incidents/responsible_ai_incident_summary.json")
    out.write_text(json.dumps(result["normalized_event"], indent=2))

    report = Path("rai_monitoring/rai_event_validation_report.md")
    report.write_text(f"""# Responsible AI Event Validation Report

## Source

- source_service: `{event.get("source_service")}`
- evaluation_run_id: `{event.get("evaluation_run_id")}`

## Validation

- valid: `{result["valid"]}`
- validation_errors: `{result["validation_errors"]}`

## Normalized incident

```json
{json.dumps(result["normalized_event"], indent=2)}
Operational interpretation

FairEval safety-regression outputs are converted into AutoOps monitoring records with severity, release impact, human-review routing, owner assignment, and release-block action.
""")

print(json.dumps(result, indent=2))

if name == "main":
main()
