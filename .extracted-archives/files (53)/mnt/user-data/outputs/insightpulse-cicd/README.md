# InsightPulse AI - Production CI/CD Package

## 📦 Package Contents

This package contains everything you need to restructure your `insightpulse-odoo` repository for production-ready CI/CD deployment.

```
insightpulse-cicd/
├── README.md                           # This file
├── DEPLOYMENT_GUIDE.md                 # Complete deployment documentation
├── MIGRATION_PLAN.md                   # Step-by-step migration guide
├── QUICK_REFERENCE.md                  # Quick command reference
│
└── GitHub Workflows (rename after copying):
    ├── .github-workflows-deploy-odoo.yml           → .github/workflows/deploy-odoo.yml
    ├── .github-workflows-deploy-mcp.yml            → .github/workflows/deploy-mcp.yml
    ├── .github-workflows-deploy-superset.yml       → .github/workflows/deploy-superset.yml
    └── .github-workflows-integration-tests.yml     → .github/workflows/integration-tests.yml
```

## 🎯 What This Package Provides

### ✅ Production-Ready CI/CD
- Automated deployments on push to `main` or `staging`
- Multi-service deployment (Odoo, MCP, Superset, OCR)
- Comprehensive integration testing
- Automated health checks
- Slack notifications
- Supabase deployment logging

### ✅ Service Isolation
- Each service in its own directory
- Independent Docker builds
- Separate deployment workflows
- Clear dependency management

### ✅ Environment Management
- Production vs Staging separation
- Secure secrets management via GitHub
- Environment-specific configurations
- Easy rollback procedures

### ✅ Monitoring & Observability
- Health check endpoints
- Automated smoke tests
- Deployment logging to Supabase
- Integration test suite

## 🚀 Quick Start (5 Minutes)

### Step 1: Download and Extract

You already have this package! Now:

```bash
cd ~/Downloads/insightpulse-cicd
ls -la
```

### Step 2: Copy to Your Repo

```bash
# Go to your insightpulse-odoo repo
cd /path/to/insightpulse-odoo

# Create workflows directory
mkdir -p .github/workflows

# Copy workflow files (remove the leading "." from filenames)
cp ~/Downloads/insightpulse-cicd/.github-workflows-*.yml .github/workflows/
cd .github/workflows
for f in .github-workflows-*.yml; do
  mv "$f" "$(echo $f | sed 's/^.github-workflows-//')"
done

# Copy documentation
cp ~/Downloads/insightpulse-cicd/*.md ./
```

### Step 3: Review Migration Plan

```bash
# Read the migration plan
cat MIGRATION_PLAN.md

# Or open in your editor
code MIGRATION_PLAN.md  # VS Code
vim MIGRATION_PLAN.md   # Vim
```

### Step 4: Configure GitHub Secrets

Go to: https://github.com/jgtolentino/insightpulse-odoo/settings/secrets/actions

Add these secrets (see DEPLOYMENT_GUIDE.md for full list):

```
DIGITALOCEAN_ACCESS_TOKEN
ODOO_ADMIN_PASSWORD
SUPERSET_ADMIN_PASSWORD
SUPABASE_ANON_KEY
```

### Step 5: Test Locally

```bash
# Test the new structure locally
docker-compose up -d

# Run smoke tests
./scripts/smoke-test.sh

# Stop services
docker-compose down
```

### Step 6: Deploy!

```bash
# Commit changes
git add .
git commit -m "Add production CI/CD workflows"

# Push to trigger deployment
git push origin main

# Watch the deployment
gh run watch
```

## 📖 Documentation Overview

### 1. DEPLOYMENT_GUIDE.md
- **Purpose**: Complete deployment documentation
- **Read this**: Before making any production changes
- **Contains**:
  - Architecture overview
  - Repository structure
  - Setup instructions
  - Monitoring procedures
  - Troubleshooting guides

### 2. MIGRATION_PLAN.md
- **Purpose**: Step-by-step repo restructuring
- **Read this**: When ready to migrate
- **Contains**:
  - Current state analysis
  - Migration strategy (5 phases)
  - Pre-migration checklist
  - Rollback plan
  - Timeline (3-4 hours total)

### 3. QUICK_REFERENCE.md
- **Purpose**: Daily operations reference
- **Read this**: When you need quick commands
- **Contains**:
  - Deploy commands
  - Health checks
  - Log viewing
  - Rollback procedures
  - Troubleshooting

## 🔧 GitHub Workflows Explained

