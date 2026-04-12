<div align="center">

# AutoOps-Insight

**Operator-facing incident triage tool that converts noisy CI and infra logs into structured incident evidence, recurrence signals, and operator-ready guidance**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Dashboard-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Primary%20Storage-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)

</div>

---

> CI failures don't fail loudly. They fail ambiguously, repeatedly, and in ways that look different each time even when they're the same underlying issue.
> **AutoOps converts raw CI and infra logs into structured incident intelligence.**

---

## Who This Helps

**On-call engineers** — Move from raw logs to structured incident evidence, likely cause, escalation path, and mitigation steps faster.

**Release owners** — Surface release-blocking regressions, nearby change correlation, and rollback/no-rollback guidance for safer release judgment.

**Platform and reliability teams** — Highlight recurring failure signatures, noisy services, blast-radius patterns, and repeated regressions across services and subsystems.

---

## Operator Workflow

```
ingest logs → classify incident → correlate changes → surface recurrence → simulate rule change → generate guidance
```

---

## What It Answers Under Pressure

- What kind of incident is this?
- Is this part of a repeated failure pattern?
- Did something change near this incident window?
- Is rollback worth considering?
- Who should own escalation?
- What should be checked first?

---

## Structured Incident Record

Each log ingestion produces a fully structured incident:

```json
{
  "predicted_issue": "timeout",
  "confidence": 0.95,
  "failure_family": "timeout",
  "severity": "high",
  "signature": "timeout:733da8a4e20740af",
  "summary": "Detected failure family: timeout. Key evidence: Timeout connecting to registry.",
  "likely_cause": "operation exceeded threshold or dependency responded too slowly",
  "first_remediation_step": "inspect the exact timed-out operation and compare recent latency trends",
  "next_debugging_action": "check downstream service latency, retries, and resource saturation",
  "probable_owner": "platform-networking",
  "release_blocking": true,
  "evidence": [{ "line_number": 1, "text": "ERROR: Timeout connecting to registry." }],
  "recurrence": {
    "total_count": 3,
    "first_seen": "2026-03-12T16:18:31Z",
    "last_seen": "2026-03-12T16:22:41Z",
    "is_recurring": true
  }
}
```

---

## Failure Taxonomy

| Family | Severity | Release blocking |
|---|---|---|
| `timeout` | high | yes |
| `oom` | critical | yes |
| `connection_refused` | high | yes |
| `dns_failure` | high | yes |
| `tls_handshake` | high | yes |
| `retry_exhausted` | medium | yes |
| `crash_loop` | critical | yes |
| `dependency_unavailable` | high | yes |
| `flaky_test_signature` | medium | context-dependent |
| `intermittent_network_flap` | medium | context-dependent |

Classification is driven by `config/rules.yaml` — no backend code changes required to add or tune patterns.

---

## Recurrence Detection: Validated

From live ingestion runs:

- **3 persisted incident records**
- **2 distinct failure families classified:** `timeout`, `dns_failure`
- **1 recurring signature detected:** `dns_failure:818a0911c2c842c0` appearing twice

The recurring signature means AutoOps identified that two separate CI failures were the same underlying infrastructure issue — not two independent problems.

---

## Detection Logic

**Rule-based layer** — deterministic pattern matching: `timeout`, `dns_failure`, `connection_refused`, `tls_handshake`, `retry_exhausted`, `oom`, `flaky_test_signature`, `dependency_unavailable`, `crash_loop`, `latency_spike`

**ML fallback** — TF-IDF vectorization and Logistic Regression trained on labeled log data (`ml_model/log_train.csv`). Each analysis record indicates which detection path was used.

---

## Timeline Correlation Engine

Correlates incident windows with nearby operational context:

- Deploy or rollout timing
- Change/config activity bursts
- Release-blocking concentration
- Owner spread and failure-family clustering

### Sample correlation output

```json
{
  "incident_id": 1,
  "window_minutes": 60,
  "correlated_incidents": [
    { "id": 2, "signature": "timeout:733da8a4e20740af", "minutes_from_anchor": 12 },
    { "id": 3, "signature": "timeout:733da8a4e20740af", "minutes_from_anchor": 24 }
  ],
  "nearby_audit_events": [{ "event_type": "rule_update", "actor": "kriti", "minutes_from_anchor": 8 }],
  "correlation_summary": {
    "burst_detected": true,
    "single_family_concentration": true,
    "release_blocking_count": 3,
    "nearby_change_detected": true,
    "rollback_review_suggested": true
  }
}
```

---

## Rule Simulation and Impact Preview

Dry-run rule changes against stored incidents before applying them.

```json
{
  "rule_id": "timeout_rule",
  "incidents_evaluated": 3,
  "incidents_impacted": 3,
  "probable_owner_changed": 3,
  "sample_impacted_incidents": [{
    "id": 3,
    "changed_fields": ["probable_owner"],
    "original":  { "probable_owner": "service-owner" },
    "simulated": { "probable_owner": "platform-networking" }
  }]
}
```

### Rollback preview

```json
{
  "audit_event_id": 1,
  "rule_id": "timeout_rule",
  "rollback_updates": { "probable_owner": "service-owner" },
  "impact_preview": { "incidents_evaluated": 3, "incidents_impacted": 3 }
}
```

---

## Release Risk Reporting

