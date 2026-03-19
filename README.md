# AutoOps-Insight


> AutoOps-Insight is an operator-facing incident triage and reporting tool that combines rule-based + ML-assisted classification, timeline correlation, runbook generation, fleet-health views, and BI-style reporting to accelerate root-cause isolation across repeated regressions.

> A reliability analytics tool for CI and infrastructure failures — classifies logs, fingerprints recurring incident signatures, tracks recurrence, previews rule-change impact, and generates release-risk summaries.

---

## What It Does

AutoOps-Insight transforms raw failure logs into structured, actionable reliability intelligence. Rather than labeling a log as simply "timeout", it produces a structured incident artifact with severity, likely cause, remediation steps, ownership, and a stable fingerprint for tracking recurrence over time.

**It answers questions like:**
- Has this failure happened before, and how often?
- Is this build environment risky enough to block a release?
- What failure patterns are dominating recent CI runs?
- Which recurring signatures should the team prioritize?

---

## Operator Workflow

```text
ingest logs → classify incident → simulate rule change → preview impact → rollback if needed
```

---

## Architecture

```text
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

## Features

### Structured Incident Analysis

Each log upload produces a structured incident record:

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

### Signature Fingerprinting

Each incident gets a stable, normalized signature like `timeout:733da8a4e20740af`. This enables cross-run recurrence tracking — the system knows when two failures are the same underlying issue despite volatile log content.

### Historical Recurrence Tracking

Results persist in SQLite. The system tracks:
- Total occurrence count per signature
- First and last seen timestamps
- Recurring signature qualification
- Recent failure-family distribution statistics

### Release-Risk Reporting

The report engine aggregates stored history into a release-risk summary (`low` / `medium` / `high` / `critical`) based on:
- Presence of release-blocking incidents
- Recurring signature concentration
- Anomaly flags (e.g. one signature accounting for 80% of recent failures)
- Window comparison vs. baseline blocker rate

### Anomaly Detection

Heuristic-based flags that surface meaningful signals without overfitting:
- Signature concentration spikes
- High-count recurring failures
- Family-level spikes
- Release blocker saturation

### Rule Simulation and Impact Preview

Admins can dry-run rule changes against stored incidents before applying them.

Simulation preview answers:
- How many incidents would be evaluated
- How many incidents would be impacted
- Whether `failure_family`, `severity`, `release_blocking`, or `probable_owner` would change
- Which stored incidents would be affected

### Rule Diff and Rollback Preview

AutoOps-Insight can show a field-level diff between the current and simulated rule, a rollback preview for an audit event, and the expected impact of reverting a previous rule update before making the change. These workflows make rule changes safer for operator-managed classification systems by showing likely impact before applying or reverting a policy update.

### Dashboard

A React/Vite frontend (`autoops-ui/`) showing release risk score, blocker count, recurring signatures, anomaly panel, recent analyses, failure-family distribution, and a markdown report preview. Log upload triggers a full incident breakdown inline.

---

## Detection Logic

The classifier uses two layers:

**Rule-based detection** checks for deterministic patterns:
`timeout` · `dns_failure` · `connection_refused` · `tls_failure` · `retry_exhausted` · `oom` · `flaky_test_signature` · `dependency_unavailable` · `crash_loop` · `latency_spike`

**ML fallback** uses TF-IDF vectorization and Logistic Regression trained on labeled log data (`ml_model/log_train.csv`). Each analysis record indicates which detection path was used.

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
| `dependency_error` | high | yes |
| `dependency_unavailable` | high | yes |

---

## API

FastAPI backend exposing:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predict` | Lightweight issue classification |
| `POST` | `/analyze` | Analyze a log and persist the result |
| `POST` | `/summarize` | Keyword-based summary extraction |
| `GET` | `/rules` | View active config-driven detection rules |
| `GET` | `/audit/recent` | Recent audit log entries |
| `GET` | `/history/recent` | Recent incident list |
| `GET` | `/history/recurring` | Top recurring signatures |
| `GET` | `/history/signature/{signature}` | Recurrence detail for a signature |
| `GET` | `/history/analysis/{analysis_id}` | Stored incident detail |
| `GET` | `/reports/summary` | Structured release-risk summary (JSON) |
| `GET` | `/reports/markdown` | Human-readable markdown report |
| `POST` | `/reports/generate` | Write report artifacts to disk |
| `GET` | `/metrics` | Prometheus counters |
| `GET` | `/healthz` | Health check |

