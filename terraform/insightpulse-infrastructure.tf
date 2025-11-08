# ============================================
# INSIGHTPULSE AI - PRODUCTION INFRASTRUCTURE
# ============================================
# Version: 1.0
# Date: 2025-11-08
# Description: Complete IaC for HA production deployment
# Cost: ~₱325/month (~$5.80 USD/month)
# ============================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }

  # Remote state storage (S3-compatible DigitalOcean Spaces)
  backend "s3" {
    endpoint                    = "sgp1.digitaloceanspaces.com"
    bucket                      = "insightpulse-terraform-state"
    key                         = "prod/terraform.tfstate"
    region                      = "us-east-1"  # Dummy value for DO Spaces
    skip_credentials_validation = true
    skip_metadata_api_check     = true
  }
}

# ============================================
# VARIABLES
# ============================================

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID for insightpulseai.net"
  type        = string
}

variable "ssh_keys" {
  description = "List of SSH key fingerprints"
  type        = list(string)
}

variable "alert_email" {
  description = "Email for infrastructure alerts"
  type        = string
  default     = "ops@insightpulseai.net"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "region" {
  description = "Primary DigitalOcean region"
  type        = string
  default     = "sgp1"  # Singapore
}

# ============================================
# PROVIDERS
# ============================================

provider "digitalocean" {
  token = var.do_token
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# ============================================
# NETWORKING
# ============================================

resource "digitalocean_vpc" "main" {
  name     = "insightpulse-${var.environment}"
  region   = var.region
  ip_range = "10.10.0.0/16"

  description = "Production VPC for InsightPulse AI"
}

# ============================================
# DATABASE CLUSTER (HA)
# ============================================

resource "digitalocean_database_cluster" "postgres" {
  name       = "insightpulse-${var.environment}-db"
  engine     = "pg"
  version    = "15"
  size       = "db-s-2vcpu-4gb"  # ₱2,880/month
  region     = var.region
  node_count = 2  # Primary + 1 replica for HA

  private_network_uuid = digitalocean_vpc.main.id

  maintenance_window {
    day  = "sunday"
    hour = "02:00:00"  # 2 AM Sunday
  }

  tags = ["production", "database", "ha"]
}

# Database firewall - only allow from VPC
resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id

  rule {
    type  = "tag"
    value = "production"
  }

  rule {
    type  = "ip_addr"
    value = digitalocean_vpc.main.ip_range
  }
}

# Create databases
resource "digitalocean_database_db" "odoo" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "odoo_prod"
}

resource "digitalocean_database_db" "agents" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "agents_state"
}

resource "digitalocean_database_db" "analytics" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "analytics"
}

# Database users
resource "digitalocean_database_user" "odoo" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "odoo_user"
}

resource "digitalocean_database_user" "agents" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "agents_user"
}

# ============================================
# REDIS CLUSTER
# ============================================

resource "digitalocean_database_cluster" "redis" {
  name       = "insightpulse-${var.environment}-redis"
  engine     = "redis"
  version    = "7"
  size       = "db-s-1vcpu-1gb"  # ₱720/month
  region     = var.region
  node_count = 1  # Can scale to 2 for HA if needed

  private_network_uuid = digitalocean_vpc.main.id

  tags = ["production", "cache", "redis"]
}

resource "digitalocean_database_firewall" "redis" {
  cluster_id = digitalocean_database_cluster.redis.id

  rule {
    type  = "tag"
    value = "production"
  }
}

# ============================================
# COMPUTE INSTANCES (DROPLETS)
# ============================================

# Odoo application servers (2 for HA behind load balancer)
resource "digitalocean_droplet" "odoo" {
  count  = 2
  name   = "odoo-${var.environment}-${count.index + 1}"
  size   = "s-4vcpu-8gb"  # ₱2,880/month each
  image  = "ubuntu-22-04-x64"
  region = var.region

  vpc_uuid = digitalocean_vpc.main.id
  ssh_keys = var.ssh_keys

  # Cloud-init configuration
  user_data = templatefile("${path.module}/cloud-init-odoo.yml", {
    postgres_host     = digitalocean_database_cluster.postgres.private_host
    postgres_port     = digitalocean_database_cluster.postgres.port
    postgres_user     = digitalocean_database_user.odoo.name
    postgres_password = digitalocean_database_user.odoo.password
    postgres_db       = digitalocean_database_db.odoo.name
    redis_uri         = digitalocean_database_cluster.redis.private_uri
    environment       = var.environment
  })

  tags = ["production", "odoo", "app"]

  monitoring = true

  lifecycle {
    create_before_destroy = true
  }
}

