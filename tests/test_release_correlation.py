from release_correlation.deployment_correlation import (
    correlate_deployments_to_incidents,
    summarize_release_risk,
)

def test_deployment_to_incident_correlation_detects_rollback_candidate():
    deployments = [
        {
            "deployment_id": "DEP-1",
            "service": "api",
            "version": "v1",
            "deployed_at": "2026-05-10T10:00:00Z",
            "change_type": "backend_release",
            "owner": "api_team",
        }
    ]

    incidents = [
        {
            "incident_id": "INC-1",
            "service": "api",
            "issue_family": "latency_or_timeout",
            "severity": "high",
            "created_at": "2026-05-10T10:20:00Z",
            "customer_impact": "timeouts",
        },
        {
            "incident_id": "INC-2",
            "service": "api",
            "issue_family": "latency_or_timeout",
            "severity": "medium",
            "created_at": "2026-05-10T10:30:00Z",
            "customer_impact": "slow dashboard",
        },
    ]

    correlations = correlate_deployments_to_incidents(deployments, incidents)

    assert correlations[0]["incident_spike"] == 2
    assert correlations[0]["rollback_candidate"] is True
    assert correlations[0]["affected_service"] == "api"

def test_release_risk_summary_counts_candidates():
    correlations = [
        {
            "service": "api",
            "deployment_id": "DEP-1",
            "release_risk": "high",
            "incident_spike": 2,
            "rollback_candidate": True,
        }
    ]

    summary = summarize_release_risk(correlations)

    assert summary["deployments_analyzed"] == 1
    assert summary["rollback_candidates"] == 1
