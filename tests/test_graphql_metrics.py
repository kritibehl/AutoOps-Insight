from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def graphql(query: str):
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    body = response.json()
    assert "errors" not in body, body.get("errors")
    return body["data"]


def test_graphql_metrics_summary_returns_expected_fields():
    data = graphql(
        """
        {
          metricsSummary {
            totalAnalyses
            releaseBlockers
            releaseRisk
            topFailureFamilies {
              failureFamily
              totalCount
            }
            topRecurringSignatures {
              signature
              totalCount
              severity
            }
          }
        }
        """
    )

    summary = data["metricsSummary"]

    assert "totalAnalyses" in summary
    assert "releaseBlockers" in summary
    assert "releaseRisk" in summary
    assert "topFailureFamilies" in summary
    assert "topRecurringSignatures" in summary
    assert isinstance(summary["totalAnalyses"], int)
    assert isinstance(summary["releaseBlockers"], int)
    assert summary["releaseRisk"] in {"low", "medium", "high", "critical", "unknown"}


def test_graphql_noisy_services_returns_service_counts():
    data = graphql(
        """
        {
          noisyServices {
            service
            totalCount
            releaseBlockingCount
          }
        }
        """
    )

    assert "noisyServices" in data
    assert isinstance(data["noisyServices"], list)

    for service in data["noisyServices"]:
        assert "service" in service
        assert "totalCount" in service
        assert "releaseBlockingCount" in service
        assert isinstance(service["totalCount"], int)
        assert isinstance(service["releaseBlockingCount"], int)


def test_graphql_recurrence_heatmap_returns_patterns():
    data = graphql(
        """
        {
          recurrenceHeatmap {
            failureFamily
            signature
            totalCount
            severity
          }
        }
        """
    )

    assert "recurrenceHeatmap" in data
    assert isinstance(data["recurrenceHeatmap"], list)

    for cell in data["recurrenceHeatmap"]:
        assert "failureFamily" in cell
        assert "signature" in cell
        assert "totalCount" in cell
        assert "severity" in cell
        assert isinstance(cell["totalCount"], int)