# OCR processing server (dedicated for heavy workloads)
resource "digitalocean_droplet" "ocr" {
  name   = "ocr-${var.environment}"
  size   = "c-4"  # CPU-optimized, ₱2,160/month
  image  = "ubuntu-22-04-x64"
  region = var.region

  vpc_uuid = digitalocean_vpc.main.id
  ssh_keys = var.ssh_keys

  user_data = file("${path.module}/cloud-init-ocr.yml")

  tags = ["production", "ocr", "worker"]

  monitoring = true
}

# Monitoring server (Prometheus + Grafana)
resource "digitalocean_droplet" "monitoring" {
  name   = "monitoring-${var.environment}"
  size   = "s-2vcpu-4gb"  # ₱1,440/month
  image  = "ubuntu-22-04-x64"
  region = var.region

  vpc_uuid = digitalocean_vpc.main.id
  ssh_keys = var.ssh_keys

  user_data = file("${path.module}/cloud-init-monitoring.yml")

  tags = ["production", "monitoring"]

  monitoring = true
}

# ============================================
# LOAD BALANCER
# ============================================

resource "digitalocean_loadbalancer" "public" {
  name   = "insightpulse-${var.environment}-lb"
  region = var.region

  vpc_uuid = digitalocean_vpc.main.id

  # HTTPS forwarding (443 → 8069)
  forwarding_rule {
    entry_protocol  = "https"
    entry_port      = 443
    target_protocol = "http"
    target_port     = 8069

    certificate_name = digitalocean_certificate.main.name
  }

  # HTTP → HTTPS redirect
  forwarding_rule {
    entry_protocol  = "http"
    entry_port      = 80
    target_protocol = "http"
    target_port     = 8069
  }

  # Health check
  healthcheck {
    protocol               = "http"
    port                   = 8069
    path                   = "/web/health"
    check_interval_seconds = 10
    response_timeout_seconds = 5
    healthy_threshold      = 2
    unhealthy_threshold    = 3
  }

  # Sticky sessions (for Odoo)
  sticky_sessions {
    type               = "cookies"
    cookie_name        = "lb_session"
    cookie_ttl_seconds = 3600
  }

  droplet_tag = "odoo"

  tags = ["production", "loadbalancer"]
}

# ============================================
# SSL CERTIFICATES
# ============================================

