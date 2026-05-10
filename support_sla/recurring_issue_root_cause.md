# Recurring Issue Root Cause Report

## Top recurring issue families

| Issue family | Likely root cause | Recommended action |
|---|---|---|
| tool_failure | external_tool_or_api_error | review dependency health and retry behavior |
| unsafe_response | safety_policy_or_guardrail_gap | escalate to safety review before launch readiness |
| latency_or_timeout | dependency_latency_or_timeout_budget | review recent deploys, upstream latency, and timeout settings |

## Root-cause interpretation

The strongest recurring patterns are tool dependency failures, unsafe responses requiring safety review, and latency/timeouts following service or deployment changes.

## Recommended operational actions

1. Improve runbook coverage for tool dependency failures.
2. Route unsafe responses to product/safety review.
3. Review latency regressions during release-readiness checks.
4. Add weekly SLA review to support business review workflow.
