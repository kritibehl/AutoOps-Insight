
from release_correlation.deployment_correlation import correlate_deployments_to_incidents, summarize_release_risk


from incident_search.search_service import search_incidents, service_owner_summary


from support_automation.incident_ingestion import normalize_support_incident
from support_automation.runbook_recommender import classify_issue_family, recommend_runbook_action
from support_automation.service_health_summary import summarize_service_health
from support_automation.escalation_router import probable_owner, escalation_path
from support_automation.ticket_lifecycle import next_status


from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge

import sqlite3
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agentgrid-seven.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)







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
from fastapi import FastAPI, Request, File, Header, HTTPException, UploadFile

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


autoops_support_incidents = Gauge(
    "autoops_support_incidents_total",
    "Total support incidents represented in AutoOps demo metrics"
)
autoops_escalations = Gauge(
    "autoops_escalations_total",
    "Total escalation workflows represented in AutoOps demo metrics"
)
autoops_agentgrid_events = Gauge(
    "autoops_agentgrid_events_ingested_total",
    "Total AgentGrid events represented in AutoOps demo metrics"
)
autoops_issue_families = Gauge(
    "autoops_issue_families_total",
    "Total issue families represented in AutoOps demo metrics"
)

autoops_support_incidents.set(102)
autoops_escalations.set(51)
autoops_agentgrid_events.set(19)
autoops_issue_families.set(6)

app = FastAPI(title="AutoOps Insight")

Instrumentator().instrument(app).expose(app, endpoint="/prometheus")




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


@app.options("/{full_path:path}")
async def preflight_handler(request: Request, full_path: str):
    return {}


@app.get("/support/metrics/live")
def support_metrics_live():
    return {
        "total_support_incidents": 102,
        "sources": 5,
        "issue_families": 6,
        "escalation_count": 51,
        "agentgrid_events_ingested": 19,
        "agentgrid_decision_breakdown": [
            {"agent_decision": "hold", "count": 1},
            {"agent_decision": "escalate", "count": 1},
            {"agent_decision": "synthetic_agentgrid_support", "count": 17}
        ],
        "top_issue_family": [
            {"issue_family": "unsafe_response", "count": 24},
            {"issue_family": "tool_failure", "count": 24},
            {"issue_family": "latency_spike", "count": 20},
            {"issue_family": "missing_context", "count": 12},
            {"issue_family": "wrong_answer", "count": 11},
            {"issue_family": "retrieval_failure", "count": 11}
        ],
        "action_counts": [
            {"action": "escalate_to_safety_review", "count": 24},
            {"action": "check_tool_dependency", "count": 24},
            {"action": "hold_release", "count": 20},
            {"action": "fix_retrieval_pipeline", "count": 12},
            {"action": "support_review", "count": 11},
            {"action": "tune_search_and_embeddings", "count": 11}
        ],
        "recurring_customer_blockers": [
            {"issue": "unsafe_response", "count": 24, "action": "escalate_to_safety_review"},
            {"issue": "tool_failure", "count": 24, "action": "check_tool_dependency"},
            {"issue": "latency_spike", "count": 20, "action": "hold_release"}
        ],
        "agentgrid_case_study": {
            "story": "AgentGrid detected missing context, emitted an event, AutoOps classified it, and generated PM, engineering, and support outputs.",
            "issue_family": "missing_context",
            "root_cause": "retrieval_or_context_pipeline_failure",
            "pm_summary": "Customer answer quality degraded due to missing context.",
            "engineering_bug_report": "Investigate retrieval pipeline and context assembly for AgentGrid workflow.",
            "support_action_plan": "Fix retrieval pipeline and provide workaround or escalation path."
        }
    }


@app.api_route("/incidents/{incident_id}/transition/live", methods=["GET", "POST"])
def transition_incident_live(
    incident_id: str,
    actor: str = "operator",
    old_state: str = "new",
    new_state: str = "triaged",
    reason: str = "operator_review"
):
    return {
        "status": "transition_recorded",
        "incident_id": incident_id,
        "actor": actor,
        "old_state": old_state,
        "new_state": new_state,
        "reason": reason,
        "audit_log": {
            "actor": actor,
            "action": "state_transition",
            "incident_id": incident_id,
            "old_state": old_state,
            "new_state": new_state,
            "reason": reason
        }
    }

@app.get("/healthz/live")
def healthz_live():
    return {
        "status": "ok",
        "service": "autoops-api",
        "deployment": "cloud-run",
        "features": [
            "support_metrics",
            "incident_lifecycle",
            "audit_logs",
            "agentgrid_events"
        ]
    }


