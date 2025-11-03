# Deployment Integration Skill

**Skill ID**: `deployment-integration`
**Category**: DevOps / Infrastructure
**Complexity**: Advanced
**Version**: 2.0.0

---

## 📋 Description

Comprehensive deployment integration skill for the InsightPulse platform, covering all deployment scenarios including Odoo ERP, Superset Analytics, PaddleOCR service, and Traefik reverse proxy on DigitalOcean infrastructure.

---

## 🎯 Use Cases

### When to Use This Skill

1. **Full platform deployment** - Deploy all services from scratch
2. **Individual service deployment** - Deploy or update a single service
3. **Environment provisioning** - Set up production or staging environments
4. **Disaster recovery** - Restore services after failure
5. **CI/CD automation** - Integrate with GitHub Actions workflows

### When NOT to Use This Skill

- Local development setup (use `docker-compose` instead)
- Database migrations only (use Odoo CLI)
- Configuration changes only (use app console)

---

## 🛠️ Prerequisites

### Required Tools

```bash
# Install required tools
brew install doctl gh curl jq  # macOS
# or
apt-get install curl jq && snap install doctl  # Linux

# Authenticate
doctl auth init
gh auth login
```

### Required Secrets

**GitHub Secrets**:
- `APP_ID` - GitHub App ID
- `INSTALLATION_ID` - App installation ID
- `PRIVATE_KEY` - GitHub App private key
- `DO_API_TOKEN` - DigitalOcean API token
- `ODOO_APP_ID` - Odoo app ID
- `SUPERSET_APP_ID` - Superset app ID

**Environment Variables**:
```bash
export DO_ACCESS_TOKEN="your-do-token"
export POSTGRES_PASSWORD="your-db-password"
export ODOO_ADMIN_PASSWORD="your-admin-password"
```

### Repository Structure

```
insightpulse-odoo/
├── infra/
│   ├── do/
│   │   ├── odoo-saas-platform.yaml
│   │   └── odoo-saas-platform-staging.yaml
│   ├── superset/
│   │   └── superset-app.yaml
│   ├── paddleocr/
│   │   ├── deploy-droplet.sh
│   │   └── docker-compose.yml
│   └── reverse-proxy/
│       ├── deploy.sh
│       └── traefik.yml
├── scripts/
│   ├── deploy-unified.sh
│   └── deploy-check.sh
└── .github/workflows/
    └── ai-auto-commit.yml
```

---

## 🚀 Usage Examples

### Example 1: Full Platform Deployment

**Scenario**: Deploy the complete InsightPulse platform from scratch

**Command**:
```bash
# Deploy all services to production
./scripts/deploy-unified.sh full production

# What gets deployed:
# 1. Traefik reverse proxy (DO Droplet)
# 2. PaddleOCR service (DO Droplet)
# 3. Odoo ERP (DO App Platform)
# 4. Superset Analytics (DO App Platform)
# 5. Health checks and validation
```

**Expected Output**:
```
╔═══════════════════════════════════════════════════════════╗
║     InsightPulse Unified Deployment System v2.0          ║
╚═══════════════════════════════════════════════════════════╝

[INFO] Deployment Type: full
[INFO] Environment: production
[STEP] Checking prerequisites...
[INFO] All prerequisites satisfied
[STEP] Deploying Traefik Reverse Proxy...
[INFO] ✅ Traefik deployment complete
[STEP] Deploying PaddleOCR Service...
[INFO] ✅ PaddleOCR deployment complete
[STEP] Deploying Odoo ERP...
[INFO] ✅ Odoo deployment complete
[STEP] Deploying Superset Analytics...
[INFO] ✅ Superset deployment complete
[STEP] Running health checks...
[INFO] ✅ All services healthy
[INFO] ═══════════════════════════════════════════
[INFO]   Deployment Complete! 🎉
[INFO] ═══════════════════════════════════════════
```

**Time**: ~20-30 minutes for full deployment

---

### Example 2: Deploy Odoo ERP Only

**Scenario**: Update Odoo ERP after code changes

**Command**:
```bash
# Production deployment
./scripts/deploy-unified.sh odoo production

# Staging deployment
./scripts/deploy-unified.sh odoo staging
```

**Alternative (Direct doctl)**:
```bash
# Get app ID
ODOO_APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "odoo-saas-platform" | awk '{print $1}')

# Trigger deployment
doctl apps create-deployment $ODOO_APP_ID --force-rebuild

# Monitor
doctl apps logs $ODOO_APP_ID --type deploy --follow
```

**Time**: ~5-8 minutes

---

### Example 3: CI/CD Automatic Deployment

**Scenario**: Automatic deployment on push to `main`

**Setup**:
1. Configure GitHub secrets (see `.github/SECRETS_SETUP.md`)
2. Push to `main` branch
3. Workflow triggers automatically

