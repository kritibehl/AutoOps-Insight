import sqlite3
import os
from fastapi import FastAPI

app = FastAPI()

SUPPORT_DB_PATH = os.getenv("SUPPORT_DB_PATH", "support_incidents.db")


def safe_fetch(conn, query):
    try:
        return [dict(r) for r in conn.execute(query)]
    except:
        return []




def init_support_db():
    conn = sqlite3.connect(SUPPORT_DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
    CREATE TABLE IF NOT EXISTS support_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        source TEXT DEFAULT 'unknown',
        customer_id TEXT,
        issue_family TEXT,
        signature TEXT,
        recurrence_total INTEGER DEFAULT 1,
        confidence REAL DEFAULT 0.0,
        root_cause TEXT,
        action TEXT,
        escalation_required INTEGER DEFAULT 0,
        pm_summary TEXT,
        engineering_bug_report TEXT,
        support_action_plan TEXT,
        agent_decision TEXT,
        trace_id TEXT,
        workflow TEXT,
        severity TEXT
    )
    """)

    existing_cols = {
        row["name"] for row in conn.execute("PRAGMA table_info(support_incidents)").fetchall()
    }

    columns = {
        "created_at": "TEXT",
        "source": "TEXT DEFAULT 'unknown'",
        "customer_id": "TEXT",
        "issue_family": "TEXT",
        "signature": "TEXT",
        "recurrence_total": "INTEGER DEFAULT 1",
        "confidence": "REAL DEFAULT 0.0",
        "root_cause": "TEXT",
        "action": "TEXT",
        "escalation_required": "INTEGER DEFAULT 0",
        "pm_summary": "TEXT",
        "engineering_bug_report": "TEXT",
        "support_action_plan": "TEXT",
        "agent_decision": "TEXT",
        "trace_id": "TEXT",
        "workflow": "TEXT",
        "severity": "TEXT",
    }

    for col, typ in columns.items():
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE support_incidents ADD COLUMN {col} {typ}")

    conn.commit()
    conn.close()


# init_support_db()









import os
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ml_predictor import analyze_log_text
from schemas import (
    DashboardSummaryResponse,
    IncidentRecord,
    IncidentsResponse,
    IngestResponse,
    MetricsResponse,
)
from storage.audit import get_recent_audit_events, init_audit_db
from support_engine.root_cause_engine import classify_issue, infer_root_cause, recommend_action, generate_summary
from storage.history import (
    get_analysis_by_id,
    get_recent_analyses,
    get_report_summary,
    get_signature_stats,
    get_top_recurring_signatures,
    init_db,
    record_analysis,
)

AUTOOPS_TOKEN = os.getenv("AUTOOPS_TOKEN", "dev-token")

app = FastAPI(title="AutoOps Insight")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4174","http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    init_audit_db()


@app.get("/")
def root():
    return {"message": "AutoOps Insight is running!"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
@app.post("/integrations/github-actions/ingest", response_model=IngestResponse)
async def ingest_github_actions_failure(
    file: UploadFile = File(...),
    x_autoops_token: str | None = Header(default=None),
    x_repo_name: str | None = Header(default=None),
    x_workflow_name: str | None = Header(default=None),
    x_run_id: str | None = Header(default=None),
):
    if x_autoops_token != AUTOOPS_TOKEN:
        raise HTTPException(status_code=401, detail="invalid token")

    content = await file.read()
    text = content.decode("utf-8")
    result = analyze_log_text(text)

    enriched = record_analysis(
        result,
        filename=file.filename,
        repo_name=x_repo_name,
        workflow_name=x_workflow_name,
        run_id=x_run_id,
        raw_text=text,
    )

    stats = get_signature_stats(result["signature"])

    return IngestResponse(
        status="ingested",
        repo=x_repo_name,
        workflow=x_workflow_name,
        run_id=x_run_id,
        incident_type=enriched["incident_type"],
        failure_family=result["failure_family"],
        signature=result["signature"],
        recurrence_total=stats["total_count"],
        confidence=enriched["confidence"],
        likely_trigger=enriched["likely_trigger"],
        trigger_confidence=enriched["trigger_confidence"],
        root_cause=enriched["root_cause"],
        release_decision=enriched["release_decision"],
        decision_confidence=enriched["decision_confidence"],
        decision_reason=enriched["decision_reason"],
        action=enriched["action"],
    )


@app.get("/incidents", response_model=IncidentsResponse)
def incidents(limit: int = 50):
    rows = get_recent_analyses(limit=limit)
    items = []
    for row in rows:
        items.append(
            IncidentRecord(
                id=row.get("id"),
                created_at=row.get("created_at"),
                repo_name=row.get("repo_name"),
                workflow_name=row.get("workflow_name"),
                run_id=row.get("run_id"),
                incident_type=row.get("predicted_issue") or row.get("failure_family", "unknown"),
                failure_family=row.get("failure_family", "unknown"),
                signature=row.get("signature", ""),
                recurrence_total=len(get_signature_stats(row.get("signature", ""))["recent_occurrences"]) or 1,
                confidence=0.91 if row.get("failure_family") != "unknown" else 0.55,
                likely_trigger=row.get("likely_trigger"),
                trigger_confidence=row.get("trigger_confidence"),
                root_cause=row.get("root_cause"),
                release_decision=row.get("release_decision") or "investigate",
                decision_confidence=row.get("decision_confidence") or 0.60,
                decision_reason=[],
                action=row.get("release_decision") or "investigate",
            )
        )
    return IncidentsResponse(items=items)


@app.get("/incidents/{analysis_id}")
def incident_by_id(analysis_id: int):
    result = get_analysis_by_id(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="analysis not found")
    return result


@app.get("/metrics", response_model=MetricsResponse)
def metrics():
    summary = get_report_summary()
    top_failure_family = None
    if summary["top_failures"]:
        top_failure_family = summary["top_failures"][0]["failure_family"]

    recent = get_recent_analyses(limit=200)
    hold_release_count = sum(1 for r in recent if r.get("release_decision") == "hold_release")
    investigate_count = sum(1 for r in recent if r.get("release_decision") == "investigate")

    return MetricsResponse(
        total_analyses=summary["total_analyses"],
        hold_release_count=hold_release_count,
        investigate_count=investigate_count,
        top_failure_family=top_failure_family,
    )


@app.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(limit: int = 100):
    summary = get_report_summary()
    recent = get_recent_analyses(limit=limit)
    return DashboardSummaryResponse(
        top_failures=summary["top_failures"],
        noisy_services=summary["noisy_services"],
        action_summary={
            "hold_release": sum(1 for r in recent if r.get("release_decision") == "hold_release"),
            "investigate": sum(1 for r in recent if r.get("release_decision") == "investigate"),
        },
        recurrence_heatmap=summary["top_recurring_signatures"],
    )


@app.get("/history/recurring")
def history_recurring(limit: int = 10):
    return {"items": get_top_recurring_signatures(limit=limit)}


@app.get("/audit/recent")
def audit_recent(limit: int = 20):
    return {"items": get_recent_audit_events(limit=limit)}

@app.post("/support/analyze")
async def analyze_support_case(payload: dict):
    text = payload.get("text", "")
    issue = classify_issue(text)
    cause = infer_root_cause(issue)
    action = recommend_action(issue)
    summary = generate_summary(issue, cause)

    return {
        "issue_type": issue,
        "root_cause": cause,
        "recommended_action": action,
        "summary": summary,
        "stakeholder_outputs": {
            "pm_summary": f"Detected {issue} support issue with likely product risk.",
            "engineering_bug_report": f"Investigate {issue}; suspected cause: {cause}.",
            "support_action_plan": f"Recommended support action: {action}.",
        },
    }



@app.get("/support/metrics")
def support_metrics():
    conn = sqlite3.connect(SUPPORT_DB_PATH)
    conn.row_factory = sqlite3.Row

    # Ensure table exists before querying
    conn.execute("""
    CREATE TABLE IF NOT EXISTS support_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        source TEXT,
        issue_family TEXT,
        signature TEXT,
        agent_decision TEXT,
        severity TEXT
    )
    """)

    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM support_incidents").fetchone()["c"]
    except:
        total = 0

    try:
        decisions = [
            dict(r) for r in conn.execute("""
                SELECT agent_decision, COUNT(*) as count
                FROM support_incidents
                GROUP BY agent_decision
            """)
        ]
    except:
        decisions = []

    conn.close()

    return {
        "agentgrid_events_ingested": total,
        "agentgrid_decision_breakdown": decisions
    }



@app.post("/support/ingest")
def ingest_agentgrid_support_event(event: dict):
    # init_support_db()

    source = event.get("source", "agentgrid")
    issue_type = event.get("issue_type", "unknown")
    severity = event.get("severity", "high")
    decision = event.get("decision", "hold")
    reason = event.get("reason", issue_type)

    escalation_required = 1 if decision == "escalate" else 0

    conn = sqlite3.connect(SUPPORT_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        INSERT INTO support_incidents (
            created_at,
            source,
            customer_id,
            issue_family,
            signature,
            recurrence_total,
            confidence,
            root_cause,
            action,
            escalation_required,
            pm_summary,
            engineering_bug_report,
            support_action_plan,
            agent_decision,
            trace_id,
            workflow,
            severity
        )
        VALUES (
            datetime('now'),
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """,
        (
            source,
            "agentgrid-demo",
            issue_type,
            reason,
            1,
            0.95,
            reason,
            decision,
            escalation_required,
            f"AgentGrid emitted {decision} for {issue_type}",
            f"Investigate AgentGrid {issue_type} event",
            f"Decision={decision}; reason={reason}; severity={severity}",
            decision,
            event.get("trace_id", ""),
            "agentgrid_eval_gate",
            severity,
        ),
    )
    conn.commit()

    row_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.close()

    return {
        "status": "ingested",
        "id": row_id,
        "source": source,
        "issue_type": issue_type,
        "decision": decision,
        "severity": severity,
    }

@app.on_event("startup")
def startup_event():
    init_support_db()
