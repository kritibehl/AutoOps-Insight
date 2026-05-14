import json
import xml.etree.ElementTree as ET
from pathlib import Path

REQUIRED_FIELDS = [
    "partner_id",
    "deployment_id",
    "event_type",
    "response_latency_ms",
    "retry_count",
]

def parse_partner_payload(path: str):
    xml_path = Path(path)
    errors = []
    extracted = {}

    try:
        root = ET.fromstring(xml_path.read_text())
    except ET.ParseError as exc:
        return {
            "valid": False,
            "parse_error": str(exc),
            "extracted_fields": {},
            "validation_errors": ["malformed_xml"],
            "support_routing_risk": "payload cannot be parsed; route to integration support for XML formatting review",
        }

    for field in REQUIRED_FIELDS:
        node = root.find(field)
        value = node.text.strip() if node is not None and node.text else None
        extracted[field] = value

        if value is None:
            errors.append(f"missing_required_field:{field}")

    # Type checks
    for numeric_field in ["response_latency_ms", "retry_count"]:
        value = extracted.get(numeric_field)
        if value is not None:
            try:
                int(value)
            except ValueError:
                errors.append(f"invalid_integer_field:{numeric_field}")

    latency_value = extracted.get("response_latency_ms") or ""
    retry_value = extracted.get("retry_count") or ""

    latency = int(latency_value) if latency_value.isdigit() else None
    retries = int(retry_value) if retry_value.isdigit() else None

    support_routing = "normal_review"
    if latency is not None and latency > 3000:
        support_routing = "route_to_latency_triage"
    if retries is not None and retries >= 3:
        support_routing = "route_to_integration_stability_review"

    return {
        "valid": len(errors) == 0,
        "extracted_fields": extracted,
        "validation_errors": errors,
        "support_routing_risk": support_routing,
        "integration_review_notes": [
            "deployment_id links partner issue to release-correlation workflows",
            "response_latency_ms and retry_count indicate whether timeout/retry instability affected the workflow",
            "missing or malformed XML fields can block support routing and delay incident triage",
        ],
    }

def main():
    result = parse_partner_payload("integrations/sample_partner_payload.xml")

    out_json = Path("integrations/partner_payload_validation_summary.json")
    out_json.write_text(json.dumps(result, indent=2))

    report = Path("integrations/xml_validation_report.md")
    fields = result.get("extracted_fields", {})
    errors = result.get("validation_errors", [])

    report.write_text(f"""# XML Validation Report

## Summary

Partner XML payload parsed and validated for integration-support review.

## Validation result

- valid: `{result["valid"]}`
- support routing risk: `{result["support_routing_risk"]}`

## Extracted fields

| Field | Value |
|---|---|
| partner_id | {fields.get("partner_id")} |
| deployment_id | {fields.get("deployment_id")} |
| event_type | {fields.get("event_type")} |
| response_latency_ms | {fields.get("response_latency_ms")} |
| retry_count | {fields.get("retry_count")} |

## Validation errors

{chr(10).join(f"- {e}" for e in errors) if errors else "- none"}

## Support impact

Malformed XML or missing required fields can prevent AutoOps from routing partner incidents to the correct support workflow. Missing `deployment_id` weakens release-correlation analysis, while invalid latency or retry fields can hide timeout and integration instability signals.

## Operational interpretation

This payload maps partner integration symptoms to deployment evidence, latency checks, retry analysis, and support-routing decisions.
""")

    print(json.dumps(result, indent=2))
    print(f"Wrote {out_json}")
    print(f"Wrote {report}")

if __name__ == "__main__":
    main()
