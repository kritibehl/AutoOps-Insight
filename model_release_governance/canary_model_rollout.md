# Canary Model Rollout

## Model

`runbook-recommendation-model`

## Release

`model-release-2026-05-mlr-01`

## Rollout stages

| Stage | Traffic | Monitoring focus | Decision |
|---|---:|---|---|
| baseline | 0% candidate | current model health | continue |
| canary-1 | 10% candidate | accuracy, latency, feature drift | monitor |
| canary-2 | 25% candidate | quality regression, latency regression | hold |
| rollback review | 0% candidate | degraded model health | rollback |

## Monitored signals

- prediction accuracy
- latency regression
- feature drift
- degraded model count
- quality regression count
- support-impact risk

## Rollback criteria

Rollback is recommended when:

- candidate accuracy drops by 5% or more
- latency increases by 35% or more
- feature drift is detected on high-impact fields
- support workflows show degraded recommendation quality

## Operational interpretation

This rollout models ML release governance for an operational support model, connecting deployment stages to monitoring signals and rollback decision criteria.