---

## CLI

```bash
python cli.py health
python cli.py analyze sample.log
python cli.py analyze sample.log --no-print-json
python cli.py replay 1
python cli.py audit
python cli.py simulate-rule timeout_rule probable_owner platform-networking
python cli.py rule-diff timeout_rule probable_owner platform-networking
python cli.py rollback-preview 1
python cli.py report
```

---

## Getting Started

### 1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Train or retrain the model

```bash
cd ml_model
python train_model.py
cd ..
```

### 3. Start the API server

```bash
uvicorn main:app --reload
```

### 4. Run the CLI

```bash
python cli.py analyze sample.log
python cli.py replay 1
python cli.py simulate-rule timeout_rule probable_owner platform-networking
python cli.py rollback-preview 1
python cli.py report
```

### 5. Start the dashboard

```bash
cd autoops-ui
npm install
npm run dev
```

---

## CI Integration

A GitHub Actions workflow automatically:

- Runs a CLI health check
- Analyzes sample logs
- Generates markdown and JSON report artifacts
- Uploads report artifacts and the SQLite DB for inspection

---

## Example Workflow

```bash
# Analyze a failing log
python cli.py analyze sample.log

# Replay a stored incident by ID
python cli.py replay 1

# Simulate a rule change before applying it
python cli.py simulate-rule timeout_rule probable_owner platform-networking

# Show only the rule diff
python cli.py rule-diff timeout_rule probable_owner platform-networking

# Update a detection rule
python cli.py update-rule-cmd timeout_rule probable_owner platform-networking --actor kriti

# Inspect the audit trail
python cli.py audit

# Preview rollback impact for an audit event
python cli.py rollback-preview 1

# Generate a release-risk report
python cli.py report
```

### Operator Workflow Steps

Typical admin flow:

- update rule
- inspect diff
- preview impacted incidents
- apply or rollback

---

## Sample JSON Incident

```json
{
  "predicted_issue": "timeout",
  "confidence": 0.95,
  "failure_family": "timeout",
  "severity": "high",
  "signature": "timeout:733da8a4e20740af",
  "summary": "Detected failure family: timeout. Key evidence: line 1: ERROR: Jenkins pipeline failed at stage Deploy. Timeout connecting to registry.",
  "likely_cause": "operation exceeded timeout threshold or a dependency responded too slowly",
  "first_remediation_step": "inspect the exact timed-out operation and compare recent latency trends",
  "next_debugging_action": "check downstream service latency, retries, and resource saturation",
  "probable_owner": "platform-networking",
  "release_blocking": true,
  "evidence": [
    {
      "line_number": 1,
      "text": "ERROR: Jenkins pipeline failed at stage Deploy. Timeout connecting to registry."
    }
  ],
  "recurrence": {
    "total_count": 3,
    "first_seen": "2026-03-12T16:18:31.621813+00:00",
    "last_seen": "2026-03-12T16:22:41.139282+00:00",
    "is_recurring": true
  }
}
```

---

## Sample Rule Simulation / Impact Preview

