# Custom Odoo 19.0 Docker Image with SaaS Parity Features

Production-ready hardened Docker image for Odoo 19.0 Enterprise with full SaaS capabilities.

---

## 🎯 Features

### Core SaaS Capabilities
- ✅ **Multi-Tenancy**: Database-per-tenant isolation with dbfilter support
- ✅ **Automated Backups**: Scheduled database and filestore backups with S3 sync
- ✅ **Tenant Provisioning**: One-command tenant creation and initialization
- ✅ **Database Management**: Full CRUD operations for multi-tenant databases
- ✅ **Health Monitoring**: Comprehensive health checks with Prometheus metrics
- ✅ **Auto-Patching**: Pre-start validation and dependency fixing
- ✅ **Security Hardening**: Non-root execution, permission management

### Technical Stack
- **Base**: Odoo 19.0 official image
- **Python**: 3.11 (Odoo 19.0 requirement)
- **Node.js**: 20.x LTS (for frontend assets)
- **Monitoring**: Prometheus metrics on port 9090
- **Backup Storage**: Local + S3-compatible object storage
- **Session Store**: Redis support for horizontal scaling

---

## 🚀 Quick Start

### Build Image
```bash
docker build -f Dockerfile.custom -t insightpulse-odoo:19.0-saas .
```

### Run Single Tenant
```bash
docker run -d \
  --name odoo-saas \
  -p 8069:8069 \
  -p 9090:9090 \
  -e ODOO_DB_HOST=postgres \
  -e ODOO_DB_USER=odoo \
  -e ODOO_DB_PASSWORD=your_password \
  -e ODOO_DB_NAME=odoo_production \
  -e ODOO_ADMIN_PASSWD=your_admin_password \
  -e ODOO_METRICS_ENABLED=true \
  -v odoo-data:/var/lib/odoo \
  -v odoo-addons:/mnt/extra-addons \
  -v odoo-backups:/mnt/backups \
  insightpulse-odoo:19.0-saas
```

### Run Multi-Tenant SaaS
```bash
docker run -d \
  --name odoo-saas \
  -p 8069:8069 \
  -p 9090:9090 \
  -e ODOO_DB_HOST=postgres \
  -e ODOO_DB_USER=odoo \
  -e ODOO_DB_PASSWORD=your_password \
  -e ODOO_DB_FILTER=^%d$ \
  -e ODOO_LIST_DB=False \
  -e ODOO_AUTO_BACKUP=true \
  -e ODOO_METRICS_ENABLED=true \
  -e AWS_S3_BUCKET=my-odoo-backups \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -v odoo-data:/var/lib/odoo \
  -v odoo-addons:/mnt/extra-addons \
  -v odoo-backups:/mnt/backups \
  insightpulse-odoo:19.0-saas
```

---

## 📦 SaaS Management Scripts

### Database Manager (`odoo-db-manager.sh`)

**Create Database**:
```bash
docker exec odoo-saas /usr/local/bin/odoo-db-manager.sh create tenant_acme
```

**Backup Database**:
```bash
docker exec odoo-saas /usr/local/bin/odoo-db-manager.sh backup tenant_acme /mnt/backups/database
```

**Restore Database**:
```bash
docker exec odoo-saas /usr/local/bin/odoo-db-manager.sh restore tenant_acme /mnt/backups/database/tenant_acme_2025-10-30.sql.gz
```

**Clone Database** (for staging):
```bash
docker exec odoo-saas /usr/local/bin/odoo-db-manager.sh clone tenant_acme tenant_acme_staging
```

**Drop Database**:
```bash
docker exec odoo-saas /usr/local/bin/odoo-db-manager.sh drop tenant_acme_staging
```

**List Databases**:
```bash
docker exec odoo-saas /usr/local/bin/odoo-db-manager.sh list
```

### Tenant Provisioning (`odoo-provision-tenant.sh`)

**Provision New Tenant**:
```bash
docker exec odoo-saas /usr/local/bin/odoo-provision-tenant.sh acme_corp
```

This will:
1. Create isolated database `odoo_acme_corp`
2. Initialize Odoo with base modules
3. Install InsightPulse modules
4. Configure tenant-specific settings

### Automated Backups (`odoo-auto-backup.sh`)

**Manual Backup Trigger**:
```bash
docker exec odoo-saas /usr/local/bin/odoo-auto-backup.sh
```

**Automatic Schedule**: Runs every 6 hours when `ODOO_AUTO_BACKUP=true`

**Backup Retention**: Configurable via `BACKUP_RETENTION_DAYS` (default: 7 days)

**S3 Sync**: Automatically uploads to S3 if `AWS_S3_BUCKET` is configured

---

## 📊 Monitoring & Metrics

### Prometheus Metrics (`odoo-metrics.py`)

**Metrics Endpoint**: `http://localhost:9090/metrics`

