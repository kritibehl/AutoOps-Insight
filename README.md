
## GraphQL Incident Analytics API

AutoOps exposes a GraphQL endpoint for dashboard clients at:

```text
POST /graphql
Metrics Summary
curl -s http://127.0.0.1:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ metricsSummary { totalAnalyses releaseBlockers releaseRisk topFailureFamilies { failureFamily totalCount } topRecurringSignatures { signature totalCount severity } } }"}' \
  | python3 -m json.tool
Incidents
curl -s http://127.0.0.1:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ incidents(limit: 5) { id failureFamily severity signature releaseBlocking confidence } }"}' \
  | python3 -m json.tool
Noisy Services + Recurrence Heatmap
curl -s http://127.0.0.1:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ noisyServices { service totalCount releaseBlockingCount } recurrenceHeatmap { failureFamily signature totalCount severity } }"}' \
  | python3 -m json.tool
API Test Coverage

AutoOps includes API tests for:

GraphQL metrics summaries
noisy service summaries
recurrence heatmaps
health checks
Prometheus metrics endpoint
dashboard/report summary responses

Run:

python3 -m pytest -q tests/test_graphql_metrics.py tests/test_service_metrics_api.py tests/test_dashboard_summary.py

