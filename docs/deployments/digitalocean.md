# DigitalOcean Deployment Guide

Detailed DigitalOcean setup and deployment instructions.

## Prerequisites

- DigitalOcean account
- doctl CLI installed and authenticated
- GitHub repository access
- Domain DNS configured (insightpulseai.net)

## Droplet Setup

### 1. Create Droplets

**Odoo ERP Droplet (SFO2)**:
```bash
doctl compute droplet create ipai-odoo-erp \
  --region sfo2 \
  --size s-2vcpu-4gb \
  --image docker-20-04 \
  --ssh-keys <your-ssh-key-id>
```

**OCR Service Droplet (SGP1)**:
```bash
doctl compute droplet create ocr-service-droplet \
  --region sgp1 \
  --size s-2vcpu-4gb \
  --image docker-20-04 \
  --ssh-keys <your-ssh-key-id>
```

### 2. Initial Droplet Configuration

**SSH to droplet**:
```bash
ssh root@165.227.10.178  # Odoo ERP droplet
```

**Install dependencies**:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker and Docker Compose (if not using Docker image)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install -y docker-compose

# Verify installation
docker --version
docker-compose --version
```

**Configure firewall**:
```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 3. Clone Repository

```bash
cd /opt
git clone https://github.com/jgtolentino/insightpulse-odoo
cd insightpulse-odoo
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
# Set:
# - POSTGRES_PASSWORD
# - ODOO_ADMIN_PASSWORD
# - OAUTH_CLIENT_ID
# - OAUTH_CLIENT_SECRET
```

### 5. Start Services

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Verify services
docker-compose ps

# Check logs
docker-compose logs -f odoo
```

## Nginx Configuration

### 1. Install Nginx

```bash
apt install -y nginx certbot python3-certbot-nginx
```

### 2. Configure Reverse Proxy

**Create Nginx config** `/etc/nginx/sites-available/odoo`:
```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

server {
    listen 80;
    server_name erp.insightpulseai.net;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.net;

    # SSL managed by certbot
    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.net/privkey.pem;

    # Proxy settings
    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /websocket {
        proxy_pass http://odoo;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable site**:
```bash
ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 3. SSL Certificate

```bash
# Obtain certificate
certbot --nginx -d erp.insightpulseai.net

# Auto-renewal
certbot renew --dry-run
```

## App Platform Setup

### 1. Superset Analytics

**Create app**:
```bash
doctl apps create --spec apps/superset/app.yaml
```

**App spec** (apps/superset/app.yaml):
```yaml
name: superset-analytics
region: sfo
services:
  - name: superset
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    dockerfile_path: apps/superset/Dockerfile
    http_port: 8088
    routes:
      - path: /
    envs:
      - key: SUPERSET_SECRET_KEY
        scope: RUN_TIME
        type: SECRET
```

### 2. MCP Coordinator

**Create app**:
```bash
doctl apps create --spec apps/mcp/app.yaml
```

**App spec** (apps/mcp/app.yaml):
```yaml
name: mcp-coordinator
region: sfo
services:
  - name: mcp
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    dockerfile_path: apps/mcp/Dockerfile
    http_port: 3000
    routes:
      - path: /
```

## DNS Configuration

**Add A records** in DigitalOcean DNS:
```
Type  Hostname   Value
A     erp        165.227.10.178 (Odoo droplet)
A     superset   <app-platform-ip>
A     mcp        <app-platform-ip>
A     bkn        <app-platform-ip>
A     chat       <app-platform-ip>
```

## GitHub Actions Setup

**Required Secrets** (Settings → Secrets and variables → Actions):
- `DO_SSH_KEY` - Private SSH key for droplet access
- `DO_API_TOKEN` - DigitalOcean API token
- `DROPLET_IP` - 165.227.10.178
- `POSTGRES_PASSWORD`
- `ODOO_ADMIN_PASSWORD`
- `OAUTH_CLIENT_ID`
- `OAUTH_CLIENT_SECRET`

## Monitoring

**DigitalOcean Monitoring**:
- Enable monitoring on droplets
- Set up alerts for CPU/memory/disk

**Logs**:
```bash
# Droplet logs
ssh root@165.227.10.178 "journalctl -u docker -f"

# App Platform logs
doctl apps logs superset-analytics --follow
doctl apps logs mcp-coordinator --follow
```

## Backup

**Database backup**:
```bash
# Automated daily backup
crontab -e
# Add:
0 2 * * * docker exec postgres-odoo pg_dump -U odoo odoo > /backups/odoo-$(date +\%Y\%m\%d).sql
```

**Volume backup**:
```bash
# DigitalOcean Volumes
doctl compute volume-snapshot create <volume-id> --snapshot-name "odoo-backup-$(date +%Y%m%d)"
```

## Troubleshooting

**Service not responding**:
```bash
# Check Docker
docker ps
docker logs odoo

# Check Nginx
nginx -t
systemctl status nginx

# Check firewall
ufw status
```

**SSL issues**:
```bash
# Verify certificate
certbot certificates

# Renew manually
certbot renew
```

**Deployment failed**:
```bash
# Check GitHub Actions logs
gh run list --workflow=cd-odoo-prod.yml

# Manual deployment
ssh root@165.227.10.178
cd /opt/insightpulse-odoo
git pull
docker-compose up -d --build
```

## References

- [Deployment Overview](overview.md) - Architecture and workflow
- [Hosting Policy](../guides/hosting-policy.md) - Deployment policy
- [CI/CD Workflows](../guides/workflows-ci-cd.md) - GitHub Actions
- [DigitalOcean Docs](https://docs.digitalocean.com/)
