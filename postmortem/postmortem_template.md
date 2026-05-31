# Blameless Postmortem

## Incident

INC-PROD-901

## Service

checkout-api

## Severity

sev1

## Customer impact

checkout requests delayed or failing for partner traffic

## What happened

checkout-api degraded after release deployment, with latency, retry, and dependency-timeout signals indicating an operational regression.

## Timeline

| Timestamp | Event |
|---|---|
| 2026-05-16T14:00:00Z | release-204 deployed |
| 2026-05-16T14:07:00Z | p95 latency increased by 212% |
| 2026-05-16T14:09:00Z | retry budget exceeded |
| 2026-05-16T14:12:00Z | payment dependency timeout cluster detected |
| 2026-05-16T14:18:00Z | rollback review started |

## Contributing factors

- deployment correlated with latency spike
- retry budget exceeded shortly after rollout
- payment dependency timeout cluster appeared during incident window

## Corrective actions

- add dependency timeout regression coverage
- tighten retry-budget alerting
- document rollback criteria
- add deployment correlation review

## Blameless note

This review focuses on system behavior, detection gaps, and process improvements, not individual fault.
