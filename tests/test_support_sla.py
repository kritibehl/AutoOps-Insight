from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_support_sla_summary():
    r = client.get("/support/sla/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_tickets"] == 4
    assert data["sla_breached"] == 2
    assert data["avg_time_to_triage_minutes"] == 31.75
    assert len(data["tickets"]) == 4
    assert data["tickets"][0]["ticket_id"] == "TCK-1001"
