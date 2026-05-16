# AIOps Incident Context Report

## Incident

INC-204

## Service

checkout-api

## Severity

sev1

## Real-time triage summary

Checkout Api latency and error rates spiked after release-204, with retries concentrated around payment dependency timeouts. Observed p95 latency delta: 212%, error-rate delta: 8.4%.

## Probable root-cause hypotheses

[
  {
    "cause": "payment dependency timeout cascade",
    "confidence": "high",
    "evidence": [
      "retry spike",
      "timeout log cluster",
      "p95 latency increase",
      "error rate increase"
    ]
  }
]

## Historical context

[
  {
    "matched_incident": "INC-137",
    "similarity_reason": "same service, retry spike, upstream timeout pattern",
    "previous_resolution": "rollback candidate release and dependency timeout mitigation"
  }
]

## Recommended next actions

- check dependency saturation
- compare against release-204
- review retry budget and rollback candidate
- inspect payment dependency timeout/error dashboards
- notify service owner and incident commander for sev1 review

## Operational value

This workflow synthesizes telemetry signals, logs, recent deployment metadata, and historical incident patterns into a triage-ready context packet for incident management workflows.
