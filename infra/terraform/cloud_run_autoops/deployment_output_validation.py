import json
from pathlib import Path

REQUIRED_OUTPUTS = [
    "project_id",
    "region",
    "service_name",
    "service_url",
    "health_endpoint",
    "required_environment_variables",
    "deployment_status",
]

def validate_deployment_outputs(data):
    missing = [field for field in REQUIRED_OUTPUTS if not data.get(field)]

    resilience_checks = []
    failed_checks = []

    if data.get("health_endpoint"):
        resilience_checks.append("health_endpoint_documented")
    else:
        failed_checks.append("health_endpoint_documented")

    if "AUTOOPS_TOKEN" in data.get("required_environment_variables", []):
        resilience_checks.append("environment_variables_declared")
    else:
        failed_checks.append("environment_variables_declared")

    if data.get("service_url", "").startswith("https://"):
        resilience_checks.append("deployment_url_exposed")
    else:
        failed_checks.append("deployment_url_exposed")

    if data.get("deployment_status") in {"serving", "ready"}:
        resilience_checks.append("deployment_status_readable")
    else:
        failed_checks.append("deployment_status_readable")

    if data.get("ingress_mode"):
        resilience_checks.append("ingress_mode_documented")
    else:
        failed_checks.append("ingress_mode_documented")

    if data.get("service_account_variable_present") is True:
        resilience_checks.append("service_account_variable_present")
    else:
        failed_checks.append("service_account_variable_present")

    return {
        "validation_status": "PASS" if not missing and not failed_checks else "REVIEW",
        "required_outputs_present": len(REQUIRED_OUTPUTS) - len(missing),
        "missing_outputs": missing,
        "resilience_checks_passed": resilience_checks,
        "resilience_checks_failed": failed_checks,
        "deployment_status_readable": data.get("deployment_status") is not None,
    }

def main():
    data = json.loads(Path("infra/terraform/cloud_run_autoops/sample_deployment_output.json").read_text())
    result = validate_deployment_outputs(data)

    out = Path("infra/terraform/cloud_run_autoops/deployment_output_validation_summary.json")
    out.write_text(json.dumps(result, indent=2))

    report = f"""# Deployment Output Validation Report

## Validation status

{result["validation_status"]}

## Required outputs present

{result["required_outputs_present"]} / {len(REQUIRED_OUTPUTS)}

## Missing outputs

{json.dumps(result["missing_outputs"], indent=2)}

## Resilience checks passed

{json.dumps(result["resilience_checks_passed"], indent=2)}

## Resilience checks failed

{json.dumps(result["resilience_checks_failed"], indent=2)}

## Operational interpretation

This validator checks whether Terraform/Cloud Run deployment outputs include required service metadata, environment configuration, health endpoint documentation, and deployment-readiness signals before relying on the service in operational workflows.
"""

    Path("infra/terraform/cloud_run_autoops/deployment_output_validation_report.md").write_text(report)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
