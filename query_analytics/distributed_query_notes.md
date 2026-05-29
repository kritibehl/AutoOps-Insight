# Trino-Style Distributed Query Notes

## Purpose

AutoOps includes Trino-style distributed query examples over warehouse-ready operational telemetry outputs.

## Query layer assumptions

The query layer assumes data has already been prepared into:

- `fact_operational_event`
- `fact_service_health_daily`
- `dim_service`
- `dim_region`

## Supported query patterns

- service-health summaries
- anomaly drilldowns
- regional latency trends
- service-owner dashboards
- monitoring and incident-review reports

## Why Trino-style

A distributed SQL query layer can query warehouse-ready telemetry across service, region, event-time, and anomaly dimensions without requiring each dashboard to know the ingestion or aggregation internals.

## Safe project scope

This project documents Trino-style SQL query patterns. It does not claim operation of a production Trino cluster.
