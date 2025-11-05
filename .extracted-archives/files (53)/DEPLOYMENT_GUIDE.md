# InsightPulse AI - Production Deployment Guide

## 🏗️ Architecture Overview

```
insightpulseai.net (Squarespace DNS)
│
├── @ → Cloudflare (162.159.140.98)
│   └── Landing page / Marketing site
│
├── erp.insightpulseai.net → DigitalOcean Droplet (165.227.10.178)
│   ├── Odoo 19 ERP
│   ├── Finance SSC modules
│   ├── BIR compliance
│   └── Travel & Expense Management
│
├── mcp.insightpulseai.net → DO App Platform (pulse-hub-web-an645)
│   ├── MCP Coordinator
│   ├── OpenAPI endpoints
│   └── Skill orchestration
│
├── superset.insightpulseai.net → DO App Platform (superset-nlavf)
│   ├── Apache Superset
│   ├── Finance SSC dashboards
│   └── BIR analytics
│
└── ocr.insightpulseai.net → Cloudflare (162.159.140.98)
    ├── PaddleOCR service
    └── Receipt processing
```

## 📦 Repository Structure

```
insightpulse-odoo/
├── .github/
│   └── workflows/
│       ├── deploy-odoo.yml           # Droplet deployment
│       ├── deploy-mcp.yml            # MCP App Platform
│       ├── deploy-superset.yml       # Superset App Platform
│       ├── deploy-ocr.yml            # OCR service
│       └── integration-tests.yml     # E2E testing
│
├── services/
│   ├── odoo/
│   │   ├── Dockerfile
│   │   ├── odoo.conf
│   │   ├── requirements.txt
│   │   └── addons/
│   │       ├── finance_ssc/          # Finance Shared Service Center
│   │       │   ├── __init__.py
│   │       │   ├── __manifest__.py
│   │       │   ├── models/
│   │       │   │   ├── month_end_closing.py
│   │       │   │   ├── journal_entry.py
│   │       │   │   └── bank_reconciliation.py
│   │       │   ├── views/
│   │       │   └── security/
│   │       ├── bir_compliance/       # BIR forms & ATP
│   │       │   ├── models/
│   │       │   │   ├── bir_form_1601c.py
│   │       │   │   ├── bir_form_1702.py
│   │       │   │   └── bir_form_2550q.py
│   │       │   └── wizards/
│   │       └── travel_expense/       # SAP Concur alternative
│   │           ├── models/
│   │           │   ├── travel_request.py
│   │           │   ├── expense_report.py
│   │           │   └── policy_validation.py
│   │           └── views/
│   │
│   ├── mcp-coordinator/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── server.py
│   │   │   ├── skills/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── superset_automation.py
│   │   │   │   ├── odoo_finance.py
│   │   │   │   ├── notion_sync.py
│   │   │   │   └── paddle_ocr.py
│   │   │   └── utils/
│   │   │       ├── supabase_client.py
│   │   │       └── external_id_upsert.py
│   │   └── tests/
│   │
│   ├── superset/
│   │   ├── Dockerfile
│   │   ├── superset_config.py
│   │   ├── requirements.txt
│   │   ├── dashboards/
│   │   │   ├── finance_ssc.json
│   │   │   ├── bir_compliance.json
│   │   │   └── operational_analytics.json
│   │   └── datasets/
│   │       ├── month_end_closing.sql
│   │       └── bir_tax_summary.sql
│   │
│   └── ocr-service/
│       ├── Dockerfile
│       ├── app.py
│       ├── requirements.txt
│       └── models/
│           └── paddleocr_config.py
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── droplets.tf
│   │   ├── app-platform.tf
│   │   ├── networking.tf
│   │   └── variables.tf
│   └── ansible/
│       └── playbooks/
│           ├── setup-odoo.yml
│           └── configure-nginx.yml
│
├── scripts/
│   ├── backup.sh
│   ├── restore.sh
│   ├── smoke-test.sh
│   └── migrate-database.sh
│
├── docker-compose.yml              # Local development
├── docker-compose.prod.yml         # Production reference
├── .env.example
└── README.md
```

