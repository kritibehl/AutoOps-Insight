# PostgreSQL Migration Guide

AutoOps supports PostgreSQL-backed operational analytics tables for incident, service-health, escalation, and reporting workflows.

## Tables

- `incidents`
- `service_health`
- `escalations`
- `reporting_snapshots`

## Local setup

```bash
createdb autoops
alembic upgrade head
psql autoops < sql/seed/postgres_seed_data.sql
Environment variable
export DATABASE_URL="postgresql+psycopg2://localhost/autoops"
Purpose

This migration adds schema-backed support analytics for SQL-driven operational analysis, reporting, escalation tracking, and service-health summaries.