```json
{
  "rule_id": "timeout_rule",
  "incidents_evaluated": 3,
  "incidents_impacted": 3,
  "reclassified_incidents": 0,
  "severity_changed": 0,
  "release_blocking_changed": 0,
  "probable_owner_changed": 3,
  "sample_impacted_incidents": [
    {
      "id": 3,
      "signature": "timeout:733da8a4e20740af",
      "changed_fields": ["probable_owner"],
      "original": {
        "failure_family": "timeout",
        "severity": "high",
        "release_blocking": true,
        "probable_owner": "service-owner"
      },
      "simulated": {
        "failure_family": "timeout",
        "severity": "high",
        "release_blocking": true,
        "probable_owner": "platform-networking"
      }
    }
  ]
}
```

---

## Sample Rollback Preview

```json
{
  "audit_event_id": 1,
  "rule_id": "timeout_rule",
  "rollback_updates": {
    "probable_owner": "service-owner"
  },
  "impact_preview": {
    "incidents_evaluated": 3,
    "incidents_impacted": 3,
    "probable_owner_changed": 3
  }
}
```

---

## Sample Markdown Report

````md
# AutoOps Insight Report

## Release Risk Summary
- Release risk: **high**
- Total analyses: **3**
- Release-blocking incidents: **3**

## Top Recurring Signatures
- `timeout:733da8a4e20740af` | family=timeout | severity=high | count=3

## Operational Recommendation
- Repeated failure signatures are present at levels that may indicate regression or release instability.
- Investigate recurring signatures before promoting the current build or environment.
````

---

## Project Structure

```text
AutoOps-Insight/
├── main.py                     # FastAPI application and API routes
├── cli.py                      # Headless CLI for analysis and reporting
├── ml_predictor.py             # Structured incident analysis + ML-backed prediction
├── config/
│   └── rules.yaml              # Config-driven detection rules
├── classifiers/
│   ├── config_loader.py        # YAML rule loader
│   ├── rule_admin.py           # Rule update helper + audit integration
│   ├── rules.py                # Deterministic failure-family detection
│   ├── taxonomy.py             # Severity, ownership, remediation metadata
│   └── simulation.py           # Rule simulation, diff, and preview logic
├── analysis/
│   ├── formatter.py            # Incident summary formatting
│   ├── signatures.py           # Signature normalization and fingerprinting
│   ├── trends.py               # Trend/distribution/window analysis
│   └── anomalies.py            # Heuristic anomaly detection
├── storage/
│   ├── history.py              # SQLite persistence and historical queries
│   └── audit.py                # Audit log persistence
├── reports/
│   ├── renderer.py             # Markdown/JSON report generation
│   └── generated/              # Generated report artifacts
├── schemas/
│   └── incident.py             # Pydantic incident schema
├── ml_model/
│   ├── log_train.csv           # Training data
│   ├── train_model.py          # Training script
│   └── log_model.pkl           # Trained model + vectorizer
├── autoops-ui/                 # React/Vite dashboard
├── docs/
│   └── runbook.md              # Sample operator workflow
├── tests/                      # Unit and API integration tests
└── .github/workflows/          # CI workflow
```

---

## Tests

```bash
python -m pytest -q
```

Current test suite: **16 passing tests**, covering:
- Deterministic rule detection
- Signature stability and normalization
- Trend and anomaly heuristics
- Markdown report rendering
- API integration for `/analyze`, `/history/recent`, `/history/recurring`, and `/reports/summary`
- Rule simulation and field-level diff behavior

---

## Observability

Prometheus counters exposed at `/metrics`:

- `logs_processed_total`
- `predict_requests_total`
- `analyze_requests_total`
- `summarize_requests_total`
- `report_requests_total`

---

## Config-Driven Rules

Detection rules live in `config/rules.yaml`. Failure-family patterns, severity, ownership hints, and remediation guidance can be updated without changing backend logic. Rule changes are recorded in an audit log with event type, rule ID, actor, timestamp, and before/after values.

---

## Execution Modes

| Mode | Description |
|---|---|
| **API** | Upload logs and query history/report endpoints via FastAPI |
| **CLI** | Analyze logs, replay incidents, simulate rule changes, and generate reports headlessly |
| **Dashboard** | Inspect release risk, recurring signatures, anomalies, and reports in the React UI |
| **CI** | Run sample analyses and upload report artifacts via GitHub Actions |

