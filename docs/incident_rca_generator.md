# Incident RCA Generator

AutoOps includes an RCA generator that converts deployment-to-incident correlation outputs into postmortem-style summaries.

## Inputs

- linked deployment
- incident spike
- impacted services
- timeline
- escalation chain
- rollback candidate
- release risk

## Outputs

- probable cause
- impacted services
- timeline
- rollback candidate decision
- next actions
- generated RCA markdown

## Why this matters

RCA generation turns operational telemetry into incident review artifacts for support, platform, and release engineering workflows.
