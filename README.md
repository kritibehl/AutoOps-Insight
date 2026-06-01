# AutoOps-Insight

> A production-style incident operations platform that classifies CI/CD failures, surfaces recurring issue patterns, generates AI-assisted RCA, and routes escalations — modeling postmortem, alert correlation, and trend analytics workflows.

`Python` · `FastAPI` · `React` · `Scikit-learn` · `Prometheus` · `Docker`

---

## Why This Project Matters

- CI/CD failures repeat: the same root cause appears as a new incident every sprint because recurring patterns aren't visible until manually identified
- Without structured classification, engineers fix symptoms instead of causes — and escalations arrive without RCA context
- AutoOps turns raw logs into structured intelligence: failure type, recurring family, RCA summary, rollback recommendation — in one API call
- This proves: incident analytics design, ML classification engineering, operational reporting discipline, and Responsible AI monitoring

---

## 30-Second Proof

| Signal | Verified output |
|---|---|
| Incidents tracked | **102** (controlled scenarios) |
| Escalations routed with RCA | **51** |
| Recurring issue families surfaced | **6** |
| Recurring incident percentage | **61%** |
| `retry_storm` trend increase | **+33.3%** |
| Classifier confidence (example) | **0.94** |
| Incident ops tests | **3/3 passing** |
| RAI toxicity rate | **0.0%** |

---

## What AutoOps Is

An incident operations platform. It models the full lifecycle from alert to postmortem:

```
Alert / CI failure
      │
      ▼
Classification  →  failure type + confidence
      │
      ▼
RCA generation  →  probable cause + rollback recommendation
      │
      ▼
Escalation routing  →  RCA context attached
      │
      ▼
Postmortem  →  recurring family detected · trend flagged
      │
      ▼
Trend analytics  →  retry_storm +33.3% · 61% recurring
```

Everything else — RAI monitoring, ML classifier, stream analytics — serves this lifecycle.

---

## Screenshots

> Add these to `docs/screenshots/` — highest ROI remaining improvement.

| Postmortem Timeline | Alert Correlation |
|---|---|
| ![Postmortem](docs/screenshots/postmortem_timeline.png) | ![Alert Correlation](docs/screenshots/alert_correlation.png) |

| Incident Trend Analytics | Runbook Quality Report |
|---|---|
| ![Trend Analytics](docs/screenshots/incident_trends.png) | ![Runbook Quality](docs/screenshots/runbook_quality.png) |

**Escalation chain — what the incident view shows:**

```
┌──────────────────────────────────────────────────────────────┐
│  Incident #47 — DependencyError                              │
├──────────────────────────────────────────────────────────────┤
│  classified_failure:   DependencyError  (confidence: 0.94)  │
│  recurring_family:     dependency_resolution_failures        │
│  previous_occurrence:  inc_031, inc_019, inc_008  (3x)       │
│  deploy_correlated:    true                                  │
│                                                             │
│  RCA:  Dependency pinning policy not enforced;               │
│        upstream 2.3.1 broke ABI contract.                   │
│                                                             │
│  recommended_action:   Pin at 2.2.x; add version-lock gate. │
│  rollback_recommended: false                                 │
│  escalated:            true                                  │
├──────────────────────────────────────────────────────────────┤
│  retry_storm trend:    +33.3% over 7 days  ← flagged        │
│  recurring_pct:        61%                                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Demo

```bash
git clone https://github.com/kritibehl/AutoOps-Insight
cd autoops-insight
make demo
```

Expected output:
```json
{
  "failure_type": "DependencyError",
  "confidence": 0.94,
  "recurring_family": "dependency_resolution_failures",
  "escalated": true,
  "rca": "Dependency pinning policy not enforced; upstream 2.3.1 broke ABI contract.",
  "recommended_action": "Pin at 2.2.x; add version-lock CI gate.",
  "rollback_recommended": false,
  "rai_status": "pass"
}
```

```bash
make test    # 3/3 incident ops tests passing
make report  # incident summary → reports/latest/incident_summary.json
```

---

## Architecture

![AutoOps Architecture](docs/architecture.png)

```
CI/CD log (uploaded .txt)
      │
      ▼
ML classifier (TF-IDF + Logistic Regression)
  → failure_type + confidence
      │
      ▼
Summarizer (keyword / LLM)
  → human-readable RCA
      │
      ▼
Incident store  →  102 incidents · 6 recurring families
      │
      ▼
Cloud Run API
  /incidents  /rca  /escalations  /rai-monitoring
      │
      ▼
