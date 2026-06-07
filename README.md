
## Live Deployment

AutoOps-Insight is deployed on Google Cloud Run.

### Live API
- https://autoops-api-126325674316.us-central1.run.app

### Demo Endpoints
- `/support/metrics/live`
- `/incidents/{incident_id}/transition/live`

### Cloud Deployment
- Google Cloud Run
- Artifact Registry
- Cloud Build
- FastAPI + GraphQL APIs


# AutoOps-Insight — CI Failure Intelligence and Release Risk Reporting

**AutoOps-Insight turns noisy CI failures into structured incident intelligence and release decisions.**

`FastAPI` · `Kafka` · `PostgreSQL` · `React/Vite` · `scikit-learn`

---

## Why This Project Matters in Hiring Terms

- Shows end-to-end backend platform engineering: log ingestion → classification → structured decision → live dashboard
- Shows release engineering judgment: not just "what failed" but "should we ship"
- Shows developer tooling design: rule-driven + ML-backed, with audit trails and rollback preview
- Relevant to: SRE, production engineering, internal developer tooling, platform infrastructure

---

## Proof, Up Front

| Signal | Result |
|---|---|
| Incident families classified | 3 named (`timeout`, `dns_failure`, `latency_spike`) + `unknown` catch-all |
| Total analyses in live run | 5 |
| Hold-release decisions generated | 3 |
| Investigate decisions generated | 2 |
| Confidence on `dns_failure` classification | **0.91** |
| Confidence on `latency_spike` classification | **0.91** |
| Recurring signature detected | `dns_failure:818a0911c2c842c0` caught twice, separate runs |
| Release-risk output | Structured JSON + markdown, machine-readable and human-readable |

![AutoOps Production Signal Intelligence Dashboard](docs/screenshots/autoops-dashboard-main.png)

*Production Signal Intelligence Dashboard — live from FastAPI endpoints. 5 total incidents · 3 hold releases · 2 investigate · top failure: `latency_spike`*

---

## Incident Feed

![AutoOps Incident Feed and Recurrence Heatmap](docs/screenshots/autoops-incident-feed.png)

*Noisy services ranked · Recurrence heatmap (service × failure family) · Full incident feed with confidence scores and root cause labels*

---

## Quick Demo

```bash
git clone https://github.com/kritibehl/AutoOps-Insight
cd AutoOps-Insight
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd ml_model && python train_model.py && cd ..
uvicorn main:app --reload &
python3 cli.py analyze sample.log   # classify a CI log
python3 cli.py report               # generate release risk report
```

---

## The Problem

When a CI pipeline fails, an on-call engineer opens a wall of logs and starts guessing. The raw log tells you what happened last. It does not tell you whether this failure has appeared before, whether something changed near the incident window, whether rollback is worth trying, or who owns the problem.

Most teams handle this with Slack noise, manual grep, and tribal knowledge. AutoOps encodes the answers.

---

## What AutoOps Does

- **Classifies** raw CI log text into named failure families via rule-based matching + ML fallback
- **Fingerprints** each incident with a stable signature (`family:hash`) for cross-run comparison
- **Detects recurrence** — identifies when two separate failures share the same root cause signature
- **Correlates** incidents with nearby audit events in a configurable time window
- **Generates runbooks** — per-family, structured: first checks, likely cause, escalation route, mitigation steps
- **Blocks releases** — outputs `hold_release` / `investigate` per incident, plus a fleet-level risk summary
- **Simulates rule changes** — dry-run before applying, with per-incident impact preview

---

## Architecture

```
Raw CI log
    │
    ▼
Rule engine (config/rules.yaml)     ← add patterns without touching backend code
    │
    ▼
ML fallback (TF-IDF + Logistic Regression)
    │
    ▼
Incident record (PostgreSQL)
    ├── failure_family · confidence · signature
    ├── probable_owner · release_blocking
    └── recurrence count
    │
    ▼
Timeline correlation engine         ← configurable window, burst detection
    │
    ▼
Release risk report
    ├── hold_release / investigate (per incident)
    ├── recurring signatures (fleet-level)
    └── rollback_review_suggested
    │
    ▼
React/Vite dashboard  ←→  FastAPI  ←→  Kafka (event stream)
```

---

## Evidence Table

