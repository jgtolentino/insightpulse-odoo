# Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying InsightPulse Odoo with Superset BI integration to production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Odoo Deployment](#odoo-deployment)
5. [PostgreSQL Configuration](#postgresql-configuration)
6. [Superset Deployment](#superset-deployment)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Scaling Strategies](#scaling-strategies)
11. [Maintenance Procedures](#maintenance-procedures)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum Production Specifications**:
- **CPU**: 4 cores (8 recommended for high-traffic)
- **RAM**: 8 GB (16+ GB recommended)
- **Storage**: 100 GB SSD (NVMe preferred)
- **Network**: 100 Mbps minimum bandwidth

**Operating System**:
- Ubuntu 22.04 LTS (recommended)
- Debian 12
- RHEL/Rocky Linux 9

### Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose v2
sudo apt install docker-compose-plugin
```

### Domain & DNS

1. **Register Domain**: `yourdomain.com`
2. **Configure DNS Records**:
   ```
   A    @              <server-ip>      # Main domain
   A    www            <server-ip>      # WWW subdomain
   A    odoo           <server-ip>      # Odoo subdomain
   A    superset       <server-ip>      # Superset subdomain
   CNAME db           odoo.yourdomain.com # Database alias (optional)
   ```

---

## Architecture Overview

### Production Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Internet (HTTPS)                    │
└───────────────────┬─────────────────────────────────────┘
                    │
            ┌───────▼────────┐
            │  Load Balancer │ (nginx/HAProxy)
            │  SSL/TLS Term  │
            └───────┬────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐     ┌───────▼────────┐
│  Odoo Worker 1 │     │  Superset      │
│  (Port 8069)   │     │  (Port 8088)   │
├────────────────┤     └────────────────┘
│  Odoo Worker 2 │              │
│  (Port 8070)   │              │
└────────┬───────┘              │
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────┐
         │   PostgreSQL 15+    │
         │   (Port 5432)       │
         │   - Odoo DB         │
         │   - Superset DB     │
         └─────────────────────┘
                    │
         ┌──────────▼──────────┐
         │      Redis          │
         │   Cache/Sessions    │
         └─────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  Storage (Volume)   │
         │  - Filestore        │
         │  - Backups          │
         └─────────────────────┘
```

### Component Overview

| Component | Purpose | Scaling Method |
|-----------|---------|----------------|
| **Nginx** | Reverse proxy, SSL termination, load balancing | Vertical (single instance) |
| **Odoo** | ERP application server | Horizontal (multiple workers) |
| **PostgreSQL** | Primary database | Vertical + read replicas |
| **Superset** | BI and analytics dashboard | Horizontal (multiple instances) |
| **Redis** | Cache, session store, queue | Vertical + clustering |

---

## Infrastructure Setup

### 1. Server Provisioning

**DigitalOcean Droplet** (Recommended):
```bash
# Using doctl CLI
doctl compute droplet create insightpulse-odoo \
  --image ubuntu-22-04-x64 \
  --size s-4vcpu-8gb \
  --region nyc3 \
  --ssh-keys <your-ssh-key-id> \
  --enable-monitoring \
  --enable-backups \
  --tag-names production,odoo,erp

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get insightpulse-odoo --format PublicIPv4 --no-header)
```

**AWS EC2** (Alternative):
```bash
# Launch t3.large instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=insightpulse-odoo}]'
```

### 2. Initial Server Setup

```bash
# SSH into server
ssh root@$DROPLET_IP

# Create application user
adduser --disabled-password --gecos "" odoo
usermod -aG sudo,docker odoo

# Configure SSH (disable password auth)
cat >> /etc/ssh/sshd_config << EOF
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
EOF
systemctl restart sshd

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw --force enable
```

### 3. Directory Structure

```bash
# Create application directories
sudo -u odoo mkdir -p /home/odoo/apps/{odoo,superset,nginx,backups}
sudo -u odoo mkdir -p /home/odoo/data/{postgres,redis,filestore}
sudo -u odoo mkdir -p /home/odoo/logs

# Set permissions
chown -R odoo:odoo /home/odoo
chmod 750 /home/odoo/data
```

---

## Odoo Deployment

### 1. Clone Repository

```bash
sudo -u odoo bash << 'EOF'
cd /home/odoo/apps/odoo
git clone https://github.com/jgtolentino/insightpulse-odoo.git .
git checkout main
EOF
```

### 2. Environment Configuration

```bash
sudo -u odoo bash << 'EOF'
cat > /home/odoo/apps/odoo/.env << 'ENVEOF'
# Database Configuration
POSTGRES_DB=odoo
POSTGRES_USER=odoo
POSTGRES_PASSWORD=$(openssl rand -base64 32)
DB_HOST=db
DB_PORT=5432
DB_MAXCONN=64
DB_TEMPLATE=template0

# Odoo Configuration
ADMIN_PASSWD=$(openssl rand -base64 32)
ODOO_VERSION=19.0
WORKERS=4
MAX_CRON_THREADS=2
LIMIT_TIME_CPU=600
LIMIT_TIME_REAL=1200
LIMIT_MEMORY_SOFT=2147483648
LIMIT_MEMORY_HARD=2684354560

# Session & Security
SESSION_TIMEOUT=7200
PROXY_MODE=true

# Email Configuration (configure based on provider)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_SSL=True

# Logging
LOG_LEVEL=info
LOG_HANDLER=:INFO
LOGFILE=/var/log/odoo/odoo.log

# Storage
DATA_DIR=/var/lib/odoo

# Superset Connection
SUPERSET_URL=https://superset.yourdomain.com
ENVEOF
EOF
```

### 3. Docker Compose Production Configuration

```bash
sudo -u odoo bash << 'EOF'
cat > /home/odoo/apps/odoo/docker-compose.prod.yml << 'COMPOSE'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: odoo-postgres
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=en_US.UTF-8"
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - /home/odoo/data/postgres:/var/lib/postgresql/data
      - /home/odoo/backups:/backups
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    command:
      - postgres
      - -c
      - max_connections=200
      - -c
      - shared_buffers=256MB
      - -c
      - effective_cache_size=1GB
      - -c
      - maintenance_work_mem=128MB
      - -c
      - checkpoint_completion_target=0.9
      - -c
      - wal_buffers=16MB
      - -c
      - default_statistics_target=100
      - -c
      - random_page_cost=1.1
      - -c
      - effective_io_concurrency=200
      - -c
      - work_mem=2MB
      - -c
      - min_wal_size=1GB
      - -c
      - max_wal_size=4GB
      - -c
      - log_destination=stderr
      - -c
      - logging_collector=on
      - -c
      - log_directory=/var/log/postgresql
      - -c
      - log_filename=postgresql-%Y-%m-%d.log
      - -c
      - log_rotation_age=1d
      - -c
      - log_line_prefix='%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
      - -c
      - log_min_duration_statement=1000

  redis:
    image: redis:7-alpine
    container_name: odoo-redis
    restart: always
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - /home/odoo/data/redis:/data
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  odoo:
    image: jgtolentino/insightpulse-odoo:main
    container_name: odoo-app
    restart: always
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - HOST=${DB_HOST}
      - PORT=${DB_PORT}
      - USER=${POSTGRES_USER}
      - PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - /home/odoo/data/filestore:/var/lib/odoo
      - /home/odoo/apps/odoo/addons:/mnt/extra-addons
      - /home/odoo/logs:/var/log/odoo
    networks:
      - odoo-network
    ports:
      - "127.0.0.1:8069:8069"
      - "127.0.0.1:8072:8072"  # Longpolling
    command: odoo --workers=${WORKERS} --max-cron-threads=${MAX_CRON_THREADS} --limit-time-cpu=${LIMIT_TIME_CPU} --limit-time-real=${LIMIT_TIME_REAL} --proxy-mode
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

networks:
  odoo-network:
    driver: bridge

COMPOSE
EOF
```

### 4. Deploy Odoo

```bash
sudo -u odoo bash << 'EOF'
cd /home/odoo/apps/odoo
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml logs -f --tail=50
EOF
```

---

## PostgreSQL Configuration

### 1. Create Read-Only User for BI Tools

```bash
docker exec -it odoo-postgres psql -U odoo -d odoo << 'SQL'
-- Create read-only user
CREATE USER odoo_readonly WITH PASSWORD 'strong_random_password_here';

-- Grant connection
GRANT CONNECT ON DATABASE odoo TO odoo_readonly;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO odoo_readonly;

-- Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO odoo_readonly;

-- Grant SELECT on all future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO odoo_readonly;

-- Create materialized views refresh function (for superuser only)
CREATE OR REPLACE FUNCTION refresh_all_mat_views()
RETURNS void AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT matviewname 
        FROM pg_matviews 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY ' || quote_ident(r.matviewname);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
SQL
```

### 2. Create Analytics Views

```bash
docker exec -it odoo-postgres psql -U odoo -d odoo << 'SQL'
-- Sales KPI by Day
CREATE OR REPLACE VIEW vw_sales_kpi_day AS
SELECT 
    date_trunc('day', so.date_order AT TIME ZONE 'UTC')::date as sale_date,
    so.company_id,
    c.name as company_name,
    COUNT(DISTINCT so.id) as order_count,
    COUNT(DISTINCT so.partner_id) as customer_count,
    SUM(so.amount_total) as total_revenue,
    SUM(so.amount_untaxed) as revenue_before_tax,
    AVG(so.amount_total) as avg_order_value,
    SUM(CASE WHEN so.state = 'sale' THEN so.amount_total ELSE 0 END) as confirmed_revenue,
    SUM(CASE WHEN so.state = 'done' THEN so.amount_total ELSE 0 END) as delivered_revenue
FROM sale_order so
JOIN res_company c ON so.company_id = c.id
WHERE so.state IN ('sale', 'done')
GROUP BY date_trunc('day', so.date_order AT TIME ZONE 'UTC')::date, so.company_id, c.name;

-- Product Performance
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT 
    pp.id as product_id,
    pt.name as product_name,
    pc.name as category_name,
    COUNT(DISTINCT sol.order_id) as order_count,
    SUM(sol.product_uom_qty) as total_quantity_sold,
    SUM(sol.price_subtotal) as total_revenue,
    AVG(sol.price_unit) as avg_unit_price,
    MAX(so.date_order) as last_sale_date
FROM product_product pp
JOIN product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN product_category pc ON pt.categ_id = pc.id
LEFT JOIN sale_order_line sol ON sol.product_id = pp.id
LEFT JOIN sale_order so ON sol.order_id = so.id AND so.state IN ('sale', 'done')
WHERE pt.active = true
GROUP BY pp.id, pt.name, pc.name;

-- Customer Lifetime Value
CREATE OR REPLACE VIEW vw_customer_ltv AS
SELECT 
    p.id as partner_id,
    p.name as customer_name,
    p.country_id,
    c.name as country_name,
    COUNT(DISTINCT so.id) as total_orders,
    SUM(so.amount_total) as lifetime_value,
    AVG(so.amount_total) as avg_order_value,
    MIN(so.date_order) as first_order_date,
    MAX(so.date_order) as last_order_date,
    MAX(so.date_order)::date - MIN(so.date_order)::date as customer_age_days
FROM res_partner p
LEFT JOIN sale_order so ON so.partner_id = p.id AND so.state IN ('sale', 'done')
LEFT JOIN res_country c ON p.country_id = c.id
WHERE p.customer_rank > 0
GROUP BY p.id, p.name, p.country_id, c.name;

-- Vendor Spend (90 days)
CREATE OR REPLACE VIEW vw_vendor_spend_90d AS
SELECT 
    p.id as vendor_id,
    p.name as vendor_name,
    COUNT(DISTINCT po.id) as purchase_order_count,
    SUM(po.amount_total) as total_spend,
    AVG(po.amount_total) as avg_order_value,
    MAX(po.date_order) as last_purchase_date
FROM res_partner p
JOIN purchase_order po ON po.partner_id = p.id
WHERE po.state IN ('purchase', 'done')
  AND po.date_order >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY p.id, p.name;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sale_order_date_state ON sale_order(date_order, state);
CREATE INDEX IF NOT EXISTS idx_sale_order_company_date ON sale_order(company_id, date_order);
CREATE INDEX IF NOT EXISTS idx_sale_order_line_product ON sale_order_line(product_id);
CREATE INDEX IF NOT EXISTS idx_purchase_order_date_state ON purchase_order(date_order, state);
SQL
```

### 3. Scheduled Maintenance

```bash
# Create cron job for database maintenance
sudo -u odoo crontab -e
# Add:
# Vacuum and analyze daily at 2 AM
0 2 * * * docker exec odoo-postgres vacuumdb -U odoo -d odoo -z -q >> /home/odoo/logs/vacuum.log 2>&1

# Backup daily at 3 AM
0 3 * * * /home/odoo/apps/odoo/scripts/backup-database.sh >> /home/odoo/logs/backup.log 2>&1
```

---

## Superset Deployment

### 1. Superset Docker Compose

```bash
sudo -u odoo bash << 'EOF'
cat > /home/odoo/apps/superset/docker-compose.yml << 'COMPOSE'
version: '3.8'

x-superset-image: &superset-image apache/superset:3.0.0
x-superset-depends-on: &superset-depends-on
  - db
  - redis

services:
  superset:
    <<: *superset-image
    container_name: superset
    restart: always
    depends_on: *superset-depends-on
    environment:
      - SUPERSET_SECRET_KEY=${SUPERSET_SECRET_KEY}
      - DATABASE_DB=superset
      - DATABASE_HOST=db
      - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
      - DATABASE_USER=${POSTGRES_USER}
      - DATABASE_PORT=5432
      - DATABASE_DIALECT=postgresql
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    ports:
      - "127.0.0.1:8088:8088"
    volumes:
      - /home/odoo/apps/superset/config:/app/pythonpath
      - /home/odoo/data/superset:/app/superset_home
    command: >
      bash -c "
      superset db upgrade &&
      superset fab create-admin --username admin --firstname Admin --lastname User --email admin@superset.com --password ${SUPERSET_ADMIN_PASSWORD} || true &&
      superset init &&
      gunicorn --bind 0.0.0.0:8088 --workers 4 --timeout 120 --limit-request-line 0 --limit-request-field_size 0 'superset.app:create_app()'
      "
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  superset-worker:
    <<: *superset-image
    container_name: superset-worker
    restart: always
    depends_on: *superset-depends-on
    environment:
      - SUPERSET_SECRET_KEY=${SUPERSET_SECRET_KEY}
      - DATABASE_DB=superset
      - DATABASE_HOST=db
      - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
      - DATABASE_USER=${POSTGRES_USER}
      - DATABASE_PORT=5432
      - DATABASE_DIALECT=postgresql
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - /home/odoo/apps/superset/config:/app/pythonpath
      - /home/odoo/data/superset:/app/superset_home
    command: celery --app=superset.tasks.celery_app:app worker --pool=prefork -O fair -c 4

networks:
  default:
    name: odoo-network
    external: true
COMPOSE
EOF
```

### 2. Superset Configuration

```bash
sudo -u odoo bash << 'EOF'
mkdir -p /home/odoo/apps/superset/config
cat > /home/odoo/apps/superset/config/superset_config.py << 'PYCONF'
import os

# Secret key for encryption
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY')

# Database connection
SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PASSWORD')}@{os.environ.get('DATABASE_HOST')}:{os.environ.get('DATABASE_PORT')}/{os.environ.get('DATABASE_DB')}"

# Redis for caching and celery
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

class CeleryConfig:
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    imports = ('superset.sql_lab',)
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    worker_prefetch_multiplier = 1
    task_acks_late = False

CELERY_CONFIG = CeleryConfig

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 1,
}

# Data cache
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 2,
}

# Enable embedding
FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDED_SUPERSET": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Row level security
ROW_LEVEL_SECURITY_ENABLED = True

# CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['https://odoo.yourdomain.com']
}

# Session configuration
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'

PYCONF
EOF
```

### 3. Deploy Superset

```bash
sudo -u odoo bash << 'EOF'
cd /home/odoo/apps/superset

# Generate secret key
export SUPERSET_SECRET_KEY=$(openssl rand -base64 42)
export SUPERSET_ADMIN_PASSWORD=$(openssl rand -base64 16)

# Save to .env
cat > .env << ENVEOF
SUPERSET_SECRET_KEY=${SUPERSET_SECRET_KEY}
SUPERSET_ADMIN_PASSWORD=${SUPERSET_ADMIN_PASSWORD}
POSTGRES_USER=odoo
POSTGRES_PASSWORD=$(grep POSTGRES_PASSWORD /home/odoo/apps/odoo/.env | cut -d'=' -f2)
ENVEOF

# Deploy
docker compose up -d
docker compose logs -f
EOF
```

---

## Security Hardening

### 1. SSL/TLS with Let's Encrypt

```bash
# Install Nginx
sudo apt install -y nginx

# Configure Nginx for Odoo
sudo tee /etc/nginx/sites-available/odoo << 'NGINX'
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoo-longpolling {
    server 127.0.0.1:8072;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name odoo.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name odoo.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/odoo.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/odoo.yourdomain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/odoo-access.log;
    error_log /var/log/nginx/odoo-error.log;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # File upload size
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;

    # Odoo app
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    # Longpolling
    location /longpolling {
        proxy_pass http://odoo-longpolling;
    }

    # Cache static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90d;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }
}
NGINX

# Enable site
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obtain SSL certificate
sudo certbot --nginx -d odoo.yourdomain.com --non-interactive --agree-tos -m admin@yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 2. Configure Superset Nginx

```bash
sudo tee /etc/nginx/sites-available/superset << 'NGINX'
upstream superset {
    server 127.0.0.1:8088;
}

server {
    listen 80;
    server_name superset.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name superset.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/superset.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/superset.yourdomain.com/privkey.pem;

    # Security headers (same as Odoo)
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://superset;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo ln -s /etc/nginx/sites-available/superset /etc/nginx/sites-enabled/
sudo certbot --nginx -d superset.yourdomain.com --non-interactive --agree-tos -m admin@yourdomain.com
sudo nginx -t && sudo systemctl restart nginx
```

### 3. Fail2ban Configuration

```bash
# Create Odoo jail
sudo tee /etc/fail2ban/jail.d/odoo.conf << 'F2B'
[odoo]
enabled = true
port = http,https
filter = odoo
logpath = /home/odoo/logs/odoo.log
maxretry = 5
bantime = 600
findtime = 300
F2B

# Create filter
sudo tee /etc/fail2ban/filter.d/odoo.conf << 'FILTER'
[Definition]
failregex = ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \d+ WARNING \S+ \S+ Login failed for db:\S+ login:\S+ from <HOST>
ignoreregex =
FILTER

sudo systemctl restart fail2ban
```

---

## Monitoring & Logging

### 1. Log Rotation

```bash
sudo tee /etc/logrotate.d/odoo << 'LOGROTATE'
/home/odoo/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 odoo odoo
    sharedscripts
    postrotate
        docker exec odoo-app kill -HUP 1 2>/dev/null || true
    endscript
}
LOGROTATE
```

### 2. Prometheus Monitoring (Optional)

```bash
# PostgreSQL exporter
docker run -d \
  --name postgres-exporter \
  --network odoo-network \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://odoo:password@db:5432/odoo?sslmode=disable" \
  prometheuscommunity/postgres-exporter

# Node exporter
docker run -d \
  --name node-exporter \
  -p 9100:9100 \
  -v "/proc:/host/proc:ro" \
  -v "/sys:/host/sys:ro" \
  -v "/:/rootfs:ro" \
  prom/node-exporter \
  --path.procfs=/host/proc \
  --path.sysfs=/host/sys \
  --collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)
```

---

## Backup & Recovery

### 1. Database Backup Script

```bash
sudo -u odoo bash << 'EOF'
cat > /home/odoo/apps/odoo/scripts/backup-database.sh << 'BACKUP'
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/home/odoo/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="odoo"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Starting database backup: $TIMESTAMP"
docker exec odoo-postgres pg_dump -U odoo -Fc $DB_NAME > "$BACKUP_DIR/odoo_${TIMESTAMP}.dump"

# Backup filestore
echo "Backing up filestore..."
tar -czf "$BACKUP_DIR/filestore_${TIMESTAMP}.tar.gz" -C /home/odoo/data filestore

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "odoo_*.dump" -mtime +30 -delete
find "$BACKUP_DIR" -name "filestore_*.tar.gz" -mtime +30 -delete

echo "Backup completed: odoo_${TIMESTAMP}.dump"

# Optional: Upload to S3
# aws s3 cp "$BACKUP_DIR/odoo_${TIMESTAMP}.dump" s3://your-bucket/backups/
BACKUP

chmod +x /home/odoo/apps/odoo/scripts/backup-database.sh
EOF
```

### 2. Restore Procedure

```bash
#!/bin/bash
# Restore from backup

BACKUP_FILE="/home/odoo/backups/odoo_20250126_030000.dump"
FILESTORE_BACKUP="/home/odoo/backups/filestore_20250126_030000.tar.gz"

# Stop Odoo
docker compose -f /home/odoo/apps/odoo/docker-compose.prod.yml stop odoo

# Drop and recreate database
docker exec odoo-postgres psql -U odoo -c "DROP DATABASE IF EXISTS odoo;"
docker exec odoo-postgres psql -U odoo -c "CREATE DATABASE odoo OWNER odoo;"

# Restore database
docker exec -i odoo-postgres pg_restore -U odoo -d odoo < "$BACKUP_FILE"

# Restore filestore
rm -rf /home/odoo/data/filestore
tar -xzf "$FILESTORE_BACKUP" -C /home/odoo/data

# Start Odoo
docker compose -f /home/odoo/apps/odoo/docker-compose.prod.yml start odoo

echo "Restore completed successfully"
```

---

## Scaling Strategies

### Horizontal Scaling (Multiple Workers)

```yaml
# docker-compose.scale.yml
services:
  odoo-worker-1:
    <<: *odoo-service
    container_name: odoo-worker-1
    ports:
      - "127.0.0.1:8069:8069"
  
  odoo-worker-2:
    <<: *odoo-service
    container_name: odoo-worker-2
    ports:
      - "127.0.0.1:8070:8069"
  
  odoo-worker-3:
    <<: *odoo-service
    container_name: odoo-worker-3
    ports:
      - "127.0.0.1:8071:8069"
```

**Nginx load balancing**:
```nginx
upstream odoo {
    least_conn;
    server 127.0.0.1:8069;
    server 127.0.0.1:8070;
    server 127.0.0.1:8071;
}
```

### Database Read Replicas

See PostgreSQL documentation for streaming replication setup.

---

## Maintenance Procedures

### Regular Maintenance Tasks

1. **Weekly**: Review logs for errors
2. **Monthly**: Update Docker images
3. **Quarterly**: Security audit and dependency updates
4. **Annually**: SSL certificate renewal check

### Update Procedure

```bash
#!/bin/bash
# Update Odoo to latest image

cd /home/odoo/apps/odoo

# Backup first
./scripts/backup-database.sh

# Pull latest image
docker compose -f docker-compose.prod.yml pull odoo

# Restart with new image
docker compose -f docker-compose.prod.yml up -d odoo

# Update modules
docker compose -f docker-compose.prod.yml exec odoo odoo -d odoo -u all --stop-after-init

# Restart
docker compose -f docker-compose.prod.yml restart odoo
```

---

## Troubleshooting

### Common Issues

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Odoo not accessible | Check container status: `docker ps` | Restart container: `docker compose restart odoo` |
| Slow performance | Check DB queries: `pg_stat_statements` | Add indexes, optimize queries |
| High CPU usage | Check Odoo workers | Adjust `--workers` parameter |
| Database connection errors | Check max connections | Increase `max_connections` in PostgreSQL |
| SSL certificate errors | Check expiry: `certbot certificates` | Renew: `certbot renew` |

### Debug Commands

```bash
# View Odoo logs
docker logs odoo-app --tail=100 -f

# Database query analysis
docker exec odoo-postgres psql -U odoo -d odoo -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check disk space
df -h

# Check memory usage
free -h

# Network connectivity
curl -I https://odoo.yourdomain.com

# Container resource usage
docker stats
```

---

## Appendix

### Environment Variables Reference

See `.env.example` in repository.

### Port Reference

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| Odoo | 8069 | 80/443 (via nginx) | Web interface |
| Odoo Longpolling | 8072 | 80/443 (via nginx) | Real-time updates |
| PostgreSQL | 5432 | - | Database |
| Redis | 6379 | - | Cache |
| Superset | 8088 | 80/443 (via nginx) | BI Dashboard |

### Support & Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/19.0/
- **Superset Documentation**: https://superset.apache.org/docs/intro
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/15/
- **Docker Documentation**: https://docs.docker.com/

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-26  
**Target Environment**: Production  
**Odoo Version**: 19.0
