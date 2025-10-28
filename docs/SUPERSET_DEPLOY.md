# Superset Deployment Guide

This guide provides step-by-step instructions for deploying Apache Superset with InsightPulse Odoo.

## Overview

Apache Superset is an open-source business intelligence platform that integrates with Odoo to provide advanced analytics and visualization capabilities.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Caddy     │─────▶│   Superset   │─────▶│  Superset   │
│ (Reverse    │      │  Application │      │  Database   │
│  Proxy)     │      │   (8088)     │      │ (PostgreSQL)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Redis     │
                     │   (Cache)    │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Odoo DB     │
                     │ (Data Source)│
                     └──────────────┘
```

## Prerequisites

- Docker and Docker Compose installed
- Odoo instance running (see `deploy/odoo.bundle.yml`)
- At least 2GB RAM allocated for Superset
- PostgreSQL database access to Odoo database

## Quick Start

### 1. Configure Environment

Copy the example environment file:

```bash
cd deploy
cp superset.env.example superset.env
```

Edit `superset.env` and update the following:

```bash
# IMPORTANT: Change these values!
SUPERSET_POSTGRES_PASSWORD=your_secure_password_here
SUPERSET_SECRET_KEY=$(openssl rand -base64 42)

# Odoo Database Connection
ODOO_DB_HOST=odoo-db
ODOO_DB_PORT=5432
ODOO_DB_NAME=odoo
ODOO_DB_USER=odoo
ODOO_DB_PASSWORD=your_odoo_db_password
```

### 2. Generate Secret Key

Generate a secure secret key:

```bash
# Linux/macOS
openssl rand -base64 42

# Or use Python
python3 -c "import secrets; print(secrets.token_urlsafe(42))"
```

Add this to `SUPERSET_SECRET_KEY` in your `superset.env` file.

### 3. Start Superset Stack

```bash
# From the repository root
docker compose -f deploy/superset.compose.yml up -d
```

This will start:
- Superset application (port 8088)
- PostgreSQL database for Superset metadata
- Redis for caching and async queries

### 4. Verify Deployment

Check that all services are running:

```bash
docker compose -f deploy/superset.compose.yml ps

# Should show:
# superset        running   8088/tcp
# superset-db     running   5432/tcp
# superset-redis  running   6379/tcp
```

### 5. Access Superset

**Direct Access:**
```
http://localhost:8088
```

**Via Caddy Reverse Proxy:**
```
https://yourdomain.com/superset
```

**Default Credentials:**
- Username: `admin`
- Password: `admin` (Change this immediately!)

## Configuration

### Reverse Proxy Setup

If using Caddy, the configuration is already set in `deploy/superset_config.py`:

```python
APPLICATION_ROOT = "/superset"
ENABLE_PROXY_FIX = True
```

Ensure Caddy is configured to forward requests (see `caddy/Caddyfile`):

```caddyfile
handle_path /superset* {
    reverse_proxy superset:8088 {
        header_up X-Forwarded-Prefix /superset
    }
}
```

### Database Connection to Odoo

Superset connects to the Odoo PostgreSQL database to query data.

1. **Access Superset UI**
2. **Go to Data → Databases**
3. **Add a new database:**

   ```
   Database Name: Odoo Production
   SQLAlchemy URI: postgresql://odoo:password@odoo-db:5432/odoo
   ```

4. **Test the connection**
5. **Save the database**

### Feature Configuration

Edit `deploy/superset_config.py` to enable/disable features:

```python
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "EMBEDDABLE_CHARTS": True,
    "SCHEDULED_QUERIES": True,
    "ALERT_REPORTS": True,
}
```

## Creating Dashboards

### 1. Create a Dataset

1. Navigate to **Data → Datasets**
2. Click **+ Dataset**
3. Select:
   - Database: Odoo Production
   - Schema: public
   - Table: (choose an Odoo table, e.g., `sale_order`)
4. Click **Add**

### 2. Create a Chart

1. Navigate to **Charts**
2. Click **+ Chart**
3. Select your dataset
4. Choose a visualization type
5. Configure metrics and dimensions
6. Save the chart

### 3. Build a Dashboard

1. Navigate to **Dashboards**
2. Click **+ Dashboard**
3. Drag and drop charts onto the dashboard
4. Configure filters and layout
5. Save the dashboard

## Security Configuration

### Change Default Admin Password

```bash
docker exec -it superset superset fab reset-password --username admin
```

### Row-Level Security (RLS)

For multi-company Odoo deployments, configure RLS:

1. Navigate to **Data → Row Level Security**
2. Add a new rule:
   ```sql
   company_id = {{ current_user_id() }}
   ```

### User Management

1. **Create Users:** Settings → List Users → +
2. **Assign Roles:**
   - **Admin**: Full access
   - **Alpha**: Can create dashboards
   - **Gamma**: View-only access

## Monitoring and Maintenance

### Health Check

```bash
# Check Superset health
curl http://localhost:8088/health