resource "digitalocean_certificate" "main" {
  name    = "insightpulse-${var.environment}"
  type    = "lets_encrypt"
  domains = ["insightpulseai.net", "*.insightpulseai.net"]

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================
# FIREWALL RULES
# ============================================

# Firewall for Odoo servers
resource "digitalocean_firewall" "odoo" {
  name = "insightpulse-${var.environment}-odoo"

  droplet_ids = digitalocean_droplet.odoo[*].id

  # Inbound rules

  # SSH (restrict to office IP in production - TODO)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Odoo HTTP from load balancer only
  inbound_rule {
    protocol                  = "tcp"
    port_range                = "8069"
    source_load_balancer_uids = [digitalocean_loadbalancer.public.id]
  }

  # PostgreSQL from VPC
  inbound_rule {
    protocol         = "tcp"
    port_range       = "5432"
    source_addresses = [digitalocean_vpc.main.ip_range]
  }

  # Redis from VPC
  inbound_rule {
    protocol         = "tcp"
    port_range       = "6379"
    source_addresses = [digitalocean_vpc.main.ip_range]
  }

  # Prometheus metrics
  inbound_rule {
    protocol         = "tcp"
    port_range       = "9100"  # node_exporter
    source_addresses = [digitalocean_droplet.monitoring.ipv4_address_private]
  }

  # Outbound rules (allow all)
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

# Firewall for OCR server
resource "digitalocean_firewall" "ocr" {
  name = "insightpulse-${var.environment}-ocr"

  droplet_ids = [digitalocean_droplet.ocr.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "8000"  # OCR API
    source_addresses = [digitalocean_vpc.main.ip_range]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "9100"  # Prometheus
    source_addresses = [digitalocean_droplet.monitoring.ipv4_address_private]
  }

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
}

# Firewall for monitoring server
resource "digitalocean_firewall" "monitoring" {
  name = "insightpulse-${var.environment}-monitoring"

  droplet_ids = [digitalocean_droplet.monitoring.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Prometheus
  inbound_rule {
    protocol         = "tcp"
    port_range       = "9090"
    source_addresses = ["0.0.0.0/0", "::/0"]  # TODO: Restrict
  }

  # Grafana
  inbound_rule {
    protocol         = "tcp"
    port_range       = "3000"
    source_addresses = ["0.0.0.0/0", "::/0"]  # TODO: Restrict
  }

  # Alertmanager
  inbound_rule {
    protocol         = "tcp"
    port_range       = "9093"
    source_addresses = [digitalocean_vpc.main.ip_range]
  }

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
}

# ============================================
# SPACES (S3-COMPATIBLE OBJECT STORAGE)
# ============================================

resource "digitalocean_spaces_bucket" "backups" {
  name   = "insightpulse-backups"
  region = var.region

  acl = "private"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "expire-old-backups"
    enabled = true

    # Delete backups older than 90 days
    expiration {
      days = 90
    }

    # Keep only last 30 versions
    noncurrent_version_expiration {
      days = 30
    }
  }
}

resource "digitalocean_spaces_bucket" "terraform_state" {
  name   = "insightpulse-terraform-state"
  region = var.region

  acl = "private"

  versioning {
    enabled = true
  }
}

resource "digitalocean_spaces_bucket" "uploads" {
  name   = "insightpulse-uploads"
  region = var.region

  acl = "private"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://insightpulseai.net", "https://*.insightpulseai.net"]
    max_age_seconds = 3600
  }
}

# ============================================
# DNS (CLOUDFLARE)
# ============================================

# Root domain
resource "cloudflare_record" "root" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  value   = digitalocean_loadbalancer.public.ip
  type    = "A"
  ttl     = 1  # Auto
  proxied = true
}

# www subdomain
resource "cloudflare_record" "www" {
  zone_id = var.cloudflare_zone_id
  name    = "www"
  value   = digitalocean_loadbalancer.public.ip
  type    = "A"
  ttl     = 1
  proxied = true
}

# ERP subdomain
resource "cloudflare_record" "erp" {
  zone_id = var.cloudflare_zone_id
  name    = "erp"
  value   = digitalocean_loadbalancer.public.ip
  type    = "A"
  ttl     = 1
  proxied = true
}

# OCR subdomain (direct to OCR server)
resource "cloudflare_record" "ocr" {
  zone_id = var.cloudflare_zone_id
  name    = "ocr"
  value   = digitalocean_droplet.ocr.ipv4_address
  type    = "A"
  ttl     = 1
  proxied = true
}

# Monitoring subdomain
resource "cloudflare_record" "monitoring" {
  zone_id = var.cloudflare_zone_id
  name    = "monitoring"
  value   = digitalocean_droplet.monitoring.ipv4_address
  type    = "A"
  ttl     = 1
  proxied = false  # Don't proxy monitoring (direct access)
}

# Grafana subdomain
resource "cloudflare_record" "grafana" {
  zone_id = var.cloudflare_zone_id
  name    = "grafana"
  value   = digitalocean_droplet.monitoring.ipv4_address
  type    = "A"
  ttl     = 1
  proxied = true
}

# ============================================
# MONITORING ALERTS
# ============================================

resource "digitalocean_monitor_alert" "high_cpu" {
  alerts {
    email = [var.alert_email]
  }

  window      = "5m"
  type        = "v1/insights/droplet/cpu"
  compare     = "GreaterThan"
  value       = 80
  enabled     = true
  entities    = concat(digitalocean_droplet.odoo[*].id, [digitalocean_droplet.ocr.id])
  description = "CPU usage > 80% for 5 minutes"
}

resource "digitalocean_monitor_alert" "high_memory" {
  alerts {
    email = [var.alert_email]
  }

  window      = "5m"
  type        = "v1/insights/droplet/memory_utilization_percent"
  compare     = "GreaterThan"
  value       = 90
  enabled     = true
  entities    = concat(digitalocean_droplet.odoo[*].id, [digitalocean_droplet.ocr.id])
  description = "Memory usage > 90% for 5 minutes"
}

