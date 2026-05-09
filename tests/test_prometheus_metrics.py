from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_prometheus_endpoint_exposes_autoops_metrics():
    r = client.get("/prometheus")
    assert r.status_code == 200
    body = r.text
    assert "autoops_support_incidents_total" in body
    assert "autoops_escalations_total" in body
    assert "autoops_agentgrid_events_ingested_total" in body