| Incident | Family | Confidence | Action | Root Cause |
|---|---|---|---|---|
| faireval latency | `latency_spike` | 0.91 | `hold_release` | `latency_regression_after_change` |
| faultline CI | `unknown` | 0.55 | `investigate` | `unknown_or_mixed_failure` |
| faireval latency (repeat) | `latency_spike` | 0.91 | `hold_release` | `latency_regression_after_change` |
| faultline CI (repeat) | `unknown` | 0.55 | `investigate` | `unknown_or_mixed_failure` |
| kubepulse DNS | `dns_failure` | 0.91 | `hold_release` | `service_discovery_or_dns_misconfiguration` |

Recurring signature `dns_failure:818a0911c2c842c0` surfaced twice across separate CI runs, automatically, without manual comparison.

---

## Example Output

**Incident analysis:**
```json
{
  "predicted_issue": "timeout",
  "confidence": 0.95,
  "failure_family": "timeout",
  "severity": "high",
  "signature": "timeout:733da8a4e20740af",
  "likely_cause": "operation exceeded threshold or dependency responded too slowly",
  "first_remediation_step": "inspect the exact timed-out operation and compare recent latency trends",
  "probable_owner": "platform-networking",
  "release_blocking": true,
  "recurrence": { "total_count": 3, "is_recurring": true }
}
```

**Release risk summary:**
```
Release Risk Summary
  Release risk:               HIGH
  Total analyses:             3
  Release-blocking incidents: 3

  Top recurring signature:
    timeout:733da8a4e20740af | family=timeout | severity=high | count=3

  Recommendation:
    Repeated failure signatures present. Investigate before promoting build.
```

**Timeline correlation:**
```json
{
  "correlation_summary": {
    "burst_detected": true,
    "nearby_change_detected": true,
    "rollback_review_suggested": true,
    "release_blocking_count": 3
  }
}
```

---

## Full Setup

