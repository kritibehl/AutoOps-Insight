# AutoOps-Insight

> A reliability analytics tool for CI and infrastructure failures — classifies logs, fingerprints recurring incident signatures, tracks historical recurrence, detects anomaly patterns, and generates release-risk summaries through an API, CLI, CI workflow, and dashboard.

---

## What It Does

AutoOps-Insight takes raw failure logs and turns them into structured, actionable reliability intelligence. Rather than simply labeling a log as "timeout", it produces a structured incident artifact with severity, likely cause, remediation steps, ownership, and a stable fingerprint for tracking recurrence over time.

The system answers questions like:
- Has this failure happened before, and how often?
- Is this build environment risky enough to block a release?
- What failure patterns are dominating recent CI runs?
- Which recurring signatures should the team prioritize?

---

## Architecture Overview

```
Log Input
   │
   ├── Rule-Based Detection (deterministic patterns)
   └── ML-Assisted Classification (TF-IDF + Logistic Regression)
          │
          ▼
   Structured Incident Analysis
   (severity, signature, cause, owner, release-blocking flag)
          │
          ▼
   SQLite Persistence
          │
   ┌──────┴──────┐
   │             │
History API   Reports
Recurrence    (JSON + Markdown)
Detection     Release-Risk Score
```

---

## Features

### Structured Incident Analysis
Each log upload produces a full incident record — not just a label:

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
Each incident gets a stable, normalized signature like `timeout:733da8a4e20740af`. This enables cross-run recurrence tracking — the system knows when two failures are the same underlying issue regardless of log noise.

### Historical Recurrence Tracking
Results are persisted in SQLite. The system tracks:
- Total occurrence count per signature
- First and last seen timestamps
- Whether a signature qualifies as recurring
- Failure family distribution over time

### Release-Risk Reporting
The report engine aggregates stored history into a release-risk summary (`low` / `medium` / `high` / `critical`) based on:
- Presence of release-blocking incidents
- Recurring signature concentration
- Anomaly flags (e.g. one signature accounts for 80% of recent failures)
- Window comparison vs. baseline blocker rate

### Anomaly Detection
Heuristic-based flags that surface meaningful signals without fake sophistication:
- Signature concentration spike
- High-count recurring failures
- Family-level spikes
- Release blocker saturation

### API
Full FastAPI backend with endpoints for:
- `POST /analyze` — analyze a log, persist the result
- `GET /history/recent` — recent incident list
- `GET /history/recurring` — top recurring signatures
- `GET /history/signature/{signature}` — recurrence detail for one signature
- `GET /history/analysis/{analysis_id}` — stored incident detail
- `GET /reports/summary` — structured release-risk summary (JSON)
- `GET /reports/markdown` — human-readable markdown report
- `POST /reports/generate` — write report artifacts to disk
- `GET /metrics` — Prometheus counters
- `GET /healthz` — health check

### CLI
Headless operation for CI and automation:

```bash
# Health check
python cli.py health

# Analyze a log file and persist it
python cli.py analyze sample.log

# Compact operator-style output (no JSON)
python cli.py analyze sample.log --no-print-json

# Generate release-risk report artifacts
python cli.py report
```

### CI Integration
GitHub Actions workflow that:
- Runs CLI health check
- Analyzes sample logs automatically
- Generates markdown and JSON report artifacts
- Uploads report artifacts and SQLite DB for inspection

### Dashboard
React frontend showing:
- Release risk score, total analyses, blocker count, recurring signatures
- Log upload with full incident breakdown
- Anomaly panel
- Recurring signatures table
- Recent analyses list
- Failure family distribution
- Markdown report preview

---

## Detection Logic

The classifier uses two layers:

**Rule-based detection** checks for deterministic patterns:
`timeout` · `dns_failure` · `connection_refused` · `tls_failure` · `retry_exhausted` · `oom` · `flaky_test_signature` · `dependency_unavailable` · `crash_loop` · `latency_spike`

**ML fallback** uses:
- TF-IDF vectorization
- Logistic Regression trained on labeled log data (`ml_model/log_train.csv`)

Each analysis record indicates whether rule-based detection or ML prediction was used.

---

## Failure Taxonomy

Each failure family maps to reliability metadata:

| Family | Severity | Release Blocking |
|---|---|---|
| `timeout` | high | yes |
| `oom` | critical | yes |
| `connection_refused` | high | yes |
| `dns_failure` | high | yes |
| `flaky_test_signature` | medium | no / context-dependent |
| `retry_exhausted` | medium | yes |
| `crash_loop` | critical | yes |
| `dependency_error` | high | yes |
| `dependency_unavailable` | high | yes |

---

## Project Structure

```text
AutoOps-Insight/
├── main.py                     # FastAPI application and API routes
├── cli.py                      # Headless CLI for analysis and reporting
├── ml_predictor.py             # Structured incident analysis + ML-backed prediction
├── classifiers/
│   ├── rules.py                # Deterministic failure-family detection
│   └── taxonomy.py             # Severity, ownership, remediation metadata
├── analysis/
│   ├── formatter.py            # Incident summary formatting
│   ├── signatures.py           # Signature normalization and fingerprinting
│   ├── trends.py               # Trend/distribution/window analysis
│   └── anomalies.py            # Heuristic anomaly detection
├── storage/
│   └── history.py              # SQLite persistence and historical queries
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
├── tests/                      # Unit and API integration tests
└── .github/workflows/          # CI workflow
```

---

## Getting Started

**Install dependencies:**
```bash
python -m pip install -r requirements.txt
```

**Train or retrain the model:**
```bash
cd ml_model
python train_model.py
cd ..
```

**Start the API server:**
```bash
uvicorn main:app --reload
```

**Run the CLI:**
```bash
python cli.py analyze sample.log
python cli.py report
```

**Start the frontend:**
```bash
cd autoops-ui
npm install
npm run dev
```

---

## Tests

```bash
python -m pytest -q
```

Current suite: **14 passing tests**

Coverage includes:
- Deterministic rule detection
- Signature stability and normalization
- Trend and anomaly heuristics
- Markdown report rendering
- API integration for `/analyze`, `/history/recent`, `/history/recurring`, and `/reports/summary`

---

## Execution Modes

AutoOps-Insight supports four usage modes:

- **API mode** — upload logs and query history/report endpoints through FastAPI
- **CLI mode** — analyze logs and generate reports headlessly for CI or local workflows
- **Dashboard mode** — inspect release risk, recurring signatures, anomalies, and reports in the React UI
- **CI mode** — run sample analyses and upload report artifacts through GitHub Actions

---

## Observability

Prometheus counters exposed at `/metrics`:

- `logs_processed_total`
- `predict_requests_total`
- `analyze_requests_total`
- `summarize_requests_total`
- `report_requests_total`

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