# InsightPulse Infrastructure Map

**Last Updated**: November 2, 2025
**Environment**: Production
**Primary Platform**: DigitalOcean App Platform

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   DigitalOcean App Platform                      │
│                     Region: SGP1 (Singapore)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐ │
│  │  pulse-hub-web       │  │  superset-analytics              │ │
│  │  ─────────────       │  │  ──────────────────              │ │
│  │  Status: ✅ Healthy  │  │  Status: ⚠️ Configured          │ │
│  │  Cost: $5/month      │  │  Cost: $27/month                 │ │
│  │                      │  │                                  │ │
│  │  Components:         │  │  Components:                     │ │
│  │  • pulse-hub-api     │  │  • superset-web (basic-xs)       │ │
│  │    (web service)     │  │  • superset-worker (basic-xxs)   │ │
│  │  • pulse-hub         │  │  • superset-beat (basic-xxs)     │ │
│  │    (static site)     │  │  • redis (basic-xxs)             │ │
│  │                      │  │                                  │ │
│  │  Routes:             │  │  Routes:                         │ │
│  │  • /                 │  │  • /superset                     │ │
│  │  • /webhook          │  │  • /health                       │ │
│  │  • /health           │  │                                  │ │
│  │                      │  │  Database:                       │ │
│  │  Repository:         │  │  • Supabase PostgreSQL          │ │
│  │  jgtolentino/        │  │    (metadata storage)            │ │
│  │  insightpulse-odoo   │  │                                  │ │
│  │  Branch: main        │  │  Repository:                     │ │
│  │                      │  │  jgtolentino/                    │ │
│  │  Auto-Deploy: ✅     │  │  insightpulse-odoo               │ │
│  │                      │  │  Branch: main                    │ │
│  │  Latest Deploy:      │  │                                  │ │
│  │  ad3439d (Nov 01)    │  │  Auto-Deploy: ✅                │ │
│  └──────────────────────┘  └──────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  pulser-hub-mcp (mentioned in report)                    │   │
│  │  ──────────────────                                      │   │
│  │  Status: ⚠️ Needs verification                           │   │
│  │  Cost: $5/month (estimated)                              │   │
│  │                                                            │   │
│  │  Note: Not visible in provided dashboard view            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                              ↓ ↓ ↓

┌─────────────────────────────────────────────────────────────────┐
│                    External Dependencies                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Supabase (PostgreSQL Database)                          │   │
│  │  ──────────                                              │   │
│  │  Project: spdtwktxdalcfigzeqrz                           │   │
│  │  Region: US East 1 (AWS)                                 │   │
│  │  Endpoint: aws-1-us-east-1.pooler.supabase.com:6543     │   │
│  │                                                            │   │
│  │  Usage:                                                    │   │
│  │  • Superset metadata storage                             │   │
│  │  • Connection pooling enabled                            │   │
│  │  • SSL required                                           │   │
│  │                                                            │   │
│  │  Cost: Free tier (up to 500MB)                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  GitHub                                                   │   │
│  │  ──────                                                   │   │
│  │  Repository: jgtolentino/insightpulse-odoo               │   │
│  │  Integration: GitHub Actions → DigitalOcean App Platform │   │
│  │  Auto-deploy: Enabled on push to main                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Application Inventory

### 1. pulse-hub-web
**Platform**: DigitalOcean App Platform
**Status**: ✅ Healthy
**Region**: SGP1 (Singapore)
**URL**: https://pulse-hub-web-an645.ondigitalocean.app
**Monthly Cost**: **$5**

#### Components
| Component | Type | Instances | CPU | RAM | Status |
|-----------|------|-----------|-----|-----|--------|
| pulse-hub-api | Web Service | 1 | 2% | 18% | ✅ Running |
| pulse-hub | Static Site | 1 | - | - | ✅ Running |

#### Configuration
- **Stack**: Ubuntu 22.04
- **Buildpacks**: Custom Build Command, Procfile, Node.js
- **Routes**: `/`, `/webhook`, `/health`
- **Static IPs**: 162.159.140.98, 172.66.0.96
- **Repository**: `jgtolentino/insightpulse-odoo` (main branch)
- **Auto-Deploy**: ✅ Enabled
- **Latest Deployment**: ad3439d (Nov 01, 2025, 2m 51s build)

---

### 2. superset-analytics
**Platform**: DigitalOcean App Platform
**Status**: ⚠️ Configured (awaiting deployment)
**Region**: SGP (Singapore)
**URL**: http://insightpulseai.net/superset
**Monthly Cost**: **$27** (recommended) or **$20** (budget)

