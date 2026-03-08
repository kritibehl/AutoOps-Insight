import json
from pathlib import Path

import typer

from ml_predictor import analyze_log_text
from reports.renderer import write_report_files, render_markdown_report
from storage.history import (
    init_db,
    record_analysis,
    get_signature_stats,
    get_report_summary,
)

app = typer.Typer(help="AutoOps Insight CLI")


@app.command()
def analyze(
    log_file: str = typer.Argument(..., help="Path to a log file"),
    persist: bool = typer.Option(True, help="Persist the analysis to SQLite history"),
    print_json: bool = typer.Option(True, "--print-json/--no-print-json", help="Print JSON result"),
):
    """
    Analyze a single log file and optionally persist the result.
    """
    init_db()

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
    """
    Generate a release-risk report from stored analysis history.
    """
    init_db()
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
def health():
    """
    Basic CLI health check for local components.
    """
    init_db()
    typer.echo("AutoOps Insight CLI is ready.")


if __name__ == "__main__":
    app()
