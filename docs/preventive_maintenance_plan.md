# AutoOps Preventive Maintenance Plan

## Purpose

This plan defines recurring checks to keep AutoOps reliable, testable, and maintainable as the API, GraphQL layer, incident schema, and dashboard clients evolve.

## Maintenance Goals

- Prevent schema drift from breaking dashboard/report endpoints
- Keep GraphQL resolvers compatible with older local data
- Maintain API test coverage for service-critical paths
- Keep dependencies documented and reproducible
- Preserve operational visibility through health checks and metrics
- Reduce recurring failures through structured incident review

## Weekly Checks

### 1. Run API Test Suite

```bash
python3 -m pytest -q tests/test_graphql_metrics.py tests/test_service_metrics_api.py tests/test_dashboard_summary.py

Expected:

all tests passing
2. Compile Core Modules
python3 -m py_compile main.py graphql_api.py storage/history.py
3. Verify GraphQL Endpoint
curl -s http://127.0.0.1:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ metricsSummary { totalAnalyses releaseBlockers releaseRisk } }"}' \
  | python3 -m json.tool
4. Verify Health and Metrics
curl -s http://127.0.0.1:8001/healthz
curl -s http://127.0.0.1:8001/metrics | head
Schema Compatibility Checks

Before adding new incident fields:

Confirm whether the field exists in old local SQLite data
Add compatibility defaults in read paths
Avoid direct dictionary indexing for optional fields
Add or update tests that cover missing-field behavior

Preferred pattern:

row.get("field_name")

or SQL fallback via:

PRAGMA table_info(analyses)
Dependency Maintenance

When adding a dependency:

Install in local venv
Add to requirements.txt
Re-run tests
Document why the dependency is needed

Current test-critical dependencies:

pytest
httpx
fastapi
strawberry-graphql
prometheus-client
API Contract Maintenance

When adding or changing endpoints:

Update docs/api_contracts.md
Add request/response examples
Add expected error cases
Add or update API tests
Confirm dashboard clients are not tightly coupled to storage schema
Observability Maintenance

Maintain these operational endpoints:

Endpoint	Purpose
/healthz	Runtime health check
/metrics	Prometheus-compatible metrics
/graphql	Dashboard analytics API
/reports/summary or /release/summary	Dashboard/report summary
Incident Review Loop

For recurring incidents:

Identify repeated signatures
Check affected failure family
Review noisy service or owner grouping
Confirm release risk
Update runbook or troubleshooting guide
Add regression test if failure can recur
Release Readiness Checklist

Before merging a backend feature:

 Conflict markers removed
 Core files compile
 API tests pass
 GraphQL endpoint returns expected JSON
 Health check works
 Metrics endpoint works
 API contract docs updated
 Troubleshooting guide updated if a new failure mode was found
 README updated for user-facing commands
Long-Term Improvements
Add CI workflow for API tests
Add sample seeded test database
Add schema migration tests
Add Grafana dashboard export
Add Power BI screenshot/export proof
Add Azure Container Apps deployment example
