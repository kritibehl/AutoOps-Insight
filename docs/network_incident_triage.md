# Network Incident Triage

## Goal

AutoOps acts as the operator-facing triage and remediation layer for network-style incidents.

KubePulse provides raw network evidence. AutoOps converts that evidence into a structured incident summary with root cause, blast radius, remediation steps, rollback guidance, and escalation path.

## Input Sources

- KubePulse reachability reports
- KubePulse latency and dependency diagnostics
- release correlation metadata
- service-health metrics
- support ticket symptoms

## Required Triage Fields

Each network incident should include:

- `incident_id`
- `affected_service`
- `severity`
- `symptoms`
- `evidence`
- `likely_root_cause`
- `blast_radius`
- `recommended_remediation`
- `rollback_or_recovery_decision`
- `human_approval_required`
- `owner`
- `escalation_path`

## Example Flow

```text
KubePulse raw network evidence
        |
        v
AutoOps incident triage
        |
        v
root cause + blast radius + remediation
        |
        v
human-approved rollback or recovery decision
Human Approval Rule

AutoOps can recommend rollback, escalation, or remediation, but production-impacting actions require human approval.

Operator Value

This makes AutoOps a safe automation layer. It does not blindly remediate production systems; it summarizes evidence and recommends next actions for operators.
