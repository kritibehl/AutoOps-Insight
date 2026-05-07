from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root_endpoint_returns_running_message():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "AutoOps Insight is running!"


def test_health_endpoint_returns_ok():
    response = client.get("/healthz")
    if response.status_code == 404:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_metrics_endpoint_exposes_prometheus_text():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert len(response.text) > 0
