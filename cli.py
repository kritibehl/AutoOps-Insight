import json
from pathlib import Path

import typer

from classifiers.rule_admin import update_rule
from ml_predictor import analyze_log_text
from reports.renderer import write_report_files, render_markdown_report
from storage.audit import init_audit_db, get_recent_audit_events
from storage.history import (
    init_db,
    record_analysis,
    get_signature_stats,
    get_report_summary,
    get_analysis_by_id,
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
def health():
    ensure_ready()
    typer.echo("AutoOps Insight CLI is ready.")


if __name__ == "__main__":
    app()
