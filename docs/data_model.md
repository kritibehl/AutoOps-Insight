# Data Model

AutoOps models CI failures as structured incidents.

## Incident Fields

- repo_name
- workflow_name
- incident_type
- failure_family
- signature (for recurrence tracking)
- recurrence_total
- confidence
- likely_trigger
- root_cause
- release_decision
- decision_confidence
- action

## Key Concepts

- Signature → stable fingerprint for recurrence detection
- Failure family → normalized classification
- Action → release decision (hold_release / investigate)
