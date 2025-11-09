# Deployment Overview

Deployment architecture and workflows for InsightPulse Odoo platform.

## Deployment Architecture

```
GitHub Repository
    ├── Push to main
    │   ├── .github/workflows/cd-odoo-prod.yml
    │   └── scripts/deploy/deploy-all.sh
    │
    ├── DigitalOcean Droplets
    │   ├── ipai-odoo-erp (SFO2)
    │   │   └── 165.227.10.178
    │   └── ocr-service-droplet (SGP1)
    │       └── 188.166.237.231
    │
    └── DigitalOcean App Platform
        ├── odoo-saas-platform
        ├── superset-analytics
        └── mcp-coordinator
```

## Deployment Environments

### Development
- **Entrypoint**: `make dev` or `docker compose up -d`
- **Domain**: localhost / 127.0.0.1
- **Compose**: docker-compose.yml
- **Purpose**: Local development and testing

### Production
- **Provider**: DigitalOcean
- **CD**: GitHub Actions → .github/workflows/cd-odoo-prod.yml
- **Manual**: scripts/deploy/deploy-all.sh
- **Domains**: erp.insightpulseai.net, superset.insightpulseai.net, etc.

## Production Droplets

### 1. ipai-odoo-erp (SFO2)
- **IP**: 165.227.10.178
- **Region**: San Francisco 2 (SFO2)
- **Role**: ERP core (Odoo CE 19)
- **Services**: Odoo, PostgreSQL, Nginx
- **URL**: https://erp.insightpulseai.net

### 2. ocr-service-droplet (SGP1)
- **IP**: 188.166.237.231
- **Region**: Singapore 1 (SGP1)
- **Role**: OCR service
- **Services**: PaddleOCR, Document processing
- **Purpose**: Expense receipt OCR automation

## App Platform Apps

### 1. odoo-saas-platform
- **Type**: Web service
- **Framework**: Odoo CE 19
- **Purpose**: Multi-tenant SaaS platform
- **URL**: Managed by App Platform

### 2. superset-analytics
- **Type**: Web service
- **Framework**: Apache Superset
- **Purpose**: BI dashboards (Tableau alternative)
- **URL**: https://superset.insightpulseai.net

### 3. mcp-coordinator
- **Type**: API service
- **Framework**: Custom MCP server
- **Purpose**: AI agent coordination
- **URL**: https://mcp.insightpulseai.net

## Deployment Workflow

### Continuous Deployment (CD)

**Trigger**: Push to main branch

**Paths**:
- odoo/**
- scripts/deploy/**
- docker-compose*.yml

**Steps**:
1. GitHub Actions workflow triggers (.github/workflows/cd-odoo-prod.yml)
2. Build Docker image with production config
3. Deploy to DigitalOcean droplet via scripts/deploy/deploy-all.sh
4. Health checks and smoke tests
5. Rollback on failure
6. Notify on success/failure

### Manual Deployment

```bash
# Deploy all services
scripts/deploy/deploy-all.sh

# Deploy specific service
scripts/deploy/deploy-odoo.sh
scripts/deploy/deploy-superset.sh
```

## Deployment Scripts

### deploy-all.sh
- **Purpose**: Deploy all services in correct order
- **Order**: Database → Odoo → Superset → MCP
- **Rollback**: Automatic on failure

### deploy-odoo.sh
- **Purpose**: Deploy Odoo CE 19 to production
- **Steps**:
  1. SSH to droplet
  2. Pull latest code
  3. Build Docker image
  4. Stop old container
  5. Start new container
  6. Run health checks

## Health Checks

**Odoo**:
```bash
curl -sf https://erp.insightpulseai.net/web/health
```

**Superset**:
```bash
curl -sf https://superset.insightpulseai.net/health
```

**MCP**:
```bash
curl -sf https://mcp.insightpulseai.net/health
```

## Rollback Procedure

**Automatic Rollback**:
- Triggered on health check failure
- Reverts to previous Docker image
- Notifies via GitHub Actions

**Manual Rollback**:
```bash
# SSH to droplet
ssh root@165.227.10.178

# List Docker images
docker images

# Start previous image
docker run -d --name odoo <previous-image-id>
```

## Monitoring

**Logs**:
```bash
# Odoo logs
ssh root@165.227.10.178 "docker logs -f odoo"

# Superset logs
doctl apps logs superset-analytics --follow
```

**Metrics**:
- DigitalOcean Monitoring dashboard
- Supabase metrics (database performance)
- GitHub Actions workflow status

## Security

**Secrets Management**:
- GitHub Secrets for production credentials
- Environment variables on droplets
- Never commit secrets to repository

**SSL/TLS**:
- Let's Encrypt for all HTTPS endpoints
- Auto-renewal via Nginx
- Force HTTPS redirect

**Firewall**:
- UFW on droplets
- Allow: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Deny: All other ports

## References

- [DigitalOcean Deployment Guide](digitalocean.md) - Detailed DO setup
- [Hosting Policy](../guides/hosting-policy.md) - Deployment policy
- [CI/CD Workflows](../guides/workflows-ci-cd.md) - GitHub Actions
- [Architecture](../architecture.md) - System architecture

## Next Steps

1. Review [DigitalOcean setup](digitalocean.md) for detailed instructions
2. Configure [GitHub Secrets](../guides/workflows-ci-cd.md#github-secrets)
3. Test [deployment locally](../guides/docker-compose.md) first
4. Monitor [CI/CD workflows](../guides/workflows-ci-cd.md)
