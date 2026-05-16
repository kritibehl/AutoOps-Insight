import json
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from aiops_incident_context.build_incident_context import build_context

client = TestClient(app)

def test_aiops_context_generation():
    bundle = json.loads(Path("aiops_incident_context/sample_telemetry_bundle.json").read_text())
    historical = json.loads(Path("aiops_incident_context/historical_incident_store.json").read_text())

    context = build_context(bundle, historical)

    assert context["incident_id"] == "INC-204"
    assert "triage_summary" in context
    assert context["probable_root_cause_hypotheses"][0]["confidence"] == "high"
    assert context["historical_context"][0]["matched_incident"] == "INC-137"

def test_aiops_context_api():
    r = client.get("/aiops/incident-context/demo")
    assert r.status_code == 200
    data = r.json()
    assert data["incident_id"] == "INC-204"
    assert data["service"] == "checkout-api"
    assert len(data["recommended_next_actions"]) >= 3
