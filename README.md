# AutoOps-Insight

**Operator-facing incident triage and reporting for repeated CI, service, and infrastructure regressions.**

[![Tests](https://github.com/kritibehl/AutoOps-Insight/actions/workflows/test.yml/badge.svg)](https://github.com/kritibehl/AutoOps-Insight/actions)
![GitHub Repo stars](https://img.shields.io/github/stars/kritibehl/AutoOps-Insight?style=social)

AutoOps-Insight transforms raw failure logs into structured, actionable reliability intelligence. Rather than labeling a log as simply "timeout," it produces a structured incident artifact with severity, likely cause, remediation steps, ownership, a stable fingerprint — and a release-risk recommendation.

**Example operator workflow:**
- Repeated `timeout` family detected and fingerprinted across 14 CI runs
- Release-risk summary escalated to `high` — surfaced as a likely release blocker
- Rule simulation previewed ownership and severity changes before the rule was applied

---

## The Problem

Repeated regressions waste time because the same questions keep getting asked from scratch:

- Has this failure happened before, and how often?
- Is this build environment risky enough to block a release?
- What failure patterns are dominating recent CI runs?
- Which recurring signatures should the team prioritize?

**Without structure:** scan logs manually, guess ownership, decide ad hoc whether to escalate or block release.

**With AutoOps-Insight:**

```
ingest logs → classify incident → simulate rule change → preview impact → rollback if needed
```

---

## Architecture

```
Log Sources
   │
   ▼
Incident Parser
   │
   ▼
Rules Engine (YAML) + ML-Assisted Classification
   │
   ▼
Structured Incident Analysis
(severity · signature · likely cause · owner · release-blocking flag)
   │
   ▼
SQLite Incident Store
   │
   ├── Recurrence / Replay
   ├── Release-Risk Reports
   ├── Audit Log
   ├── Rule Simulation / Impact Preview
   └── Dashboard / API / CLI
```

---

## Structured Incident Schema

Each log upload produces a full incident record:

| Field | Description |
|---|---|
| `predicted_issue` | Failure type (e.g. `timeout`, `oom`, `flaky_test_signature`) |
| `confidence` | ML classification confidence |
| `failure_family` | Normalized operational category |
| `severity` | `low` / `medium` / `high` / `critical` |
| `signature` | Stable fingerprint for recurrence tracking |
| `summary` | Human-readable incident summary |
| `likely_cause` | Taxonomy-based likely cause hint |
| `first_remediation_step` | What to check first |
| `next_debugging_action` | Suggested follow-up |
| `probable_owner` | Probable service/team ownership hint |
| `release_blocking` | Whether this should gate a release |
| `evidence` | Supporting log lines |
| `recurrence` | How many times this signature has appeared |

**Example output:**

```json
{
  "id": 1,
  "failure_family": "timeout",
  "severity": "high",
  "release_blocking": true,
  "probable_owner": "service-owner",
  "likely_cause": "operation exceeded timeout threshold or downstream latency increased",
  "first_remediation_step": "inspect timed-out operation and compare recent latency trends",
  "next_debugging_action": "check dependency latency, retries, and saturation signals"
}
```

---

## Screenshots

### Audit Log Traceability
Rule update with actor, timestamp, and before/after diff.

![AutoOps audit log](docs/screenshots/autoops-audit-log.png)

### Incident Replay and Test Validation
Replayed stored incident with recurrence metadata and passing test run.

![AutoOps incident replay](docs/screenshots/autoops-incident-replay.png)

### Audit Diff and Rollback Preview UI
Audit-backed rule review in the dashboard, including selected audit event context and field-level diff inspection for a rule update.

![AutoOps audit diff and rollback preview UI](docs/screenshots/autoops-audit-diff-rollback-ui.png)

---

## Detection Logic

Two classification layers work in combination:

**Rule-based detection** checks for deterministic patterns: `timeout` · `dns_failure` · `connection_refused` · `tls_failure` · `retry_exhausted` · `oom` · `flaky_test_signature` · `dependency_unavailable` · `crash_loop` · `latency_spike`

**ML fallback** uses TF-IDF vectorization and Logistic Regression trained on labeled log data. Each analysis record indicates which detection path was used.

---

## Failure Taxonomy

| Family | Severity | Release Blocking |
|---|---|---|
| `timeout` | high | yes |
| `oom` | critical | yes |
| `connection_refused` | high | yes |
| `dns_failure` | high | yes |
| `flaky_test_signature` | medium | context-dependent |
| `retry_exhausted` | medium | yes |
| `crash_loop` | critical | yes |
| `dependency_unavailable` | high | yes |

---

## Key Capabilities

**Signature Fingerprinting** — Each incident gets a stable, normalized signature like `timeout:733da8a4e20740af`. The system knows when two failures are the same underlying issue despite volatile log content, enabling cross-run recurrence tracking.

**Historical Recurrence Tracking** — Tracks total occurrence count, first/last seen timestamps, recurring signature qualification, and failure-family distribution across runs.

**Release-Risk Reporting** — Aggregates stored history into a `low` / `medium` / `high` / `critical` release-risk summary based on release-blocking incidents, recurring signature concentration, and anomaly flags.

**Rule Simulation and Impact Preview** — Admins can dry-run rule changes against stored incidents before applying them: how many incidents would be impacted, which fields would change, which stored incidents would be affected.

**Rule Diff and Rollback Preview** — Shows field-level diffs between current and simulated rules, and rollback previews for audit events — making rule changes auditable and safe to evolve.

**Dashboard** — A React/Vite frontend showing release risk score, blocker count, recurring signatures, anomaly panel, failure-family distribution, and inline incident breakdown on log upload.

---

## CLI

```bash
python cli.py analyze sample.log
python cli.py replay 1
python cli.py audit
python cli.py simulate-rule timeout_rule probable_owner platform-networking
python cli.py rule-diff timeout_rule probable_owner platform-networking
python cli.py rollback-preview 1
python cli.py report
python cli.py fleet-health
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Analyze a log and persist the result |
| `GET` | `/rules` | View active detection rules |
| `GET` | `/audit/recent` | Recent audit log entries |
| `GET` | `/history/recurring` | Top recurring signatures |
| `GET` | `/history/signature/{sig}` | Recurrence detail for a signature |
| `GET` | `/reports/summary` | Structured release-risk summary (JSON) |
| `GET` | `/reports/markdown` | Human-readable markdown report |
| `POST` | `/incident-runbook/<family>` | Generate runbook guidance |
| `POST` | `/incident-correlate` | Correlate incident against nearby changes |
| `GET` | `/fleet-health` | Fleet-level incident summary |
| `GET` | `/metrics` | Prometheus counters |
| `GET` | `/healthz` | Health check |

---

## Quickstart

```bash
git clone https://github.com/kritibehl/AutoOps-Insight.git
cd AutoOps-Insight

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python cli.py analyze sample.log
python cli.py report
```

---

## Engineering Decisions

**YAML rules** instead of hardcoded-only logic so detection patterns, severity, ownership hints, and remediation guidance can be updated without backend code changes.

**Stable signature fingerprinting** to identify recurring incidents across noisy repeated logs and make recurrence tracking deterministic.

**SQLite persistence** to keep replay, recurrence tracking, reporting, and preview workflows simple, inspectable, and easy to run locally.

**Heuristic anomaly detection** instead of overfit ML to preserve explainability for operational triage and release-risk review.

---

## Repo Structure

```
api/              service endpoints
cli/              command-line workflows
analysis/         correlation, fingerprinting, release-risk logic
rules/            incident classification rules
ml_model/         TF-IDF + LR training data and model
autoops-ui/       React/Vite dashboard
reports/          generated reports
exports/          BI-style outputs
sample_logs/      representative log inputs
tests/            behavior coverage
docs/screenshots/ UI / dashboard assets
```

---

## Running Tests

```bash
pytest
```

---

## Why This Project Stands Out

This is an operator workflow tool, not generic log analytics. It demonstrates operational thinking around repeated regressions, stable incident fingerprinting, release-risk interpretation tied to deployment timelines, and auditable rule evolution — making it especially strong for Production Engineering, SRE, and reliability-oriented roles.

---

## Related Projects

- [Faultline](https://github.com/kritibehl/faultline) — correctness under failure
- [KubePulse](https://github.com/kritibehl/KubePulse) — resilience validation
- [DetTrace](https://github.com/kritibehl/dettrace) — replay and incident reconstruction
- [FairEval-Suite](https://github.com/kritibehl/FairEval-Suite) — release gating for GenAI systems

## License

MIT
