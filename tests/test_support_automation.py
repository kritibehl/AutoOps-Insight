from fastapi.testclient import TestClient
from main import app
from support_automation.ticket_lifecycle import is_valid_transition

client = TestClient(app)

def test_support_ingest_generates_triage_outputs():
    payload = {
        "service": "reporting-api",
        "severity": "medium",
        "issue_type": "api_timeout",
        "symptom": "requests timing out after deployment",
        "customer_impact": "reporting delayed",
        "source": "support_channel"
    }

    r = client.post("/support/ingest", json=payload)
    assert r.status_code == 200

    data = r.json()
    assert data["issue_family"] == "latency_or_timeout"
    assert data["probable_owner"] == "reporting_platform_team"
    assert "recommended_runbook_action" in data
    assert "service_health" in data
    assert data["status_transition"]["old_status"] == "new"
    assert data["status_transition"]["new_status"] == "triaged"

def test_ticket_lifecycle_transition():
    assert is_valid_transition("new", "triaged")
    assert not is_valid_transition("new", "resolved")
