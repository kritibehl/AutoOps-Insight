# AutoOps Insight

CI/CD Reliability Analytics Engine for Recurring Pipeline Failures

AutoOps Insight analyzes CI/CD execution logs, detects recurring failure patterns, exports reliability metrics, and generates structured summaries to reduce mean time to diagnosis (MTTD).

Designed as a reliability signal extraction layer for DevOps and platform teams.

---

## Why This Exists

CI/CD systems fail repeatedly for the same root causes:

- Dependency resolution issues  
- Test regressions  
- Build tool misconfigurations  
- Environment drift  
- Resource exhaustion  

But failure patterns are often buried inside verbose logs.

AutoOps Insight transforms unstructured logs into:

- Structured failure classification  
- Prometheus-exported reliability metrics  
- Human-readable failure summaries  
- Recurrence detection signals  

Focus: make CI failures observable, measurable, and trendable.

---

## System Overview

Architecture:

- React frontend (log upload + dashboard)
- FastAPI backend (log parsing + classification)
- ML classifier (TF-IDF + Logistic Regression)
- Prometheus metrics endpoint
- Optional LLM-based summarizer

Flow:

Logs → Feature Extraction → Failure Classification → Metrics Export → Dashboard Visualization

---

## Core Capabilities

### 1. Failure Type Classification

- TF-IDF vectorization
- Logistic Regression classifier
- Predicts common CI/CD failure categories
- Extensible label taxonomy

Example failure classes:

- Dependency Error
- Test Failure
- Compilation Error
- Timeout
- Configuration Error

---

### 2. Failure Recurrence Detection

- Aggregates classified failures
- Identifies repeating error signatures
- Enables trend tracking across runs
- Designed for MTTR reduction workflows

---

### 3. Prometheus Metrics Export

`/metrics` endpoint exposes:

- `ci_failure_total{type="dependency_error"}`
- `ci_pipeline_runs_total`
- `ci_failure_rate`
- `ci_failure_recurring_total`

Integrates directly with Grafana dashboards.

Operational value:
Convert CI reliability into measurable SLO-aligned signals.

---

### 4. Structured Log Summarization

Two modes:

1. Deterministic keyword-based summarizer  
2. Optional LLM-based summarizer (API-key gated)

Goal: compress large CI logs into actionable summaries.

---

## Tech Stack

Frontend:
- React (Vite)
- Tailwind CSS
- Axios

Backend:
- FastAPI
- Python
- scikit-learn
- python-dotenv

Machine Learning:
- TF-IDF
- Logistic Regression classifier

Observability:
- Prometheus metrics endpoint
- Docker-ready deployment

---

## Example Workflow

1. Upload CI/CD log file  
2. System predicts failure category  
3. Failure count increments in Prometheus  
4. Summary generated for fast diagnosis  
5. Reliability metrics visible via `/metrics`

---

## Design Principles

AutoOps Insight was built around:

- Deterministic classification pipeline
- Observable reliability signals
- Low-latency inference
- Extendable failure taxonomy
- Production-friendly integration

It is intentionally structured as an analytics layer, not just a dashboard.

---

## Local Setup

### Clone

```bash
git clone https://github.com/kritibehl/AutoOps-Insight.git
cd AutoOps-Insight

Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Frontend
cd frontend
npm install
npm run dev
Prometheus Test
curl http://localhost:8000/metrics
Future Extensions

Historical run storage (PostgreSQL)

Failure fingerprinting via hashing

Time-series trend analysis

CI plugin integration (GitHub Actions / Jenkins)

Alerting hooks (Slack / Webhooks)

SLO-based CI reliability scoring