#### Components
| Component | Type | Instance Size | Cost | Purpose |
|-----------|------|---------------|------|---------|
| superset-web | Web Service | basic-xs | $12/mo | Main web interface (Gunicorn) |
| superset-worker | Worker | basic-xxs | $5/mo | Celery worker (async queries) |
| superset-beat | Worker | basic-xxs | $5/mo | Celery scheduler (cron tasks) |
| redis | Worker | basic-xxs | $5/mo | Cache & message broker |

#### Configuration
- **Dockerfile**: `docker/superset/Dockerfile`
- **App Spec**: `infra/superset/superset-app.yaml`
- **Config**: `config/superset/superset_config_production.py`
- **Port**: 8088
- **Health Check**: `/health` (300s initial delay, 30s period)
- **Database**: Supabase PostgreSQL (aws-1-us-east-1.pooler.supabase.com:6543)
- **Repository**: `jgtolentino/insightpulse-odoo` (main branch)
- **Auto-Deploy**: ✅ Enabled

#### Features
- ✅ Production-ready with security hardening
- ✅ Async workers (gevent, 1000 connections)
- ✅ Redis caching (data, thumbnails, results)
- ✅ Connection pooling (10 pool, 20 overflow)
- ✅ OWASP Top 10 compliance
- ✅ Automated backups (via Supabase)

#### Deployment Status
- **Spec Created**: ✅ Yes
- **Docker Image**: ✅ Ready
- **Configuration**: ✅ Complete
- **Secrets**: ✅ Configured in spec
- **Deployed**: ⚠️ Pending (awaiting `doctl apps create`)

---

### 3. pulser-hub-mcp
**Platform**: DigitalOcean App Platform
**Status**: ⚠️ Mentioned but not verified
**Monthly Cost**: **$5** (estimated)

#### Notes
- Mentioned in completion report as one of 3 canonical apps
- Not visible in provided dashboard view
- Likely needs restart (per completion report)
- Requires full dashboard access or doctl to verify

---

## 💰 Cost Summary

| Application | Monthly Cost | Status |
|-------------|--------------|--------|
| pulse-hub-web | $5 | ✅ Running |
| superset-analytics | $27 (or $20 budget) | ⚠️ Configured |
| pulser-hub-mcp | $5 (estimated) | ⚠️ Unverified |
| **Supabase PostgreSQL** | Free tier | ✅ Active |
| **Total (if all deployed)** | **$37-42/month** | - |
| **Current (verified only)** | **$5/month** | - |

### Cost Optimization Options

**Superset Budget Mode** ($20/month instead of $27/month):
- Change all services to `basic-xxs` (512MB RAM, 1 vCPU)
- Total: 4 services × $5 = $20/month
- Trade-off: Reduced performance for high traffic

---

## 🔧 Deployment Architecture

### Choice: DigitalOcean App Platform (NOT Kubernetes or Droplets)

**Why App Platform?**
- ✅ Fully managed (no server maintenance)
- ✅ Auto-scaling and health checks
- ✅ Built-in CI/CD with GitHub integration
- ✅ Lower cost than Kubernetes ($5/service vs $12+ for cluster)
- ✅ Simpler than managing Droplets
- ✅ Includes SSL, load balancing, monitoring

**Why NOT Kubernetes?**
- ❌ Higher cost (minimum $12/month for cluster + node costs)
- ❌ More complex to manage
- ❌ Overkill for current scale (3 apps)
- ❌ No Kubernetes configs found in codebase

**Why NOT Droplets?**
- ❌ Manual server management required
- ❌ Need to configure load balancing, SSL, monitoring separately
- ❌ Higher maintenance overhead
- ❌ No auto-scaling
- ❌ No Droplet configs found in codebase

---

## 📂 Configuration Files

### Superset Deployment Files
```
infra/superset/
├── superset-app.yaml         # DigitalOcean App Platform spec
├── superset-single.yaml      # Alternative single-service deployment
└── superset-official.yaml    # Official Superset configuration

config/superset/
└── superset_config_production.py  # Production configuration

docker/superset/
├── Dockerfile                # Production Docker image
├── Dockerfile.single         # Single-service variant
├── entrypoint.sh             # Initialization script
├── entrypoint-single.sh      # Single-service entrypoint
└── supervisord.conf          # Process management

deploy/superset/
├── deploy.sh                 # Automated deployment script
├── traefik.yml               # Reverse proxy configuration
└── superset.compose.yml      # Docker Compose (local dev)

docs/superset/
├── README.md                 # Project overview
├── DEPLOYMENT_GUIDE.md       # Deployment instructions
├── SUPERCLAUDE_DEPLOYMENT_SUMMARY.md  # Deployment summary
└── CREDENTIALS.md            # Access credentials

security/superset/
└── secrets.env.example       # Security configuration template
```