---

## Runbook

A sample operator workflow is included in [`docs/runbook.md`](docs/runbook.md), covering:
- latest log analysis
- recurrence inspection
- incident replay
- rule review
- audit trail inspection
- release-risk triage

---

## Screenshots

These screenshots show the operator workflow for audit-backed rule changes and replayable incident triage.

### Audit Log Traceability
Rule update with actor, timestamp, and before/after diff.

![AutoOps audit log](docs/screenshots/autoops-audit-log.png)

### Incident Replay and Test Validation
Replayed stored incident with recurrence metadata and passing test run.

![AutoOps incident replay](docs/screenshots/autoops-incident-replay.png)

### Audit Diff and Rollback Preview UI
Shows audit-backed rule review in the dashboard, including selected audit event context and field-level diff inspection for a rule update.

![AutoOps audit diff and rollback preview UI](docs/screenshots/autoops-audit-diff-rollback-ui.png)


---

## Engineering Decisions

- **YAML rules** instead of hardcoded-only logic so detection patterns, severity, ownership hints, and remediation guidance can be updated without backend code changes.
- **Stable signature fingerprinting** to identify recurring incidents across noisy repeated logs and make recurrence tracking deterministic.
- **SQLite persistence** to keep replay, recurrence tracking, reporting, and preview workflows simple, inspectable, and easy to run locally.
- **Heuristic anomaly detection** instead of overfit ML to preserve explainability for operational triage and release-risk review.
- **API + CLI + dashboard + CI support** so the same system can support debugging, automation, visual inspection, artifact generation, and admin preview workflows.

---

## What This Is Not (Yet)

- Multi-source ingestion from system logs, containers, or metrics agents
- Time-series anomaly detection with robust statistical baselines
- Deep root-cause inference
- Multi-tenant incident correlation
- Production-scale storage or querying
- Real release gating inside a deployment pipeline
- Learned summarization or recommendation models

---

## Roles This Maps To

SRE · Production Engineering · Release Engineering · Internal Tooling · Platform / Infrastructure
---

## Operator Workflow and Incident Case Studies

AutoOps-Insight is designed to support operator-facing incident triage, not just passive reporting. In addition to rule-based + ML-assisted classification, the system correlates nearby changes, repeated incident signatures, release-blocking signals, and probable ownership to help responders move from detection to action faster.

### Before vs After Operator Triage Flow

**Before**
1. Notice repeated failures in logs or CI output
2. Manually inspect stack traces and error strings
3. Search dashboards for nearby latency or timeout spikes
4. Check whether a deploy or rule/config change happened nearby
5. Guess likely owner and escalation path
6. Manually draft mitigation or rollback decision

**After**
1. Classify the incident into a concrete failure family
2. Correlate nearby incidents and change events in a bounded timeline window
3. Surface likely owner, blast-radius hints, and repeated-signature patterns
4. Generate operator runbook guidance:
   - first checks
   - likely cause
   - rollback / no-rollback guidance
   - escalation route
   - mitigation sequence
5. Use fleet-level views to spot recurrence and noisy services

This reduces triage ambiguity and makes repeated incidents easier to classify, escalate, and mitigate consistently.

---

## Incident Case Study 1 — DNS / Connectivity Failure

**Incident family:** `dns`

**Observed signal**
- Resolver-related failures surfaced in log analysis
- Repeated host lookup failures clustered around the same affected dependency
- Operator workflow suggested DNS-focused checks rather than generic timeout investigation

**Correlated nearby change**
- No deploy rollback should be assumed automatically
- The correct first move is to verify whether a recent service discovery or DNS-related change occurred near the incident window

**Suggested rollback**
- Roll back only when correlation is strong with a recent config or service-discovery change
- Otherwise treat as a platform/network or name-resolution incident first

