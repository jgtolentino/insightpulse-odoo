# Docker Compose Guide

Docker Compose setup for InsightPulse Odoo platform.

## Services Overview

```yaml
services:
  odoo:           # Odoo CE 19 ERP
  postgres-odoo:  # Odoo database
  supabase-db:    # Supabase PostgreSQL
  superset:       # Apache Superset analytics
```

## Quick Start

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f odoo

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build
```

## Service Details

### Odoo Service
- **Image**: Custom build from Dockerfile
- **Port**: 8069 (host) → 8069 (container)
- **Volumes**:
  - ./odoo/addons:/opt/odoo/custom/addons
  - ./oca:/opt/odoo/oca
- **Environment**:
  - POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- **Depends on**: postgres-odoo

### PostgreSQL Service
- **Image**: postgres:15
- **Port**: 5432 (internal only)
- **Volumes**:
  - postgres-data:/var/lib/postgresql/data
- **Environment**:
  - POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

### Supabase Service
- **Image**: supabase/postgres
- **Port**: 5433 (host) → 5432 (container)
- **Volumes**:
  - supabase-data:/var/lib/postgresql/data
  - ./supabase/schema:/docker-entrypoint-initdb.d

### Superset Service
- **Image**: apache/superset:latest
- **Port**: 8088 (host) → 8088 (container)
- **Volumes**:
  - ./apps/superset/dashboards:/app/dashboards
- **Environment**:
  - SUPERSET_SECRET_KEY

## Development Workflow

```bash
# 1. Start services
docker compose up -d

# 2. Access Odoo
open http://localhost:8069

# 3. Make code changes
# Edit files in odoo/addons/

# 4. Restart Odoo to apply changes
docker compose restart odoo

# 5. View logs
docker compose logs -f odoo
```

## Production Differences

**Development** (docker-compose.yml):
- Exposed ports for debugging
- Volume mounts for live code reload
- Debug mode enabled

**Production** (DigitalOcean):
- Nginx reverse proxy
- HTTPS with Let's Encrypt
- Environment variables from secrets
- Health checks and auto-restart
- No volume mounts (baked into image)

## Troubleshooting

**Odoo won't start**:
```bash
# Check logs
docker compose logs odoo

# Common issue: database not ready
docker compose restart odoo
```

**Port conflicts**:
```bash
# Check what's using port 8069
lsof -i :8069

# Kill the process or change port in docker-compose.yml
```

**Permission issues**:
```bash
# Fix ownership
sudo chown -R $(whoami):$(whoami) odoo/addons/
```

## References

- [Getting Started](../getting-started.md)
- [Architecture](../architecture.md)
- [Deployment Guide](../deployments/overview.md)
