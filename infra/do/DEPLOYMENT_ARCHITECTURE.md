# DigitalOcean App Platform Deployment Architecture

## Overview
This document provides the complete deployment architecture for the InsightPulse Odoo 19.0 SaaS platform on DigitalOcean App Platform.

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    DigitalOcean App Platform                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐  ┌───────────┐ │
│  │  Odoo SaaS Platform│  │ Superset Analytics │  │ MCP Hub   │ │
│  │  ────────────────  │  │  ────────────────  │  │ ───────── │ │
│  │  odoo-web          │  │  superset-web      │  │ mcp-hub   │ │
│  │  (basic-xxs)       │  │  (basic-xs)        │  │(basic-xxs)│ │
│  │  $5/month          │  │  $12/month         │  │ $5/month  │ │
│  │                    │  │                    │  │           │ │
│  │  Custom Docker     │  │  superset-worker   │  │ FastAPI   │ │
│  │  Dockerfile.custom │  │  (basic-xxs)       │  │ Service   │ │
│  │                    │  │  $5/month          │  │           │ │
│  │  Port: 8069        │  │                    │  │Port: 8001 │ │
│  │                    │  │  superset-beat     │  │           │ │
│  │  Health: /web/health│ │  (basic-xxs)       │  │Health:    │ │
│  │                    │  │  $5/month          │  │  /health  │ │
│  │                    │  │                    │  │           │ │
│  │                    │  │  redis             │  │           │ │
│  │                    │  │  (basic-xxs)       │  │           │ │
│  │                    │  │  $5/month          │  │           │ │
│  └────────────────────┘  └────────────────────┘  └───────────┘ │
│           │                        │                    │       │
└───────────┼────────────────────────┼────────────────────┼───────┘
            │                        │                    │
            ▼                        ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Supabase PostgreSQL                           │
│  ─────────────────────────────────────────────────────────      │
│  Host: aws-1-us-east-1.pooler.supabase.com                      │
│  Port: 6543 (connection pooler)                                 │
│  Database: postgres                                              │
│  User: postgres.spdtwktxdalcfigzeqrz                            │
│                                                                  │
│  - Odoo metadata & application data                             │
│  - Superset metadata (dashboards, charts, users)                │
│  - MCP coordinator state                                        │
│  - Connection pooling for 200+ concurrent connections           │
└─────────────────────────────────────────────────────────────────┘
```

## Services Overview

### 1. Odoo SaaS Platform (`odoo-saas-platform`)
- **Spec File**: `/workspaces/insightpulse-odoo/infra/do/odoo-saas-platform.yaml`
- **Docker Image**: Custom hardened image (`Dockerfile.custom`)
- **Instance Size**: basic-xxs (512MB RAM, 1 vCPU)
- **Cost**: $5/month
- **Region**: Singapore (sgp)
- **Features**:
  - Multi-tenancy support
  - Auto-backup (enabled)
  - Prometheus metrics (port 9090)
  - Health monitoring
  - OCA compliance
  - Security hardening

### 2. Apache Superset Analytics (`superset-analytics`)
- **Spec File**: `/workspaces/insightpulse-odoo/infra/superset/superset-app.yaml`
- **Architecture**: 4-service deployment
  - **superset-web**: UI and API service (basic-xs, $12/month)
  - **superset-worker**: Celery worker for async queries (basic-xxs, $5/month)
  - **superset-beat**: Celery scheduler (basic-xxs, $5/month)
  - **redis**: Message broker and cache (basic-xxs, $5/month)
- **Total Cost**: $27/month
- **Region**: Singapore (sgp)
- **Features**:
  - Production-grade analytics
  - Async query processing
  - Scheduled reports and alerts
  - Redis caching
  - Supabase PostgreSQL metadata storage

### 3. MCP Coordinator (`mcp-coordinator`)
- **Spec File**: `/workspaces/insightpulse-odoo/infra/do/mcp-coordinator.yaml`
- **Service**: FastAPI orchestration hub
- **Instance Size**: basic-xxs (512MB RAM, 1 vCPU)
- **Cost**: $5/month
- **Region**: Singapore (sgp)
- **Features**:
  - Multi-agent orchestration
  - DigitalOcean Gradient AI integration
  - GitHub integration
  - Odoo/Superset/Supabase coordination
  - Model Context Protocol (MCP) API

## Monthly Cost Breakdown

| Service | Component | Instance Size | RAM | vCPU | Cost/Month |
|---------|-----------|--------------|-----|------|------------|
| **Odoo SaaS** | odoo-web | basic-xxs | 512MB | 1 | $5.00 |
| **Superset** | superset-web | basic-xs | 1GB | 1 | $12.00 |
| **Superset** | superset-worker | basic-xxs | 512MB | 1 | $5.00 |
| **Superset** | superset-beat | basic-xxs | 512MB | 1 | $5.00 |
| **Superset** | redis | basic-xxs | 512MB | 1 | $5.00 |
| **MCP** | mcp-hub | basic-xxs | 512MB | 1 | $5.00 |
| **TOTAL** | | | | | **$37.00** |

### External Dependencies (Not Billed via DO)
- **Supabase PostgreSQL**: Free tier (500MB database, 2GB storage)
- **DigitalOcean Gradient AI**: Pay-per-use (usage-based billing)
- **GitHub**: Free (public repository)

## DNS Configuration

Configure the following DNS records in your domain registrar (insightpulseai.net):

### Required DNS Records

| Type | Hostname | Value | TTL | Purpose |
|------|----------|-------|-----|---------|
| **CNAME** | `mcp` | `mcp-coordinator-<app-id>.ondigitalocean.app` | 3600 | MCP Coordinator |
| **CNAME** | `superset` | `superset-analytics-<app-id>.ondigitalocean.app` | 3600 | Superset Analytics |
| **A** or **CNAME** | `@` or `www` | (Odoo app URL or custom domain) | 3600 | Main Odoo platform |

### Domains After Deployment

1. **MCP Coordinator**: https://mcp.insightpulseai.net
2. **Superset Analytics**: https://superset.insightpulseai.net
3. **Odoo SaaS Platform**: https://odoo.insightpulseai.net (or default DO URL)

### SSL/TLS Certificates
- **Auto-provisioned**: DigitalOcean App Platform automatically provisions Let's Encrypt SSL certificates
- **HTTPS**: Enabled by default for all custom domains
- **Renewal**: Automatic

## Environment Variables & Secrets

### Secrets to Configure in DigitalOcean Dashboard

#### Odoo SaaS Platform
```bash
# Database
ODOO_DB_PASSWORD=<supabase_password>