**Available Metrics**:
- `odoo_database_size_bytes{database="tenant_name"}` - Database size per tenant
- `odoo_memory_usage_bytes` - Current memory usage
- `odoo_cpu_usage_percent` - CPU utilization
- `odoo_active_connections{database="tenant_name"}` - Active database connections
- `odoo_session_count` - Active user sessions

**Enable Metrics**:
```bash
-e ODOO_METRICS_ENABLED=true
```

### Health Checks (`health-check.sh`)

**Health Check Endpoint**: `http://localhost:8069/web/health`

**Docker Health Status**:
```bash
docker ps --filter name=odoo-saas --format "table {{.Names}}\t{{.Status}}"
```

**Health Check Criteria**:
1. ✅ Odoo process running
2. ✅ HTTP endpoint responding
3. ✅ Database connectivity
4. ⚠️ Memory usage within limits

---

## 🔧 Configuration

### Environment Variables

#### Database Configuration
```bash
ODOO_DB_HOST=postgres          # Database host
ODOO_DB_PORT=5432              # Database port (default: 5432)
ODOO_DB_USER=odoo              # Database user
ODOO_DB_PASSWORD=secret        # Database password
ODOO_DB_NAME=odoo_production   # Database name (single-tenant)
```

#### Multi-Tenancy Configuration
```bash
ODOO_DB_FILTER=^%d$            # Database filter regex (subdomain-based)
ODOO_LIST_DB=False             # Hide database selector (True for dev)
```

#### Security Configuration
```bash
ODOO_ADMIN_PASSWD=master_pwd   # Master admin password
ODOO_PROXY_MODE=True           # Enable proxy mode for HTTPS
```

#### Performance Configuration
```bash
ODOO_WORKERS=4                 # Worker processes (CPU cores)
ODOO_MAX_CRON_THREADS=2        # Cron threads
ODOO_LIMIT_MEMORY_SOFT=2147483648   # Soft memory limit (2GB)
ODOO_LIMIT_MEMORY_HARD=2684354560   # Hard memory limit (2.5GB)
```

#### SaaS Features
```bash
ODOO_AUTO_BACKUP=true          # Enable automated backups
ODOO_METRICS_ENABLED=true      # Enable Prometheus metrics
BACKUP_RETENTION_DAYS=7        # Backup retention (days)
```

#### Email Configuration (Optional)
```bash
ODOO_SMTP_SERVER=smtp.gmail.com
ODOO_SMTP_PORT=587
ODOO_SMTP_SSL=False
ODOO_SMTP_USER=noreply@example.com
ODOO_SMTP_PASSWORD=app_password
```

#### Redis Session Store (Optional)
```bash
ODOO_ENABLE_REDIS=True
ODOO_REDIS_HOST=redis
ODOO_REDIS_PORT=6379
ODOO_REDIS_DBINDEX=1
ODOO_REDIS_PASSWORD=redis_secret
```

#### S3 Backup Configuration (Optional)
```bash
AWS_S3_BUCKET=my-odoo-backups
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
```

---

## 🐳 Docker Compose Example

### Single Tenant Setup
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo_password
    volumes:
      - postgres-data:/var/lib/postgresql/data

  odoo:
    image: insightpulse-odoo:19.0-saas
    depends_on:
      - postgres
    ports:
      - "8069:8069"
      - "9090:9090"
    environment:
      ODOO_DB_HOST: postgres
      ODOO_DB_USER: odoo
      ODOO_DB_PASSWORD: odoo_password
      ODOO_DB_NAME: odoo_production
      ODOO_ADMIN_PASSWD: admin_master_password
      ODOO_METRICS_ENABLED: "true"
    volumes:
      - odoo-data:/var/lib/odoo
      - odoo-addons:/mnt/extra-addons
      - odoo-backups:/mnt/backups

volumes:
  postgres-data:
  odoo-data:
  odoo-addons:
  odoo-backups:
```

### Multi-Tenant SaaS Setup
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo_password
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass redis_password

  odoo:
    image: insightpulse-odoo:19.0-saas
    depends_on:
      - postgres
      - redis
    ports:
      - "8069:8069"
      - "9090:9090"
    environment:
      # Database
      ODOO_DB_HOST: postgres
      ODOO_DB_USER: odoo
      ODOO_DB_PASSWORD: odoo_password

      # Multi-tenancy
      ODOO_DB_FILTER: "^%d$"
      ODOO_LIST_DB: "False"

      # Security
      ODOO_ADMIN_PASSWD: admin_master_password
      ODOO_PROXY_MODE: "True"

      # Performance
      ODOO_WORKERS: 4

      # SaaS Features
      ODOO_AUTO_BACKUP: "true"
      ODOO_METRICS_ENABLED: "true"
      BACKUP_RETENTION_DAYS: 7

      # Redis Session Store
      ODOO_ENABLE_REDIS: "True"
      ODOO_REDIS_HOST: redis
      ODOO_REDIS_PASSWORD: redis_password

      # S3 Backups
      AWS_S3_BUCKET: my-odoo-backups
      AWS_ACCESS_KEY_ID: your_key
      AWS_SECRET_ACCESS_KEY: your_secret

    volumes:
      - odoo-data:/var/lib/odoo
      - odoo-addons:/mnt/extra-addons
      - odoo-backups:/mnt/backups

volumes:
  postgres-data:
  odoo-data:
  odoo-addons:
  odoo-backups:
```

