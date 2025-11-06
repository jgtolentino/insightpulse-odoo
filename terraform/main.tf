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
  }

  # Backend configuration for state management
  backend "s3" {
    # DigitalOcean Spaces configuration
    endpoint                    = "sgp1.digitaloceanspaces.com"
    region                      = "us-east-1"  # Required but not used by DO Spaces
    bucket                      = "insightpulse-terraform-state"
    key                         = "production/terraform.tfstate"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
  }
}

# DigitalOcean Provider Configuration
provider "digitalocean" {
  token = var.do_token
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

# Domain configuration
resource "digitalocean_domain" "insightpulseai" {
  name = "insightpulseai.net"
}

# DNS Records
resource "digitalocean_record" "root" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "@"
  value  = digitalocean_app.odoo_saas.live_url_base
  ttl    = 300
}

resource "digitalocean_record" "erp" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "erp"
  value  = "${digitalocean_app.odoo_saas.default_ingress}."
  ttl    = 300
}

resource "digitalocean_record" "superset" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "superset"
  value  = "${digitalocean_app.superset.default_ingress}."
  ttl    = 300
}

resource "digitalocean_record" "mcp" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "mcp"
  value  = "${digitalocean_app.mcp_server.default_ingress}."
  ttl    = 300
}

resource "digitalocean_record" "ocr" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "ocr"
  value  = digitalocean_droplet.paddleocr.ipv4_address
  ttl    = 300
}

resource "digitalocean_record" "llm" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "llm"
  value  = digitalocean_droplet.paddleocr.ipv4_address
  ttl    = 300
}

resource "digitalocean_record" "agent" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "agent"
  value  = "${digitalocean_app.mcp_server.default_ingress}."
  ttl    = 300
}

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

# Outputs
output "odoo_url" {
  value       = digitalocean_app.odoo_saas.live_url
  description = "Odoo SaaS platform URL"
}

output "superset_url" {
  value       = digitalocean_app.superset.live_url
  description = "Superset analytics URL"
}

output "mcp_server_url" {
  value       = digitalocean_app.mcp_server.live_url
  description = "MCP Server URL"
}

output "ocr_droplet_ip" {
  value       = digitalocean_droplet.paddleocr.ipv4_address
  description = "PaddleOCR Droplet IP"
  sensitive   = false
}

output "vpc_id" {
  value       = digitalocean_vpc.insightpulse_vpc.id
  description = "VPC ID for private networking"
}
