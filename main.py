from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from analytics_reporting import rebuild_reporting_tables, fetch_table
from analytics_quality import validate_data_quality
from analytics_stats import compare_recent_windows
from analytics_exports import export_powerbi_bundle
from analysis.network_signatures import infer_network_family
from analysis.runbooks import get_runbook
from analysis.correlation import correlate_incident
from analysis.fleet_health import fleet_summary
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest

from classifiers.config_loader import load_rules_config
from genai_summarizer import summarize_log
from classifiers.simulation import simulate_rule_update, build_rule_diff
from storage.history import get_all_analyses, get_audit_event_by_id
from ml_predictor import predict_log_issue, analyze_log_text
from reports.renderer import render_markdown_report, write_report_files
from storage.audit import init_audit_db, get_recent_audit_events
from storage.history import (
    init_db,
    record_analysis,
    get_signature_stats,
    get_top_recurring_signatures,
    get_recent_analyses,
    get_report_summary,
    get_analysis_by_id,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_audit_db()
    yield

app = FastAPI(title="AutoOps Insight", lifespan=lifespan)


def _prefer_network_family(log_text: str, predicted_family: str) -> str:
    inferred = infer_network_family(log_text)
    return inferred or predicted_family


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"^https:\/\/.*\.azurewebsites\.net$|^https:\/\/.*\.azurecontainerapps\.io$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logs_processed = Counter("logs_processed_total", "Number of logs processed")
predict_requests = Counter("predict_requests_total", "Number of prediction requests")
analyze_requests = Counter("analyze_requests_total", "Number of structured analysis requests")
summarize_requests = Counter("summarize_requests_total", "Number of summary requests")
report_requests = Counter("report_requests_total", "Number of report generation requests")


@app.get("/")
def root():
    return {"message": "AutoOps Insight is running!"}


@app.get("/rules")
def rules():
    return {"items": load_rules_config()}


@app.get("/audit/recent")
def audit_recent(limit: int = 20):
    return {"items": get_recent_audit_events(limit=limit)}


@app.post("/predict")
async def predict_log(file: UploadFile = File(...)):
    logs_processed.inc()
    predict_requests.inc()
    content = await file.read()
    text = content.decode("utf-8")
    return predict_log_issue(text)


@app.post("/analyze")
async def analyze_log(file: UploadFile = File(...)):
    logs_processed.inc()
    analyze_requests.inc()
    content = await file.read()
    text = content.decode("utf-8")

    result = analyze_log_text(text)
    record_analysis(result, filename=file.filename)
    result["recurrence"] = get_signature_stats(result["signature"])
    return result


@app.post("/summarize")
async def summarize_log_endpoint(file: UploadFile = File(...)):
    summarize_requests.inc()
    content = await file.read()
    text = content.decode("utf-8")
    summary = summarize_log(text)
    return {"summary": summary}


@app.get("/history/recent")
def history_recent(limit: int = 20):
    return {"items": get_recent_analyses(limit=limit)}


@app.get("/history/recurring")
def history_recurring(limit: int = 10):
    return {"items": get_top_recurring_signatures(limit=limit)}


@app.get("/history/signature/{signature}")
def history_signature(signature: str):
    return get_signature_stats(signature)


@app.get("/history/analysis/{analysis_id}")
def history_analysis(analysis_id: int):
    result = get_analysis_by_id(analysis_id)
    if result is None:
        return {"error": "analysis not found"}
    result["recurrence"] = get_signature_stats(result["signature"])
    return result


@app.get("/reports/summary")
def reports_summary():
    report_requests.inc()
    return get_report_summary()


@app.get("/reports/markdown", response_class=PlainTextResponse)
def reports_markdown():
    report_requests.inc()
    summary = get_report_summary()
    return render_markdown_report(summary)


@app.post("/reports/generate")
def reports_generate():
    report_requests.inc()
    summary = get_report_summary()
    return write_report_files(summary)


@app.get("/audit/{audit_id}")
def get_audit_event_endpoint(audit_id: int):
    event = get_audit_event_by_id(audit_id)
    if event is None:
        return {"error": "audit event not found", "audit_id": audit_id}
    if event.get("before") and event.get("after"):
        event["diff"] = build_rule_diff(event["before"], event["after"])
    else:
        event["diff"] = {}
    return event


@app.get("/audit/{audit_id}/rollback-preview")
def get_rollback_preview_endpoint(audit_id: int):
    event = get_audit_event_by_id(audit_id)
    if event is None:
        return {"error": "audit event not found", "audit_id": audit_id}
    if event.get("event_type") != "rule_update":
        return {"error": "rollback preview only supports rule_update events", "audit_id": audit_id}

    before = event.get("before") or {}
    after = event.get("after") or {}
    rollback_updates = {}

    for key, value in before.items():
        if after.get(key) != value:
            rollback_updates[key] = value

    incidents = get_all_analyses()
    impact_preview = simulate_rule_update(event["rule_id"], rollback_updates, incidents)

    return {
        "audit_event_id": audit_id,
        "rule_id": event["rule_id"],
        "rollback_updates": rollback_updates,
        "impact_preview": impact_preview,
    }


@app.get("/audit/{audit_id}")
def get_audit_event_endpoint(audit_id: int):
    event = get_audit_event_by_id(audit_id)
    if event is None:
        return {"error": "audit event not found", "audit_id": audit_id}
    if event.get("before") and event.get("after"):
        event["diff"] = build_rule_diff(event["before"], event["after"])
    else:
        event["diff"] = {}
    return event


@app.get("/audit/{audit_id}/rollback-preview")
def get_rollback_preview_endpoint(audit_id: int):
    event = get_audit_event_by_id(audit_id)
    if event is None:
        return {"error": "audit event not found", "audit_id": audit_id}
    if event.get("event_type") != "rule_update":
        return {"error": "rollback preview only supports rule_update events", "audit_id": audit_id}

    before = event.get("before") or {}
    after = event.get("after") or {}
    rollback_updates = {}

    for key, value in before.items():
        if after.get(key) != value:
            rollback_updates[key] = value

    incidents = get_all_analyses()
    impact_preview = simulate_rule_update(event["rule_id"], rollback_updates, incidents)

    return {
        "audit_event_id": audit_id,
        "rule_id": event["rule_id"],
        "rollback_updates": rollback_updates,
        "impact_preview": impact_preview,
    }


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return generate_latest()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}



