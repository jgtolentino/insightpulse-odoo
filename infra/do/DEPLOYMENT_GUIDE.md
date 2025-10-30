# DigitalOcean App Platform Deployment Guide

Complete guide for deploying InsightPulse Odoo 19.0 to DigitalOcean App Platform.

---

## Prerequisites

### 1. Install Required Tools

```bash
# Install doctl (DigitalOcean CLI)
brew install doctl  # macOS
# OR
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz | tar -xzv
sudo mv doctl /usr/local/bin

# Verify installation
doctl version

# Install GitHub CLI (optional, for secrets management)
brew install gh  # macOS
# OR
curl -sL https://github.com/cli/cli/releases/download/v2.40.0/gh_2.40.0_linux_amd64.tar.gz | tar -xzv
sudo mv gh_2.40.0_linux_amd64/bin/gh /usr/local/bin
```

### 2. Authenticate with DigitalOcean

```bash
# Get your DigitalOcean API token
# Visit: https://cloud.digitalocean.com/account/api/tokens

# Initialize doctl with your token
doctl auth init

# Verify authentication
doctl account get
```

### 3. Prepare Supabase Database

```bash
# Get your Supabase connection details
# Visit: https://app.supabase.com/project/[your-project]/settings/database

# Connection string format:
postgresql://postgres:[PASSWORD]@aws-1-us-east-1.pooler.supabase.com:6543/postgres

# Test connection
psql "postgresql://postgres:[PASSWORD]@aws-1-us-east-1.pooler.supabase.com:6543/postgres" -c "SELECT version();"
```

---

## Step 1: Create DigitalOcean App

### Option A: Using doctl CLI (Recommended)

```bash
# Navigate to repository root
cd /Users/tbwa/insightpulse-odoo

# Create app from spec
doctl apps create --spec infra/do/odoo-saas-platform.yaml

# Note the app ID from output
# Example: b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
```

### Option B: Using DigitalOcean Console

1. Visit: https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Select "GitHub" as source
4. Choose repository: `insightpulse-odoo`
5. Branch: `main`
6. Click "Edit Your App Spec"
7. Paste contents of `infra/do/odoo-saas-platform.yaml`
8. Click "Save" and "Create Resources"

---

## Step 2: Configure Environment Variables

Environment variables are defined in the app spec, but you need to provide actual values for secrets.

### Using DigitalOcean Console

1. Go to your app: https://cloud.digitalocean.com/apps/[app-id]/settings
2. Navigate to "Environment Variables" tab
3. Update these secret values:
   - `POSTGRES_HOST`: Your Supabase pooler host
   - `POSTGRES_USER`: `postgres` (or your database user)
   - `POSTGRES_PASSWORD`: Your Supabase database password
   - `ODOO_ADMIN_PASSWORD`: Generate with `openssl rand -base64 32`

### Using doctl CLI

```bash
# Update environment variables
doctl apps update [app-id] --spec infra/do/odoo-saas-platform.yaml

# Verify environment variables
doctl apps get [app-id] --format ID,Spec.Name,Spec.Services
```

---

## Step 3: Configure GitHub Secrets

Required for CI/CD automated deployments.

```bash
# Add secrets to GitHub repository
gh secret set DO_ACCESS_TOKEN --body "dop_v1_your_token_here"
gh secret set DO_APP_ID --body "your_app_id_here"
gh secret set POSTGRES_HOST --body "aws-1-us-east-1.pooler.supabase.com"
gh secret set POSTGRES_USER --body "postgres"
gh secret set POSTGRES_PASSWORD --body "your_supabase_password"
gh secret set ODOO_ADMIN_PASSWORD --body "$(openssl rand -base64 32)"

# Verify secrets
gh secret list
```

---

## Step 4: Deploy Application

### Option A: Manual Deployment (First Time)

```bash
# Get your app ID
doctl apps list --format ID,Spec.Name

# Create deployment
doctl apps create-deployment [app-id] --force-rebuild

# Monitor deployment progress
doctl apps list-deployments [app-id] --format ID,Phase,Progress

# View build logs
doctl apps logs [app-id] --type build --follow

# View runtime logs
doctl apps logs [app-id] --type run --follow
```

