# InsightPulse AI - Infrastructure Outputs
# All outputs from the infrastructure deployment

# ========================================
# Application URLs
# ========================================

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

output "monitor_url" {
  value       = digitalocean_app.monitor.live_url
  description = "InsightPulse Monitor URL"
}

# ========================================
# Droplet IPs
# ========================================

output "ocr_droplet_ip" {
  value       = digitalocean_droplet.paddleocr.ipv4_address
  description = "PaddleOCR + Ollama Droplet IP"
  sensitive   = false
}

output "monitoring_droplet_ip" {
  value       = digitalocean_droplet.monitoring.ipv4_address
  description = "Prometheus + Grafana Droplet IP"
  sensitive   = false
}

# ========================================
# Monitoring URLs
# ========================================

output "prometheus_url" {
  value       = "http://${digitalocean_droplet.monitoring.ipv4_address}:9090"
  description = "Prometheus dashboard URL"
}

output "grafana_url" {
  value       = "http://${digitalocean_droplet.monitoring.ipv4_address}:3000"
  description = "Grafana dashboard URL"
}

# ========================================
# Service URLs
# ========================================

output "paddleocr_api_url" {
  value       = "http://${digitalocean_droplet.paddleocr.ipv4_address}:8000"
  description = "PaddleOCR API URL"
}

output "ollama_api_url" {
  value       = "http://${digitalocean_droplet.paddleocr.ipv4_address}:11434"
  description = "Ollama LLM API URL"
}

# ========================================
# Network Resources
# ========================================

output "vpc_id" {
  value       = digitalocean_vpc.insightpulse_vpc.id
  description = "VPC ID for private networking"
}

output "vpc_urn" {
  value       = digitalocean_vpc.insightpulse_vpc.urn
  description = "VPC URN"
}

output "reserved_ip" {
  value       = digitalocean_reserved_ip.odoo_ip.ip_address
  description = "Reserved IP for Odoo production"
}

# ========================================
# Volume IDs
# ========================================

output "prometheus_volume_id" {
  value       = digitalocean_volume.prometheus_data.id
  description = "Prometheus data volume ID"
}

output "grafana_volume_id" {
  value       = digitalocean_volume.grafana_data.id
  description = "Grafana data volume ID"
}

# ========================================
# Complete Infrastructure Summary
# ========================================

output "infrastructure_summary" {
  value = {
    # Applications
    odoo_url        = digitalocean_app.odoo_saas.live_url
    superset_url    = digitalocean_app.superset.live_url
    mcp_url         = digitalocean_app.mcp_server.live_url
    monitor_url     = digitalocean_app.monitor.live_url

    # Droplets
    ocr_ip          = digitalocean_droplet.paddleocr.ipv4_address
    monitoring_ip   = digitalocean_droplet.monitoring.ipv4_address

    # Monitoring
    grafana         = "http://${digitalocean_droplet.monitoring.ipv4_address}:3000"
    prometheus      = "http://${digitalocean_droplet.monitoring.ipv4_address}:9090"

    # Services
    paddleocr_api   = "http://${digitalocean_droplet.paddleocr.ipv4_address}:8000"
    ollama_api      = "http://${digitalocean_droplet.paddleocr.ipv4_address}:11434"

    # Network
    vpc_id          = digitalocean_vpc.insightpulse_vpc.id
    reserved_ip     = digitalocean_reserved_ip.odoo_ip.ip_address
  }
  description = "Complete infrastructure summary"
}

# ========================================
# Quick Access Commands
# ========================================

output "quick_access_commands" {
  value = <<-EOT
    # SSH into OCR/LLM Droplet
    ssh root@${digitalocean_droplet.paddleocr.ipv4_address}

    # SSH into Monitoring Droplet
    ssh root@${digitalocean_droplet.monitoring.ipv4_address}

    # Access Odoo
    open ${digitalocean_app.odoo_saas.live_url}

    # Access Superset
    open ${digitalocean_app.superset.live_url}

    # Access Grafana
    open http://${digitalocean_droplet.monitoring.ipv4_address}:3000

    # Test PaddleOCR API
    curl http://${digitalocean_droplet.paddleocr.ipv4_address}:8000/health

    # Test Ollama API
    curl http://${digitalocean_droplet.paddleocr.ipv4_address}:11434/api/tags
  EOT
  description = "Quick access commands for SSH and service testing"
}
