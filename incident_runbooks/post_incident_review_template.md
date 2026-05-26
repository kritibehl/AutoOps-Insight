# Production Incident Runbook Automation

## Incident

INC-PROD-901

## AI-assisted runbook summary

checkout-api degraded after release-204. p95 latency increased by 212% and error rate increased by 8.4%. Retry spike and dependency timeout evidence detected.

## Incident timeline

| Step | Timestamp | Event |
|---:|---|---|
| 1 | 2026-05-16T14:00:00Z | release-204 deployed to checkout-api |
| 2 | 2026-05-16T14:07:00Z | p95 latency increased by 212% |
| 3 | 2026-05-16T14:09:00Z | retry budget exceeded |
| 4 | 2026-05-16T14:12:00Z | payment dependency timeout cluster detected |

## Rollback recommendation

{
  "rollback_candidate": true,
  "deployment_id": "release-204",
  "reason": "sev1 latency spike and retry exhaustion detected after deployment",
  "recommended_action": "prepare rollback review"
}

## Post-incident review template

{
  "incident_id": "INC-PROD-901",
  "service": "checkout-api",
  "severity": "sev1",
  "customer_impact": "checkout requests delayed or failing for partner traffic",
  "timeline_steps": 4,
  "rollback_candidate": true,
  "service_health_evidence": {
    "status": "degraded",
    "p95_latency_delta_pct": 212,
    "error_rate_delta_pct": 8.4,
    "retry_spike": true
  },
  "follow_up_items": [
    "add dependency timeout regression coverage",
    "tighten retry-budget alerting",
    "document rollback criteria",
    "add deployment correlation review"
  ]
}

## Operational value

This workflow converts deployment context, incident events, service-health evidence, and logs into a production-review artifact with rollback guidance and follow-up actions.
