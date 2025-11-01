# Production Deployment Guide

This guide provides step-by-step instructions for deploying InsightPulse Odoo to production using the hardened, multi-stage Docker setup with automated CI/CD.

## Prerequisites

- Linux server with Docker and Docker Compose installed
- Minimum 4GB RAM, 2 CPU cores (8GB RAM, 4 cores recommended)
- Domain name pointed to your server
- SSH access with sudo privileges
- GitHub account with access to the repository

## Architecture Overview

```
┌─────────────────┐
│   Caddy Proxy   │ :80, :443 (SSL/TLS)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Odoo App      │ :8069 (internal), :8072 (longpolling)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Postgres│ │ Redis  │
│   :5432 │ │  :6379 │
└─────────┘ └────────┘
```

## Step 1: Server Setup

### Install Docker and Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### Create deployment directory

```bash
# Create deployment directory
sudo mkdir -p /opt/insightpulse
sudo chown $USER:$USER /opt/insightpulse
cd /opt/insightpulse

# Create required subdirectories
mkdir -p config/odoo backups
```

## Step 2: Configuration Files

### Copy production compose file

```bash
# Download docker-compose.prod.yml from repo
curl -O https://raw.githubusercontent.com/jgtolentino/insightpulse-odoo/main/docker-compose.prod.yml
```

### Create Odoo configuration file

```bash
# Create config/odoo/odoo.conf
cat > config/odoo/odoo.conf << 'EOF'
[options]
# Database
db_host = db
db_port = 5432
db_user = odoo
db_password = False  # Set via environment
db_maxconn = 64
db_name = False
db_template = template0

# Server
http_port = 8069
longpolling_port = 8072
proxy_mode = True
workers = 4
max_cron_threads = 2

# Limits
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 120
limit_time_real = 240
limit_time_real_cron = 3600
limit_request = 8192

# Logging
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log
logrotate = True

# Addons
addons_path = /mnt/extra-addons/insightpulse,/mnt/extra-addons/custom,/mnt/extra-addons/oca,/usr/lib/python3/dist-packages/odoo/addons

# Security
admin_passwd = False  # Set via environment
list_db = False
db_filter = ^%d$

# Sessions
session_gc_enable = True
EOF
```

### Create environment file

```bash
# Copy example and edit
cp .env.production.example .env
nano .env

# Set strong passwords:
# - POSTGRES_PASSWORD
# - ODOO_ADMIN_PASSWORD
# Adjust resource limits based on your server specs
```

### Secure the environment file

```bash
chmod 600 .env
```

## Step 3: SSL/TLS Setup with Caddy

### Install Caddy

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

### Configure Caddyfile

```bash
sudo nano /etc/caddy/Caddyfile
```

Add:

```caddyfile
insightpulseai.net {
  encode zstd gzip

  # Security headers
  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "SAMEORIGIN"
    Referrer-Policy "strict-origin-when-cross-origin"
    -Server
  }

  # Block database manager
  @dbm path /web/database/* /database/*
  respond @dbm 403

  # Health check endpoint
  @health path /web/health
  reverse_proxy @health localhost:8069

  # Odoo main application
  reverse_proxy localhost:8069 {
    header_up X-Real-IP {remote_host}
    header_up X-Forwarded-For {remote_host}
    header_up X-Forwarded-Proto {scheme}
  }
}
```

### Reload Caddy

```bash
sudo systemctl reload caddy
sudo systemctl status caddy
```

## Step 4: GitHub Container Registry Authentication

```bash
# Create a GitHub Personal Access Token with read:packages scope
# Then login:
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

## Step 5: Initial Deployment

### Pull and start services

```bash
cd /opt/insightpulse

# Pull latest image
docker compose -f docker-compose.prod.yml pull

# Start services
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

### Verify deployment

```bash
# Check container health
docker compose -f docker-compose.prod.yml ps

# Test health endpoint
curl http://localhost:8069/web/health

# Test via domain
curl https://insightpulseai.net/web/health
```

## Step 6: GitHub Actions Setup

### Required GitHub Secrets

