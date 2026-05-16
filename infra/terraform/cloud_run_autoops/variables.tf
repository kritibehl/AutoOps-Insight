variable "project_id" {
  description = "Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "Cloud Run region."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name."
  type        = string
  default     = "autoops-api"
}

variable "container_image" {
  description = "Container image for AutoOps."
  type        = string
}

variable "autoops_token" {
  description = "AutoOps API token."
  type        = string
  sensitive   = true
}

variable "service_account_email" {
  description = "Service account used by Cloud Run."
  type        = string
}
