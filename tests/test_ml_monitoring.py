from fastapi.testclient import TestClient

from main import app
from ml_monitoring.anomaly_detection_pipeline import MODEL_RUNS, summarize_model_health

client = TestClient(app)

def test_ml_monitoring_detects_degraded_models():
    dashboard = summarize_model_health(MODEL_RUNS)

    assert dashboard["models_monitored"] == 3
    assert dashboard["degraded_models"] == 2
    assert dashboard["feature_drift_alerts"] == 2
    assert dashboard["quality_regressions"] == 2
    assert dashboard["monitoring_status"] == "REVIEW"

def test_ml_monitoring_api():
    r = client.get("/ml-monitoring/model-health")
    assert r.status_code == 200

    data = r.json()
    assert data["models_monitored"] == 3
    assert data["degraded_models"] == 2
    assert "model_evaluations" in data
