# Partner Support Triage

## Goal

AutoOps provides partner-support triage workflows that classify external integration issues, estimate severity, collect evidence, and recommend the right action path.

## Supported Issue Types

| Issue type | Examples |
|---|---|
| playback | video playback failure, latency, buffering |
| API | endpoint errors, 403/404/500 responses, schema mismatch |
| authentication | token scope failure, OAuth issue, expired credentials |
| dashboard | missing analytics, dashboard load failure |
| data quality | missing rows, delayed exports, inconsistent aggregates |

## Required Output Fields

Each partner issue should produce:

- issue type
- affected partner
- affected service
- severity
- confidence
- recommended action
- evidence
- likely root cause
- escalation path
- partner-safe summary

## Recommended Actions

| Condition | Recommended action |
|---|---|
| partner misconfiguration | partner_fix |
| internal service regression | internal_escalation |
| release-correlated outage | rollback |
| weak signal / low impact | monitor |

## Evidence Sources

- HTTP status
- browser/network logs
- service logs
- API response body
- SQL signal
- recent release correlation
- dashboard/export metrics

## Example Decision

```json
{
  "issue_type": "API",
  "affected_partner": "external_integration_partner",
  "severity": "high",
  "confidence": 0.82,
  "recommended_action": "internal_escalation"
}
Operational Value

This workflow makes AutoOps useful for partner support, technical solutions engineering, TAM workflows, FDE workflows, and support escalation review.