### Option B: Automated CI/CD (After First Deployment)

```bash
# Push to main branch triggers automatic deployment
git add .
git commit -m "feat: initial deployment configuration"
git push origin main

# OR trigger manual deployment via GitHub Actions
gh workflow run digitalocean-deploy.yml

# Monitor workflow
gh run list --workflow=digitalocean-deploy.yml
gh run watch
```

---

## Step 5: Verify Deployment

### 1. Get App URL

```bash
# Get default ingress URL
doctl apps get [app-id] --format DefaultIngress --no-header

# Example output: odoo-saas-platform-xyz123.ondigitalocean.app
```

### 2. Health Check

```bash
# Test health endpoint
curl -sf https://[app-url]/web/health

# Expected output: {"status": "ok"}
```

### 3. Smoke Tests

```bash
# Test main page
curl -sf https://[app-url]/web

# Test database selector
curl -sf https://[app-url]/web/database/selector

# Test login page
curl -sf https://[app-url]/web/login
```

### 4. Access Odoo Web Interface

1. Open browser: `https://[app-url]/web`
2. You should see Odoo login page
3. Create database or login with existing credentials

---

## Step 6: Post-Deployment Configuration

### 1. Create Odoo Database (First Time)

```bash
# Access database manager
https://[app-url]/web/database/manager

# OR use Odoo CLI (via doctl exec)
doctl apps exec [app-id] --component odoo-web -- odoo-bin -d odoo --init base --stop-after-init
```

### 2. Install Custom Modules

```bash
# Access Odoo interface
https://[app-url]/web

# Navigate to Apps menu
# Search for "InsightPulse" or "Custom"
# Click "Install" on your custom modules
```

### 3. Configure Custom Domain (Optional)

```bash
# Add custom domain in DigitalOcean console
# Settings > Domains > Add Domain

# Update DNS records (in your domain registrar):
# Type: CNAME
# Name: odoo (or subdomain of choice)
# Value: [app-url]
# TTL: 3600

# OR use doctl
doctl apps update [app-id] --spec infra/do/odoo-saas-platform.yaml
# (Update spec with domain configuration)
```

---

## Monitoring and Maintenance

### View Application Metrics

```bash
# Get app details
doctl apps get [app-id]

# View deployments
doctl apps list-deployments [app-id]

# View logs
doctl apps logs [app-id] --type run --follow

# View alerts (if configured)
doctl apps alerts list [app-id]
```

### Database Monitoring

```sql
-- Connect to database
psql "$POSTGRES_URL"

-- Check database size
SELECT pg_size_pretty(pg_database_size('postgres')) as db_size;

-- Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Check connection count
SELECT count(*) FROM pg_stat_activity;
```

### Cost Monitoring

```bash
# View billing
doctl invoice list

# View current month's usage
doctl invoice get latest

# Set up billing alerts (in DigitalOcean console)
# Settings > Billing > Alerts > Create Alert
# Threshold: $10/month (to stay under $15 target)
```

---

## Troubleshooting

### Deployment Fails

```bash
# Check build logs
doctl apps logs [app-id] --type build --follow

# Common issues:
# 1. Missing environment variables
# 2. Docker build failures
# 3. Database connection issues

# Verify environment variables
doctl apps get [app-id] --format Spec.Services

# Rebuild with force
doctl apps create-deployment [app-id] --force-rebuild
```

### Health Check Fails

```bash
# Check runtime logs
doctl apps logs [app-id] --type run --follow

# Common issues:
# 1. Database connection timeout
# 2. Odoo startup issues
# 3. Memory limits exceeded

# Verify database connection
psql "$POSTGRES_URL" -c "SELECT version();"

# Check app resource usage
doctl apps get [app-id] --format Spec.Services
```

### Database Connection Issues