React dashboard  →  postmortem · alert correlation · trend analytics
      │
      ▼
Prometheus /metrics  →  incident counts · escalation rate · classifier confidence
```

**RCA generation pipeline:**
```
telemetry / log  →  classify  →  cluster by family
      →  deploy correlation check  →  recurrence check
      →  RCA summary + rollback recommendation
      →  escalation if warranted
```

---

## Core Workflows

### 1. CI/CD log classification

Upload a build log, receive failure type, confidence score, recurring family tag, and RCA recommendation.

```bash
make demo
# → failure_type: DependencyError · confidence: 0.94
```

### 2. Recurring issue detection

Groups incidents by root-cause family. Surfaces that 61% of incidents are recurring — the same patterns repeating every sprint.

```
Top families:
  dependency_resolution    38 incidents  ← sprint-recurring
  flaky_tests              21 incidents
  runtime_oom              14 incidents
  retry_storm:  trend +33.3%  ← escalating
```

### 3. Postmortem + trend analytics

Rolling incident windows with surge detection, escalation heatmap, and `retry_storm` trend tracking.

```
retry_storm trend: +33.3% over 7 days  →  flagged for review
escalation_rate_1h: 0.61
recurring_incident_pct: 61%
```

---

## Failure Scenarios Covered

| Failure type | Example | Classifier output |
|---|---|---|
| Dependency error | Missing transitive dependency | `DependencyError` · 0.94 |
| Test failure | Flaky integration test | `TestFailure` · 0.89 |
| Build error | Compilation failure | `BuildError` · 0.91 |
| Runtime OOM | Memory limit exceeded | `RuntimeError` · 0.87 |
| Retry storm | Auth service retry amplification | `retry_storm` family |
| Deploy correlation | Failure follows deploy | `deploy_correlated: true` |

---

## Engineering Decisions

**Why TF-IDF + Logistic Regression instead of a larger model:** Log classification is a structured text problem with narrow vocabulary. TF-IDF captures signal-bearing terms (library names, error codes); LR gives calibrated confidence scores. No GPU required, sub-100ms inference.

**Why recurring family detection:** Individual RCA fixes symptoms. Family detection fixes causes. Surfacing that 38 incidents share a `dependency_resolution` root cause changes the priority of the fix.

**Why a RAI monitoring endpoint:** AI-generated summaries can hallucinate. Tracking toxicity rate and hallucination rate per summary cohort ensures the AI layer doesn't introduce new failure modes while fixing the ones it's supposed to catch.

---

## What Is Intentionally Out of Scope

- 102 incidents are from controlled scenarios, not production customer incidents
- ML classifier trained on synthetic examples, not a production-scale labeled dataset
- Cloud Run deployment is a proof artifact, not enterprise production infrastructure
- LLM summarization is optional and requires an OpenAI API key

---

## Resume Bullets

- Built an AIOps incident platform with TF-IDF + Logistic Regression log classification (0.94 confidence), surfacing 6 recurring issue families across 102 incidents — 61% recurring rate
- Detected a +33.3% retry storm trend increase and routed 51 escalations with structured RCA context via a Cloud Run API
- Implemented Responsible AI monitoring (toxicity rate, hallucination detection, quality scoring) on AI-generated summaries as a first-class platform signal

---

## Interview Walkthrough

*"AutoOps models what incident tooling should do: not just alert, but classify, group, and explain. I built an ML classifier that takes a raw build log and outputs failure type with confidence. Then I added a recurring-family layer — 61% of the 102 incidents I tested share a root cause family. That's the signal that changes what you fix. I also track a retry storm trend (+33.3% over 7 days) and emit that as an escalation trigger. The RAI monitoring endpoint makes sure the AI summaries themselves don't introduce new failure modes."*

---

## Run Locally

```bash
git clone https://github.com/kritibehl/AutoOps-Insight && cd autoops-insight
pip install -r requirements.txt
make demo    # classify + RCA demo
make test    # 3/3 incident ops tests
make report  # incident summary
```

React dashboard:
```bash
cd autoops-ui && npm install && npm run dev
# → http://localhost:5173
```

---

## Repository Map

```
autoops-insight/
├── backend/         FastAPI + ML classifier + summarizer
├── autoops-ui/      React dashboard (Vite + Tailwind)
├── sample_logs/     Example CI/CD log files
├── reports/         Incident summaries + trend analytics
└── docs/            Architecture + screenshots
```
