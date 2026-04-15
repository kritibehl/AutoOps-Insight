import os

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from ml_predictor import analyze_log_text
from storage.audit import get_recent_audit_events, init_audit_db
from storage.history import (
    get_all_analyses,
    get_analysis_by_id,
    get_audit_event_by_id,
    get_recent_analyses,
    get_report_summary,
    get_signature_stats,
    get_top_recurring_signatures,
    init_db,
    record_analysis,
)
from analysis.release.fleet_views import (
    release_window_blast_radius,
    service_level_recurrence_heatmap,
    top_noisy_components,
)

AUTOOPS_TOKEN = os.getenv("AUTOOPS_TOKEN", "dev-token")

app = FastAPI(title="AutoOps Insight")


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


@app.post("/analyze")
async def analyze_log(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    result = analyze_log_text(text)
    enriched = record_analysis(result, filename=file.filename, raw_text=text)
    stats = get_signature_stats(result["signature"])

    return {
        "failure_family": result["failure_family"],
        "signature": result["signature"],
        "severity": result["severity"],
        "summary": result["summary"],
        "root_cause": enriched.get("root_cause") if isinstance(enriched, dict) else None,
        "release_decision": enriched.get("release_decision") if isinstance(enriched, dict) else None,
        "decision_confidence": enriched.get("decision_confidence") if isinstance(enriched, dict) else None,
        "recurrence_total": stats["total_count"],
    }


@app.post("/integrations/github-actions/ingest")
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

    filename = f"{x_repo_name or 'unknown'}__{x_workflow_name or 'unknown'}__{x_run_id or 'unknown'}.log"
    enriched = record_analysis(
        result,
        filename=filename,
        repo_name=x_repo_name,
        workflow_name=x_workflow_name,
        run_id=x_run_id,
        raw_text=text,
    )

    stats = get_signature_stats(result["signature"])

    return {
        "status": "ingested",
        "repo": x_repo_name,
        "workflow": x_workflow_name,
        "run_id": x_run_id,
        "failure_family": result["failure_family"],
        "signature": result["signature"],
        "root_cause": enriched.get("root_cause") if isinstance(enriched, dict) else None,
        "release_decision": enriched.get("release_decision") if isinstance(enriched, dict) else None,
        "decision_confidence": enriched.get("decision_confidence") if isinstance(enriched, dict) else None,
        "rule_based_confidence": enriched.get("rule_based_confidence") if isinstance(enriched, dict) else None,
        "ml_fallback_confidence": enriched.get("ml_fallback_confidence") if isinstance(enriched, dict) else None,
        "ambiguous_classification": enriched.get("ambiguous_classification") if isinstance(enriched, dict) else None,
        "runbook_confidence": enriched.get("runbook_confidence") if isinstance(enriched, dict) else None,
        "recurrence_total": stats["total_count"],
    }


@app.get("/history/recent")
def history_recent(limit: int = 20):
    return {"items": get_recent_analyses(limit=limit)}


@app.get("/history/recurring")
def history_recurring(limit: int = 10):
    return {"items": get_top_recurring_signatures(limit=limit)}


@app.get("/history/analysis/{analysis_id}")
def history_analysis(analysis_id: int):
    result = get_analysis_by_id(analysis_id)
    if result is None:
        return {"error": "analysis not found"}
    return result


@app.get("/reports/summary")
def reports_summary():
    return get_report_summary()


@app.get("/audit/recent")
def audit_recent(limit: int = 20):
    return {"items": get_recent_audit_events(limit=limit)}


@app.get("/audit/{audit_id}")
def get_audit_event_endpoint(audit_id: int):
    event = get_audit_event_by_id(audit_id)
    if event is None:
        return {"error": "audit event not found", "audit_id": audit_id}
    return event


@app.get("/intelligence/clusters")
def intelligence_clusters(limit: int = 20):
    return {"items": get_top_recurring_signatures(limit=limit)}


@app.get("/fleet/recurrence-heatmap")
def fleet_recurrence_heatmap(limit: int = 200):
    rows = get_recent_analyses(limit=limit)
    return {"items": service_level_recurrence_heatmap(rows)}


@app.get("/fleet/top-noisy-components")
def fleet_top_noisy_components(limit: int = 200, top_k: int = 10):
    rows = get_recent_analyses(limit=limit)
    return {"items": top_noisy_components(rows, limit=top_k)}


@app.get("/release/blast-radius")
def release_blast_radius(limit: int = 200):
    rows = get_recent_analyses(limit=limit)
    return release_window_blast_radius(rows)


@app.get("/release/summary")
def release_summary():
    return get_report_summary()


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return ""