### deploy-odoo.yml
- **Triggers**: Push to `main` or `staging` (services/odoo/**)
- **Actions**:
  1. Build Docker image
  2. Push to DigitalOcean Container Registry
  3. Deploy to droplet via SSH
  4. Run health checks
  5. Notify Slack

### deploy-mcp.yml
- **Triggers**: Push to `main` or `staging` (services/mcp-coordinator/**)
- **Actions**:
  1. Build Docker image
  2. Deploy to App Platform
  3. Wait for deployment completion
  4. Run integration tests
  5. Log to Supabase

### deploy-superset.yml
- **Triggers**: Push to `main` or `staging` (services/superset/**)
- **Actions**:
  1. Generate secret key
  2. Build and deploy to App Platform
  3. Run smoke tests
  4. Import Finance SSC dashboards
  5. Notify Slack

### integration-tests.yml
- **Triggers**: 
  - After successful deployments
  - Scheduled (every 6 hours)
  - Manual dispatch
- **Actions**:
  1. Health checks all services
  2. Test Odoo database
  3. Verify Finance SSC module
  4. Check MCP skills
  5. Test Superset connection
  6. Run end-to-end workflow
  7. BIR compliance check
  8. Log results to Supabase

## 🎯 Migration Checklist

Before you start migration, ensure:

- [ ] Current production is backed up
- [ ] You have `doctl` installed and configured
- [ ] You have access to DigitalOcean console
- [ ] You have access to Supabase dashboard
- [ ] You have GitHub admin access
- [ ] You have SSH access to droplet (165.227.10.178)
- [ ] You understand the rollback procedure
- [ ] You have 3-4 hours available
- [ ] You've read DEPLOYMENT_GUIDE.md
- [ ] You've read MIGRATION_PLAN.md

## 🔥 Your Current DNS (Already Correct ✅)

```
insightpulseai.net DNS Records:
├── erp → 165.227.10.178 (Odoo droplet)
├── mcp → pulse-hub-web-an645.ondigitalocean.app (MCP)
├── superset → superset-nlavf.ondigitalocean.app (Superset)
├── ocr → 162.159.140.98 (OCR service)
└── @ → 162.159.140.98 (Landing page)
```

No DNS changes needed—your configuration is already production-ready!

## 💡 Recommended Migration Timeline

### Option A: Safe Weekend Migration (Recommended)
- **Friday 3PM**: Start migration
- **Friday 5PM**: Complete Phase 1-3 (structure + workflows)
- **Saturday 10AM**: Deploy to staging and test
- **Saturday 4PM**: Deploy to production
- **Sunday**: Monitor and fix any issues

### Option B: Quick Weeknight Migration
- **Wednesday 6PM**: Start migration
- **Wednesday 9PM**: Complete all phases
- **Wednesday 10PM**: Deploy and monitor
- **Next day**: Review and optimize

### Option C: Staged Migration (Most Conservative)
- **Week 1**: Restructure repo, add workflows (no deploy)
- **Week 2**: Deploy to staging environment
- **Week 3**: Test integration thoroughly
- **Week 4**: Deploy to production

## 🆘 Getting Help

If you encounter issues during migration:

1. **Check GitHub Actions logs**
   ```bash
   gh run list
   gh run view <RUN_ID>
   ```

2. **Check service logs**
   ```bash
   # See QUICK_REFERENCE.md for log commands
   ```

3. **Review Supabase deployment logs**
   ```bash
   curl "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/deployment_logs" \
     -H "apikey: $SUPABASE_ANON_KEY" | jq .
   ```

4. **Rollback if needed**
   ```bash
   # See MIGRATION_PLAN.md rollback section
   ```

## 🎉 Success Criteria

After successful migration, you'll have:

- ✅ Automated deployments working
- ✅ All services running on correct domains
- ✅ Integration tests passing
- ✅ Health checks returning 200 OK
- ✅ Slack notifications working
- ✅ Supabase logging operational
- ✅ No manual SSH deployments needed
- ✅ Clear rollback procedures
- ✅ Comprehensive monitoring

## 🚀 Next Steps After Migration

1. **Enable automated backups** (critical!)
2. **Set up monitoring alerts** (Datadog, Sentry)
3. **Load test the system**
4. **Train team on new workflow**
5. **Document runbooks**
6. **Schedule first month-end closing**

## 📚 Additional Resources

- **Odoo Development**: https://www.odoo.com/documentation/19.0/
- **Apache Superset**: https://superset.apache.org/docs/intro
- **MCP Protocol**: https://modelcontextprotocol.io/
- **DigitalOcean**: https://docs.digitalocean.com/products/app-platform/
- **GitHub Actions**: https://docs.github.com/en/actions

## 📞 Support Contacts

- **Your Odoo Expert**: Jake Tolentino
- **DigitalOcean Project**: 29cde7a1-8280-46ad-9fdf-dea7b21a7825
- **Supabase Project**: spdtwktxdalcfigzeqrz
- **GitHub Repo**: jgtolentino/insightpulse-odoo

---

## 🎯 TL;DR - Super Quick Start

```bash
# 1. Copy files to your repo
cd /path/to/insightpulse-odoo
cp -r ~/Downloads/insightpulse-cicd/.github-workflows-*.yml .github/workflows/
for f in .github/workflows/.github-workflows-*.yml; do mv "$f" "$(echo $f | sed 's/\/.github-workflows-/\//g')"; done

# 2. Read migration plan
cat ~/Downloads/insightpulse-cicd/MIGRATION_PLAN.md

# 3. Configure GitHub secrets
# Go to: https://github.com/jgtolentino/insightpulse-odoo/settings/secrets/actions

# 4. Run migration script from MIGRATION_PLAN.md
# (See Phase 1 in MIGRATION_PLAN.md)

# 5. Commit and push
git add .
git commit -m "Add production CI/CD"
git push origin main

# 6. Watch deployment
gh run watch
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-04  
**Status**: ✅ Production Ready  
**Estimated Migration Time**: 3-4 hours  
**Risk Level**: Low (with proper backups)