---

## 🔒 Security Features

### Non-Root Execution
- Container runs as `odoo` user (UID 101)
- All directories owned by `odoo:odoo`
- Proper file permissions (750 for data directories)

### Secret Management
- Passwords via environment variables (never in config files)
- Support for Docker Secrets
- S3 credentials encrypted in transit

### Network Security
- Proxy mode for HTTPS termination
- Database connection encryption support
- Redis password authentication

### Multi-Tenancy Isolation
- Database-per-tenant architecture
- Row-level security (RLS) via Odoo's access control
- No cross-tenant data leakage

---

## 📈 Performance Optimization

### Worker Configuration
```bash
# Formula: (CPU cores * 2) + 1
ODOO_WORKERS=4  # For 2-core server

# Adjust based on server resources:
# - 1 CPU core: workers=2
# - 2 CPU cores: workers=4
# - 4 CPU cores: workers=8
```

### Memory Limits
```bash
# Soft limit triggers worker recycling
ODOO_LIMIT_MEMORY_SOFT=2147483648  # 2GB per worker

# Hard limit kills worker immediately
ODOO_LIMIT_MEMORY_HARD=2684354560  # 2.5GB per worker
```

### Database Connection Pooling
```bash
# Max connections per worker
ODOO_DB_MAXCONN=64

# Adjust based on worker count:
# Total DB connections = workers * maxconn + cron_threads
# Example: 4 workers * 64 + 2 = 258 connections
```

### Redis Session Store
- Enables horizontal scaling across multiple Odoo instances
- Reduces database load for session management
- Faster session retrieval and updates

---

## 🧪 Testing

### Build Test
```bash
docker build -f Dockerfile.custom -t insightpulse-odoo:19.0-saas-test .
```

### Smoke Test
```bash
docker run --rm \
  -e ODOO_DB_HOST=postgres \
  -e ODOO_DB_USER=odoo \
  -e ODOO_DB_PASSWORD=odoo \
  insightpulse-odoo:19.0-saas-test \
  odoo --version
```

### Health Check Test
```bash
docker run -d --name odoo-test \
  -e ODOO_DB_HOST=postgres \
  -e ODOO_DB_USER=odoo \
  -e ODOO_DB_PASSWORD=odoo \
  insightpulse-odoo:19.0-saas-test

# Wait 60 seconds for startup
sleep 60

# Check health
docker exec odoo-test /usr/local/bin/health-check.sh

# Cleanup
docker rm -f odoo-test
```

---

## 🚧 Troubleshooting

### Issue: Container exits immediately
**Cause**: Missing required environment variables

**Solution**:
```bash
# Check logs
docker logs odoo-saas

# Ensure these are set:
ODOO_DB_HOST
ODOO_DB_USER
ODOO_DB_PASSWORD
ODOO_ADMIN_PASSWD
```

### Issue: Database connection fails
**Cause**: PostgreSQL not ready or incorrect credentials

**Solution**:
```bash
# Test database connectivity
docker exec odoo-saas psql -h $ODOO_DB_HOST -U $ODOO_DB_USER -c "SELECT 1"

# Check PostgreSQL logs
docker logs postgres
```

### Issue: Metrics endpoint not responding
**Cause**: Metrics not enabled or port not exposed

**Solution**:
```bash
# Enable metrics
-e ODOO_METRICS_ENABLED=true

# Expose port
-p 9090:9090

# Check metrics process
docker exec odoo-saas ps aux | grep odoo-metrics
```

### Issue: Backups not running
**Cause**: Auto-backup not enabled or S3 credentials missing

**Solution**:
```bash
# Enable auto-backup
-e ODOO_AUTO_BACKUP=true

# Verify cron job
docker exec odoo-saas crontab -l

# Manual backup test
docker exec odoo-saas /usr/local/bin/odoo-auto-backup.sh
```

---

## 📚 Related Documentation

- [Odoo 19.0 Documentation](https://www.odoo.com/documentation/19.0/)
- [OCA Development Guidelines](https://github.com/OCA/maintainer-tools)
- [Auto-Patch System Guide](./AUTO-PATCH-GUIDE.md)
- [Prometheus Metrics](https://prometheus.io/docs/introduction/overview/)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

**Generated by**: SuperClaude Framework
**Last Updated**: 2025-10-30
**Status**: ✅ Production Ready