**Escalation route**
- `service-owner -> platform-networking -> dns/platform team`

**Mitigation sequence**
1. Retry resolution from multiple hosts or regions
2. Compare whether one hostname / zone is disproportionately affected
3. Shift to a known-good endpoint if one exists
4. Roll back recent DNS/service-discovery change if correlation is strong
5. Escalate with affected hostnames, regions, and timestamps

**Why it matters**
This shows the system can distinguish DNS-style failures from generic application-level regressions and give an operator a targeted next action path.

---

## Incident Case Study 2 — Release-Blocking Regression Near a Change Window

**Incident family:** `timeout`

**Observed signal**
- Multiple release-blocking incidents appeared within the same correlation window
- The correlation engine detected:
  - nearby change activity
  - multi-event burst behavior
  - single-family clustering
  - release-blocking incident concentration

**Example correlated nearby change**
- Audit history captured a nearby `rule_update` event in the incident window
- The system flagged that a rollback-oriented review could be useful because the incident burst aligned closely with a recent change

**Suggested rollback**
- Rollback guidance is treated as conditional, not automatic
- When nearby change timing and incident clustering align strongly, rollback becomes a recommended operator path to evaluate quickly

**Escalation route**
- `service-owner -> platform-networking` or the owner tied to the correlated change

**Mitigation sequence**
1. Identify the exact operation timing out
2. Compare timing, retries, and dependency latency before/after the nearby change
3. Check whether the incident is isolated or part of a broader burst
4. Evaluate rollback if the change window correlation is strong
5. Escalate with timestamps, affected services, and blocking scope

**Why it matters**
This makes the project feel like a production support system: it does not just label an error, it ties incident behavior to nearby operational changes and helps responders decide whether rollback is worth pursuing.

---

## Incident Case Study 3 — Noisy-Service Recurrence and Fleet Health

**Observed signal**
Fleet health views surfaced:
- recurring incident sources
- noisy-service ranking
- highest blast-radius regressions
- recurrence by subsystem
- MTTR-style recurrence windows

**Example fleet view**
In one dataset, the platform-networking owner surfaced as the highest-noise service grouping, while timeout-related signatures appeared repeatedly across the same source and subsystem patterns.

**Operator value**
This helps answer:
- Which service or subsystem is the noisiest?
- Which repeated signatures deserve deeper ownership attention?
- Which incidents are localized vs broad in blast radius?
- Which services repeatedly generate release-blocking conditions?

**Suggested action path**
1. Rank recurring sources by incident volume
2. Group repeated signatures by owner + failure family
3. Investigate services with repeated release-blocking impact
4. Use recurrence windows to prioritize long-running or reappearing issues
5. Route systemic issues to platform owners instead of treating them as isolated one-offs

**Why it matters**
This shifts the project from one-off incident labeling into recurring operational intelligence and incident pattern management.

---

## Example Operator Output Structure

A single incident workflow can now surface:

- **incident family:** `timeout`, `dns`, `tls_handshake`, `service_unreachable`, etc.
- **correlated nearby change:** deploy, rollout, rule update, or other audit-window activity
- **suggested rollback:** conditional guidance based on timing correlation and incident clustering
- **escalation route:** service-owner, platform-networking, platform-security, or owning dependency team
- **mitigation sequence:** ordered steps for immediate triage and containment

This makes AutoOps-Insight useful as an incident support tool, not just an analytics dashboard.


## Why This Matters for Production Engineering

This project is aimed at the operational gap between raw error logs and real responder action.

It helps operators answer:
- What kind of incident is this?
- Did it correlate with a nearby deploy or change?
- Is rollback likely helpful?
- Who should own escalation?
- What mitigation steps should happen first?
- Is this a recurring noisy-service problem or a one-off issue?

That framing makes the system more relevant for Production Engineering and operational backend roles than a generic reporting dashboard.
