# InsightPulse AI - DNS Configuration
# All DNS records for insightpulseai.net domain

# Domain configuration
resource "digitalocean_domain" "insightpulseai" {
  name = "insightpulseai.net"
}

# Root domain (insightpulseai.net)
# Points to Odoo SaaS App Platform
resource "digitalocean_record" "root" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "@"
  value  = digitalocean_app.odoo_saas.live_url_base
  ttl    = 300
}

# ERP subdomain (erp.insightpulseai.net)
# Points to Odoo SaaS App Platform
resource "digitalocean_record" "erp" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "erp"
  value  = "${digitalocean_app.odoo_saas.default_ingress}."
  ttl    = 300
}

# Superset subdomain (superset.insightpulseai.net)
# Points to Superset Analytics App Platform
resource "digitalocean_record" "superset" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "superset"
  value  = "${digitalocean_app.superset.default_ingress}."
  ttl    = 300
}

# MCP subdomain (mcp.insightpulseai.net)
# Points to MCP Server App Platform
resource "digitalocean_record" "mcp" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "mcp"
  value  = "${digitalocean_app.mcp_server.default_ingress}."
  ttl    = 300
}

# Agent subdomain (agent.insightpulseai.net)
# Points to MCP Server App Platform (same as mcp.insightpulseai.net)
resource "digitalocean_record" "agent" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "CNAME"
  name   = "agent"
  value  = "${digitalocean_app.mcp_server.default_ingress}."
  ttl    = 300
}

# OCR subdomain (ocr.insightpulseai.net)
# Points to PaddleOCR Droplet
resource "digitalocean_record" "ocr" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "ocr"
  value  = digitalocean_droplet.paddleocr.ipv4_address
  ttl    = 300
}

# LLM subdomain (llm.insightpulseai.net)
# Points to PaddleOCR Droplet (hosts both OCR and Ollama LLM)
resource "digitalocean_record" "llm" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "llm"
  value  = digitalocean_droplet.paddleocr.ipv4_address
  ttl    = 300
}

# Monitoring subdomain (monitoring.insightpulseai.net)
# Points to Prometheus + Grafana Droplet
resource "digitalocean_record" "monitoring" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "monitoring"
  value  = digitalocean_droplet.monitoring.ipv4_address
  ttl    = 300
}

# Grafana subdomain (grafana.insightpulseai.net)
# Points to Prometheus + Grafana Droplet
resource "digitalocean_record" "grafana" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "grafana"
  value  = digitalocean_droplet.monitoring.ipv4_address
  ttl    = 300
}

# Prometheus subdomain (prometheus.insightpulseai.net)
# Points to Prometheus + Grafana Droplet
resource "digitalocean_record" "prometheus" {
  domain = digitalocean_domain.insightpulseai.id
  type   = "A"
  name   = "prometheus"
  value  = digitalocean_droplet.monitoring.ipv4_address
  ttl    = 300
}

# Output the domain and nameservers
output "domain_name" {
  value       = digitalocean_domain.insightpulseai.name
  description = "Domain name"
}

output "domain_urn" {
  value       = digitalocean_domain.insightpulseai.urn
  description = "Domain URN"
}
