# Metric Scope

The support-validation metrics in this repository are generated from controlled failure scenarios across AgentGrid, KubePulse, Faultline, FairEval, and CI-style logs.

They are not customer production incidents.

## Why this matters

The goal is to demonstrate production-style incident intelligence behavior in a safe and reproducible environment:

- ingesting structured events
- classifying failure families
- detecting recurrence
- generating support actions
- producing engineering follow-up summaries
- exposing release-risk and escalation metrics

## Current support-validation snapshot

| Metric | Value |
|---|---:|
| Support-validation incidents | 102 |
| Escalations | 51 |
| Sources | 5 |
| Issue families | 6 |
| Unsafe shipments | 0 |

## Source systems

- AgentGrid
- KubePulse
- Faultline
- FairEval
- CI-style logs
