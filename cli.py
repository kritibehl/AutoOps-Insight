import json
from pathlib import Path

import typer

from analytics_reporting import rebuild_reporting_tables
from analytics_quality import validate_data_quality
from analytics_stats import compare_recent_windows
from analytics_exports import export_powerbi_bundle
from analysis.runbooks import get_runbook
from analysis.correlation import correlate_incident
from analysis.fleet_health import fleet_summary
from analysis.decision_engine import automated_decision, blast_radius_estimate


from classifiers.rule_admin import update_rule
from classifiers.simulation import simulate_rule_update, build_rule_diff
from ml_predictor import analyze_log_text
from reports.renderer import write_report_files, render_markdown_report
from storage.audit import init_audit_db, get_recent_audit_events
from storage.history import (
    init_db,
    record_analysis,
    get_signature_stats,
    get_report_summary,
    get_analysis_by_id,
    get_all_analyses,
    get_audit_event_by_id,
)

app = typer.Typer(help="AutoOps Insight CLI")


def ensure_ready():
    init_db()
    init_audit_db()


@app.command()
def analyze(
    log_file: str = typer.Argument(..., help="Path to a log file"),
    persist: bool = typer.Option(True, help="Persist the analysis to SQLite history"),
    print_json: bool = typer.Option(True, "--print-json/--no-print-json", help="Print JSON result"),
):
    ensure_ready()

    path = Path(log_file)
    if not path.exists():
        typer.echo(f"Error: file not found: {log_file}")
        raise typer.Exit(code=1)

    text = path.read_text(encoding="utf-8")
    result = analyze_log_text(text)

    if persist:
        record_analysis(result, filename=path.name)
        result["recurrence"] = get_signature_stats(result["signature"])
    else:
        result["recurrence"] = {
            "total_count": 0,
            "first_seen": None,
            "last_seen": None,
            "is_recurring": False,
            "recent_occurrences": [],
        }

    if print_json:
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(f"predicted_issue={result['predicted_issue']}")
        typer.echo(f"severity={result['severity']}")
        typer.echo(f"signature={result['signature']}")
        typer.echo(f"release_blocking={result['release_blocking']}")


@app.command()
def report(
    output_dir: str = typer.Option("reports/generated", help="Directory to write generated reports"),
    write_files: bool = typer.Option(True, "--write-files/--no-write-files", help="Write markdown/json report files"),
):
    ensure_ready()
    summary = get_report_summary()

    typer.echo(json.dumps(summary, indent=2))

    if write_files:
        paths = write_report_files(summary, output_dir=output_dir)
        typer.echo("")
        typer.echo("Generated report files:")
        typer.echo(f"- markdown: {paths['markdown_path']}")
        typer.echo(f"- json: {paths['json_path']}")
    else:
        typer.echo("")
        typer.echo(render_markdown_report(summary))


@app.command()
def replay(incident_id: int):
    ensure_ready()
    incident = get_analysis_by_id(incident_id)
    if incident is None:
        typer.echo(f"Error: incident not found: {incident_id}")
        raise typer.Exit(code=1)

    incident["recurrence"] = get_signature_stats(incident["signature"])
    typer.echo(json.dumps(incident, indent=2))


@app.command()
def audit(limit: int = 20):
    ensure_ready()
    typer.echo(json.dumps({"items": get_recent_audit_events(limit=limit)}, indent=2))


@app.command()
def update_rule_cmd(
    rule_id: str,
    field: str,
    value: str,
    actor: str = typer.Option("local-admin"),
):
    ensure_ready()

    parsed_value: object = value
    lowered = value.lower()
    if lowered == "true":
        parsed_value = True
    elif lowered == "false":
        parsed_value = False

    updated = update_rule(rule_id, {field: parsed_value}, actor=actor)
    typer.echo(json.dumps(updated, indent=2))


@app.command()
def simulate_rule(
    rule_id: str,
    field: str,
    value: str,
):
    ensure_ready()

    parsed_value: object = value
    lowered = value.lower()
    if lowered == "true":
        parsed_value = True
    elif lowered == "false":
        parsed_value = False

    incidents = get_all_analyses()
    result = simulate_rule_update(rule_id, {field: parsed_value}, incidents)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def rule_diff(rule_id: str, field: str, value: str):
    ensure_ready()

    parsed_value: object = value
    lowered = value.lower()
    if lowered == "true":
        parsed_value = True
    elif lowered == "false":
        parsed_value = False

    incidents = get_all_analyses()
    result = simulate_rule_update(rule_id, {field: parsed_value}, incidents)
    diff = build_rule_diff(result["before"], result["after"])
    typer.echo(json.dumps({
        "rule_id": rule_id,
        "diff": diff,
    }, indent=2))


@app.command()
def rollback_preview(audit_id: int):
    ensure_ready()

    event = get_audit_event_by_id(audit_id)
    if event is None:
        typer.echo(f"Error: audit event not found: {audit_id}")
        raise typer.Exit(code=1)

    if event["event_type"] != "rule_update":
        typer.echo("Error: rollback preview only supports rule_update events")
        raise typer.Exit(code=1)

    before = event["before"] or {}
    after = event["after"] or {}
    rollback_updates = {}

    for key, value in before.items():
        if after.get(key) != value:
            rollback_updates[key] = value

    incidents = get_all_analyses()
    result = simulate_rule_update(event["rule_id"], rollback_updates, incidents)
    typer.echo(json.dumps({
        "audit_event_id": audit_id,
        "rule_id": event["rule_id"],
        "rollback_updates": rollback_updates,
        "impact_preview": result,
    }, indent=2))


@app.command()
def health():
    ensure_ready()
    typer.echo("AutoOps Insight CLI is ready.")




@app.command("rebuild-reporting")
def rebuild_reporting() -> None:
    result = rebuild_reporting_tables()
    print(result)


@app.command("validate-data")
def validate_data() -> None:
    result = validate_data_quality()
    print(result)


@app.command("compare-windows")
def compare_windows(before_limit: int = 10, after_limit: int = 10) -> None:
    result = compare_recent_windows(before_limit=before_limit, after_limit=after_limit)
    print(result)


@app.command("export-powerbi")
def export_powerbi() -> None:
    result = export_powerbi_bundle()
    print(result)





@app.command("incident-runbook")
def incident_runbook(failure_family: str) -> None:
    print(get_runbook(failure_family))


@app.command("incident-correlate")
def incident_correlate(incident_id: int = 0, signature: str = "", window_minutes: int = 30) -> None:
    incident_id_arg = incident_id if incident_id > 0 else None
    signature_arg = signature or None
    print(correlate_incident(incident_id=incident_id_arg, signature=signature_arg, window_minutes=window_minutes))


@app.command("fleet-health")
def fleet_health_cmd() -> None:
    print(fleet_summary())





@app.command("incident-decision")
def incident_decision_cmd(incident_id: int) -> None:
    print(automated_decision(incident_id))


@app.command("incident-blast-radius")
def incident_blast_radius_cmd(incident_id: int, window_minutes: int = 60) -> None:
    print(blast_radius_estimate(incident_id, window_minutes=window_minutes))

if __name__ == "__main__":
    app()



