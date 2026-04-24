<div align="center">

# AutoOps-Insight — CI Failure Intelligence and Release Risk Reporting

**
AutoOps-Insight turns noisy CI failures into structured incident intelligence and release decisions.

FastAPI · Kafka · PostgreSQL · React/Vite **

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Dashboard-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Primary%20Storage-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)

</div>

---

## From Raw Logs → Release Decision

```json
{
  "incident_type": "dns_failure",
  "recurrence": 3,
  "release_decision": "hold_release"
}
```

Full incident record:

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
  "recurrence": {
    "total_count": 3,
    "is_recurring": true
  }
}
```

---

## The Problem

When a CI pipeline fails, an on-call engineer opens a wall of logs and starts guessing.

The raw log tells you what happened last. It does not tell you whether this failure has appeared before, whether something changed near the incident window, whether rollback is worth trying, or who owns the problem. AutoOps encodes those answers.

---

## Release Risk Output

```markdown
## Release Risk Summary
- Release risk:               HIGH
- Total analyses:             3
- Release-blocking incidents: 3

Top recurring signature:
  timeout:733da8a4e20740af | family=timeout | severity=high | count=3

Recommendation:
  Repeated failure signatures present. Investigate before promoting build.
```

---

## Dashboard Screenshots

**Fleet Health and Root-Cause Report** — Noisy-service ranking, top recurring signatures, root-cause distribution:

![AutoOps fleet health and root-cause report](docs/screenshots/autoops-fleet-health-root-cause.png)

**Audit Log Traceability** — Rule update with actor, timestamp, and before/after diff:

![AutoOps audit log](docs/screenshots/autoops-audit-log.png)

**Incident Replay and Test Validation** — Replayed stored incident with recurrence metadata and passing test run:

![AutoOps incident replay](docs/screenshots/autoops-incident-replay.png)

**Audit Diff and Rollback Preview UI** — Field-level diff inspection for a rule update:

![AutoOps audit diff and rollback preview UI](docs/screenshots/autoops-audit-diff-rollback-ui.png)

---

## Operator Workflow

```
ingest logs → classify incident → fingerprint → correlate changes → surface recurrence → release decision
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

## Recurrence Detection: Validated

From live ingestion runs:

- **3 persisted incident records**
- **2 distinct failure families classified:** `timeout`, `dns_failure`
- **1 recurring signature detected:** `dns_failure:818a0911c2c842c0` appearing twice

The recurring signature means AutoOps identified that two separate CI failures were the same underlying infrastructure issue — not two independent problems.

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

## Timeline Correlation Engine

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

Dry-run rule changes against stored incidents before applying:

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

### Rollback Preview

```json
{
  "audit_event_id": 1,
  "rule_id": "timeout_rule",
  "rollback_updates": { "probable_owner": "service-owner" },
  "impact_preview": { "incidents_evaluated": 3, "incidents_impacted": 3 }
}
```

---

## Operator Runbook Generation

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

## Detection Logic

**Rule-based layer** — deterministic pattern matching for: `timeout`, `dns_failure`, `connection_refused`, `tls_handshake`, `retry_exhausted`, `oom`, `flaky_test_signature`, `dependency_unavailable`, `crash_loop`, `latency_spike`

**ML fallback** — TF-IDF vectorization and Logistic Regression trained on labeled log data (`ml_model/log_train.csv`). Each analysis record indicates which detection path was used.

---

## Before vs After Triage

| Before | After AutoOps |
|---|---|
| Read raw logs manually | Classify into concrete failure family |
| Guess likely owner from error strings | Surface probable owner and escalation route |
| Check dashboards separately for timing | Correlate nearby incidents and changes in bounded window |
| Search for nearby deploys by hand | Automated timeline correlation |
| Decide rollback with incomplete context | Fleet-level recurrence and blast-radius signals |

---

## Storage and Persistence

**Primary:** PostgreSQL with Alembic-managed schema migrations

**Fallback:** SQLite for local development

```bash
docker run -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15
alembic upgrade head
uvicorn main:app --reload
```

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

# View fleet health
python3 cli.py fleet-health

# Simulate a rule change
python3 cli.py simulate-rule timeout_rule probable_owner platform-networking

# Start dashboard
cd autoops-ui && npm install && npm run dev
```

---

## CI Integration

GitHub Actions workflow automatically: runs CLI health check, analyzes sample logs, generates markdown and JSON report artifacts, uploads artifacts and SQLite DB for inspection.

---

## Why This Matters in Production

On-call triage is a time and context problem. Engineers who have been with a system for two years can glance at a log and know if a failure is new or recurring, which team owns it, and whether rollback is worth trying. That knowledge doesn't transfer and doesn't scale. AutoOps structures it: stable fingerprints replace pattern memory, correlation windows replace manual dashboard-hopping, runbook generation replaces tribal knowledge. The result is faster triage and better release judgment regardless of who is on call.

---

## Scope and Limitations

- Log-based analysis, not real-time metric stream ingestion
- ML model trained on labeled sample data; performance on novel log formats requires retraining
- Correlation is time-window based, not causal trace analysis
- SQLite fallback; PostgreSQL recommended for production use

---

## Signals For

`SRE` · `Production Engineering` · `Release Engineering` · `Internal Developer Tooling` · `Platform / Infrastructure`

---

## Stack

Python · FastAPI · React/Vite · PostgreSQL · SQLite · Alembic · scikit-learn · Docker · GitHub Actions

---

## Related

- [KubePulse](https://github.com/kritibehl/KubePulse) — Kubernetes resilience validation and deployment safety
- [Faultline](https://github.com/kritibehl/faultline) — exactly-once execution under distributed failure
- [DetTrace](https://github.com/kritibehl/dettrace) — deterministic replay for concurrency failures
- [Postmortem Atlas](https://github.com/kritibehl/postmortem-atlas) — historical production outage analysis