@app.get("/correlation/demo")
def correlation_demo():
    import json
    from pathlib import Path
    from correlation_engine.incident_graph import build_incident_graph, summarize_graph
    from correlation_engine.root_cause_ranker import rank_root_causes

    events = json.loads(Path("samples/correlation/agentgrid_autoops_trace.json").read_text())
    graph = build_incident_graph(events)
    ranked_causes = rank_root_causes(events)

    return {
        "correlated_traces": len(graph),
        "events_analyzed": len(events),
        "graph_summary": summarize_graph(graph),
        "ranked_root_causes": ranked_causes,
        "top_root_cause": ranked_causes[0] if ranked_causes else None,
    }

@app.post("/support/ingest/enriched")
def ingest_support_incident_enriched(payload: dict):
    incident = normalize_support_incident(payload)
    issue_family = classify_issue_family(incident["issue_type"])
    runbook_action = recommend_runbook_action(issue_family)
    owner = probable_owner(incident["service"], issue_family)
    path = escalation_path(incident["severity"], issue_family)
    status_after_triage = next_status(incident["status"], incident["severity"])
    health = summarize_service_health(incident)

    return {
        "status": "ingested",
        **incident,
        "issue_family": issue_family,
        "probable_owner": owner,
        "recommended_runbook_action": runbook_action,
        "escalation_path": path,
        "customer_business_impact_summary": health["customer_impact_summary"],
        "service_health": health,
        "status_transition": {
            "old_status": incident["status"],
            "new_status": status_after_triage,
        },
    }

from fastapi import Depends
from auth.api_key_auth import get_role, require_permission
from auth.access_audit import write_access_audit

@app.post("/support/ingest/protected")
def ingest_support_incident_protected(payload: dict, role: str = Depends(get_role)):
    require_permission(role, "ingest")
    audit = write_access_audit(role, "/support/ingest/protected", "ingest", True)

    incident = normalize_support_incident(payload)
    issue_family = classify_issue_family(incident["issue_type"])
    runbook_action = recommend_runbook_action(issue_family)
    owner = probable_owner(incident["service"], issue_family)
    path = escalation_path(incident["severity"], issue_family)
    status_after_triage = next_status(incident["status"], incident["severity"])
    health = summarize_service_health(incident)

    return {
        "status": "ingested",
        "role": role,
        "access_audit": audit,
        **incident,
        "issue_family": issue_family,
        "probable_owner": owner,
        "recommended_runbook_action": runbook_action,
        "escalation_path": path,
        "customer_business_impact_summary": health["customer_impact_summary"],
        "service_health": health,
        "status_transition": {
            "old_status": incident["status"],
            "new_status": status_after_triage,
        },
    }

@app.get("/reports/service-health/protected")
def service_health_report_protected(role: str = Depends(get_role)):
    require_permission(role, "read_reports")
    audit = write_access_audit(role, "/reports/service-health/protected", "read_reports", True)

    return {
        "role": role,
        "access_audit": audit,
        "report": {
            "total_incidents": 102,
            "total_escalations": 51,
            "agentgrid_events_ingested": 19,
            "top_issue_family": "unsafe_response",
            "service_health": {
                "agentgrid": "degraded",
                "reporting-api": "watch",
                "faireval": "watch",
                "kubepulse": "watch"
            }
        }
    }

@app.post("/incidents/{incident_id}/escalate/protected")
def escalate_incident_protected(
    incident_id: str,
    reason: str = "service_owner_review",
    role: str = Depends(get_role)
):
    require_permission(role, "escalate")
    audit = write_access_audit(role, "/incidents/escalate/protected", "escalate", True)

    return {
        "status": "escalated",
        "incident_id": incident_id,
        "role": role,
        "reason": reason,
        "access_audit": audit,
        "escalation_control": {
            "allowed_roles": ["service_owner", "admin"],
            "executed_by": role
        }
    }


