# API Contracts

## GET /support/metrics/live

Returns:
- incident counts
- issue-family breakdowns
- escalation counts
- AgentGrid metrics
- customer blockers

## POST /incidents/{incident_id}/transition/live

Tracks lifecycle transitions:
- new
- triaged
- acknowledged
- escalated
- suppressed
- resolved
- reopened

Includes:
- actor
- audit log output
- transition reason
