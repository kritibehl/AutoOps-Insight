# Dimensional Modeling Notes

## Model

AutoOps uses a simple star-schema style design for operational telemetry.

## Dimensions

- `dim_service`
- `dim_region`

## Facts

- `fact_operational_event`
- `fact_service_health_daily`

## Query patterns

- service-level anomaly counts
- regional latency trends
- daily operational health summaries
- incident-monitoring dashboards
- escalation and service-owner reports

## Why this matters

This design supports SQL analytics, monitoring reports, and dashboard-ready operational telemetry.
