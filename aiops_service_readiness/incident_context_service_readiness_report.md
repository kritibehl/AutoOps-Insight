# AIOps Incident Context Service Readiness Report

## Endpoint

https://autoops-api-126325674316.us-central1.run.app/aiops/incident-context/demo

## Benchmark summary

| Metric | Value |
|---|---:|
| total_requests | 10 |
| successful_responses | 10 |
| failed_requests | 0 |
| schema_valid_responses | 10 |
| p50_latency_ms | 188.12 |
| p95_latency_ms | 2234.87 |
| max_latency_ms | 2234.87 |
| health_check_success_rate | 1.0 |
| readiness_status | PASS |

## Required fields checked

{
  "incident_id": 10,
  "triage_summary": 10,
  "probable_root_cause_hypotheses": 10,
  "historical_context": 10,
  "recommended_next_actions": 10
}

## Operational interpretation

This benchmark validates that the live AIOps incident-context endpoint returns successful responses, required incident-context fields, and latency summaries suitable for service-readiness review.
