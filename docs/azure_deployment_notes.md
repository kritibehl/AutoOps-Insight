# Azure-Adjacent Deployment Notes

These notes describe how AutoOps could be deployed as a containerized API on Azure. This is deployment documentation, not a claim of production Azure hosting.

## Container Image

Build:

```bash
docker build -t autoops-api:local .
Run locally:

docker run --rm -p 8000:8000 \
  -e AUTOOPS_DB_PATH=/tmp/autoops.db \
  autoops-api:local
Candidate Azure Services
Azure Container Apps
Azure App Service for Containers
Azure Container Registry
Azure Monitor / Log Analytics
Required Configuration
Variable	Purpose	Example
AUTOOPS_DB_PATH	SQLite DB path for local/demo mode	/tmp/autoops.db
DATABASE_URL	Optional managed database connection string	postgresql://...
ALLOWED_ORIGINS	Frontend/dashboard CORS origins	https://example-dashboard.azurewebsites.net
Health Check

Use:

GET /healthz

Expected:

{ "status": "ok" }
Metrics

Use:

GET /metrics

This endpoint exposes Prometheus-compatible metrics that can be scraped or adapted for Azure Monitor-style dashboards.

Logging

Recommended production logging:

structured JSON logs
request ID per request
error-level logging for failed analyses
latency logging for dashboard/API endpoints
separate logs for ingestion, classification, GraphQL, and reporting
Production Hardening Notes

Before production deployment:

replace local SQLite with managed PostgreSQL
store secrets in Azure Key Vault
restrict public ingress
configure authenticated dashboard/API access
enable request tracing
configure deployment rollback strategy
run API tests in CI before deployment