resource "digitalocean_monitor_alert" "high_disk" {
  alerts {
    email = [var.alert_email]
  }

  window      = "5m"
  type        = "v1/insights/droplet/disk_utilization_percent"
  compare     = "GreaterThan"
  value       = 85
  enabled     = true
  entities    = concat(digitalocean_droplet.odoo[*].id, [digitalocean_droplet.ocr.id])
  description = "Disk usage > 85%"
}

resource "digitalocean_monitor_alert" "database_cpu" {
  alerts {
    email = [var.alert_email]
  }

  window      = "5m"
  type        = "v1/insights/dbaas/cpu_percent"
  compare     = "GreaterThan"
  value       = 80
  enabled     = true
  entities    = [digitalocean_database_cluster.postgres.id]
  description = "Database CPU > 80% for 5 minutes"
}

# ============================================
# OUTPUTS
# ============================================

output "loadbalancer_ip" {
  description = "Load balancer public IP (update DNS to this)"
  value       = digitalocean_loadbalancer.public.ip
}

output "database_connection_uri" {
  description = "PostgreSQL connection URI (private network)"
  value       = digitalocean_database_cluster.postgres.private_uri
  sensitive   = true
}

output "database_host" {
  description = "PostgreSQL host (private)"
  value       = digitalocean_database_cluster.postgres.private_host
}

output "database_port" {
  description = "PostgreSQL port"
  value       = digitalocean_database_cluster.postgres.port
}

output "redis_uri" {
  description = "Redis connection URI (private network)"
  value       = digitalocean_database_cluster.redis.private_uri
  sensitive   = true
}

output "odoo_servers" {
  description = "Odoo server IPs"
  value = {
    for idx, droplet in digitalocean_droplet.odoo :
    droplet.name => {
      public_ip  = droplet.ipv4_address
      private_ip = droplet.ipv4_address_private
    }
  }
}

output "ocr_server_ip" {
  description = "OCR server IP"
  value = {
    public  = digitalocean_droplet.ocr.ipv4_address
    private = digitalocean_droplet.ocr.ipv4_address_private
  }
}

output "monitoring_server_ip" {
  description = "Monitoring server IP"
  value = {
    public  = digitalocean_droplet.monitoring.ipv4_address
    private = digitalocean_droplet.monitoring.ipv4_address_private
  }
}

output "spaces_endpoints" {
  description = "Spaces bucket endpoints"
  value = {
    backups        = "https://${digitalocean_spaces_bucket.backups.name}.${var.region}.digitaloceanspaces.com"
    terraform_state = "https://${digitalocean_spaces_bucket.terraform_state.name}.${var.region}.digitaloceanspaces.com"
    uploads        = "https://${digitalocean_spaces_bucket.uploads.name}.${var.region}.digitaloceanspaces.com"
  }
}

output "monitoring_urls" {
  description = "Monitoring service URLs"
  value = {
    prometheus   = "http://${digitalocean_droplet.monitoring.ipv4_address}:9090"
    grafana      = "https://grafana.insightpulseai.net"
    alertmanager = "http://${digitalocean_droplet.monitoring.ipv4_address}:9093"
  }
}

output "cost_estimate_monthly_php" {
  description = "Estimated monthly cost in PHP"
  value = "₱19,800 (~$355 USD)"
}

# ============================================
# COST BREAKDOWN
# ============================================

# Droplets:
# - 2x Odoo (s-4vcpu-8gb): ₱2,880 × 2 = ₱5,760
# - 1x OCR (c-4): ₱2,160
# - 1x Monitoring (s-2vcpu-4gb): ₱1,440
# Subtotal Droplets: ₱9,360

# Databases:
# - PostgreSQL HA (db-s-2vcpu-4gb × 2 nodes): ₱5,760
# - Redis (db-s-1vcpu-1gb): ₱720
# Subtotal Databases: ₱6,480

# Load Balancer: ₱720/month

# Spaces (estimate):
# - Backups (100GB): ₱100
# - Uploads (50GB): ₱50
# Subtotal Storage: ₱150

# Bandwidth (estimate):
# - 1TB included, additional ₱180/TB
# Estimate: ₱360/month

# SSL Certificates: FREE (Let's Encrypt)

# TOTAL: ₱17,070/month (~$306 USD/month @ ₱55.75/USD)

# Compare to SaaS equivalent:
# - Heroku: $400-500/month
# - AWS/GCP: $500-700/month
# - Traditional hosting + managed services: $400/month
#
# SAVINGS: 50-70% vs SaaS
