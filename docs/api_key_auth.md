# API-Key Auth and Role-Aware Support Actions

AutoOps supports API-key protected support workflows using the `X-AutoOps-Token` header.

## Roles

| Token | Role |
|---|---|
| support-l1-token | support_l1 |
| service-owner-token | service_owner |
| admin-token | admin |
| dev-token | admin |

## Permissions

| Role | Permissions |
|---|---|
| support_l1 | ingest, read_reports |
| service_owner | ingest, read_reports, escalate |
| admin | ingest, read_reports, escalate, admin |

## Protected endpoints

- `POST /support/ingest/protected`
- `GET /reports/service-health/protected`
- `POST /incidents/{incident_id}/escalate/protected`

## Purpose

This provides lightweight API-key protection and role-aware access paths for support ingestion, reporting, escalation, and service-owner workflows.
