# GKE Black Ops Cluster Configuration
# Terraform configuration for a dedicated GKE cluster for the Black Ops Lab.
# 
# This is a stub configuration - modify values for your environment.

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Uncomment and configure for remote state
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "black-ops-lab"
  # }
}

# Variables
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for the cluster"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone for the cluster"
  type        = string
  default     = "us-central1-a"
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  default     = "black-ops-lab"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 2
}

variable "machine_type" {
  description = "Machine type for cluster nodes"
  type        = string
  default     = "e2-medium"
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Cluster
resource "google_container_cluster" "black_ops_lab" {
  name     = var.cluster_name
  location = var.zone

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = "default"
  subnetwork = "default"

  # Enable Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Logging and monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus {
      enabled = true
    }
  }

  # Release channel for automatic upgrades
  release_channel {
    channel = "REGULAR"
  }

  # Security settings
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Enable Binary Authorization (optional)
  # binary_authorization {
  #   evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  # }

  # Labels for organization
  resource_labels = {
    environment = "lab"
    purpose     = "black-ops-experiments"
    team        = "strategickhaos-swarm"
  }
}

# Managed Node Pool for experiments
resource "google_container_node_pool" "lab_nodes" {
  name       = "lab-pool"
  location   = var.zone
  cluster    = google_container_cluster.black_ops_lab.name
  node_count = var.node_count

  node_config {
    machine_type = var.machine_type
    
    # Google recommends custom service accounts that have cloud-platform scope
    # and permissions granted via IAM Roles.
    # For the lab, we use the default compute SA with limited scopes.
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Labels for the nodes
    labels = {
      environment = "lab"
      pool        = "experiments"
    }

    # Taints to prevent scheduling of non-lab workloads
    taint {
      key    = "lab"
      value  = "black-ops"
      effect = "NO_SCHEDULE"
    }

    # Spot VMs for cost savings (remove for production-like testing)
    spot = true
  }

  # Autoscaling configuration
  autoscaling {
    min_node_count = 1
    max_node_count = 5
  }

  # Management configuration
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Outputs
output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.black_ops_lab.name
}

output "cluster_endpoint" {
  description = "Endpoint for the GKE cluster"
  value       = google_container_cluster.black_ops_lab.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "CA certificate for the cluster"
  value       = google_container_cluster.black_ops_lab.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "get_credentials_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${var.cluster_name} --zone ${var.zone} --project ${var.project_id}"
}