```bash
git clone https://github.com/kritibehl/AutoOps-Insight
cd AutoOps-Insight
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd ml_model && python train_model.py && cd ..
uvicorn main:app --reload

python3 cli.py fleet-health
python3 cli.py simulate-rule timeout_rule probable_owner platform-networking

cd autoops-ui && npm install && npm run dev

# With PostgreSQL
docker run -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15
alembic upgrade head
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Classify a CI log, persist incident |
| `GET` | `/incidents` | List all persisted incidents |
| `GET` | `/history/recurring` | Top recurring signatures |
| `GET` | `/reports/summary` | Fleet release-risk summary |
| `GET` | `/incident/runbook/{family}` | Structured operator runbook |
| `GET` | `/incident/correlate` | Correlate incident against nearby changes |
| `GET` | `/fleet/health` | Noisy-service ranking + recurrence view |
| `POST` | `/reporting/export-powerbi` | BI-ready CSV export |
| `GET` | `/metrics` | Prometheus counters |
| `GET` | `/healthz` | Health check |

---

## Failure Taxonomy

| Family | Severity | Release blocking |
|---|---|---|
| `timeout` | high | yes |
| `dns_failure` | high | yes |
| `latency_spike` | high | yes |
| `oom` | critical | yes |
| `connection_refused` | high | yes |
| `crash_loop` | critical | yes |
| `retry_exhausted` | medium | yes |
| `flaky_test_signature` | medium | context-dependent |

---

## Why This Matters

The knowledge gap on-call engineers carry — "is this new or recurring, who owns it, is rollback worth it" — doesn't transfer and doesn't scale. AutoOps structures it: stable fingerprints replace pattern memory, correlation windows replace manual dashboard-hopping, runbook generation replaces tribal knowledge.

The two-layer classification design means deterministic rules handle the high-confidence cases (fast, auditable, no model dependency), and ML picks up the long tail. Both paths write to the same incident schema, so the release decision layer is independent of which path classified the incident.

---

## Limitations

- Log-based analysis only — not real-time metric stream ingestion
- ML model trained on labeled sample data; novel log formats require retraining
- Correlation is time-window based, not causal trace analysis
- Kafka is wired into the architecture and validated locally, not as a distributed production cluster
- PostgreSQL recommended for any real-volume use; SQLite available for local development

---

## Interview Notes

**Design decision:** Two-layer classification — deterministic rules first, ML fallback second. Keeps high-confidence cases fast and auditable; reserves ML for the long tail. Tradeoff: ML accuracy depends on training coverage, so the rule layer carries reliability in practice.

**Hard problem:** Stable fingerprinting. Using `family:hash(normalized_log_signature)` rather than raw text means minor log format differences don't break recurrence detection — but the normalization logic becomes load-bearing. Getting it wrong produces false recurrence signals.

**Metric I'd highlight:** 0.91 confidence on `dns_failure` with a rule-based classifier, no GPU, no transformer model. Fast, explainable, debuggable — which matters more for on-call tooling than raw accuracy.

**What I'd build next:** Event-triggered correlation. Fixed 60-minute windows produce false positives when incidents cluster non-uniformly. An event-driven model would tighten that to causally adjacent incidents.

---

## Relevant To

`SRE` · `Production Engineering` · `Release Engineering` · `Internal Developer Tooling` · `Platform / Infrastructure`

---

## Stack

Python · FastAPI · React/Vite · PostgreSQL · SQLite · Alembic · scikit-learn · Docker · GitHub Actions

---

## Related

- [Faultline](https://github.com/kritibehl/faultline) — exactly-once execution under distributed failure
- [KubePulse](https://github.com/kritibehl/KubePulse) — Kubernetes resilience validation and deployment safety
- [DetTrace](https://github.com/kritibehl/dettrace) — deterministic replay for concurrency failures
- [Postmortem Atlas](https://github.com/kritibehl/postmortem-atlas) — historical production outage analysis


## Proof Snapshot

- 102 support incidents
- 5 sources
- 6 AI issue families
- 51 escalations
- 19 AgentGrid events ingested


## AgentGrid Case Study

AgentGrid detected a missing-context failure, emitted a support incident event, and AutoOps classified it into a structured incident with:

- issue family: missing_context
- root cause: retrieval_or_context_pipeline_failure
- stakeholder outputs:
  - PM summary
  - engineering bug report
  - support action plan

See `docs/agentgrid_case_study.md`.


## Customer Blockers (Top Issues)

| Issue | Count | Action |
|---|---:|---|
| unsafe_response | 24 | escalate_to_safety_review |
| tool_failure | 24 | check_tool_dependency |
| latency_spike | 20 | hold_release |


## SQL and Reporting Proof

AutoOps includes SQL-backed reporting artifacts for business and support operations workflows:

- `reports/weekly_business_review.md`
- `reports/incident_trends.csv`
- `reports/service_health_summary.json`
- `sql/incident_trend_queries.sql`
- `sql/service_health_queries.sql`

These reports summarize incident trends, recurring issue families, escalation outcomes, stakeholder requests, service-health summaries, and operational metrics.


## SLA and Ticket Lifecycle Reporting

AutoOps includes SLA-aware ticket lifecycle artifacts for support operations workflows:

- `support_sla/sla_policy.yaml`
- `support_sla/ticket_lifecycle_report.md`
- `support_sla/escalation_age_report.csv`
- `support_sla/support_backlog_summary.json`
- `support_sla/recurring_issue_root_cause.md`

The live API exposes `/support/sla/summary` with ticket ownership, SLA breach status, time-to-triage, escalation count, service owner, and recommended next action.


## Final Ops Polish: RBAC, SLA Breaches, and Release Risk

AutoOps includes final operational-platform artifacts for:

- RBAC-style role matrix and escalation permissions
- SLA breach examples and escalation deadlines
- deployment-to-incident rollback risk summaries
- change-failure dashboard artifact

Artifacts:
- `auth/role_matrix.md`
- `auth/escalation_permissions.json`
- `sla/sla_breach_examples.json`
- `sla/escalation_deadlines.md`
- `release_analytics/rollback_risk_summary.json`
- `release_analytics/deploy_vs_incident_dashboard.png`


## Integration Review and Partner Support Artifacts

AutoOps includes partner-facing support and integration review documentation:

- `docs/integration_issue_review.md`
- `docs/partner_workflow_summary.md`
- `docs/support_requirements_matrix.md`

These artifacts demonstrate integration troubleshooting, operational evidence review, workaround guidance, escalation workflows, and support-documentation updates.


## Partner XML Payload Validation

AutoOps includes a partner-integration XML validation example:

- `integrations/sample_partner_payload.xml`
- `integrations/parse_partner_payload.py`
- `integrations/xml_validation_report.md`
- `integrations/partner_payload_validation_summary.json`

The parser extracts partner ID, deployment ID, event type, response latency, and retry count, then flags missing or invalid fields that could affect support routing and release-correlation workflows.


## Responsible AI Incident Monitoring

AutoOps includes Responsible AI monitoring artifacts that convert FairEval safety-regression outputs into operational incidents.

Artifacts:
- `rai_monitoring/ingest_rai_safety_event.py`
- `rai_monitoring/rai_monitoring_metrics.json`
- `rai_monitoring/rai_risk_trend_report.md`
- `ai_safety_incidents/responsible_ai_incident_summary.md`
- `ai_safety_incidents/safety_monitoring_metrics.json`

Live endpoints:
- `/rai/monitoring/summary`
- `/rai/incidents/{incident_id}`

These workflows normalize safety-regression events into severity-ranked incidents, release-impact flags, human-review indicators, release-block recommendations, and recurring risk-family metrics.


## AIOps Service Readiness and Infrastructure Output Validation

AutoOps includes service-readiness and deployment-output validation artifacts:

- `aiops_service_readiness/benchmark_incident_context_api.py`
- `aiops_service_readiness/incident_context_benchmark_summary.json`
- `aiops_service_readiness/incident_context_service_readiness_report.md`
- `infra/terraform/cloud_run_autoops/deployment_output_validation.py`
- `infra/terraform/cloud_run_autoops/sample_deployment_output.json`
- `infra/terraform/cloud_run_autoops/deployment_output_validation_report.md`

These workflows benchmark the live AIOps incident-context API and validate Terraform/Cloud Run deployment outputs for required service metadata, health endpoint documentation, environment configuration, and deployment-readiness signals.


## Event-Driven Incident Ingestion

AutoOps includes an event-driven incident ingestion workflow with validation, retry tracking, and dead-letter queue handling.

Artifacts:
- `event_ingestion/sample_incident_events.jsonl`
- `event_ingestion/process_incident_events.py`
- `event_ingestion/incident_ingestion_summary.json`
- `event_ingestion/dead_letter_queue.json`
- `event_ingestion/incident_ingestion_report.md`

Live/API workflow:
- `/events/ingestion/summary`

This models async incident ingestion patterns used in AIOps, SRE, platform support, and reliability tooling.


## Field Feedback and Customer-Friction Intelligence

AutoOps includes field-feedback artifacts that convert recurring GenAI failures into reusable incident patterns, customer blocker summaries, and product feedback.

Artifacts:
- `genai_incidents/recurring_genai_failures.json`
- `field_patterns/summarize_field_patterns.py`
- `field_patterns/recurring_rag_failure_patterns.json`
- `field_patterns/field_pattern_summary.md`
- `product_feedback/customer_blocker_summary.md`
- `product_feedback/feature_request_summary.md`
- `product_feedback/field_to_product_feedback_template.md`

Live/API workflow:
- `/field-patterns/summary`

This supports identifying recurring field patterns, customer friction points, support blockers, and engineering-facing product recommendations.


## Production Incident Runbook Automation

AutoOps includes incident-response automation that generates production review artifacts from service-health evidence, logs, deployment context, and incident timelines.

Artifacts:
- `incident_runbooks/sample_production_incident.json`
- `incident_runbooks/generate_runbook_package.py`
- `incident_runbooks/incident_response_package.json`
- `incident_runbooks/post_incident_review_template.md`

Live/API workflow:
- `/incident-runbooks/demo`

This workflow produces incident timelines, rollback candidates, AI-assisted runbook summaries, post-incident review templates, and follow-up actions for production review.


## Streaming Incident Analytics and Cassandra-Style Event Design

AutoOps includes streaming-style incident analytics and Cassandra-style telemetry schema design.

Artifacts:
- `streaming_analytics/incident_stream_processor.py`
- `streaming_analytics/stream_window_metrics.json`
- `streaming_analytics/rolling_failure_analysis.md`
- `cassandra_design/cassandra_event_schema.cql`
- `cassandra_design/telemetry_partitioning.md`

Live/API workflow:
- `/streaming/incident-analytics/summary`

These workflows model rolling-window failure analysis, incident spike detection, escalation burst tracking, moving averages, and high-volume telemetry partitioning design.


## Distributed Analytics Pipeline Simulation

AutoOps includes a compact end-to-end analytics pipeline simulation for operational telemetry.

Artifacts:
- `pipeline_simulation/run_pipeline_simulation.py`
- `pipeline_simulation/pipeline_output.json`
- `pipeline_simulation/pipeline_report.md`
- `pipeline_simulation/end_to_end_pipeline_diagram.md`

Stages:
- ingest
- aggregate
- warehouse
- anomaly detection
- dashboard

This supports Apple Data Engineer / monitoring-data positioning by showing telemetry ingestion, service-level aggregation, warehouse-ready outputs, anomaly detection, and dashboard-facing monitoring summaries.


## ML Monitoring Workflows

AutoOps includes ML monitoring workflows that track feature drift, prediction-quality regression, latency regression, anomaly patterns, and dashboard-ready model-health metrics.

Artifacts:
- `ml_monitoring/anomaly_detection_pipeline.py`
- `ml_monitoring/feature_drift_report.md`
- `ml_monitoring/prediction_quality_metrics.json`
- `ml_monitoring/model_health_dashboard.json`

Live/API workflow:
- `/ml-monitoring/model-health`

This supports ML monitoring, AI service quality, data-platform support, and operational model-health review.


## Trino-Style Distributed Query Layer

AutoOps includes Trino-style distributed query examples over warehouse-ready operational telemetry outputs.

Artifacts:
- `query_analytics/trino_style_query_examples.sql`
- `query_analytics/distributed_query_notes.md`
- `query_analytics/dashboard_query_patterns.md`

These examples cover service-health summaries, regional latency trends, anomaly drilldowns, service-owner dashboards, and operational monitoring query patterns.


## ML Release Governance

AutoOps includes ML release-monitoring artifacts that model canary rollout, model-health monitoring, regression detection, rollback decisioning, and human-review routing.

Artifacts:
- `model_release_governance/canary_model_rollout.md`
- `model_release_governance/rollback_decision.json`
- `model_release_governance/model_degradation_report.md`

This workflow shows deploy → monitor → detect regression → rollback for operational ML support workflows.


## SRE Operations Automation

AutoOps includes SRE-style incident operations workflows for postmortems, alert correlation, and runbook-quality analytics.

Artifacts:
- `postmortem/timeline_builder.py`
- `postmortem/action_item_tracker.py`
- `postmortem/postmortem_template.md`
- `alert_correlation/correlate_alerts.py`
- `alert_correlation/alert_families.json`
- `alert_correlation/reports/alert_correlation_report.md`
- `runbook_quality/runbook_success_rate.py`
- `runbook_quality/unresolved_steps.json`
- `runbook_quality/runbook_gap_report.md`

These workflows convert incident timelines, alerts, service-health evidence, and runbook outcomes into review-ready operational artifacts.


## Incident Trend Analytics

AutoOps includes incident-trend analytics for recurring operational failure families.

Artifacts:
- `incident_trends/incident_history.json`
- `incident_trends/analyze_incident_trends.py`
- `incident_trends/incident_trend_summary.json`
- `incident_trends/incident_trend_report.md`

This workflow identifies top recurring incident families, month-over-month growth rates, trend status, and recommended remediation actions for support/SRE operations.


## Customer Incident Workspace and SLA/SLO Risk Dashboard

AutoOps includes customer-facing incident workspace artifacts and SLA/SLO risk dashboard workflows.

Artifacts:
- `customer_incident_workspace/sample_customer_incident.json`
- `customer_incident_workspace/analyze_customer_incident.py`
- `customer_incident_workspace/customer_incident_summary.json`
- `customer_incident_workspace/customer_incident_report.md`
- `slo_risk_dashboard/build_slo_dashboard.py`
- `slo_risk_dashboard/slo_risk_summary.json`
- `slo_risk_dashboard/escalation_ageing_report.json`
- `slo_risk_dashboard/slo_dashboard_report.md`

These workflows convert customer issue reports and operational incident data into support-ready severity, evidence, rollback recommendations, customer-safe summaries, SLA risk, SLO pressure, and escalation-aging metrics.
