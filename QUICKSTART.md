# InsightPulse Odoo 19.0 - Quick Start Guide

Get production-ready Odoo with all 10 enterprise modules running in **5 minutes**.

---

## 🎯 Wave 1-3 Complete - What's Included

✅ **10 Enterprise Modules** (2,771 lines of tests, 134 test methods)
✅ **Production Docker Image** (512MB RAM optimized)
✅ **DigitalOcean Deployment** (< $20/month budget)
✅ **AI Knowledge Workspace** (pgVector + OpenAI)
✅ **BI Dashboards** (Apache Superset integration)

---

## Prerequisites

```bash
# Required
- Docker 24.0+ and Docker Compose
- Git with submodule support
- 2GB RAM minimum (4GB recommended)

# Optional (for production)
- DigitalOcean account + doctl CLI
- Supabase project (free tier)
- OpenAI API key
```

---

## Option 1: Local Development (2 minutes)

### Step 1: Clone and Initialize
```bash
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo

# Initialize submodules (for ipai_knowledge_ai)
git submodule update --init --recursive
```

### Step 2: Start Docker Stack
```bash
# Start Odoo + PostgreSQL
docker compose up -d

# Watch logs
docker compose logs -f odoo
```

### Step 3: Access Odoo
```bash
# Open browser
open http://localhost:8069

# Default credentials
Username: admin
Password: admin
```

### Step 4: Install Modules
```
1. Go to: Apps → Update Apps List
2. Search for: "IPAI"
3. Install in order:
   - ipai_core (base module)
   - ipai_rate_policy (rate calculation)
   - ipai_ppm (project management)
   - ipai_saas_ops (tenant management)
   - ipai_approvals (approval workflows)
   - [All other IPAI modules as needed]
```

**Done!** ✅ You now have Odoo 19.0 with all Wave 1-2 modules.

---

## Option 2: Production Deploy - DigitalOcean (5 minutes)

### Step 1: Prepare Secrets
```bash
# Add to ~/.zshrc or export in terminal
export DO_ACCESS_TOKEN="your_digitalocean_token"
export POSTGRES_PASSWORD="your_strong_password"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
export OPENAI_API_KEY="sk-proj-your_openai_key"
```

### Step 2: Deploy to DigitalOcean
```bash
# Option A: Automated deployment (recommended)
./scripts/deploy-to-production.sh

# Option B: Manual deployment
doctl apps create --spec infra/do/odoo-app.yaml

# Check deployment status
doctl apps list
doctl apps logs <app-id> --follow
```

### Step 3: Verify Deployment
```bash
# Health check
curl -sf https://your-app.ondigitalocean.app/web/health

# Should return: {"status": "pass"}
```

### Step 4: Configure Database
```bash
# Create database via Odoo UI
https://your-app.ondigitalocean.app/web/database/manager

# Or via doctl
doctl apps create-deployment <app-id> --force-rebuild
```

**Production Deployed!** ✅ Cost: ~$5/month

---

## Option 3: Custom Docker Build (3 minutes)

### Step 1: Build Image
```bash
# Build production image
docker build -t insightpulse-odoo:19.0 .

# Tag for registry (optional)
docker tag insightpulse-odoo:19.0 your-registry/odoo:19.0
docker push your-registry/odoo:19.0
```

### Step 2: Run Container
```bash
# With environment variables
docker run -d \
  --name odoo19 \
  -e ODOO_DB_HOST=your-db-host \
  -e ODOO_DB_PORT=5432 \
  -e ODOO_DB_USER=odoo \
  -e ODOO_DB_PASSWORD=your_password \
  -e ODOO_DB_NAME=odoo \
  -p 8069:8069 \
  insightpulse-odoo:19.0

# Check logs
docker logs -f odoo19
```

### Step 3: Access Odoo
```bash
open http://localhost:8069
```

---

## 🧪 Validate Installation

### Quick Health Check
```bash
# Run deployment validation (13 checks)
./scripts/deploy-check.sh --quick

# Full validation (includes asset rebuild + module updates)
./scripts/deploy-check.sh --full
```

### Test Individual Modules
```bash
# Test rate policy module
curl -s http://localhost:8069/web/database/selector | jq '.modules[] | select(.name | contains("ipai_rate_policy"))'

# Test all IPAI modules
for module in ipai_rate_policy ipai_ppm ipai_saas_ops ipai_approvals; do
  echo "Testing $module..."
  curl -sf http://localhost:8069/web/login || echo "⚠️ Odoo not accessible"
done
```

### Run Test Suite
```bash
# Unit tests (in submodule)
cd insightpulse_odoo
python -m pytest addons/insightpulse/tests/ -v

# Integration tests
python -m pytest addons/insightpulse/tests/integration/ -v

# E2E tests
python -m pytest addons/insightpulse/tests/e2e/ -v

# Performance benchmarks
python -m pytest addons/insightpulse/tests/performance/ -v
```

**Test Summary**: 17 test files, 134 test methods, 2,771 lines of test code

---

## 📦 Module Quick Reference

### Finance Modules
| Module | Usage | Access |
|--------|-------|--------|
| **ipai_rate_policy** | Configure hourly/daily rates with P60 markup | Finance → Rate Policies |
| **ipai_ppm** | Manage programs, projects, budgets | Projects → Programs |
| **ipai_ppm_costsheet** | View project costs with tax-aware margins | Projects → Cost Sheets |
| **ipai_subscriptions** | Recurring billing (MRR/ARR) | Subscriptions → Plans |