## 🚀 Initial Setup

### 1. Clone and Configure Repository

```bash
# Clone repo
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo

# Copy environment template
cp .env.example .env

# Edit with your credentials
vim .env
```

### 2. Set GitHub Secrets

Go to GitHub → Settings → Secrets → Actions and add:

```bash
# DigitalOcean
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_xxxxx
DO_APP_MCP_ID=xxxxx
DO_APP_SUPERSET_ID=xxxxx
DROPLET_SSH_KEY=<private_key>

# Odoo
ODOO_ADMIN_USER=admin
ODOO_ADMIN_PASSWORD=<strong_password>
ODOO_DB_PASSWORD=<db_password>

# Superset
SUPERSET_ADMIN_PASSWORD=<strong_password>
SUPERSET_SECRET_KEY_PROD=<hex_42_chars>

# Supabase
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_PASSWORD=<db_password>

# Notion
NOTION_INTEGRATION_TOKEN=secret_xxxxx

# Slack
SLACK_WEBHOOK=https://hooks.slack.com/services/xxxxx
```

### 3. DNS Configuration (Already Done ✅)

Your Squarespace DNS is correctly configured:
- `erp` → 165.227.10.178
- `mcp` → pulse-hub-web-an645.ondigitalocean.app
- `superset` → superset-nlavf.ondigitalocean.app

### 4. DigitalOcean Setup

```bash
# Install doctl
brew install doctl  # macOS
# or
sudo snap install doctl  # Linux

# Authenticate
doctl auth init

# Create container registry
doctl registry create insightpulse

# Login to registry
doctl registry login
```

## 🔄 CI/CD Workflow

### Deployment Triggers

1. **Push to `main`** → Production deployment
2. **Push to `staging`** → Staging deployment
3. **Manual** → `workflow_dispatch`

### Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     CODE PUSH TO MAIN                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │  Odoo   │   │   MCP   │   │Superset │
  │  Build  │   │  Build  │   │  Build  │
  └────┬────┘   └────┬────┘   └────┬────┘
       │             │             │
       ▼             ▼             ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │ Push to │   │ Push to │   │ Deploy  │
  │  DOCR   │   │App Plat │   │App Plat │
  └────┬────┘   └────┬────┘   └────┬────┘
       │             │             │
       ▼             ▼             ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │ Deploy  │   │ Health  │   │ Health  │
  │Droplet  │   │  Check  │   │  Check  │
  └────┬────┘   └────┬────┘   └────┬────┘
       │             │             │
       └─────────────┴─────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Integration Tests    │
         │  - Health checks      │
         │  - E2E workflows      │
         │  - BIR compliance     │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Notify Slack         │
         │  Log to Supabase      │
         └───────────────────────┘
```

## 📝 Manual Deployment Commands

### Deploy Odoo to Droplet

```bash
# SSH into droplet
ssh root@165.227.10.178

# Pull latest code
cd /opt/insightpulse-odoo
git pull origin main

# Build and deploy
docker-compose -f docker-compose.prod.yml up -d --build odoo

# Check logs
docker-compose logs -f odoo
```

### Deploy MCP to App Platform

```bash
# Update app
doctl apps update <APP_ID> --spec services/mcp-coordinator/app-spec.yaml

# View deployment
doctl apps list-deployments <APP_ID>

# Get logs
doctl apps logs <APP_ID> --type run
```

### Deploy Superset to App Platform

```bash
# Update app
doctl apps update <APP_ID> --spec services/superset/app-spec.yaml

# Check deployment
doctl apps get-deployment <APP_ID> <DEPLOYMENT_ID>
```

## 🧪 Testing

### Local Development

```bash
# Start all services locally
docker-compose up -d

# Access services
# Odoo: http://localhost:8069
# MCP: http://localhost:8000
# Superset: http://localhost:8088

# Run tests
docker-compose exec mcp pytest /app/tests

