import json
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from event_ingestion.process_incident_events import run_pipeline

client = TestClient(app)

def test_event_ingestion_pipeline_generates_dlq():
    run_pipeline()
    summary = json.loads(Path("event_ingestion/incident_ingestion_summary.json").read_text())

    assert summary["events_received"] == 4
    assert summary["events_processed"] == 3
    assert summary["dead_lettered_events"] == 1
    assert summary["pipeline_status"] == "PASS"

def test_event_ingestion_api():
    run_pipeline()
    r = client.get("/events/ingestion/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["retry_attempts"] >= 1
    assert data["dead_lettered_events"] == 1
