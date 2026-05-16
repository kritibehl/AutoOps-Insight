output "service_url" {
  description = "Cloud Run AutoOps service URL."
  value       = google_cloud_run_v2_service.autoops.uri
}

output "service_name" {
  description = "Cloud Run service name."
  value       = google_cloud_run_v2_service.autoops.name
}

output "region" {
  description = "Cloud Run deployment region."
  value       = var.region
}
