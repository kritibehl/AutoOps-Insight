# NPE Incident Response Playbook

## Goal

Provide an operator-facing workflow for network-style production incidents using AutoOps as the triage and remediation layer.

## Inputs

AutoOps can consume or reference outputs from:

- KubePulse network diagnostics
- Faultline network partition/fault reports
- service-health telemetry
- release correlation reports
- support ticket summaries

## Triage fields

Each incident should identify:

- incident type
- affected service
- severity
- likely root cause
- evidence
- customer impact
- recommended remediation
- owner
- escalation path

## Network-style signals

| Signal | Meaning |
|---|---|
| DNS failure | service discovery or resolver issue |
| TCP reachability failure | endpoint routing, firewall, or dependency availability issue |
| high latency | congestion, timeout budget, overloaded dependency, or bad release |
| retry storm | client-side amplification or dependency degradation |
| partial partition | asymmetric reachability or stale worker/dependency behavior |
| release correlation | possible deployment/config regression |

## Escalation paths

| Condition | Escalate to |
|---|---|
| customer-visible latency | SRE on-call |
| dependency reachability failure | Network Production Engineering |
| release-correlated regression | release engineering + service owner |
| stale write or partition correctness risk | distributed systems owner |
| unresolved customer impact | support L2 / incident commander |

## Remediation workflow

1. Confirm service health and customer impact.
2. Check DNS resolution.
3. Check TCP reachability.
4. Compare incident window against release timeline.
5. Review dependency timeout/retry budgets.
6. Identify rollback candidate.
7. Route to service owner or network production engineering.
8. Document post-incident action items.

## Operator value

This playbook makes AutoOps the operator-facing layer that turns diagnostics from projects like KubePulse and Faultline into actionable triage, escalation, and remediation reports.