@app.get("/support/sla/summary")
def support_sla_summary():
    return {
        "reporting_period": "2026-W18",
        "total_tickets": 4,
        "open_tickets": 3,
        "resolved_tickets": 1,
        "sla_breached": 2,
        "avg_time_to_triage_minutes": 31.75,
        "high_priority_open": 2,
        "tickets": [
            {
                "ticket_id": "TCK-1001",
                "service": "reporting-api",
                "severity": "medium",
                "created_at": "2026-05-10T10:00:00Z",
                "status": "triaged",
                "owner": "reporting_platform_team",
                "sla_due_at": "2026-05-11T10:00:00Z",
                "sla_breached": False,
                "time_to_triage_minutes": 42,
                "time_to_resolution_hours": None,
                "escalation_count": 1,
                "recommended_next_action": "monitor dependency latency and update customer"
            },
            {
                "ticket_id": "TCK-1002",
                "service": "agentgrid",
                "severity": "high",
                "created_at": "2026-05-10T08:30:00Z",
                "status": "escalated",
                "owner": "platform_runtime_team",
                "sla_due_at": "2026-05-10T16:30:00Z",
                "sla_breached": True,
                "time_to_triage_minutes": 25,
                "time_to_resolution_hours": None,
                "escalation_count": 2,
                "recommended_next_action": "engineering escalation for tool dependency failure"
            },
            {
                "ticket_id": "TCK-1003",
                "service": "agentgrid",
                "severity": "critical",
                "created_at": "2026-05-10T07:00:00Z",
                "status": "escalated",
                "owner": "safety_review_team",
                "sla_due_at": "2026-05-10T11:00:00Z",
                "sla_breached": True,
                "time_to_triage_minutes": 10,
                "time_to_resolution_hours": None,
                "escalation_count": 3,
                "recommended_next_action": "safety owner review before release"
            },
            {
                "ticket_id": "TCK-1004",
                "service": "faireval",
                "severity": "medium",
                "created_at": "2026-05-10T09:15:00Z",
                "status": "resolved",
                "owner": "evaluation_platform_team",
                "sla_due_at": "2026-05-11T09:15:00Z",
                "sla_breached": False,
                "time_to_triage_minutes": 50,
                "time_to_resolution_hours": 5,
                "escalation_count": 0,
                "recommended_next_action": "document regression pattern and close"
            }
        ],
        "recurring_issue_families": [
            "tool_failure",
            "unsafe_response",
            "latency_or_timeout"
        ]
    }


@app.get("/incident-search")
def incidents_search(
    service: str | None = None,
    owner: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    issue_family: str | None = None,
):
    return search_incidents(
        service=service,
        owner=owner,
        severity=severity,
        status=status,
        issue_family=issue_family,
    )

@app.get("/service-owners/dashboard")
def service_owners_dashboard():
    return {
        "owners": service_owner_summary(),
        "summary": {
            "total_owners": len(service_owner_summary()),
            "total_incidents": 4,
            "open_incidents": 3,
            "critical_or_high": 2,
        }
    }

@app.get("/incidents/{incident_id}/timeline")
def incident_timeline(incident_id: str):
    results = search_incidents()["items"]
    for item in results:
        if item["incident_id"] == incident_id:
            return {
                "incident_id": incident_id,
                "service": item["service"],
                "owner": item["owner"],
                "timeline": item["timeline"],
                "current_status": item["status"],
            }
    return {"error": "incident_not_found", "incident_id": incident_id}


@app.get("/release-correlation/demo")
def release_correlation_demo():
    import json
    from pathlib import Path

    deployments = json.loads(Path("samples/release_correlation/deployments.json").read_text())
    incidents = json.loads(Path("samples/release_correlation/incidents_after_deploy.json").read_text())

    correlations = correlate_deployments_to_incidents(deployments, incidents)
    summary = summarize_release_risk(correlations)

    return {
        "summary": summary,
        "correlations": correlations,
    }


@app.get("/rca/demo")
def rca_demo():
    import json
    from pathlib import Path

    data = json.loads(Path("rca/escalation_chain.json").read_text())
    return {
        "incident_id": data["incident_id"],
        "probable_cause": data["probable_cause"],
        "impacted_services": data["impacted_services"],
        "timeline": data["timeline"],
        "rollback_candidate": data["rollback_candidate"],
        "release_risk": data["release_risk"],
        "next_actions": data["next_actions"],
    }


@app.get("/rai/monitoring/summary")
def rai_monitoring_summary():
    import json
    from pathlib import Path

    metrics = json.loads(Path("rai_monitoring/rai_monitoring_metrics.json").read_text())
    return metrics

@app.get("/rai/incidents/{incident_id}")
def rai_incident_detail(incident_id: str):
    import json
    from pathlib import Path

    incident = json.loads(Path("ai_safety_incidents/responsible_ai_incident_summary.json").read_text())
    if incident.get("incident_id") == incident_id:
        return incident

    return {
        "error": "incident_not_found",
        "incident_id": incident_id,
        "available_incident_id": incident.get("incident_id")
    }


@app.get("/aiops/incident-context/demo")
def aiops_incident_context_demo():
    import json
    from pathlib import Path

    return json.loads(Path("aiops_incident_context/incident_context_summary.json").read_text())
