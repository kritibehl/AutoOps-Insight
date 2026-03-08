import io
import os
import tempfile

from fastapi.testclient import TestClient


def test_api_end_to_end():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_autoops.db")
        os.environ["AUTOOPS_DB_PATH"] = db_path

        from main import app
        client = TestClient(app)

        sample_log = b"ERROR: Jenkins pipeline failed at stage Deploy. Timeout connecting to registry."

        response = client.post(
            "/analyze",
            files={"file": ("sample.log", io.BytesIO(sample_log), "text/plain")},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["failure_family"] == "timeout"
        assert "signature" in payload
        assert "recurrence" in payload

        recent = client.get("/history/recent")
        assert recent.status_code == 200
        recent_payload = recent.json()
        assert "items" in recent_payload
        assert len(recent_payload["items"]) >= 1

        recurring = client.get("/history/recurring")
        assert recurring.status_code == 200
        assert "items" in recurring.json()

        summary = client.get("/reports/summary")
        assert summary.status_code == 200
        summary_payload = summary.json()
        assert "release_risk" in summary_payload
        assert "anomalies" in summary_payload
