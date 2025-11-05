# 🏗️ Infrastructure - Deployment & Configuration

This directory contains infrastructure-as-code, deployment configurations, and orchestration files for InsightPulse Odoo.

## 📁 Directory Structure

```
infrastructure/
├── docker/              # Docker configurations
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── docker-compose.prod.yml
│   └── Dockerfile.*
├── terraform/           # Terraform IaC
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
├── kubernetes/          # K8s manifests (future)
├── ansible/             # Configuration management
└── cloudformation/      # AWS CloudFormation (if needed)
```

## 🎯 Purpose

Infrastructure management provides:
- **Container Orchestration**: Docker Compose for local/dev
- **Infrastructure as Code**: Terraform for cloud resources
- **Configuration Management**: Ansible for server setup
- **Deployment Automation**: CI/CD integration
- **Environment Parity**: Dev/Staging/Prod consistency

## 🚀 Quick Start

### Local Development
```bash
# Start all services
make dev

# Or manually
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

### Production Deployment
```bash
# Deploy to DigitalOcean
make deploy-prod

# Or manually
cd infrastructure/terraform
terraform init
terraform apply
```

## 🐳 Docker Services

### Core Services
- **Odoo** (Port 8069) - Main ERP application
- **PostgreSQL** (Port 5432) - Primary database
- **Redis** (Port 6379) - Cache and session storage
- **Nginx** (Port 80/443) - Reverse proxy and load balancer

### Supporting Services
- **Superset** (Port 8088) - Business intelligence
- **n8n** (Port 5678) - Workflow automation
- **Authentik** (Port 9000) - SSO and identity
- **MinIO** (Port 9001) - Object storage
- **Qdrant** (Port 6333) - Vector database

### Monitoring Stack
- **Prometheus** (Port 9090) - Metrics collection
- **Grafana** (Port 3000) - Dashboards
- **Alertmanager** (Port 9093) - Alert routing

## 🌍 Terraform Configuration

### Cloud Providers
- **Primary**: DigitalOcean
- **Backup**: AWS (optional)
- **CDN**: Cloudflare

### Resources Managed
```hcl
# Droplets
resource "digitalocean_droplet" "odoo" {
  image  = "ubuntu-22-04-x64"
  name   = "insightpulse-odoo"
  region = "nyc3"
  size   = "s-2vcpu-4gb"
}

# Database
resource "digitalocean_database_cluster" "postgres" {
  name       = "insightpulse-db"
  engine     = "pg"
  version    = "15"
  size       = "db-s-2vcpu-4gb"
  region     = "nyc3"
  node_count = 1
}

# Load Balancer
resource "digitalocean_loadbalancer" "public" {
  name   = "insightpulse-lb"
  region = "nyc3"
}
```

### Apply Terraform
```bash
cd infrastructure/terraform

# Initialize
terraform init

# Plan changes
terraform plan

# Apply
terraform apply

# Destroy (careful!)
terraform destroy
```

## 📦 Environment Configuration

### Environment Files
```bash
config/
├── .env.example      # Template
├── .env.dev          # Development
├── .env.staging      # Staging
└── .env.prod         # Production
```

### Required Variables
```env
# Database
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<secret>
POSTGRES_DB=odoo

# Odoo
ODOO_ADMIN_PASSWORD=<secret>
ODOO_DB_HOST=postgres
ODOO_DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379

# Secrets
SECRET_KEY=<secret>
ENCRYPTION_KEY=<secret>
```

## 🔐 Secrets Management

### Development
```bash
# Use .env files (not committed)
cp config/.env.example config/.env.dev
```

### Production
```bash
# Use environment variables
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Or use secrets manager
terraform state pull | jq '.resources[] | select(.type=="digitalocean_database_cluster") | .instances[0].attributes.password'
```

## 🌐 Networking

### Port Mapping
| Service | Internal | External | Protocol |
|---------|----------|----------|----------|
| Odoo | 8069 | 80/443 | HTTP/HTTPS |
| PostgreSQL | 5432 | - | TCP |
| Superset | 8088 | 8088 | HTTP |
| n8n | 5678 | 5678 | HTTP |
| Grafana | 3000 | 3000 | HTTP |

### Firewall Rules
```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow SSH (restricted)
ufw allow from <your-ip> to any port 22

# Block database from internet
ufw deny 5432/tcp
```

## 📊 Resource Sizing

### Development
- **CPU**: 2 vCPUs
- **Memory**: 4 GB RAM
- **Storage**: 50 GB SSD

### Production
- **CPU**: 4-8 vCPUs
- **Memory**: 16-32 GB RAM
- **Storage**: 200-500 GB SSD
- **Database**: Managed PostgreSQL (2 vCPU, 4 GB RAM)

## 🔄 Deployment Strategies

### Rolling Deployment
```bash
# Zero-downtime deployment
docker-compose -f infrastructure/docker/docker-compose.yml up -d --no-deps --build odoo
```

### Blue-Green Deployment
```bash
# Deploy to green environment
terraform workspace select green
terraform apply

# Switch traffic
# Update load balancer
```

### Canary Deployment
```bash
# Deploy to 10% of traffic
# Monitor metrics
# Roll out to 100% if healthy
```

## 🛠️ Maintenance

### Backup
```bash
# Database backup
make backup

# Full system backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/ config/
```

### Updates
```bash
# Update Docker images
docker-compose pull

# Update Terraform providers
terraform init -upgrade

# Apply updates
docker-compose up -d
```

### Scaling
```bash
# Scale horizontally
docker-compose up -d --scale odoo=3

# Scale vertically (Terraform)
# Update droplet size in terraform/variables.tf
terraform apply
```

## 🔗 Related Documentation

- [Docker Compose Files](docker/)
- [Terraform Modules](terraform/)
- [Deployment Scripts](../scripts/deployment/)
- [Monitoring](../monitoring/README.md)

---

**For more information, see the main [README](../README.md)**