```markdown
# AutoOps Insight Report

## Release Risk Summary
- Release risk: **high**
- Total analyses: **3**
- Release-blocking incidents: **3**

## Top Recurring Signatures
- `timeout:733da8a4e20740af` | family=timeout | severity=high | count=3

## Recommendation
Repeated failure signatures are present at levels that may indicate regression or release instability.
Investigate recurring signatures before promoting the current build.
```

---

## Operator Runbook Generation

For each incident family, AutoOps generates structured guidance:

```json
{
  "failure_family": "dns_failure",
  "first_checks": [
    "verify DNS resolver reachability from affected hosts",
    "check whether one hostname or zone is disproportionately impacted",
    "compare resolution success rate before and after the incident window"
  ],
  "likely_cause": "resolver misconfiguration, zone propagation delay, or service-discovery change near incident window",
  "rollback_guidance": "roll back only if a recent DNS or service-discovery change correlates strongly with incident window",
  "escalation_route": "service-owner → platform-networking → dns/platform team",
  "mitigation_sequence": [
    "retry resolution from multiple hosts or regions",
    "shift to a known-good endpoint if available",
    "roll back recent DNS/service-discovery change if correlation is strong",
    "escalate with affected hostnames, regions, and timestamps"
  ]
}
```

---

## Storage and Persistence

**Primary:** PostgreSQL with Alembic-managed schema migrations

**Fallback:** SQLite for local development

The pluggable persistence layer decouples classification from storage — one configuration line swaps backends, not N modules.

```bash
docker run -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15
alembic upgrade head
uvicorn main:app --reload
```

---

## Dashboard

React/Vite frontend (`autoops-ui/`) surfacing:

- Release risk score and blocker count
- Recurring signature panel
- Anomaly context
- Recent incident breakdown
- Failure-family distribution
- Markdown report preview
- Audit log with field-level diff inspection

### Screenshots

**Audit Log Traceability** — Rule update with actor, timestamp, and before/after diff:

![AutoOps audit log](docs/screenshots/autoops-audit-log.png)

**Incident Replay and Test Validation** — Replayed stored incident with recurrence metadata:

![AutoOps incident replay](docs/screenshots/autoops-incident-replay.png)

**Audit Diff and Rollback Preview UI** — Field-level diff inspection for a rule update:

![AutoOps audit diff and rollback preview UI](docs/screenshots/autoops-audit-diff-rollback-ui.png)

**Fleet Health and Root-Cause Report** — Noisy-service ranking and top recurring signatures:

![AutoOps fleet health and root-cause report](docs/screenshots/autoops-fleet-health-root-cause.png)

---

## Fleet Health View

Surfaces across all services:

- Top recurring incident sources
- Noisy-service ranking
- Highest blast-radius regressions
- Incident recurrence by subsystem
- MTTR-style recurrence windows

---

## Power BI Export

Generates BI-ready CSV exports under `bi_exports/`:

`reporting_daily_summary.csv` · `reporting_weekly_summary.csv` · `reporting_pipeline_trends.csv` · `reporting_root_cause_counts.csv` · `reporting_deployment_regressions.csv`

```bash
python3 cli.py export-powerbi
```

---

## Before vs After Triage

| Before | After AutoOps |
|---|---|
| Read raw logs manually | Classify into a concrete failure family |
| Guess likely owner from error strings | Surface probable owner and escalation route |
| Check dashboards separately for timing | Correlate with nearby incidents and changes in a bounded window |
| Search for nearby deploys by hand | Automated timeline correlation |
| Decide rollback with incomplete context | Fleet-level recurrence and blast-radius signals |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Analyze a log and persist the result |
| `GET` | `/history/recurring` | Top recurring signatures |
| `GET` | `/reports/summary` | Structured release-risk summary |
| `GET` | `/incident/runbook/{family}` | Operator runbook for a failure family |
| `GET` | `/incident/correlate` | Correlate incident against nearby changes |
| `GET` | `/fleet/health` | Fleet-level health and recurrence view |
| `POST` | `/reporting/export-powerbi` | Export Power BI-ready CSV artifacts |
| `GET` | `/metrics` | Prometheus counters |

---

## CI Integration

GitHub Actions workflow automatically: runs CLI health check, analyzes sample logs, generates markdown and JSON report artifacts, uploads artifacts and SQLite DB for inspection.

---

## Key Engineering Decisions

**YAML rules** — detection patterns, severity, ownership hints, and remediation guidance update without backend code changes.

**Stable signature fingerprinting** — recurring incidents are identified across noisy repeated logs deterministically.

**Heuristic anomaly detection** — preserves explainability for operational triage without overfitting.

**Rule simulation before commit** — operators preview impact of any rule change before it affects live classification.

**API + CLI + dashboard + CI** — same system supports debugging, automation, visual inspection, and admin workflows.

---

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Train model
cd ml_model && python train_model.py && cd ..

# Start API
uvicorn main:app --reload

# Analyze a log
python3 cli.py analyze sample.log

# Generate release risk report
python3 cli.py report

# Start dashboard
cd autoops-ui && npm install && npm run dev
```

---

## Stack

Python · FastAPI · React/Vite · PostgreSQL · SQLite · Alembic · scikit-learn · Docker · GitHub Actions

---

## Related

- [KubePulse](https://github.com/kritibehl/KubePulse) — Kubernetes resilience validation and deployment safety
- [Faultline](https://github.com/kritibehl/faultline) — exactly-once execution under distributed failure
- [Postmortem Atlas](https://github.com/kritibehl/postmortem-atlas) — historical production outage analysis
- [DetTrace](https://github.com/kritibehl/dettrace) — deterministic replay for concurrency failures
