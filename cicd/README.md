# InsightPulse Odoo - Production CI/CD Migration Package

## 🎯 What's This?

This package contains **everything you need** to migrate `github.com/jgtolentino/insightpulse-odoo` from manual deployments to a production-grade CI/CD workflow with GitHub Actions.

**Current Problem:** Your repo structure doesn't match your multi-service infrastructure (Odoo droplet + App Platform services).

**Solution:** Complete repo restructure + automated CI/CD with zero-downtime deployments.

## 📦 Package Contents

```
insightpulse-cicd-migration.tar.gz
├── insightpulse-migration-plan.md    # 30-page comprehensive guide
└── repo-structure/
    ├── .github/workflows/
    │   └── odoo-deploy.yml           # Production deployment workflow
    ├── services/
    │   └── odoo/
    │       ├── Dockerfile.production # Multi-stage optimized build
    │       ├── docker-compose.prod.yml
    │       └── odoo.conf             # Finance SSC configuration
    ├── scripts/
    │   └── smoke-test.sh             # Post-deploy validation
    ├── docs/
    │   └── DEPLOYMENT.md             # Step-by-step guide
    └── .env.example                  # All environment variables
```

## ⚡ Quick Start (Choose Your Path)

### Option A: Full Migration (Recommended - 2 hours)

**What you get:**
- ✅ Automated deployments on `git push`
- ✅ Zero-downtime rolling updates
- ✅ Automated database backups before deploy
- ✅ Container vulnerability scanning
- ✅ Comprehensive smoke tests
- ✅ Automatic rollback on failure

**Steps:**

1. **Extract package:**
   ```bash
   cd ~/Downloads
   tar -xzf insightpulse-cicd-migration.tar.gz
   cd repo-structure
   ```

2. **Follow the deployment guide:**
   ```bash
   cat docs/DEPLOYMENT.md
   # Follow Phase 1-7 (90 minutes total)
   ```

3. **Test deployment:**
   ```bash
   # Just push to main!
   git push origin main
   # GitHub Actions does the rest
   ```

### Option B: Quick Test (30 minutes)

**Just want to see the workflows work?**

1. **Copy GitHub Actions workflow:**
   ```bash
   cd ~/projects/insightpulse-odoo
   mkdir -p .github/workflows
   cp ~/Downloads/repo-structure/.github/workflows/odoo-deploy.yml .github/workflows/
   ```

2. **Set GitHub secrets:**
   ```bash
   gh secret set DIGITALOCEAN_TOKEN -b "your_token"
   gh secret set DROPLET_SSH_KEY < ~/.ssh/id_ed25519
   ```

3. **Push and watch:**
   ```bash
   git add .github/workflows/odoo-deploy.yml
   git commit -m "test: add CI/CD workflow"
   git push origin main
   gh run watch
   ```

### Option C: Manual Review First (15 minutes)

**Want to understand before implementing?**

1. **Read the migration plan:**
   ```bash
   cat insightpulse-migration-plan.md
   # 30-page guide with rationale
   ```

2. **Review key files:**
   ```bash
   # Workflow definition
   cat repo-structure/.github/workflows/odoo-deploy.yml
   
   # Production Dockerfile
   cat repo-structure/services/odoo/Dockerfile.production
   
   # Smoke tests
   cat repo-structure/scripts/smoke-test.sh
   ```

3. **Check deployment guide:**
   ```bash
   cat repo-structure/docs/DEPLOYMENT.md
   ```

## 🎯 Immediate Benefits

### Before (Current State)
```bash
# Manual process:
1. SSH into droplet
2. Pull latest code
3. Build Docker image
4. Stop Odoo
5. Start Odoo
6. Hope nothing broke
7. No automated testing
8. No automated backups
9. Downtime during deploy
```

### After (With CI/CD)
```bash
# Automated process:
git push origin main

# GitHub Actions automatically:
1. ✅ Runs tests
2. ✅ Builds optimized image
3. ✅ Pushes to container registry
4. ✅ Backs up database
5. ✅ Zero-downtime rolling update
6. ✅ Runs smoke tests
7. ✅ Auto-rollback if failed
8. ✅ Notifies MCP endpoint

Total time: <5 minutes
Downtime: 0 seconds
```

## 🏗️ Architecture Overview

```
GitHub Repository
    │
    ├─ Push to main
    │
    ├─ GitHub Actions Triggers
    │   │
    │   ├─ Test & Lint
    │   │
    │   ├─ Build Docker Image
    │   │   └─ Push to DO Registry
    │   │
    │   ├─ Backup Database
    │   │
    │   ├─ Rolling Deploy
    │   │   ├─ Start new container
    │   │   ├─ Health check
    │   │   └─ Stop old container
    │   │
    │   └─ Smoke Tests
    │       ├─ DNS resolution
    │       ├─ SSL certificates
    │       ├─ Service health
    │       ├─ Database connectivity
    │       ├─ Module validation
    │       └─ Agency configuration
    │
    └─ Production Deployment
        │
        ├─ erp.insightpulseai.net (165.227.10.178)
        │   └─ Odoo 19 + Finance SSC modules
        │
        ├─ mcp.insightpulseai.net (App Platform)
        │   └─ MCP Coordinator
        │
        └─ superset.insightpulseai.net (App Platform)
            └─ Apache Superset
```

## 🔑 Required GitHub Secrets

```bash
# DigitalOcean
DIGITALOCEAN_TOKEN=dop_v1_xxxxx
DROPLET_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----

# Supabase
SUPABASE_TOKEN=sbp_xxxxx
SUPABASE_DB_PASSWORD=xxxxx

# Odoo
ODOO_ADMIN_PASSWORD=xxxxx
POSTGRES_PASSWORD=xxxxx

# App Platform IDs
MCP_APP_ID=xxxxx
SUPERSET_APP_ID=xxxxx
```

