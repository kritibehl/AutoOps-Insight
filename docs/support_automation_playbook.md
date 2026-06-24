# Support Automation Playbook

## Goal

AutoOps supports L1/L2-style issue review by converting customer-reported symptoms and operational signals into structured triage outputs, escalation paths, and engineering feedback.

## Inputs

- support ticket
- affected customer
- service name
- issue family
- release correlation
- latency/error metrics
- customer impact
- recurring failure signature

## Triage Output

Each ticket should produce:

- severity
- suspected cause
- evidence
- operational risk
- recommended action
- review-required state
- escalation target
- customer-safe summary

## Escalation Paths

| Condition | Escalation |
|---|---|
| customer-impacting latency regression | SRE |
| recurring dependency timeout | service owner |
| release-correlated regression | release engineering |
| unsafe AI output or false allow | AI safety review |
| unclear ownership | support L2 review |

## Review-Required States

A ticket requires review when:

- SLA breach is present
- customer impact is medium/high
- issue family is recurring
- release correlation is detected
- rollback candidate is true
- root-cause hypothesis points to infrastructure or deployment regression

## Feedback Loop

Recurring signatures should generate:

- runbook update
- release gate improvement
- service-owner review
- monitoring dashboard update
- customer-safe communication template

## Operational Value

This playbook makes AutoOps read as support automation tooling, not just generic incident triage. It connects L1/L2 support review, SRE escalation, root-cause summaries, release risk, and engineering feedback loops.
