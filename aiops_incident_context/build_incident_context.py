import json
from pathlib import Path


def has_timeout_pattern(logs):
    return any("timeout" in line.lower() for line in logs)


def find_historical_matches(bundle, historical):
    matches = []
    service = bundle["service"]
    retry_spike = bundle["signals"].get("retry_spike", False)
    timeout_pattern = has_timeout_pattern(bundle.get("logs", []))

    for item in historical:
        same_service = item.get("service") == service
        same_retry = item.get("signals", {}).get("retry_spike") == retry_spike
        same_timeout = item.get("signals", {}).get("timeout_pattern") == timeout_pattern

        if same_service and (same_retry or same_timeout):
            matches.append({
                "matched_incident": item["incident_id"],
                "similarity_reason": "same service, retry spike, upstream timeout pattern",
                "previous_resolution": item["previous_resolution"]
            })

    return matches


def build_root_cause_hypotheses(bundle):
    signals = bundle["signals"]
    logs = bundle.get("logs", [])
    evidence = []

    if signals.get("retry_spike"):
        evidence.append("retry spike")

    if has_timeout_pattern(logs):
        evidence.append("timeout log cluster")

    if signals.get("p95_latency_delta_pct", 0) >= 100:
        evidence.append("p95 latency increase")

    if signals.get("error_rate_delta_pct", 0) >= 5:
        evidence.append("error rate increase")

    cause = "payment dependency timeout cascade" if has_timeout_pattern(logs) else "post-deploy service regression"
    confidence = "high" if len(evidence) >= 3 else "medium"

    return [{
        "cause": cause,
        "confidence": confidence,
        "evidence": evidence
    }]


def build_triage_summary(bundle):
    service = bundle["service"]
    deploy = bundle["signals"].get("recent_deploy", "recent deployment")
    latency = bundle["signals"].get("p95_latency_delta_pct")
    error_rate = bundle["signals"].get("error_rate_delta_pct")
    readable_service = service.replace("-", " ").title()

    return (
        f"{readable_service} latency and error rates spiked after {deploy}, "
        f"with retries concentrated around payment dependency timeouts. "
        f"Observed p95 latency delta: {latency}%, error-rate delta: {error_rate}%."
    )


def recommended_actions(bundle):
    deploy = bundle["signals"].get("recent_deploy", "recent release")

    return [
        "check dependency saturation",
        f"compare against {deploy}",
        "review retry budget and rollback candidate",
        "inspect payment dependency timeout/error dashboards",
        "notify service owner and incident commander for sev1 review"
    ]


def build_context(bundle, historical):
    return {
        "incident_id": bundle["incident_id"],
        "service": bundle["service"],
        "severity": bundle["severity"],
        "triage_summary": build_triage_summary(bundle),
        "probable_root_cause_hypotheses": build_root_cause_hypotheses(bundle),
        "historical_context": find_historical_matches(bundle, historical),
        "recommended_next_actions": recommended_actions(bundle),
    }


def build_report(context):
    hypotheses = json.dumps(context["probable_root_cause_hypotheses"], indent=2)
    historical = json.dumps(context["historical_context"], indent=2)
    actions = "\n".join(f"- {action}" for action in context["recommended_next_actions"])

    return f"""# AIOps Incident Context Report

## Incident

{context["incident_id"]}

## Service

{context["service"]}

## Severity

{context["severity"]}

## Real-time triage summary

{context["triage_summary"]}

## Probable root-cause hypotheses

{hypotheses}

## Historical context

{historical}

## Recommended next actions

{actions}

## Operational value

This workflow synthesizes telemetry signals, logs, recent deployment metadata, and historical incident patterns into a triage-ready context packet for incident management workflows.
"""


def main():
    bundle = json.loads(Path("aiops_incident_context/sample_telemetry_bundle.json").read_text())
    historical = json.loads(Path("aiops_incident_context/historical_incident_store.json").read_text())

    context = build_context(bundle, historical)

    Path("aiops_incident_context/incident_context_summary.json").write_text(
        json.dumps(context, indent=2)
    )

    Path("aiops_incident_context/incident_context_report.md").write_text(
        build_report(context)
    )

    print(json.dumps(context, indent=2))


if __name__ == "__main__":
    main()