Add these secrets to your repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | Example |
|------------|-------------|---------|
| `PROD_HOST` | Server IP or hostname | `192.168.1.100` |
| `PROD_SSH_USER` | SSH username | `deploy` |
| `PROD_SSH_KEY` | SSH private key (PEM format) | `-----BEGIN RSA PRIVATE KEY-----...` |
| `PROD_COMPOSE_DIR` | Deployment directory | `/opt/insightpulse` |

### SSH Key Setup

```bash
# On your local machine, generate a deployment key
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/github_deploy.pub $USER@your-server

# Add private key to GitHub Secrets as PROD_SSH_KEY
cat ~/.ssh/github_deploy
```

### Test Automated Deployment

```bash
# Make a small change and push to main
git add .
git commit -m "test: trigger deployment"
git push origin main

# Watch GitHub Actions run the workflow
# Check https://github.com/jgtolentino/insightpulse-odoo/actions
```

## Step 7: Database Initialization

### First-time database setup

```bash
# Access Odoo web interface
# Go to https://insightpulseai.net

# Create master database:
# - Database Name: production
# - Admin Password: (set strong password)
# - Language: English
# - Demo data: No

# Install required modules
```

## Step 8: Backup Configuration

### Create backup script

```bash
cat > /opt/insightpulse/backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/opt/insightpulse/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="production"

# Backup database
docker compose -f /opt/insightpulse/docker-compose.prod.yml exec -T db \
  pg_dump -U odoo -Fc $DB_NAME > "$BACKUP_DIR/db_${DB_NAME}_${TIMESTAMP}.dump"

# Backup filestore
docker compose -f /opt/insightpulse/docker-compose.prod.yml exec -T odoo \
  tar czf - /var/lib/odoo/filestore/$DB_NAME > "$BACKUP_DIR/filestore_${DB_NAME}_${TIMESTAMP}.tar.gz"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.dump" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x /opt/insightpulse/backup.sh
```

### Schedule daily backups

```bash
# Add to crontab
crontab -e

# Add line for daily backup at 2 AM
0 2 * * * /opt/insightpulse/backup.sh >> /opt/insightpulse/backup.log 2>&1
```

## Step 9: Monitoring

### Check logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Odoo only
docker compose -f docker-compose.prod.yml logs -f odoo

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 odoo
```

### Monitor resources

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Step 10: Rollback Procedure

If a deployment fails, rollback to previous version:

```bash
cd /opt/insightpulse

# Stop current version
docker compose -f docker-compose.prod.yml down

# Set previous tag in .env
nano .env
# Change ODOO_TAG=latest to ODOO_TAG=v19.0.X

# Pull and restart
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Verify health
curl https://insightpulseai.net/web/health
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs odoo

# Check container status
docker compose -f docker-compose.prod.yml ps

# Restart services
docker compose -f docker-compose.prod.yml restart
```

### Database connection issues

```bash
# Check PostgreSQL is running
docker compose -f docker-compose.prod.yml ps db

# Test database connection
docker compose -f docker-compose.prod.yml exec db psql -U odoo -d odoo -c "SELECT version();"
```

### Out of memory

```bash
# Check memory usage
free -h
docker stats

# Reduce workers in .env
ODOO_WORKERS=2
ODOO_MAX_CRON_THREADS=1

# Restart
docker compose -f docker-compose.prod.yml restart odoo
```

### SSL certificate issues

```bash
# Check Caddy logs
sudo journalctl -u caddy -f

# Reload Caddy
sudo systemctl reload caddy

# Test certificate
curl -vI https://insightpulseai.net
```

## Maintenance

### Update Odoo

```bash
# Updates are automatic via GitHub Actions
# Manual update:
cd /opt/insightpulse
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Clean up Docker resources

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (careful!)
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

## Security Checklist

- [x] SSL/TLS enabled via Caddy
- [x] Database manager disabled (`/web/database` blocked)
- [x] Strong passwords set in .env
- [x] `.env` file has 600 permissions
- [x] Odoo running as non-root user
- [x] Database filtering enabled
- [x] Database listing disabled
- [x] Firewall configured (only ports 80, 443, 22 open)
- [x] Automated backups configured
- [x] Monitoring and logging enabled

## Support

For issues or questions:
- GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- Documentation: See README.md and other docs in repo
