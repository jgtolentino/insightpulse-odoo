# InsightPulse AI - Infrastructure as Code (Terraform)
# Provider: DigitalOcean
# Region: Singapore (sgp1)

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.34"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration is now in backend.tf
}

# DigitalOcean Provider Configuration
provider "digitalocean" {
  token = var.do_token
}

# AWS Provider Configuration (for S3 backend)
provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

# Data sources for existing resources
data "digitalocean_project" "insightpulse" {
  name = "InsightPulse AI"
}

# VPC for secure private networking
resource "digitalocean_vpc" "insightpulse_vpc" {
  name     = "insightpulse-vpc-sgp1"
  region   = var.region
  ip_range = "10.10.0.0/16"

  description = "Private network for InsightPulse AI services"
}

# Firewall Rules
resource "digitalocean_firewall" "web_firewall" {
  name = "insightpulse-web-firewall"

  # Droplet tags to apply firewall
  tags = ["insightpulse", "web", "production"]

  # Inbound Rules
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.admin_ip_whitelist
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "8069"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "8088"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Outbound Rules
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# DNS configuration is now in dns.tf

# SSH Key for Droplets
resource "digitalocean_ssh_key" "insightpulse_admin" {
  name       = "insightpulse-admin-key"
  public_key = var.ssh_public_key
}

# Tags for resource organization
resource "digitalocean_tag" "production" {
  name = "production"
}

resource "digitalocean_tag" "insightpulse" {
  name = "insightpulse"
}

resource "digitalocean_tag" "web" {
  name = "web"
}

resource "digitalocean_tag" "database" {
  name = "database"
}

resource "digitalocean_tag" "monitoring" {
  name = "monitoring"
}

# Reserve IP for production
resource "digitalocean_reserved_ip" "odoo_ip" {
  region = var.region
}

# Cloud Monitoring Alerts
resource "digitalocean_monitor_alert" "cpu_alert" {
  alerts {
    email = var.alert_emails
  }
  window      = "5m"
  type        = "v1/insights/droplet/cpu"
  compare     = "GreaterThan"
  value       = 80
  enabled     = true
  entities    = [digitalocean_droplet.paddleocr.id]
  description = "CPU usage exceeded 80%"
}

resource "digitalocean_monitor_alert" "memory_alert" {
  alerts {
    email = var.alert_emails
  }
  window      = "5m"
  type        = "v1/insights/droplet/memory_utilization_percent"
  compare     = "GreaterThan"
  value       = 85
  enabled     = true
  entities    = [digitalocean_droplet.paddleocr.id]
  description = "Memory usage exceeded 85%"
}

resource "digitalocean_monitor_alert" "disk_alert" {
  alerts {
    email = var.alert_emails
  }
  window      = "5m"
  type        = "v1/insights/droplet/disk_utilization_percent"
  compare     = "GreaterThan"
  value       = 90
  enabled     = true
  entities    = [digitalocean_droplet.paddleocr.id]
  description = "Disk usage exceeded 90%"
}

# Outputs are now in outputs.tf
