import json
from pathlib import Path

from aiops_service_readiness.benchmark_incident_context_api import schema_valid
from infra.terraform.cloud_run_autoops.deployment_output_validation import validate_deployment_outputs

def test_incident_context_schema_validation():
    data = json.loads(Path("aiops_incident_context/incident_context_summary.json").read_text())
    assert schema_valid(data) is True

def test_deployment_output_validation_passes_required_fields():
    data = json.loads(Path("infra/terraform/cloud_run_autoops/sample_deployment_output.json").read_text())
    result = validate_deployment_outputs(data)

    assert result["validation_status"] == "PASS"
    assert result["required_outputs_present"] == 7
    assert result["missing_outputs"] == []
    assert "health_endpoint_documented" in result["resilience_checks_passed"]
    assert "deployment_url_exposed" in result["resilience_checks_passed"]