## 📋 Pre-Flight Checklist

Before starting migration:

### Infrastructure
- [ ] Droplet accessible via SSH (165.227.10.178)
- [ ] Docker and Docker Compose installed on droplet
- [ ] Nginx configured with Let's Encrypt
- [ ] DNS records pointing correctly (see your Squarespace screenshot)

### Access & Credentials
- [ ] GitHub access to jgtolentino/insightpulse-odoo
- [ ] DigitalOcean API token (`doctl auth init`)
- [ ] Supabase credentials
- [ ] SSH key added to droplet

### Backups (Critical!)
- [ ] Current Odoo database backup
- [ ] Current filestore backup
- [ ] Current git repository backup branch

## 🚨 Safety Features

### Automatic Rollback
If deployment fails:
1. Health check detects failure
2. Workflow automatically restores previous backup
3. Previous Docker image redeployed
4. You're notified via MCP webhook

### Database Backups
- **Before every deployment**: Automatic backup to `/backups/odoo`
- **Daily at 2 AM Manila time**: Automated backup via cron
- **Retention**: Last 7 days kept automatically

### Zero-Downtime Deployment
1. New container starts alongside old container
2. Health check validates new container
3. Only after passing does old container stop
4. If health check fails, rollback immediately

## 📊 What Gets Tested

Every deployment runs:

1. **Code Quality**
   - Python linting (flake8)
   - Odoo module linting (pylint-odoo)
   - Manifest validation

2. **Container Security**
   - Vulnerability scanning
   - Image layer analysis

3. **Service Health**
   - DNS resolution
   - SSL certificates
   - HTTP endpoints
   - Database connectivity

4. **Odoo Validation**
   - Module installation status
   - Database schema
   - Agency configuration (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
   - Performance metrics

5. **Integration Tests**
   - JSON-RPC endpoint
   - Database list API
   - Health endpoint

## 🎓 Training & Documentation

### For Your Team

1. **Developers:**
   - Just `git push` to deploy
   - Monitor progress: `gh run watch`
   - View logs: GitHub Actions UI

2. **DevOps:**
   - `docs/DEPLOYMENT.md` - full deployment guide
   - `scripts/smoke-test.sh` - manual testing
   - `insightpulse-migration-plan.md` - architecture deep-dive

3. **Finance SSC Users:**
   - No changes to Odoo UI
   - Same login URL: https://erp.insightpulseai.net
   - Deployments happen with zero downtime

## 📈 Success Metrics

After 1 week, you should see:

| Metric | Before | After |
|--------|--------|-------|
| Deployment time | 30-60 min | <5 min |
| Downtime per deploy | 5-10 min | 0 sec |
| Failed deployments | Unknown | Caught by tests |
| Rollback time | 30+ min | <2 min |
| Database backup coverage | Manual | 100% automated |

## 🆘 Troubleshooting

### Deployment Failed?

```bash
# View workflow logs
gh run view --log

# Check droplet
ssh root@165.227.10.178 'docker logs odoo-web'

# Manual rollback
ssh root@165.227.10.178 'cd /opt/insightpulse-odoo && bash scripts/rollback.sh odoo <previous-sha>'
```

### Need Help?

1. **Check docs:** `cat repo-structure/docs/DEPLOYMENT.md`
2. **Review plan:** `cat insightpulse-migration-plan.md`
3. **Smoke tests:** `bash repo-structure/scripts/smoke-test.sh`

## 🎯 Decision Matrix

**Should you implement this?**

| Your Priority | Implement Now | Wait If |
|--------------|---------------|---------|
| Faster deployments | ✅ Yes | You deploy <1x/month |
| Zero downtime | ✅ Yes | Downtime acceptable |
| Automated testing | ✅ Yes | No test requirements |
| Rollback capability | ✅ Yes | Manual rollback OK |
| Team collaboration | ✅ Yes | Solo developer |
| Production stability | ✅ Yes | Still in development |

**For Finance SSC with multi-agency operations:** ✅ **Strongly Recommended**

## 📅 Implementation Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1 | 30 min | Repository restructure |
| Phase 2 | 10 min | GitHub secrets setup |
| Phase 3 | 5 min | Container registry |
| Phase 4 | 15 min | Droplet preparation |
| Phase 5 | 10 min | Nginx configuration |
| Phase 6 | 20 min | Initial deployment |
| Phase 7 | 10 min | Verification |
| **Total** | **100 min** | **~2 hours** |

## 🎉 What's Next?

After successful migration:

1. **Week 1:** Test workflow with small changes
2. **Week 2:** Migrate remaining custom modules
3. **Week 3:** Add monitoring and alerting
4. **Week 4:** Team training

## 📚 Resources

- **Migration Plan:** `insightpulse-migration-plan.md` (30 pages)
- **Deployment Guide:** `repo-structure/docs/DEPLOYMENT.md`
- **GitHub Actions Docs:** https://docs.github.com/actions
- **DigitalOcean App Platform:** https://docs.digitalocean.com/products/app-platform/
- **Odoo 19 Docs:** https://www.odoo.com/documentation/19.0/

## ✅ Ready to Start?

```bash
# Extract and read the guide
tar -xzf insightpulse-cicd-migration.tar.gz
cat repo-structure/docs/DEPLOYMENT.md

# Start with Phase 1
cd ~/projects/insightpulse-odoo
# Follow the guide step-by-step
```

---

**Package Version:** 1.0.0  
**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**For:** Jake Tolentino - InsightPulse AI  
**Repository:** https://github.com/jgtolentino/insightpulse-odoo
