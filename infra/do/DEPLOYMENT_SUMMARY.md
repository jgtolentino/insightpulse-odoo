# DigitalOcean Deployment Infrastructure - Summary

Complete deployment infrastructure created for InsightPulse Odoo 19.0 Enterprise SaaS Platform.

**Status**: ✅ Ready for deployment
**Budget**: $5/month base cost (75% under $20 target)
**Created**: 2025-10-30

---

## Files Created

### 1. Infrastructure Configuration

#### `/infra/do/odoo-saas-platform.yaml`
**Purpose**: DigitalOcean App Platform application specification

**Key Configuration**:
- **Service**: Web service (Odoo 19.0)
- **Instance**: basic-xxs (512MB RAM, 1 vCPU, $5/month)
- **Region**: Singapore (sgp)
- **Source**: GitHub repo (tbwahacker/insightpulse-odoo)
- **Auto-deploy**: Enabled on push to `main` branch
- **Health check**: `/web/health` endpoint
- **Workers**: 2 Odoo workers + 1 cron thread
- **Memory limits**: 400MB hard, 320MB soft (80% of instance)

**Environment Variables**:
- Database: Supabase connection pooler (port 6543)
- Odoo: Admin password, worker configuration
- AI: Self-hosted Ollama (Llama 3.2)

---

### 2. Docker Configuration

#### `/Dockerfile`
**Purpose**: Production-optimized Odoo 19.0 container image

**Features**:
- Base: Official `odoo:19.0` image
- Python dependencies from `requirements.txt`
- Custom addons: InsightPulse, custom, OCA modules
- Health check: `/web/health` endpoint (30s interval)
- Memory optimization: 80% of 512MB instance
- Security: Runs as `odoo` user (non-root)

**Build Process**:
- DigitalOcean App Platform builds from Dockerfile
- No local Docker required (remote builds only)
- Automatic rebuild on git push

---

### 3. CI/CD Pipeline

#### `/.github/workflows/digitalocean-deploy.yml`
**Purpose**: Automated deployment workflow

**Triggers**:
- Push to `main` branch (automatic)
- Manual trigger via GitHub Actions UI
- Path filters: `addons/`, `Dockerfile`, `requirements.txt`, `infra/do/`

**Jobs**:
1. **Validate**: Lint Python, validate manifests, check YAML syntax
2. **Deploy**: Update app spec, create deployment, wait for completion
3. **Verify**: Health check, smoke tests, deployment summary

**Duration**: ~15-20 minutes per deployment

---

### 4. Documentation

#### `/infra/do/DEPLOYMENT_GUIDE.md`
**Purpose**: Complete deployment guide with step-by-step instructions

**Contents**:
- Prerequisites and tool installation
- Step-by-step deployment process
- Post-deployment configuration
- Monitoring and maintenance
- Troubleshooting common issues
- Rollback procedures
- Scaling and upgrade paths

#### `/infra/do/DEPLOYMENT_CHECKLIST.md`
**Purpose**: Pre-deployment and post-deployment checklist

**Checklists**:
- Pre-deployment (prerequisites, config, security)
- Deployment (initial, monitoring, verification)
- Post-deployment (performance, security, monitoring)
- CI/CD activation
- Ongoing maintenance (weekly, monthly, quarterly)

#### `/infra/budget-optimization.md`
**Purpose**: Budget optimization strategies and cost projections

**Key Points**:
- **Current cost**: $5/month base (Supabase Free + DO basic-xxs)
- **Target**: $15/month (with $10 buffer for overages)
- **Savings**: 95% reduction from $100 Azure budget
- Cost breakdown and optimization strategies
- Growth projections and upgrade paths
- Monitoring and alert thresholds

#### `/infra/do/secrets-template.md`
**Purpose**: GitHub Secrets configuration guide

