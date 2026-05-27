import json
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from streaming_analytics.incident_stream_processor import SAMPLE_EVENTS, analyze_stream

client = TestClient(app)

def test_streaming_analysis_detects_spikes():
    summary = analyze_stream(SAMPLE_EVENTS)

    assert summary["events_processed"] == 8
    assert summary["spike_windows_detected"] >= 1
    assert summary["escalation_bursts_detected"] >= 1
    assert summary["stream_status"] == "PASS"

def test_streaming_analytics_api():
    r = client.get("/streaming/incident-analytics/summary")
    assert r.status_code == 200
    data = r.json()

    assert data["events_processed"] == 8
    assert data["spike_windows_detected"] >= 1
