import json
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from incident_runbooks.generate_runbook_package import build_runbook_package

client = TestClient(app)

def test_runbook_package_generates_timeline_and_rollback():
    incident = json.loads(Path("incident_runbooks/sample_production_incident.json").read_text())
    package = build_runbook_package(incident)

    assert package["incident_id"] == "INC-PROD-901"
    assert len(package["incident_timeline"]) == 4
    assert package["rollback_recommendation"]["rollback_candidate"] is True
    assert "post_incident_review" in package

def test_incident_runbook_api():
    r = client.get("/incident-runbooks/demo")
    assert r.status_code == 200
    data = r.json()

    assert data["incident_id"] == "INC-PROD-901"
    assert data["rollback_recommendation"]["rollback_candidate"] is True
    assert "ai_assisted_runbook_summary" in data