**Workflow**:
```yaml
# .github/workflows/ai-auto-commit.yml
name: AI Auto Commit & Deploy
on:
  push:
    branches: [main]

jobs:
  ai_ops:
    runs-on: ubuntu-latest
    steps:
      # ... authentication ...

      - name: Trigger Odoo Deployment
        run: |
          curl -X POST \
            "https://api.digitalocean.com/v2/apps/${ODOO_APP_ID}/deployments" \
            -H "Authorization: Bearer ${DO_API_TOKEN}"

      - name: Trigger Superset Deployment
        run: |
          curl -X POST \
            "https://api.digitalocean.com/v2/apps/${SUPERSET_APP_ID}/deployments" \
            -H "Authorization: Bearer ${DO_API_TOKEN}"
```

**Result**:
- Automatic deployments on every push
- GitHub issue created with deployment status
- Notifications on completion

---

### Example 4: PaddleOCR Service Deployment

**Scenario**: Deploy OCR service to dedicated droplet

**Command**:
```bash
./scripts/deploy-unified.sh paddleocr production
```

**Alternative (Manual)**:
```bash
cd infra/paddleocr
./deploy-droplet.sh
```

**What it does**:
1. Creates DO droplet (1GB RAM, $6/month)
2. Installs Docker and dependencies
3. Deploys PaddleOCR FastAPI service
4. Configures Nginx reverse proxy
5. Sets up SSL with Let's Encrypt
6. Runs health checks

**Time**: ~10-15 minutes

---

### Example 5: Traefik Reverse Proxy Setup

**Scenario**: Set up reverse proxy for path-based routing

**Command**:
```bash
./scripts/deploy-unified.sh traefik production
```

**Alternative (Manual)**:
```bash
cd infra/reverse-proxy
./deploy.sh
```

**Configuration**:
```yaml
# infra/reverse-proxy/dynamic.yml
http:
  routers:
    odoo-erp:
      rule: "Host(`insightpulseai.net`) && PathPrefix(`/odoo`)"
      service: odoo-erp
      middlewares:
        - odoo-stripprefix
        - secure-headers

    superset-dashboard:
      rule: "Host(`insightpulseai.net`) && PathPrefix(`/superset`)"
      service: superset-dashboard
```

**Result**:
- https://insightpulseai.net/odoo → Odoo ERP
- https://insightpulseai.net/superset → Superset
- https://ocr.insightpulseai.net → PaddleOCR

---

## 🔍 Advanced Usage

### Deployment with Health Checks

```bash
# Deploy and verify
./scripts/deploy-unified.sh odoo production && \
  ./scripts/deploy-check.sh
```

### Blue-Green Deployment

```bash
# Using DO App Platform automatic blue-green
doctl apps create --spec infra/do/odoo-saas-platform.yaml

# Wait for deployment
doctl apps list-deployments <NEW_APP_ID>

# Test new deployment
curl https://<new-app-url>/web/health

# Switch traffic (automatic via App Platform)
# Delete old app when verified
doctl apps delete <OLD_APP_ID>
```

### Rollback Deployment

```bash
# Get deployment history
doctl apps list-deployments <APP_ID>

# Rollback to previous deployment
doctl apps rollback <APP_ID> <PREVIOUS_DEPLOYMENT_ID>
```

### Monitor Deployment

```bash
# Real-time logs
doctl apps logs <APP_ID> --type deploy --follow

# Check deployment status
doctl apps get <APP_ID> --format ActiveDeployment.Phase

# View resource usage
doctl apps get <APP_ID> --format Spec
```

---

## 📊 Architecture Overview

### Deployment Flow

```
┌────────────────────┐
│  Developer Push    │
│  to main branch    │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│  GitHub Actions    │
│  Workflow Trigger  │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│  Authenticate via  │
│  GitHub App        │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│  Trigger DO        │
│  Deployments       │
└────┬───────┬───────┘
     │       │
     ▼       ▼
┌─────────┐ ┌──────────┐
│  Odoo   │ │ Superset │
│  Deploy │ │ Deploy   │
└────┬────┘ └────┬─────┘
     │           │
     └─────┬─────┘
           │
           ▼
┌────────────────────┐
│  Monitor Status    │
│  (10 minutes max)  │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│  Report Results    │
│  (GitHub Issue)    │
└────────────────────┘
```

### Service Architecture

```
                    insightpulseai.net
                            │
                    ┌───────▼────────┐
                    │  Traefik Proxy │
                    │  (DO Droplet)  │
                    └────────┬───────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│  Odoo ERP      │  │  Superset      │  │  PaddleOCR     │
│  /odoo         │  │  /superset     │  │  ocr.domain    │
│  (App Platform)│  │  (App Platform)│  │  (Droplet)     │
└───────┬────────┘  └───────┬────────┘  └────────────────┘
        │                   │
        └─────────┬─────────┘
                  │
          ┌───────▼────────┐
          │  Supabase      │
          │  PostgreSQL    │
          │  (Free Tier)   │
          └────────────────┘
```

---

