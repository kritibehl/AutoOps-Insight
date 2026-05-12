# Incident Search and Service Owner Dashboard

AutoOps includes a dashboard-facing incident search workflow for operational support and infrastructure roles.

## API endpoints

- `GET /incidents/search`
- `GET /service-owners/dashboard`
- `GET /incidents/{incident_id}/timeline`

## Search filters

- service
- owner
- severity
- status
- issue_family

## Why this matters

This turns incident analytics into an operator-facing workflow: service owners can filter incidents, review ownership, inspect current status, and view incident timelines.
