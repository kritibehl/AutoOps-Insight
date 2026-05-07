# Feature Delivery Notes

## Feature: GraphQL Incident Analytics API

### Goal

Expose AutoOps incident history through a dashboard-friendly GraphQL API.

### User Story

As a dashboard client, I need to query incident records, noisy services, recurrence patterns, and release-risk summaries without calling multiple REST endpoints or understanding the storage schema.

### Implemented Queries

- `incidents`
- `incident(id)`
- `metricsSummary`
- `noisyServices`
- `recurrenceHeatmap`

### Validation

Covered by:

- `tests/test_graphql_metrics.py`
- `tests/test_service_metrics_api.py`
- `tests/test_dashboard_summary.py`

### Compatibility Notes

The local SQLite database may not always include newer fields such as `release_blocking` or `filename`. GraphQL resolvers should avoid direct dictionary indexing when reading optional fields and should compute dashboard summaries from available incident rows where possible.

### Review Checklist

- [ ] Endpoint is mounted at `/graphql`
- [ ] GraphQL query returns JSON without resolver errors
- [ ] Health endpoint returns OK
- [ ] Metrics endpoint emits Prometheus-compatible text
- [ ] Dashboard/report summary endpoint returns expected fields
- [ ] Tests pass locally
