import json
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from rai_monitoring.ingest_rai_safety_event import normalize_rai_event
from rai_monitoring.summarize_rai_monitoring import summarize_events

client = TestClient(app)

def test_rai_event_normalization():
    event = json.loads(Path("rai_monitoring/sample_rai_safety_event.json").read_text())
    result = normalize_rai_event(event)

    assert result["valid"] is True
    normalized = result["normalized_event"]
    assert normalized["incident_type"] == "responsible_ai_safety_regression"
    assert normalized["severity"] == "sev1"
    assert normalized["release_impact"] == "blocked"
    assert normalized["human_review_required"] is True

def test_rai_monitoring_summary():
    events = json.loads(Path("rai_monitoring/safety_events.json").read_text())
    metrics = summarize_events(events)

    assert metrics["total_safety_events"] == 3
    assert metrics["release_blocks"] == 2
    assert metrics["false_allow_incidents"] == 2

def test_rai_api_summary():
    r = client.get("/rai/monitoring/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["release_blocks"] == 2
    assert data["human_review_escalations"] == 2

def test_rai_incident_detail():
    incident_id = "RAI-rai-eval-2026-05-15"
    r = client.get(f"/rai/incidents/{incident_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["incident_type"] == "responsible_ai_safety_regression"
    assert data["owner"] == "ai_safety_review_queue"
