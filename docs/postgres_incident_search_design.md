# PostgreSQL Incident Search Design

The incident-search workflow is designed around PostgreSQL-backed incident tables.

## Intended tables

- incidents
- service_health
- escalations
- reporting_snapshots

## Query patterns

- filter by service owner
- filter by severity
- filter by lifecycle status
- filter by issue family
- timeline lookup by incident ID
- service-owner workload summaries

## Production migration path

The current API uses demo-safe incident records for Cloud Run visibility, while the PostgreSQL schema and Alembic migration artifacts define the persistent backend path.