# Check logs
docker logs superset
docker logs superset-db
docker logs superset-redis
```

### Backup Database

```bash
# Backup Superset metadata database
docker exec superset-db pg_dump -U superset superset > superset_backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Restore from backup
cat superset_backup_20241027.sql | docker exec -i superset-db psql -U superset superset
```

### Database Migrations

When upgrading Superset:

```bash
docker exec superset superset db upgrade
```

### Clear Cache

```bash
# Clear Redis cache
docker exec superset-redis redis-cli FLUSHALL
```

## Performance Optimization

### Caching Strategy

Edit `deploy/superset_config.py`:

```python
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 3600,  # 1 hour
}
```

### Async Queries

Enable async query execution for large datasets:

```python
FEATURE_FLAGS = {
    "GLOBAL_ASYNC_QUERIES": True,
}
```

### Database Connection Pooling

```python
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_MAX_OVERFLOW = 10
```

## Troubleshooting

### Issue: Cannot connect to Odoo database

**Solution:**
```bash
# Test database connectivity
docker exec superset psql -h odoo-db -U odoo -d odoo -c "SELECT version();"

# Check network connectivity
docker exec superset ping odoo-db
```

### Issue: 500 Internal Server Error

**Solution:**
```bash
# Check Superset logs
docker logs superset

# Check if secret key is set
docker exec superset printenv SUPERSET_SECRET_KEY

# Verify configuration
docker exec superset superset check-config
```

### Issue: Charts not loading

**Solution:**
```bash
# Clear cache
docker exec superset-redis redis-cli FLUSHALL

# Restart Superset
docker compose -f deploy/superset.compose.yml restart superset
```

### Issue: SSL/HTTPS issues behind reverse proxy

**Solution:**

Update `deploy/superset.env`:
```bash
PREFERRED_URL_SCHEME=https
WTF_CSRF_ENABLED=True
```

Ensure Caddy sends correct headers:
```caddyfile
header_up X-Forwarded-Proto {scheme}
header_up X-Forwarded-Host {host}
```

## Integration with Odoo

### Embedding Dashboards in Odoo

Use the `superset_connector` module to embed dashboards:

1. Install the module in Odoo
2. Configure Superset connection in Odoo
3. Add dashboard menu items
4. Embed using iframe integration

See [SUPERSET_INTEGRATION.md](./SUPERSET_INTEGRATION.md) for details.

### Automated Data Sync

Set up scheduled jobs to refresh data:

1. **SQL Lab → SQL Editor**
2. Create a query to refresh materialized views
3. **Save → Schedule**
4. Set cron expression (e.g., `0 */6 * * *` for every 6 hours)

## Upgrade Guide

### Upgrading Superset

```bash
# Pull latest image
docker compose -f deploy/superset.compose.yml pull

# Stop and remove old container
docker compose -f deploy/superset.compose.yml down

# Start with new image
docker compose -f deploy/superset.compose.yml up -d

# Run database migrations
docker exec superset superset db upgrade

# Clear cache
docker exec superset-redis redis-cli FLUSHALL
```

## Production Checklist

- [ ] Strong admin password set
- [ ] Secret key generated and stored securely
- [ ] Database backups configured
- [ ] SSL/HTTPS enabled via Caddy
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up
- [ ] User accounts created with appropriate roles
- [ ] Row-level security configured for multi-company
- [ ] Cache configured for performance
- [ ] Health checks validated

## References

- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [Superset Configuration Reference](https://superset.apache.org/docs/installation/configuring-superset)
- [Odoo Integration Guide](./SUPERSET_INTEGRATION.md)
- [Domain Configuration](./DOMAIN_CONFIGURATION.md)