### Infrastructure Status
```
infra/status.yaml             # Infrastructure status tracking
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions → DigitalOcean App Platform

**Trigger**: Push to `main` branch
**Flow**:
```
1. Developer pushes to main branch
   ↓
2. GitHub Actions workflow triggered
   ↓
3. DigitalOcean App Platform detects push
   ↓
4. Remote Docker build (using Dockerfile in repo)
   ↓
5. Health check validation
   ↓
6. Deploy to production (zero-downtime)
   ↓
7. Post-deployment verification
```

**Workflows**:
- ✅ `quick-ci.yml` - Fast PR validation (linting, formatting)
- 🔇 `parity.yml.disabled` - Disabled to reduce noise
- 🔇 `oca-fetch-test.yml.disabled` - Disabled to reduce noise
- 🔇 `quality-gate.yml.disabled` - Disabled to reduce noise
- 🔇 `odoo-module-tools.yml.disabled` - Disabled to reduce noise

---

## 🔐 Security Configuration

### Superset Security Features
- ✅ Strong SECRET_KEY (42 characters)
- ✅ HTTPS enforcement
- ✅ Content Security Policy (CSP)
- ✅ HTTP Strict Transport Security (HSTS)
- ✅ Rate limiting (100 req/s, burst 200)
- ✅ Database SSL required
- ✅ Secrets managed via DigitalOcean environment variables
- ✅ Row Level Security ready

### Database Security
- ✅ Supabase PostgreSQL with SSL
- ✅ Connection pooling (reduces connection overhead)
- ✅ Environment-based credentials
- ✅ Automated backups (7 days free tier, 30 days Pro)

---

## 📡 Network Configuration

### Public Endpoints

| Service | URL | Type | Status |
|---------|-----|------|--------|
| pulse-hub-web | https://pulse-hub-web-an645.ondigitalocean.app | Web + API | ✅ Live |
| superset (planned) | http://insightpulseai.net/superset | BI Dashboard | ⚠️ Pending |

### Static IPs (pulse-hub-web)
- 162.159.140.98
- 172.66.0.96

### DNS Configuration
- **Domain**: insightpulseai.net
- **Provider**: (Not specified in codebase)
- **Current**: Direct DO App Platform URLs
- **Planned**: Custom domain with Traefik reverse proxy for path routing

---

## 🚀 Deployment Commands

### Deploy Superset
```bash
# Automated deployment (recommended)
./deploy/superset/deploy.sh

# Manual deployment
doctl apps create --spec infra/superset/superset-app.yaml
```

### Check App Status
```bash
# List all apps
doctl apps list

# Get specific app details
doctl apps get <APP_ID>

# View logs
doctl apps logs <APP_ID> --follow
```

### Update App
```bash
# Update from spec
doctl apps update <APP_ID> --spec infra/superset/superset-app.yaml

# Create new deployment
doctl apps create-deployment <APP_ID> --force-rebuild
```

---

## 📈 Monitoring & Observability

### DigitalOcean App Platform Insights
- ✅ CPU usage
- ✅ Memory usage
- ✅ Request throughput
- ✅ Response times
- ✅ Deployment history
- ✅ Build logs

### Health Checks
- **pulse-hub-web**: `/health` (responding HTTP 200)
- **superset-analytics**: `/health` (configured, 300s initial delay)

### Alerting
- ⚠️ Pending: Email alerts for deployment failures
- ⚠️ Pending: Slack notifications for app health

---

## 🎯 Next Steps

### Immediate
1. ✅ Verify pulse-hub-web is healthy
2. ⚠️ Deploy superset-analytics using deployment script
3. ⚠️ Verify pulser-hub-mcp status (requires doctl or dashboard access)
4. ⚠️ Restart pulser-hub-mcp if needed

### Short-term
1. Setup Traefik reverse proxy for `/superset` path routing
2. Configure custom domain DNS
3. Test Superset OAuth flow
4. Create Superset database connections
5. Setup monitoring and alerting

### Medium-term
1. Monitor costs and optimize instance sizes
2. Configure automated backups
3. Setup staging environment
4. Implement blue-green deployments
5. Add application performance monitoring (APM)

---

## 🤔 Questions & Verification Needs

### Unverified Items
- ❓ Does `pulser-hub-mcp` exist and what is its status?
- ❓ Is `superset-analytics` deployed or just configured?
- ❓ Are there any other apps in the DigitalOcean account?
- ❓ What is the actual total monthly DigitalOcean bill?

### To Verify
Run these commands with `doctl`:
```bash
# List all apps
doctl apps list

# Check superset status
doctl apps list | grep superset

# Verify total count
doctl apps list --format Name,Status | wc -l
```

---

**Infrastructure Map Status**: ✅ Complete (based on available data)
**Last Verified**: November 2, 2025
**Next Review**: After deploying superset-analytics