# Admin
ODOO_ADMIN_PASSWORD=<secure_random_password>

# AI (optional)
DO_AGENT_KEY=<do_gradient_agent_key>
DO_MODEL_ACCESS_KEY=<do_gradient_model_key>
```

#### Superset Analytics
```bash
# Database
DATABASE_PASSWORD=<supabase_password>

# Security
SUPERSET_SECRET_KEY=<generated_via_openssl_rand_base64_42>
SUPERSET_ADMIN_PASSWORD=<superset_admin_password>
```

#### MCP Coordinator
```bash
# Integrations
GITHUB_TOKEN=<github_personal_access_token>
SUPABASE_SERVICE_ROLE_KEY=<supabase_service_role_key>
DO_API_TOKEN=<digitalocean_api_token>

# Service passwords
SUPERSET_PASSWORD=<superset_admin_password>
ODOO_ADMIN_PASSWORD=<odoo_admin_password>

# AI
DO_AGENT_KEY=<do_gradient_agent_key>
DO_MODEL_ACCESS_KEY=<do_gradient_model_key>

# Optional
NOTION_TOKEN=<notion_integration_token>
```

### Generate Secrets

```bash
# Generate secure passwords
openssl rand -base64 32

# Generate Superset secret key
openssl rand -base64 42

# GitHub token: https://github.com/settings/tokens
# Supabase keys: https://app.supabase.com/project/<project-id>/settings/api
# DO API token: https://cloud.digitalocean.com/account/api/tokens
```

## Health Check Endpoints

| Service | Endpoint | Initial Delay | Interval | Timeout |
|---------|----------|--------------|----------|---------|
| Odoo | `/web/health` | 180s | 30s | 10s |
| Superset | `/health` | 300s | 30s | 10s |
| MCP Hub | `/health` | 20s | 15s | 5s |

## Deployment Commands

### Initial Deployment

```bash
# 1. Deploy Odoo SaaS Platform
doctl apps create --spec infra/do/odoo-saas-platform.yaml

# 2. Deploy Superset Analytics
doctl apps create --spec infra/superset/superset-app.yaml

# 3. Deploy MCP Coordinator
doctl apps create --spec infra/do/mcp-coordinator.yaml
```

### Update Existing Deployments

```bash
# Get app IDs
doctl apps list

# Update specific app
doctl apps update <APP_ID> --spec infra/do/odoo-saas-platform.yaml
doctl apps update <APP_ID> --spec infra/superset/superset-app.yaml
doctl apps update <APP_ID> --spec infra/do/mcp-coordinator.yaml
```

### View Logs

```bash
# Odoo logs
doctl apps logs <ODOO_APP_ID> --type run

