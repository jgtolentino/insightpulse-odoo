# Terraform Variables for InsightPulse AI Infrastructure

# ========================================
# Cloud Provider Credentials
# ========================================

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region for resources"
  type        = string
  default     = "sgp1"
}

variable "ssh_public_key" {
  description = "SSH public key for droplet access"
  type        = string
}

variable "admin_ip_whitelist" {
  description = "List of IP addresses allowed SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict in production
}

variable "alert_emails" {
  description = "Email addresses for monitoring alerts"
  type        = list(string)
  default     = ["admin@insightpulseai.net"]
}

# Database Configuration (Supabase)
variable "supabase_db_host" {
  description = "Supabase PostgreSQL host"
  type        = string
  default     = "aws-1-us-east-1.pooler.supabase.com"
}

variable "supabase_db_port" {
  description = "Supabase PostgreSQL port"
  type        = number
  default     = 6543
}

variable "supabase_db_name" {
  description = "Supabase database name"
  type        = string
  default     = "postgres"
}

variable "supabase_db_user" {
  description = "Supabase database user"
  type        = string
  default     = "postgres.spdtwktxdalcfigzeqrz"
  sensitive   = true
}

variable "supabase_db_password" {
  description = "Supabase database password"
  type        = string
  sensitive   = true
}

# Odoo Configuration
variable "odoo_admin_password" {
  description = "Odoo admin master password"
  type        = string
  sensitive   = true
}

variable "odoo_workers" {
  description = "Number of Odoo worker processes"
  type        = number
  default     = 2
}

variable "odoo_db_maxconn" {
  description = "Maximum database connections"
  type        = number
  default     = 8
}

# GitHub Configuration
variable "github_app_id" {
  description = "GitHub App ID for MCP server"
  type        = string
  default     = "2191216"
}

variable "github_private_key" {
  description = "GitHub App private key"
  type        = string
  sensitive   = true
}

variable "github_installation_id" {
  description = "GitHub App installation ID"
  type        = string
  sensitive   = true
}

# Droplet Configuration
variable "droplet_size_small" {
  description = "Small droplet size"
  type        = string
  default     = "s-1vcpu-1gb"  # $6/month
}

variable "droplet_size_medium" {
  description = "Medium droplet size"
  type        = string
  default     = "s-2vcpu-2gb"  # $18/month
}

variable "droplet_image" {
  description = "Base droplet image"
  type        = string
  default     = "ubuntu-22-04-x64"
}

# App Platform Configuration
variable "app_instance_size" {
  description = "App Platform instance size"
  type        = string
  default     = "basic-xxs"  # $5/month
}

variable "app_instance_count" {
  description = "Number of app instances"
  type        = number
  default     = 1
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable DigitalOcean monitoring"
  type        = bool
  default     = true
}

variable "enable_backups" {
  description = "Enable weekly backups for droplets"
  type        = bool
  default     = true
}

# Cost Management
variable "monthly_budget_alert" {
  description = "Monthly budget alert threshold in USD"
  type        = number
  default     = 50
}

# Environment Tags
variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "insightpulse-ai"
}
