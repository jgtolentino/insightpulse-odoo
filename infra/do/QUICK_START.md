# Quick Start - Odoo SaaS Platform Deployment

**Status**: ⚠️ Ready for execution - requires secret configuration

---

## Prerequisites (30 seconds)

```bash
# 1. Get Supabase password
# Visit: https://app.supabase.com/project/xkxyvboeubffxxbebsll/settings/database
# Copy password from connection string

# 2. Set environment variables
export POSTGRES_PASSWORD="your_supabase_password_here"
export ODOO_ADMIN_PASSWORD="$(openssl rand -base64 32)"

# 3. Save for future use (optional)
echo "export POSTGRES_PASSWORD='$POSTGRES_PASSWORD'" >> ~/.zshrc
echo "export ODOO_ADMIN_PASSWORD='$ODOO_ADMIN_PASSWORD'" >> ~/.zshrc
source ~/.zshrc
```

---

## Deploy Staging (10-15 minutes)

```bash
cd /Users/tbwa/insightpulse-odoo

# Deploy
./infra/do/deploy-staging.sh

# Output will show:
# ✅ App ID: [staging-app-id]
# ✅ App URL: https://[staging-url]

# Monitor deployment (wait for ACTIVE status)
doctl apps logs [staging-app-id] --type build --follow

# Run smoke tests
./infra/do/smoke-tests.sh [staging-url]
```

---

## Deploy Production (15-20 minutes)

```bash
# Deploy with blue-green strategy
./infra/do/deploy-production.sh

# Script will:
# 1. Create green environment
# 2. Deploy and wait for ACTIVE
# 3. Run smoke tests automatically
# 4. Show cutover instructions

# Output will show:
# ✅ Green environment: [green-app-id]
# ✅ Production URL: https://[prod-url]
# ✅ All smoke tests passed
```

---

## Setup Monitoring (5 minutes)

```bash
# Get production app ID
PROD_APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "odoo-saas-platform$" | awk '{print $1}')

# Setup monitoring
./infra/do/setup-monitoring.sh $PROD_APP_ID

# Start monitoring stack
cd infra/monitoring
docker-compose up -d

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

---

## Validation Checklist

### Staging
- [ ] App created: `doctl apps list`
- [ ] Build successful: `doctl apps logs [id] --type build`
- [ ] Health check passes: `curl https://[url]/web/health`
- [ ] Smoke tests pass: `./infra/do/smoke-tests.sh [url]`

### Production
- [ ] Green environment active: `doctl apps get [id]`
- [ ] Smoke tests pass automatically
- [ ] Web interface accessible: `https://[url]/web`
- [ ] All 10 modules available

### Monitoring
- [ ] Prometheus scraping: http://localhost:9090/targets
- [ ] Grafana dashboards: http://localhost:3000
- [ ] Alerts configured: Check Grafana alerts

---

## Troubleshooting

### Deployment Fails

```bash
# Check build logs
doctl apps logs [app-id] --type build

# Check runtime logs
doctl apps logs [app-id] --type run

# Common issues:
# 1. Wrong POSTGRES_PASSWORD → verify in Supabase console
# 2. GitHub branch not found → check branch name in app spec
# 3. Out of memory → upgrade to basic-xs ($12/month)

# Retry deployment
doctl apps create-deployment [app-id] --force-rebuild
```

### Health Check Fails

```bash
# Check runtime logs
doctl apps logs [app-id] --type run --follow

# Test database connection
psql "postgresql://postgres.xkxyvboeubffxxbebsll:$POSTGRES_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres" -c "SELECT 1"

# Increase health check timeout if needed
# Edit app spec: initial_delay_seconds: 300
doctl apps update [app-id] --spec infra/do/odoo-saas-platform.yaml
```

### Rollback Production

```bash
# If green environment has issues
doctl apps delete [green-app-id]
# Blue environment (if exists) takes over immediately

# OR rollback to specific deployment
doctl apps list-deployments [app-id]
doctl apps rollback [app-id] --deployment-id [previous-deployment-id]
```

---

## Budget & Performance

**Cost**: $10/month (50% under $20 budget)
- Staging: $5/month
- Production: $5/month
- Database: Free (Supabase)
- Monitoring: Free (self-hosted)

**Performance Targets**:
- P95 Latency: < 500ms
- Error Rate: < 0.1%
- Uptime: 99.9%
- Memory: < 400MB

---

## Support

**Documentation**:
- Full guide: `infra/do/DEPLOYMENT_GUIDE.md`
- Status report: `infra/do/DEPLOYMENT_STATUS.md`
- Checklist: `infra/do/DEPLOYMENT_CHECKLIST.md`

**Scripts**:
- Staging: `infra/do/deploy-staging.sh`
- Production: `infra/do/deploy-production.sh`
- Smoke tests: `infra/do/smoke-tests.sh`
- Monitoring: `infra/do/setup-monitoring.sh`

**DigitalOcean Resources**:
- Console: https://cloud.digitalocean.com/apps
- Docs: https://docs.digitalocean.com/products/app-platform/
- Support: https://cloud.digitalocean.com/support/tickets

---

**Total Time**: 30-40 minutes (prerequisites + staging + production + monitoring)
