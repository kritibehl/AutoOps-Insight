import json
from pathlib import Path

from customer_incident_workspace.analyze_customer_incident import analyze_customer_incident
from slo_risk_dashboard.build_slo_dashboard import INCIDENTS, build_slo_risk_dashboard

def test_customer_incident_workspace_detects_deployment_regression():
    payload = json.loads(Path("customer_incident_workspace/sample_customer_incident.json").read_text())
    summary = analyze_customer_incident(payload)

    assert summary["severity"] == "sev2"
    assert summary["suspected_cause"] == "deployment_regression"
    assert summary["recommended_action"] == "rollback_candidate"
    assert "release_id matched" in summary["evidence"]

def test_slo_risk_dashboard_flags_high_risk():
    dashboard = build_slo_risk_dashboard(INCIDENTS)

    assert dashboard["open_incidents"] == 3
    assert dashboard["sla_breaches"] == 2
    assert dashboard["repeated_issue_family"] == "retry_storm"
    assert dashboard["risk_level"] == "high"
