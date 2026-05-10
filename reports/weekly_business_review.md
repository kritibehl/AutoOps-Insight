# Weekly Business Review — AutoOps Incident Intelligence

## Reporting period

2026-W18

## Executive summary

AutoOps analyzed 102 support and operational incidents across 5 sources and 6 issue families. The system identified 51 escalation cases, 19 AgentGrid events, and recurring blockers across unsafe responses, tool failures, and latency spikes.

## Key metrics

| Metric | Value |
|---|---:|
| Total incidents | 102 |
| Escalations | 51 |
| AgentGrid events ingested | 19 |
| Issue families | 6 |
| Top issue family | unsafe_response |

## Incident trend summary

| Issue family | Count | Escalations | Primary action |
|---|---:|---:|---|
| unsafe_response | 24 | 24 | escalate_to_safety_review |
| tool_failure | 24 | 24 | check_tool_dependency |
| latency_spike | 20 | 0 | hold_release |
| missing_context | 12 | 0 | fix_retrieval_pipeline |
| wrong_answer | 11 | 0 | support_review |
| retrieval_failure | 11 | 0 | tune_search_and_embeddings |

## Recurring issue families

- unsafe_response: highest escalation volume
- tool_failure: recurring dependency reliability pattern
- latency_spike: release-readiness risk
- missing_context: retrieval/context quality issue

## Data-quality and reporting checks

- Required fields present: service, severity, issue type, source, customer impact
- Issue-family classification applied
- Escalation path generated
- Service-health summary generated
- Business impact summary generated

## Stakeholder requests

| Stakeholder | Request |
|---|---|
| Product | summarize customer-impact patterns |
| Engineering | identify probable owners and runbook actions |
| Support | provide escalation paths and customer-facing next steps |
| Business Ops | track weekly volume and recurring issue categories |

## Recommended actions

1. Review unsafe_response escalation pattern with product/safety owners.
2. Investigate tool_failure recurrence with service owners.
3. Treat latency_spike as a release-readiness blocker.
4. Improve retrieval runbook for missing_context and retrieval_failure cases.