@app.post("/reporting/rebuild")
def reporting_rebuild():
    return rebuild_reporting_tables()


@app.get("/reporting/daily")
def reporting_daily(limit: int = 100):
    return {"items": fetch_table("reporting_daily_summary", limit=limit)}


@app.get("/reporting/weekly")
def reporting_weekly(limit: int = 100):
    return {"items": fetch_table("reporting_weekly_summary", limit=limit)}


@app.get("/reporting/pipeline-trends")
def reporting_pipeline_trends(limit: int = 100):
    return {"items": fetch_table("reporting_pipeline_trends", limit=limit)}


@app.get("/reporting/root-causes")
def reporting_root_causes(limit: int = 100):
    return {"items": fetch_table("reporting_root_cause_counts", limit=limit)}


@app.get("/reporting/deployment-regressions")
def reporting_deployment_regressions(limit: int = 100):
    return {"items": fetch_table("reporting_deployment_regressions", limit=limit)}


@app.get("/reporting/data-quality")
def reporting_data_quality():
    return validate_data_quality()


@app.get("/reporting/compare")
def reporting_compare(before_limit: int = 10, after_limit: int = 10):
    return compare_recent_windows(before_limit=before_limit, after_limit=after_limit)


@app.post("/reporting/export-powerbi")
def reporting_export_powerbi():
    return export_powerbi_bundle()



@app.get("/incident/runbook/{failure_family}")
def incident_runbook(failure_family: str):
    return get_runbook(failure_family)


@app.get("/incident/correlate")
def incident_correlate(incident_id: int | None = None, signature: str | None = None, window_minutes: int = 30):
    return correlate_incident(incident_id=incident_id, signature=signature, window_minutes=window_minutes)


@app.get("/fleet/health")
def fleet_health_view():
    return fleet_summary()
