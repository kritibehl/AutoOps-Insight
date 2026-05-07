from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_dashboard_or_report_summary_endpoint_returns_expected_fields():
    candidate_paths = [
        "/dashboard/summary",
        "/reports/summary",
        "/release/summary",
    ]

    successful = None

    for path in candidate_paths:
        response = client.get(path)
        if response.status_code == 200:
            successful = (path, response.json())
            break

    assert successful is not None, "No dashboard/report summary endpoint returned 200"

    path, body = successful
    assert isinstance(body, dict), f"{path} should return a JSON object"

    expected_any_fields = {
        "total_analyses",
        "totalAnalyses",
        "release_blockers",
        "releaseBlockers",
        "release_risk",
        "releaseRisk",
        "top_failure_families",
        "topFailureFamilies",
        "items",
        "summary",
    }

    assert expected_any_fields.intersection(body.keys()), (
        f"{path} response did not include expected dashboard/report summary fields: {body.keys()}"
    )
