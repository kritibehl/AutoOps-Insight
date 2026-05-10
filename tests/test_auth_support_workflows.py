from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

payload = {
    "service": "reporting-api",
    "severity": "medium",
    "issue_type": "api_timeout",
    "symptom": "requests timing out after deployment",
    "customer_impact": "reporting delayed",
    "source": "support_channel"
}

def test_protected_ingest_requires_token():
    r = client.post("/support/ingest/protected", json=payload)
    assert r.status_code == 401

def test_support_l1_can_ingest():
    r = client.post(
        "/support/ingest/protected",
        json=payload,
        headers={"X-AutoOps-Token": "support-l1-token"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["role"] == "support_l1"
    assert data["issue_family"] == "latency_or_timeout"

def test_support_l1_cannot_escalate():
    r = client.post(
        "/incidents/SUP-1001/escalate/protected",
        headers={"X-AutoOps-Token": "support-l1-token"},
    )
    assert r.status_code == 403

def test_service_owner_can_escalate():
    r = client.post(
        "/incidents/SUP-1001/escalate/protected",
        headers={"X-AutoOps-Token": "service-owner-token"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "escalated"