```bash
# Test connection from local machine
psql "$POSTGRES_URL" -c "SELECT 1;"

# Verify Supabase pooler is accessible
nc -zv aws-1-us-east-1.pooler.supabase.com 6543

# Check Supabase project status
# Visit: https://app.supabase.com/project/[project-ref]

# Common issues:
# 1. Wrong password
# 2. Firewall blocking port 6543
# 3. Supabase project paused (free tier after 1 week inactivity)
```

### Out of Memory Errors

```bash
# Check logs for OOM errors
doctl apps logs [app-id] --type run | grep -i "memory"

# Solutions:
# 1. Reduce ODOO_WORKERS to 1
# 2. Lower ODOO_LIMIT_MEMORY_HARD
# 3. Upgrade to basic-xs tier ($12/month, 1GB RAM)

# Update app spec
# Edit infra/do/odoo-saas-platform.yaml
# Change: instance_size_slug: basic-xs
doctl apps update [app-id] --spec infra/do/odoo-saas-platform.yaml
```

---

## Rollback Procedures

### Rollback to Previous Deployment

```bash
# List deployments
doctl apps list-deployments [app-id] --format ID,Phase,CreatedAt

# Rollback to specific deployment
doctl apps rollback [app-id] --deployment-id [deployment-id]

# Verify rollback
doctl apps get [app-id] --format ActiveDeployment.ID
```

### Rollback via Git

```bash
# Revert last commit
git revert HEAD
git push origin main

# OR reset to specific commit
git reset --hard [commit-hash]
git push --force origin main
```

---

## Scaling and Upgrades

### Upgrade Instance Size

```bash
# Edit infra/do/odoo-saas-platform.yaml
# Change: instance_size_slug: basic-xs (1GB RAM, $12/month)

# Update app
doctl apps update [app-id] --spec infra/do/odoo-saas-platform.yaml

# Create deployment
doctl apps create-deployment [app-id]
```

### Horizontal Scaling (Multiple Instances)

```bash
# Edit infra/do/odoo-saas-platform.yaml
# Change: instance_count: 2

# Note: Requires session storage configuration for multi-instance
# Requires load balancer (included in App Platform)
```

### Database Upgrade (Supabase)

```bash
# When database approaches 500MB limit:
# 1. Upgrade to Supabase Pro tier ($25/month, 8GB database)
# 2. Visit: https://app.supabase.com/project/[project-ref]/settings/billing
# 3. No code changes required - connection string stays the same
```

---

## Security Best Practices

1. **Rotate secrets regularly** (quarterly recommended)
2. **Enable 2FA** on DigitalOcean and GitHub accounts
3. **Use separate environments** (dev/staging/prod)
4. **Monitor access logs** in DigitalOcean console
5. **Keep Odoo updated** to latest security patches
6. **Use RLS policies** in Supabase for data security
7. **Limit API token scopes** to minimum required

---

## Support and Resources

### DigitalOcean Resources
- **Documentation**: https://docs.digitalocean.com/products/app-platform/
- **Community**: https://www.digitalocean.com/community/tags/app-platform
- **Support**: https://cloud.digitalocean.com/support/tickets

### Supabase Resources
- **Documentation**: https://supabase.com/docs
- **Discord**: https://discord.supabase.com
- **Support**: https://app.supabase.com/support

### Odoo Resources
- **Documentation**: https://www.odoo.com/documentation/19.0/
- **Community**: https://www.odoo.com/forum
- **GitHub**: https://github.com/odoo/odoo

---

## Quick Reference

```bash
# Create app
doctl apps create --spec infra/do/odoo-saas-platform.yaml

# Update app
doctl apps update [app-id] --spec infra/do/odoo-saas-platform.yaml

# Deploy
doctl apps create-deployment [app-id] --force-rebuild

# Logs
doctl apps logs [app-id] --type run --follow

# Status
doctl apps get [app-id]

# Rollback
doctl apps rollback [app-id] --deployment-id [deployment-id]
```

---

**Budget**: $5/month base cost (75% under $20 target)
**Scaling**: $12-37/month as you grow
**Support**: Community + official documentation