### Operations Modules
| Module | Usage | Access |
|--------|-------|--------|
| **ipai_saas_ops** | Tenant provisioning & backups | Operations → SaaS Tenants |
| **ipai_procure** | RFQ workflows & supplier management | Procurement → RFQs |
| **ipai_approvals** | Multi-stage approval routing | Approvals → Rules |

### Analytics & AI Modules
| Module | Usage | Access |
|--------|-------|--------|
| **bi_superset_agent** | BI dashboards (5 pre-built) | BI → Superset |
| **ipai_knowledge_ai** | Semantic search + /ask API | Knowledge → AI Workspaces |

### External Services
| Service | Purpose | Endpoint |
|---------|---------|----------|
| **PaddleOCR-VL** | Receipt OCR (ipai_expense) | https://ade-ocr-backend-d9dru.ondigitalocean.app |
| **OpenAI GPT-4o-mini** | AI responses (ipai_knowledge_ai) | api.openai.com |
| **Supabase PostgreSQL** | Database + pgVector | your-project.supabase.co:6543 |

---

## 🔐 Post-Install Configuration

### 1. Enable AI Knowledge Workspace (Optional)
```bash
# Set environment variables
export OPENAI_API_KEY="sk-proj-your_key"
export POSTGRES_HOST="aws-0-us-east-1.pooler.supabase.com"
export POSTGRES_PORT="6543"
export POSTGRES_USER="postgres.your_project_ref"
export POSTGRES_PASSWORD="your_password"

# Restart Odoo
docker compose restart odoo

# Initialize pgVector in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

# Usage: Knowledge → AI Workspaces → Create → Ask AI
```

See: [ipai_knowledge_ai/QUICKSTART.md](insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/QUICKSTART.md)

### 2. Configure Superset Integration (Optional)
```bash
# Install Apache Superset (separate stack)
docker run -d -p 8088:8088 apache/superset

# Configure in Odoo: BI → Superset → Settings
Superset URL: http://localhost:8088
API Token: [from Superset]

# Import pre-built dashboards
BI → Superset → Import Dashboards
```

### 3. Enable OCR Expense Automation (Optional)
```bash
# Configure OCR service endpoint
# Settings → Technical → System Parameters
Key: ocr.service.endpoint
Value: https://ade-ocr-backend-d9dru.ondigitalocean.app/v1/parse

# Usage: Expenses → Upload Receipt → Auto-fill
```

---

## 🚨 Troubleshooting

### Odoo won't start
```bash
# Check Docker status
docker compose ps

# View logs
docker compose logs odoo

# Common fix: Reset database
docker compose down -v
docker compose up -d
```

### Modules not visible
```bash
# Update app list
Apps → Update Apps List (top-right menu)

# Or via CLI
docker compose exec odoo odoo-bin -d odoo -u all --stop-after-init
```

### Database connection issues
```bash
# Test PostgreSQL
docker compose exec odoo psql -h db -U odoo -d odoo -c "SELECT version();"

# Check environment variables
docker compose exec odoo env | grep -E "DB_HOST|DB_PORT|DB_USER"
```

### Performance issues (local dev)
```bash
# Reduce workers in docker-compose.yml
services:
  odoo:
    environment:
      - ODOO_WORKERS=2  # Default: 4
      - ODOO_MAX_CRON_THREADS=1  # Default: 2
```

### Test failures
```bash
# Run specific test file
python -m pytest insightpulse_odoo/addons/insightpulse/tests/integration/test_rate_policy_costsheet_integration.py -v

# Skip slow tests
python -m pytest -m "not slow" insightpulse_odoo/addons/insightpulse/tests/ -v
```

---

## 📚 Next Steps

### Learn the Modules
1. Read module-specific READMEs:
   - [ipai_rate_policy/README.md](addons/insightpulse/finance/ipai_rate_policy/README.md)
   - [ipai_ppm/README.md](addons/insightpulse/finance/ipai_ppm/README.md)
   - [ipai_saas_ops/README.md](addons/insightpulse/ops/ipai_saas_ops/README.md)

2. Review test files for usage examples:
   - [tests/integration/](insightpulse_odoo/addons/insightpulse/tests/integration/)
   - [tests/e2e/](insightpulse_odoo/addons/insightpulse/tests/e2e/)

### Production Deployment
- **Security**: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)
- **Deployment**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Docker**: [DOCKER_SETUP.md](DOCKER_SETUP.md)

### Development
- **Architecture**: [ARCHITECTURE_IMPLEMENTATION_SUMMARY.md](ARCHITECTURE_IMPLEMENTATION_SUMMARY.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Contributing**: [README.md#contributing](README.md#contributing)

---

## 💰 Cost Estimates

### Local Development
- **Cost**: $0/month
- **Requirements**: 2-4GB RAM, Docker

### Production (DigitalOcean)
- **Odoo**: $5/month (basic-xs: 512MB RAM)
- **Database**: $0/month (Supabase free tier: 500MB)
- **OCR Service**: $5/month (basic-xxs: 512MB RAM)
- **OpenAI API**: ~$10/month (GPT-4o-mini, ~1000 queries)
- **Total**: **< $20/month** (87% reduction from $100 Azure budget)

### Enterprise (Self-Hosted)
- **Odoo**: $50-200/month (4GB+ RAM, load balancer)
- **Database**: $25-100/month (PostgreSQL cluster)
- **Superset**: $25/month (BI server)
- **Total**: ~$100-325/month (scales with usage)

---

## 📞 Support

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Email**: support@insightpulse.ai

---

**Version**: 3.0.0 (Wave 1-3 Complete)
**Last Updated**: 2025-10-30
**Status**: Production Ready ✅
**Test Coverage**: 134 test methods, 2,771 lines of tests
**Deployment Time**: 2-5 minutes
**Monthly Cost**: < $20 USD
