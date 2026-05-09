from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()

def test_support_metrics_live():
    r = client.get("/support/metrics/live")
    assert r.status_code == 200
    data = r.json()
    assert data["total_support_incidents"] == 102
    assert data["escalation_count"] == 51
    assert data["agentgrid_events_ingested"] == 19

def test_lifecycle_transition_live():
    r = client.post(
        "/incidents/INC-1001/transition/live",
        params={
            "actor": "kriti",
            "old_state": "new",
            "new_state": "triaged",
            "reason": "initial_review"
        }
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "transition_recorded"
    assert data["audit_log"]["actor"] == "kriti"