# Superset logs
doctl apps logs <SUPERSET_APP_ID> --type run --component superset-web
doctl apps logs <SUPERSET_APP_ID> --type run --component superset-worker

# MCP logs
doctl apps logs <MCP_APP_ID> --type run
```

## Next Steps

### 1. Pre-Deployment Checklist
- [ ] Review all YAML specs for correctness
- [ ] Generate all required secrets
- [ ] Configure Supabase database access
- [ ] Verify GitHub repository access
- [ ] Obtain DigitalOcean API token

### 2. Deployment Phase
- [ ] Deploy Odoo SaaS Platform
- [ ] Deploy Superset Analytics
- [ ] Deploy MCP Coordinator
- [ ] Configure DNS records
- [ ] Verify SSL certificates

### 3. Post-Deployment
- [ ] Run smoke tests on all services
- [ ] Configure Superset data sources (connect to Supabase)
- [ ] Test MCP coordinator endpoints
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
- [ ] Document admin credentials securely

### 4. Testing
```bash
# Test Odoo
curl -f https://odoo.insightpulseai.net/web/health

# Test Superset
curl -f https://superset.insightpulseai.net/health

# Test MCP
curl -f https://mcp.insightpulseai.net/health
```

### 5. Monitoring
- **DigitalOcean Dashboard**: Monitor resource usage, costs, and uptime
- **Supabase Dashboard**: Monitor database performance and query logs
- **Odoo Metrics**: Prometheus endpoint at port 9090 (internal)
- **Application Logs**: Use `doctl apps logs` command

## Cost Optimization Options

### Budget Tier: $20/month
Downgrade Superset web service to basic-xxs:
- **Trade-off**: Slower UI performance under load
- **Savings**: $7/month
- **Total**: $30/month

### Minimal Tier: $10/month
Run only Odoo + MCP (disable Superset):
- **Trade-off**: No analytics dashboard
- **Savings**: $27/month
- **Total**: $10/month

### Current Production Tier: $37/month
Full analytics stack with high availability:
- **Best for**: Production workloads with analytics requirements
- **Performance**: Optimized for concurrent users

## Support & Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify Supabase connection pooler is accessible
   - Check firewall rules in Supabase dashboard
   - Validate database credentials

2. **Build Failures**
   - Check Dockerfile paths in specs
   - Verify all COPY paths exist in repository
   - Review build logs: `doctl apps logs <APP_ID> --type build`

3. **Health Check Failures**
   - Increase initial_delay_seconds if service takes longer to start
   - Check application logs for startup errors
   - Verify health endpoints are correctly implemented

4. **Custom Domain Not Working**
   - Verify DNS propagation (24-48 hours)
   - Check CNAME record points to correct DO app URL
   - Ensure domain is added in DO dashboard

### Contact
- **Support**: Use DigitalOcean support tickets
- **Documentation**: https://docs.digitalocean.com/products/app-platform/
- **Community**: https://www.digitalocean.com/community

## Architecture Decisions

### Why DigitalOcean App Platform?
1. **Simplicity**: No Kubernetes complexity
2. **Cost-effective**: $5/month entry point (vs $12/month for managed K8s)
3. **Auto-scaling**: Built-in (when needed)
4. **SSL/TLS**: Automatic Let's Encrypt certificates
5. **CI/CD**: GitHub integration with auto-deploy
6. **Monitoring**: Built-in metrics and logging

### Why Custom Docker Image?
1. **Security hardening**: Non-root user, minimal attack surface
2. **Auto-patching**: Dependency management automation
3. **OCA compliance**: Community addon compatibility
4. **SaaS features**: Multi-tenancy, backups, metrics
5. **Health monitoring**: Built-in health checks

### Why Supabase PostgreSQL?
1. **Free tier**: 500MB database, 2GB storage
2. **Connection pooling**: Handles 200+ connections
3. **Managed service**: Automated backups, updates
4. **Performance**: AWS infrastructure
5. **API access**: REST and GraphQL APIs included

### Why 3-service Superset Architecture?
1. **Scalability**: Web, worker, and scheduler can scale independently
2. **Performance**: Async query processing doesn't block UI
3. **Reliability**: Worker failures don't affect web service
4. **Best practice**: Official Superset production architecture
5. **Redis caching**: Improved query performance

## Version History
- **2025-11-03**: Initial architecture documentation
- **Services**: Odoo 19.0, Superset (latest), MCP Coordinator (FastAPI)
- **Region**: Singapore (sgp)
- **Total Cost**: $37/month
