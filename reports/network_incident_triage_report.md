# Network Incident Triage Report

## Incident ID

`NET-204`

## Affected Service

`checkout-api`

## Severity

`sev2`

## Symptoms

- checkout latency spike after release
- retry storm detected
- payment dependency timeout errors
- customer-facing requests delayed

## Evidence

- TCP reachability failure to `payment-api:443`
- p95 latency increased by 240%
- error rate increased by 3.2%
- `release-204` matched the incident window
- dependency reachability degraded after rollout

## Likely Root Cause

Dependency reachability degradation after release.

## Blast Radius

| Field | Value |
|---|---|
| Customers impacted | enterprise traffic |
| Services impacted | checkout-api, payment-api |
| Risk level | medium_high |

## Recommended Remediation

1. Verify DNS resolution for `payment-api`.
2. Test TCP reachability to `payment-api:443`.
3. Review `release-204` network and routing changes.
4. Inspect retry budget and dependency timeout configuration.
5. Prepare rollback if reachability failures persist.

## Rollback or Recovery Decision

`rollback_candidate`

## Human Approval Required

`true`

## Owner / Escalation Path

1. support_l1
2. sre_oncall
3. network_production_engineering
4. checkout_platform_team

## Operator Summary

KubePulse gives raw network evidence, and AutoOps turns it into an operator-ready incident summary with root cause, blast radius, remediation, rollback guidance, and escalation path.

## Safe Automation Note

AutoOps recommends remediation and rollback readiness, but human approval is required before rollback or production-impacting recovery actions.
