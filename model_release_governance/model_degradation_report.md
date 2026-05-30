# Model Degradation Report

## Release

`model-release-2026-05-mlr-01`

## Model

`runbook-recommendation-model`

## Release status

rollback recommended

## Degradation signals

| Signal | Baseline | Candidate | Result |
|---|---:|---:|---|
| accuracy | 0.86 | 0.79 | regression |
| latency_ms | 210 | 390 | regression |
| feature drift | none | incident_family | drift detected |

## Release flow

```text
deploy candidate
        |
        v
monitor canary metrics
        |
        v
detect quality + latency regression
        |
        v
rollback candidate model
Operational interpretation

The candidate model shows prediction-quality degradation, latency regression, and feature drift during canary rollout. AutoOps marks the release for rollback and routes the decision to ML platform review.

Follow-up actions
continue serving baseline model
inspect training-data distribution shift
add regression test coverage for incident-family features
compare runbook recommendation quality on recent support incidents
require human review before retrying rollout
