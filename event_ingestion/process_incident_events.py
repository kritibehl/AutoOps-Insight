import json
from pathlib import Path

REQUIRED_FIELDS = ["event_id", "source", "service", "severity", "issue_family", "action"]

def validate_event(event):
    return [f for f in REQUIRED_FIELDS if not event.get(f)]

def process_event(event):
    missing = validate_event(event)
    if missing:
        raise ValueError(f"missing_required_fields:{missing}")

    return {
        "event_id": event["event_id"],
        "status": "processed",
        "service": event["service"],
        "severity": event["severity"],
        "issue_family": event["issue_family"],
        "recommended_queue": "sev1_escalation" if event["severity"] == "sev1" else "standard_triage",
        "action": event["action"],
    }

def run_pipeline(input_path="event_ingestion/sample_incident_events.jsonl", max_retries=2):
    processed = []
    retry_queue = []
    dead_letter_queue = []

    for line in Path(input_path).read_text().splitlines():
        event = json.loads(line)
        attempt = 0

        while attempt <= max_retries:
            try:
                result = process_event(event)
                result["attempts"] = attempt + 1
                processed.append(result)
                break
            except Exception as exc:
                attempt += 1
                if attempt <= max_retries:
                    retry_queue.append({
                        "event_id": event.get("event_id"),
                        "attempt": attempt,
                        "error": str(exc)
                    })
                else:
                    dead_letter_queue.append({
                        "event": event,
                        "error": str(exc),
                        "attempts": attempt
                    })

    summary = {
        "events_received": len(processed) + len(dead_letter_queue),
        "events_processed": len(processed),
        "retry_attempts": len(retry_queue),
        "dead_lettered_events": len(dead_letter_queue),
        "processed_events": processed,
        "retry_queue": retry_queue,
        "dead_letter_queue": dead_letter_queue,
        "pipeline_status": "PASS" if processed else "REVIEW"
    }

    Path("event_ingestion/incident_ingestion_summary.json").write_text(json.dumps(summary, indent=2))
    Path("event_ingestion/dead_letter_queue.json").write_text(json.dumps(dead_letter_queue, indent=2))

    report = f"""# Event-Driven Incident Ingestion Report

## Summary

- Events received: {summary["events_received"]}
- Events processed: {summary["events_processed"]}
- Retry attempts: {summary["retry_attempts"]}
- Dead-lettered events: {summary["dead_lettered_events"]}
- Pipeline status: {summary["pipeline_status"]}

## Operational value

This workflow models asynchronous incident ingestion with validation, retry tracking, and dead-letter handling for malformed events.
"""

    Path("event_ingestion/incident_ingestion_report.md").write_text(report)

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    run_pipeline()