## 🔒 Security Considerations

### Authentication

1. **GitHub App** (preferred):
   - Limited permissions
   - Token auto-expiry
   - Audit trail

2. **DigitalOcean API**:
   - Read/write access
   - Rotate every 90 days
   - Store in GitHub Secrets

### Network Security

- HTTPS only (Let's Encrypt)
- Rate limiting on all endpoints
- Firewall rules on droplets
- Private networking between services

### Secret Management

```bash
# GitHub Secrets (encrypted at rest)
gh secret set DO_API_TOKEN --body "$TOKEN"
gh secret set ODOO_ADMIN_PASSWORD --body "$PASSWORD"

# Environment variables (runtime only)
export POSTGRES_PASSWORD="secret"
./scripts/deploy-unified.sh odoo production

# Never commit secrets to git!
git secret add .env
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Deployment Fails with "App not found"

**Symptom**: `Error: App with ID xxx not found`

**Solution**:
```bash
# List all apps
doctl apps list

# Verify app ID
echo $ODOO_APP_ID

# Re-create app if needed
doctl apps create --spec infra/do/odoo-saas-platform.yaml
```

#### 2. Health Check Fails

**Symptom**: `❌ Health check failed`

**Solution**:
```bash
# Check app logs
doctl apps logs <APP_ID> --type run --follow

# Check health endpoint directly
curl -v https://<app-url>/web/health

# Verify database connection
doctl apps get <APP_ID> --format Spec.Envs
```

#### 3. Deployment Stuck in "BUILDING"

**Symptom**: Deployment doesn't progress beyond BUILDING phase

**Solution**:
```bash
# Check build logs
doctl apps logs <APP_ID> --type build

# Cancel and retry
doctl apps list-deployments <APP_ID>
# Wait or force new deployment
doctl apps create-deployment <APP_ID> --force-rebuild
```

#### 4. GitHub Actions Workflow Fails

**Symptom**: `❌ GitHub App authentication failed`

**Solution**:
```bash
# Verify secrets
gh secret list

# Test GitHub App token
python scripts/test-github-app.py

# Re-generate private key if needed
# GitHub Settings → Apps → Your App → Generate new key
```

---

## 📚 Related Documentation

1. **Architecture**: `infra/UNIFIED_DEPLOYMENT_ARCHITECTURE.md`
2. **CI/CD Setup**: `.github/workflows/README.md`
3. **Secrets Management**: `.github/SECRETS_SETUP.md`
4. **Consolidation Guide**: `DEPLOYMENT_CONSOLIDATION.md`
5. **Mobile App**: `infra/mobile/MOBILE_APP_SPECIFICATION.md`

---

## 🎓 Learning Resources

### DigitalOcean App Platform
- [Official Documentation](https://docs.digitalocean.com/products/app-platform/)
- [Deployment Methods](https://docs.digitalocean.com/products/app-platform/how-to/manage-deployments/)
- [App Spec Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)

### GitHub Actions
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps)
- [Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

### Odoo Deployment
- [Odoo Deployment Guide](https://www.odoo.com/documentation/19.0/administration/on_premise/deploy.html)
- [Performance Optimization](https://www.odoo.com/documentation/19.0/administration/on_premise/performance.html)

---

## ✨ Best Practices

### Before Deployment

1. **Test locally** with `docker-compose`
2. **Run validation** with `./scripts/deploy-check.sh`
3. **Backup database** before major changes
4. **Review changes** in staging first
5. **Notify team** about deployment window

### During Deployment

1. **Monitor logs** in real-time
2. **Check health endpoints** immediately
3. **Verify database migrations** completed
4. **Test critical workflows** (login, API, etc.)
5. **Keep rollback plan** ready

### After Deployment

1. **Run smoke tests** on all endpoints
2. **Check error rates** in metrics
3. **Verify all services** are responding
4. **Update documentation** if architecture changed
5. **Post deployment summary** in team chat

---

## 🔄 Continuous Improvement

### Metrics to Track

- Deployment frequency
- Deployment duration
- Failure rate
- Time to recovery
- Resource utilization

### Automation Opportunities

- [ ] Automated rollback on health check failure
- [ ] Slack/Email notifications
- [ ] Performance benchmarks after deployment
- [ ] Automated smoke tests
- [ ] Cost monitoring and alerts

---

## 📞 Support

**For deployment issues**:
1. Check this skill documentation
2. Review logs: `doctl apps logs <APP_ID>`
3. Run health checks: `./scripts/deploy-check.sh`
4. Contact: devops@insightpulseai.net

**Emergency rollback**:
```bash
# Immediate rollback
doctl apps list-deployments <APP_ID>
doctl apps rollback <APP_ID> <PREVIOUS_DEPLOYMENT_ID>
```

---

**Skill Maintained By**: InsightPulse DevOps Team
**Last Updated**: 2025-11-02
**Skill Version**: 2.0.0
**Platform Version**: InsightPulse v3.0.0
