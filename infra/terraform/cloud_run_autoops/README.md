# AutoOps Cloud Run Terraform Template

This Terraform template documents repeatable provisioning for the AutoOps AIOps service on Google Cloud Run.

## Resources

- Cloud Run v2 service
- public invoker IAM binding
- environment variable configuration
- service account placeholder
- output service URL

## Variables

- `project_id`
- `region`
- `service_name`
- `container_image`
- `autoops_token`
- `service_account_email`

## Example

```bash
terraform init

terraform plan \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="container_image=us-central1-docker.pkg.dev/YOUR_PROJECT/autoops/autoops-api:latest" \
  -var="autoops_token=dev-token" \
  -var="service_account_email=SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com"

terraform apply
Health check
curl "$(terraform output -raw service_url)/healthz/live"
Purpose

This provides repeatable serverless deployment documentation for AutoOps reliability tooling infrastructure.
