terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_v2_service" "autoops" {
  name     = var.service_name
  location = var.region

  template {
    service_account = var.service_account_email

    containers {
      image = var.container_image

      env {
        name  = "AUTOOPS_TOKEN"
        value = var.autoops_token
      }

      ports {
        container_port = 8080
      }
    }
  }

  ingress = "INGRESS_TRAFFIC_ALL"
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  location = google_cloud_run_v2_service.autoops.location
  name     = google_cloud_run_v2_service.autoops.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