**Secrets Required**:
- DigitalOcean: `DO_ACCESS_TOKEN`, `DO_APP_ID`
- Supabase: `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Odoo: `ODOO_ADMIN_PASSWORD`
- Optional: `OPENAI_API_KEY` (not needed with self-hosted AI)

---

### 5. Environment Configuration

#### `/.env.example`
**Purpose**: Environment variables template

**Categories**:
- Database: Supabase connection settings
- Odoo: Configuration and resource limits
- DigitalOcean: App Platform settings
- AI: Ollama vs OpenAI configuration
- GitHub: OAuth and API tokens
- Security: Admin passwords and access control

**Usage**:
- Local development: Copy to `.env` and fill in values
- Production: Set in DigitalOcean App Platform console
- CI/CD: Set as GitHub Secrets

---

### 6. Validation Tools

#### `/scripts/validate-manifests.py`
**Purpose**: Validate Odoo module manifest files

**Checks**:
- Valid Python syntax
- Required manifest keys (name, version, category, etc.)
- Version format (X.Y.Z)
- Dependency format
- License validity
- Recommended keys

**Usage**:
```bash
python scripts/validate-manifests.py
```

**Integration**:
- CI/CD: Runs in validation job
- Pre-commit: Can be added to git hooks

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                   (insightpulse-odoo)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ git push main
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions CI/CD                       │
│  (Validate → Deploy → Verify)                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ doctl apps deploy
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            DigitalOcean App Platform (Singapore)            │
│  ┌──────────────────────────────────────────────┐          │
│  │     Odoo 19.0 Web Service (basic-xxs)        │          │
│  │  - 512MB RAM, 1 vCPU                         │          │
│  │  - 2 workers + 1 cron thread                 │          │
│  │  - Port 8069                                 │          │
│  │  - Health: /web/health                       │          │
│  └──────────────────────┬───────────────────────┘          │
└─────────────────────────┼─────────────────────────────────┘
                          │
                          │ Connection pooler (port 6543)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│           Supabase PostgreSQL (Free Tier)                   │
│  - 500MB database                                           │
│  - 2GB bandwidth                                            │
│  - Connection pooler (200+ connections)                     │
│  - Automatic daily backups                                  │
│  - RLS policies enabled                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Budget Breakdown

| Service | Tier | Monthly Cost | Details |
|---------|------|--------------|---------|
| **Supabase PostgreSQL** | Free | $0 | 500MB DB, 2GB bandwidth, pooler |
| **DigitalOcean App Platform** | basic-xxs | $5 | 512MB RAM, 1 vCPU, SGP region |
| **Self-hosted AI (Ollama)** | N/A | $0 | Llama 3.2 (no API costs) |
| **DigitalOcean Monitoring** | Included | $0 | Built-in metrics dashboard |
| **GitHub Actions** | Free | $0 | 2000 minutes/month (well under) |
| **Total Base Cost** | | **$5/month** | 75% under $20 target |
| **Buffer (overages)** | | $10/month | Traffic spikes, temporary scaling |
| **Target Budget** | | **$15/month** | Actual: $5/month achieved |

### Cost Savings vs Azure

| Component | Azure (Old) | DO + Supabase (New) | Savings |
|-----------|-------------|---------------------|---------|
| Container Registry | ACR: $5 | N/A | $5 |
| Compute | ACI: $30 | DO App: $5 | $25 |
| Database | Azure PG: $25 | Supabase: $0 | $25 |
| Document AI | Azure Doc: $20 | PaddleOCR: $0 | $20 |
| AI API | Azure OpenAI: $15 | Ollama: $0 | $15 |
| Key Vault | Azure KV: $5 | Env vars: $0 | $5 |
| **Total** | **$100/month** | **$5/month** | **$95 (95%)** |

---

## Deployment Process

### Initial Setup (One-time)

1. **Create DigitalOcean app**:
   ```bash
   doctl apps create --spec infra/do/odoo-saas-platform.yaml
   ```

2. **Configure GitHub Secrets**:
   - Add required secrets (see `infra/do/secrets-template.md`)
   - Verify with `gh secret list`

3. **First deployment**:
   ```bash
   doctl apps create-deployment [app-id] --force-rebuild
   ```

4. **Verify deployment**:
   ```bash
   curl -sf https://[app-url]/web/health
   ```

### Automated Deployments (Ongoing)

1. **Push to main branch**:
   ```bash
   git push origin main
   ```

2. **GitHub Actions automatically**:
   - Validates code (lint, manifests)
   - Updates app spec
   - Creates deployment
   - Waits for completion
   - Runs health checks
   - Smoke tests

3. **Monitor workflow**:
   ```bash
   gh run watch
   ```

### Manual Deployments (Optional)

```bash
# Trigger via GitHub Actions UI
gh workflow run digitalocean-deploy.yml

# OR via doctl directly
doctl apps update [app-id] --spec infra/do/odoo-saas-platform.yaml
doctl apps create-deployment [app-id] --force-rebuild
```

---

## Environment Variables

### Required (Production)

```bash
# Database (Supabase)
POSTGRES_HOST=aws-1-us-east-1.pooler.supabase.com
POSTGRES_PORT=6543
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[your-supabase-password]

