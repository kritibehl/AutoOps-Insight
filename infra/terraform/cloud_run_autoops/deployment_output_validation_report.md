# Deployment Output Validation Report

## Validation status

PASS

## Required outputs present

7 / 7

## Missing outputs

[]

## Resilience checks passed

[
  "health_endpoint_documented",
  "environment_variables_declared",
  "deployment_url_exposed",
  "deployment_status_readable",
  "ingress_mode_documented",
  "service_account_variable_present"
]

## Resilience checks failed

[]

## Operational interpretation

This validator checks whether Terraform/Cloud Run deployment outputs include required service metadata, environment configuration, health endpoint documentation, and deployment-readiness signals before relying on the service in operational workflows.