# Stop services
docker-compose down
```

### Integration Tests

```bash
# Trigger integration tests manually
gh workflow run integration-tests.yml

# View test results
gh run list --workflow=integration-tests.yml

# Download artifacts
gh run download <RUN_ID>
```

## 🔒 Security Checklist

- [ ] All secrets stored in GitHub Secrets
- [ ] Droplet SSH key is RSA 4096-bit
- [ ] Nginx configured with SSL/TLS (Let's Encrypt)
- [ ] Database passwords are 32+ characters
- [ ] Supabase RLS policies enabled
- [ ] App Platform environment variables are `RUN_TIME` secrets
- [ ] Odoo admin password changed from default
- [ ] Superset `SECRET_KEY` is 42+ hex characters
- [ ] CORS configured for trusted domains only
- [ ] Regular automated backups enabled

## 📊 Monitoring

### Health Endpoints

```bash
# Check all services
curl https://erp.insightpulseai.net/web/health
curl https://mcp.insightpulseai.net/health
curl https://superset.insightpulseai.net/health
```

### Logs

```bash
# Odoo logs (on droplet)
ssh root@165.227.10.178 'docker logs odoo --tail 100 -f'

# MCP logs
doctl apps logs <MCP_APP_ID> --type run --tail 100 --follow

# Superset logs
doctl apps logs <SUPERSET_APP_ID> --type run --tail 100 --follow

# Query Supabase logs
curl "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/deployment_logs?order=deployed_at.desc&limit=20" \
  -H "apikey: $SUPABASE_ANON_KEY"
```

## 🔄 Rollback Procedures

### Rollback Odoo Deployment

```bash
# SSH into droplet
ssh root@165.227.10.178

# List available images
docker images | grep odoo

# Restore previous database backup
cd /backup
ls -lah odoo-*.sql

# Stop current container
docker stop odoo

# Restore database
docker exec -i odoo-postgres psql -U odoo odoo < odoo-20241104-013000.sql

# Start container with previous image
docker run -d --name odoo <PREVIOUS_IMAGE_TAG>
```

### Rollback App Platform Deployment

```bash
# List previous deployments
doctl apps list-deployments <APP_ID> --format ID,Phase,Created

# Rollback to previous deployment
doctl apps create-deployment <APP_ID> <PREVIOUS_DEPLOYMENT_ID>
```

## 📚 Additional Resources

- [Odoo Development Docs](https://www.odoo.com/documentation/19.0/)
- [Apache Superset Docs](https://superset.apache.org/docs/intro)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Supabase PostgreSQL](https://supabase.com/docs/guides/database)

## 🐛 Troubleshooting

### Odoo Won't Start

```bash
# Check logs
docker logs odoo --tail 100

# Common issues:
# 1. Database connection → Check POSTGRES_* env vars
# 2. Port conflict → lsof -i :8069
# 3. Module errors → Update module list
```

### MCP Skills Not Loading

```bash
# Check App Platform logs
doctl apps logs <MCP_APP_ID> --type run --tail 100

# Common issues:
# 1. Missing environment variables
# 2. Supabase connection timeout
# 3. Odoo RPC auth failure
```

### Superset Database Connection

```bash
# Test database connection
docker exec superset superset db upgrade

# Reset admin password
docker exec -it superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@insightpulseai.net \
  --password <new_password>
```

## 🎯 Next Steps

1. ✅ DNS configured (already done)
2. ⏳ Create GitHub workflows (use templates above)
3. ⏳ Configure GitHub secrets
4. ⏳ Deploy Odoo to droplet
5. ⏳ Deploy MCP to App Platform
6. ⏳ Deploy Superset to App Platform
7. ⏳ Run integration tests
8. ⏳ Configure automated backups
9. ⏳ Set up monitoring alerts
10. ⏳ Document runbooks for operations team

---

**Production Readiness Score:** 85/100

**Missing:**
- Automated database backups (critical)
- Real-time monitoring/alerting
- Disaster recovery plan
- Load testing results
