# Ticket Lifecycle Report

## Purpose

This report tracks support-ticket ownership, SLA status, triage timing, escalation age, and recommended next actions.

## Ticket lifecycle fields

| Field | Meaning |
|---|---|
| ticket_id | Support ticket identifier |
| service | Affected service |
| severity | Impact level |
| created_at | Ticket creation time |
| status | Current lifecycle state |
| owner | Current owner/team |
| sla_due_at | SLA target timestamp |
| sla_breached | Whether SLA was missed |
| time_to_triage | Time from creation to triage |
| time_to_resolution | Time from creation to resolution |
| escalation_count | Number of escalations |
| recommended_next_action | Operational next step |

## Current summary

- Total tickets: 4
- Open tickets: 3
- Resolved tickets: 1
- SLA breaches: 2
- Average time to triage: 31.75 minutes
- High-priority open tickets: 2

## Operational review

AgentGrid has the highest support load and SLA breach risk due to unsafe response and tool-failure patterns. Reporting API is degraded but currently within SLA.
