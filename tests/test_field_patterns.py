import json
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from field_patterns.summarize_field_patterns import summarize_patterns

client = TestClient(app)

def test_field_pattern_summary_detects_top_failure_family():
    incidents = json.loads(Path("genai_incidents/recurring_genai_failures.json").read_text())
    summary = summarize_patterns(incidents)

    assert summary["total_incidents_reviewed"] == 4
    assert summary["top_failure_family"] == "rag_missing_context"
    assert summary["failure_family_distribution"]["rag_missing_context"] == 2

def test_field_patterns_api():
    r = client.get("/field-patterns/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["top_failure_family"] == "rag_missing_context"
    assert "reusable_incident_patterns" in data
