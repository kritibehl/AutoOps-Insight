# Network Incident Summary

## Incident

`NET-204`

## Affected service

`checkout-api`

## Severity

`sev2`

## Source signals

This incident combines operator-facing evidence from KubePulse-style service diagnostics and Faultline-style network fault scenarios.

## Likely root cause

Dependency reachability degradation after release.

## Evidence

- TCP reachability failure to `payment-api:443`
- p95 latency increased by 240%
- retry storm detected
- `release-204` correlated with incident window
- Faultline profile matched `high_latency` + `partial_partition`

## Owner

`checkout_platform_team`

## Escalation path

1. support_l1
2. sre_oncall
3. network_production_engineering
4. checkout_platform_team

## Operational value

This report converts network-style telemetry, dependency reachability failures, release correlation, and fault-injection evidence into an operator-ready triage summary.
