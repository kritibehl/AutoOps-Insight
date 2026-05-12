from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_incident_search_filters_by_service():
    r = client.get("/incident-search", params={"service": "agentgrid"})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    assert all(item["service"] == "agentgrid" for item in data["items"])

def test_service_owner_dashboard():
    r = client.get("/service-owners/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["total_incidents"] == 4
    assert data["summary"]["open_incidents"] == 3

def test_incident_timeline():
    r = client.get("/incidents/INC-1002/timeline")
    assert r.status_code == 200
    data = r.json()
    assert data["incident_id"] == "INC-1002"
    assert data["current_status"] == "escalated"
    assert len(data["timeline"]) == 3