# Odoo
ODOO_ADMIN_PASSWORD=[generated-with-openssl]
ODOO_WORKERS=2
ODOO_MAX_CRON_THREADS=1
ODOO_DB_MAXCONN=8

# Memory limits (80% of 512MB)
ODOO_LIMIT_MEMORY_HARD=419430400
ODOO_LIMIT_MEMORY_SOFT=335544320

# Timeout limits
ODOO_LIMIT_TIME_CPU=300
ODOO_LIMIT_TIME_REAL=600

# AI (self-hosted)
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Optional

```bash
# OpenAI fallback (costs apply)
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini

# GitHub integration
# GITHUB_TOKEN=github_pat_...
# GITHUB_OAUTH_CLIENT_ID=...
# GITHUB_OAUTH_CLIENT_SECRET=...
```

---

## Next Steps

### 1. Initial Deployment

Follow the deployment guide:
```bash
# 1. Authenticate with DigitalOcean
doctl auth init

# 2. Create app
doctl apps create --spec infra/do/odoo-saas-platform.yaml

# 3. Note app ID and add to GitHub secrets
gh secret set DO_APP_ID --body "[app-id]"

# 4. Configure remaining secrets (see secrets-template.md)

# 5. Deploy
doctl apps create-deployment [app-id] --force-rebuild

# 6. Monitor logs
doctl apps logs [app-id] --type run --follow

# 7. Verify deployment
curl -sf https://[app-url]/web/health
```

### 2. Configure CI/CD

```bash
# Add all GitHub secrets
gh secret set DO_ACCESS_TOKEN --body "[token]"
gh secret set POSTGRES_HOST --body "[host]"
gh secret set POSTGRES_USER --body "postgres"
gh secret set POSTGRES_PASSWORD --body "[password]"
gh secret set ODOO_ADMIN_PASSWORD --body "$(openssl rand -base64 32)"

# Push to main to trigger first automated deployment
git push origin main

# Monitor workflow
gh run watch
```

### 3. Access Odoo

```bash
# Get app URL
doctl apps get [app-id] --format DefaultIngress --no-header

# Open in browser
open https://[app-url]/web

# Create database (first time)
# Navigate to: https://[app-url]/web/database/manager
# Or use CLI:
doctl apps exec [app-id] --component odoo-web -- \
  odoo-bin -d odoo --init base --stop-after-init
```

### 4. Install Modules

1. Login to Odoo: `https://[app-url]/web`
2. Navigate to Apps menu
3. Search for "InsightPulse" or "Custom"
4. Click "Install" on your modules
5. Verify all modules loaded correctly

### 5. Configure Monitoring

```bash
# Set up billing alerts (DigitalOcean console)
# Settings > Billing > Alerts > Create Alert
# Threshold: $10/month

# Monitor database size (Supabase)
psql "$POSTGRES_URL" -c "SELECT pg_size_pretty(pg_database_size('postgres'));"

# Set up uptime monitoring (optional - Uptime Robot free tier)
# https://uptimerobot.com/
```

---

## Troubleshooting

### Common Issues

1. **Deployment timeout**:
   - Check build logs: `doctl apps logs [app-id] --type build --follow`
   - Verify Dockerfile syntax
   - Check for large files in addons/

2. **Database connection failed**:
   - Test connection: `psql "$POSTGRES_URL" -c "SELECT 1;"`
   - Verify Supabase project is active (free tier pauses after 1 week)
   - Check password is correct

3. **Health check fails**:
   - Check runtime logs: `doctl apps logs [app-id] --type run --follow`
   - Verify Odoo started successfully
   - Check memory usage isn't exceeding limits

4. **Out of memory**:
   - Reduce workers to 1
   - Lower memory limits
   - Upgrade to basic-xs ($12/month, 1GB RAM)

### Support

- **Deployment Guide**: `infra/do/DEPLOYMENT_GUIDE.md`
- **Checklist**: `infra/do/DEPLOYMENT_CHECKLIST.md`
- **DigitalOcean Docs**: https://docs.digitalocean.com/products/app-platform/
- **Supabase Docs**: https://supabase.com/docs

---

## Success Criteria

✅ **All infrastructure files created**
✅ **DigitalOcean App Platform spec validated**
✅ **CI/CD workflow configured**
✅ **Budget optimized to $5/month** (75% under target)
✅ **Documentation complete**
✅ **Validation tools created**

**Status**: Ready for deployment

**Next**: Follow deployment guide to create app and deploy
