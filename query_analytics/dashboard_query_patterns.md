# Dashboard Query Patterns

## Dashboard tiles

| Tile | Query source | Purpose |
|---|---|---|
| Service health summary | `fact_service_health_daily` | monitor daily latency/error/anomaly counts |
| Top impacted services | `fact_operational_event` + `dim_service` | identify services with repeated anomalies |
| Regional latency trends | `fact_operational_event` + `dim_region` | detect region-specific degradation |
| Service-owner review | `dim_service` + event facts | route operational review to owner teams |
| Anomaly drilldown | event-level fact table | inspect individual high-risk telemetry events |

## Query-readiness checklist

- fact tables expose event counts and anomaly flags
- dimension tables expose service and region metadata
- dashboards can aggregate by service, region, day, and owner
- anomaly drilldowns preserve event-level detail
- operational reports can separate daily summaries from raw telemetry

## Operational value

These query patterns make AutoOps dashboard outputs more realistic for monitoring, analytics, service-health review, and incident investigation workflows.
