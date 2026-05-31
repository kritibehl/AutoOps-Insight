# Runbook Gap Report

## Summary

- Total steps reviewed: 4
- Resolved steps: 2
- Unresolved steps: 2
- Escalation triggers: 2
- Overall success rate: 0.5

## Runbook summaries

[
  {
    "runbook": "checkout-api-latency",
    "steps_observed": 3,
    "resolved_steps": 2,
    "success_rate": 0.67,
    "unresolved_steps": [
      "identify rollback criteria"
    ],
    "recommended_update": "add clearer rollback/dependency-owner guidance"
  },
  {
    "runbook": "payment-dependency-timeout",
    "steps_observed": 1,
    "resolved_steps": 0,
    "success_rate": 0.0,
    "unresolved_steps": [
      "confirm dependency owner"
    ],
    "recommended_update": "add clearer rollback/dependency-owner guidance"
  }
]

## Operational value

This workflow tracks repeated incident patterns, unresolved diagnostic steps, escalation triggers, and recommended runbook updates.
