# AutoOps API Contracts

AutoOps exposes REST and GraphQL APIs for incident intelligence, recurrence tracking, service metrics, and dashboard-facing summaries.

## REST Endpoints

| Endpoint | Method | Purpose | Success Response | Error Cases | Test Coverage |
|---|---:|---|---|---|---|
| `/` | GET | Service root check | `{ "message": "AutoOps Insight is running!" }` | Service unavailable | `test_root_endpoint_returns_running_message` |
| `/healthz` | GET | Health check for deployment/runtime monitoring | `{ "status": "ok" }` | 404 if route not mounted, 500 if startup fails | `test_health_endpoint_returns_ok` |
| `/metrics` | GET | Prometheus-compatible service metrics | Prometheus text format | 500 if metrics registry fails | `test_metrics_endpoint_exposes_prometheus_text` |
| `/reports/summary` or `/release/summary` | GET | Dashboard/report summary | JSON summary of incidents and release risk | Empty history, schema mismatch | `test_dashboard_or_report_summary_endpoint_returns_expected_fields` |

## GraphQL Endpoint

### Endpoint

`POST /graphql`

### Query: `metricsSummary`

Returns dashboard-facing metrics over AutoOps incident history.

Request:

```graphql
{
  metricsSummary {
    totalAnalyses
    releaseBlockers
    releaseRisk
    topFailureFamilies {
      failureFamily
      totalCount
    }
    topRecurringSignatures {
      signature
      totalCount
      severity
    }
  }
}
Response fields:

Field	Type	Meaning
totalAnalyses	Integer	Number of incident analyses considered
releaseBlockers	Integer	Count of release-blocking incidents
releaseRisk	String	Computed release risk level
topFailureFamilies	List	Aggregated incident family counts
topRecurringSignatures	List	Repeated failure signatures
Query: incidents

Returns incident records.

{
  incidents(limit: 5) {
    id
    failureFamily
    severity
    signature
    releaseBlocking
    confidence
  }
}
Query: noisyServices

Returns service or owner groupings with incident counts.

{
  noisyServices {
    service
    totalCount
    releaseBlockingCount
  }
}
Query: recurrenceHeatmap

Returns repeated signatures and failure families.

{
  recurrenceHeatmap {
    failureFamily
    signature
    totalCount
    severity
  }
}
Error Handling Notes
GraphQL should return structured errors if a resolver fails.
Resolvers should tolerate older local SQLite rows by using safe .get(...) access.
Dashboard-facing endpoints should avoid assuming every local database has the newest migration columns.
Feature Review Notes

This API layer is designed to support dashboard clients without coupling frontend code directly to storage schema details.
