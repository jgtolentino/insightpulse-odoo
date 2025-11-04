# InsightPulse Odoo - Complete Deployment Guide

**One-shot deployment for all services: Docs, RAG, Supabase, Odoo, DO App Platform**

---

## Quick Start (TL;DR)

```bash
# Set secrets in environment
export CR_PAT="ghp_..."
export SUPABASE_ACCESS_TOKEN="sbp_..."
export DIGITALOCEAN_ACCESS_TOKEN="dop_..."
export SUPABASE_ANON_KEY="eyJ..."
export RAG_REINDEX_TOKEN="..."

# Deploy everything
make deploy-now

# Or deploy specific components
make deploy-fast        # Odoo image + DO App only
make deploy-db          # Supabase only
make deploy-docs        # Documentation only
```

---

## Prerequisites

### 1. Required Tools

```bash
# macOS
brew install gh doctl docker supabase

# Verify installation
gh --version
doctl version
docker --version
supabase --version
```

### 2. Authentication

```bash
# GitHub CLI
gh auth login

# DigitalOcean
doctl auth init

# Supabase
supabase login

# Docker (for GHCR)
echo "$CR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin
```

### 3. Required Secrets

Create these secrets in your environment or GitHub Secrets:

| Secret | Description | Get From |
|--------|-------------|----------|
| `CR_PAT` | GitHub Container Registry token | https://github.com/settings/tokens |
| `SUPABASE_ACCESS_TOKEN` | Supabase API token | https://app.supabase.com/account/tokens |
| `SUPABASE_ANON_KEY` | Supabase anon key | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Supabase Dashboard → Settings → API |
| `DIGITALOCEAN_ACCESS_TOKEN` | DigitalOcean API token | https://cloud.digitalocean.com/account/api/tokens |
| `RAG_REINDEX_TOKEN` | RAG reindex webhook token | (Optional) Custom token for RAG |

---

## Deployment Methods

### Method 1: Makefile (Recommended)

**Full deployment:**
```bash
make deploy-now
```

**What it does:**
1. Validates all secrets are set
2. Triggers GitHub Actions workflows (docs, RAG)
3. Deploys Supabase migrations and edge functions
4. Builds and pushes Odoo Docker image to GHCR
5. Updates DigitalOcean App Platform
6. Runs health checks on all services

**Partial deployments:**
```bash
make deploy-fast          # Odoo + DO only
make deploy-db            # Supabase only
make deploy-docs          # Docs only
make setup-ph-localization # PH accounting setup
```

**Monitoring:**
```bash
make deployment-status    # Check DO deployment
make logs                 # Tail DO App logs
make odoo-logs           # Tail Odoo droplet logs
make health-check        # Run health checks
```

### Method 2: GitHub Actions (Automatic)

**On every push to main:**
```bash
git push origin main
# Automatically triggers .github/workflows/deploy-unified.yml
```

**Manual trigger:**
```bash
gh workflow run deploy-unified.yml --ref main
```

**Monitor workflow:**
```bash
gh run list --workflow deploy-unified.yml
gh run watch
```

### Method 3: Manual Step-by-Step

**Step 1: Supabase**
```bash
supabase link --project-ref spdtwktxdalcfigzeqrz
supabase db push
supabase functions deploy search
supabase functions deploy answer
supabase functions deploy ingest
```

**Step 2: Build Odoo Image**
```bash
COMMIT=$(git rev-parse --short HEAD)
IMAGE="ghcr.io/jgtolentino/insightpulse-odoo:prod-$COMMIT"

echo "$CR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin
docker build -f ops/odoo/Dockerfile -t "$IMAGE" .
docker push "$IMAGE"
docker tag "$IMAGE" ghcr.io/jgtolentino/insightpulse-odoo:latest-prod
docker push ghcr.io/jgtolentino/insightpulse-odoo:latest-prod
```

**Step 3: Update DigitalOcean App**
```bash
doctl apps update b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 --spec infra/do/ade-ocr-service.yaml
doctl apps create-deployment b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
```

**Step 4: Health Checks**
```bash
curl -I https://erp.insightpulseai.net/web/login
curl -I https://ade-ocr-backend-d9dru.ondigitalocean.app/health
```

---

## Philippine Accounting Localization

### Quick Setup

```bash
# On the ERP droplet
ssh root@165.227.10.178
cd /opt/insightpulse-odoo
chmod +x scripts/setup-ph-localization.sh
./scripts/setup-ph-localization.sh
```

**Or via Makefile:**
```bash
make setup-ph-localization
make verify-ph-localization
```

### What It Does

1. ✅ Installs `l10n_ph` (Philippine Chart of Accounts)
2. ✅ Installs `l10n_ph_withholding` (EWT/2307) if available
3. ✅ Loads Philippine tax configurations (VAT 12%, Zero-rated, Exempt)
4. ✅ Creates default journals and fiscal positions
5. ✅ Runs verification tests

### Manual Configuration (Required)

After running the script, complete these steps in Odoo web interface:

**1. Company Settings**
```
Settings → Companies → Your Company
- Country: Philippines
- Currency: PHP
- TIN: (your BIR TIN)
```

**2. Tax Configuration**
```
Accounting → Configuration → Taxes
Verify:
- VAT 12% (Sales and Purchase)
- Zero-rated 0%
- VAT Exempt
- EWT rates (1%, 2%, 5%, 10%)
```

**3. Fiscal Positions**
```
Accounting → Configuration → Fiscal Positions
Create:
- Domestic VATable
- Zero-rated (Export)
- VAT Exempt
```

**4. Test Transaction**
```
Create test invoice → Verify VAT 12% calculates correctly
Check: Tax Report shows correct figures
```

### BIR Forms

**Required Monthly/Quarterly Forms:**
- 1601-C (Monthly Withholding Tax)
- 1601-F (Monthly Final Withholding Tax)
- 2550Q (Quarterly VAT Return)
- 1702-RT (Annual Income Tax Return)

**Notes:**
- Base `l10n_ph` provides Chart of Accounts and taxes
- BIR form templates may require custom reports or OCA modules
- eFiling integration requires third-party service

---

## Health Checks

### Automated Health Check

```bash
make health-check
```

**Checks:**
- ✅ Odoo ERP (https://erp.insightpulseai.net)
- ✅ Documentation (if deployed)
- ✅ Supabase Edge Functions
- ✅ OCR Service (if deployed)

### Manual Health Checks

**Odoo ERP:**
```bash
curl -I https://erp.insightpulseai.net/web/login
# Expected: HTTP/2 200 or 303
```

**Supabase Edge Functions:**
```bash
curl -sS -X POST "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/search" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"health check","k":1}'
# Expected: JSON response
```

**DigitalOcean App:**
```bash
doctl apps deployments list b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 --format Phase --no-header
# Expected: ACTIVE
```

---

## Monitoring & Logs

### View Logs

**DigitalOcean App:**
```bash
make logs
# Or directly:
doctl apps logs b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 --follow
```

**Odoo Droplet:**
```bash
make odoo-logs
# Or directly:
ssh root@165.227.10.178 "journalctl -u odoo16 -f"
```

### Check Deployment Status

```bash
make deployment-status
# Or directly:
doctl apps deployments list b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
```

---

## Rollback Procedures

### Quick Rollback (DigitalOcean)

```bash
make rollback
```

**What it does:**
- Identifies previous successful deployment
- Rolls back DO App to that deployment
- Preserves database (no data loss)

### Manual Rollback

```bash
# List recent deployments
doctl apps deployments list b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9

# Rollback to specific deployment
doctl apps deployments rollback b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 <DEPLOYMENT_ID>
```

### Docker Image Rollback

```bash
# List recent image tags
doctl registry repository list-tags insightpulse-odoo

# Update app to use specific tag
# Edit infra/do/ade-ocr-service.yaml → change image tag
doctl apps update b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 --spec infra/do/ade-ocr-service.yaml
```

---

## Troubleshooting

### Common Issues

**1. "Dockerfile not found"**
```bash
# Create missing Dockerfile
mkdir -p ops/odoo
cp ops/odoo/Dockerfile.example ops/odoo/Dockerfile
```

**2. "Database does not exist"**
```bash
# Create production database first
# URL: https://erp.insightpulseai.net/web/database/manager
# Master Password: 2ca2a768b7c9016f52364921bb78ab2a359da05a23dd0bf1
```

**3. "Permission denied" on Docker**
```bash
# Add user to docker group (macOS/Linux)
sudo usermod -aG docker $USER
newgrp docker
```

**4. "Secret not set"**
```bash
# Check environment
env | grep -E "(CR_PAT|SUPABASE|DIGITALOCEAN)"

# Set missing secrets
export CR_PAT="ghp_..."
# Or add to ~/.zshrc for persistence
```

**5. "Deployment stuck in PENDING"**
```bash
# Check deployment logs
make logs

# Check resource limits
doctl apps tier list

# Force new deployment
doctl apps create-deployment b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 --force-rebuild
```

### Debug Commands

```bash
# Show deployment configuration
make info

# Test Supabase connection
supabase status

# Test GitHub authentication
gh auth status

# Test DigitalOcean authentication
doctl account get

# Check Docker images
docker images | grep insightpulse-odoo
```

---

## Security Best Practices

### Secret Rotation

```bash
make rotate-secrets
# Follow the prompts to rotate tokens
```

**Rotation Schedule:**
- GitHub PAT: Every 90 days
- Supabase tokens: Every 180 days
- DigitalOcean tokens: Every 90 days

### Update GitHub Secrets

```bash
gh secret set CR_PAT -R jgtolentino/insightpulse-odoo
gh secret set SUPABASE_ACCESS_TOKEN -R jgtolentino/insightpulse-odoo
gh secret set DIGITALOCEAN_ACCESS_TOKEN -R jgtolentino/insightpulse-odoo
```

---

## Advanced Configuration

### Custom Branch Deployment

```bash
BRANCH=feature/new-module make deploy-now
```

### Staging Environment

```bash
# Create staging app spec
cp infra/do/ade-ocr-service.yaml infra/do/ade-ocr-staging.yaml

# Deploy to staging
DO_APP_ID=<STAGING_APP_ID> make deploy-do-app
```

### Multi-Region Deployment

```bash
# Deploy to Singapore droplet
ODOO_HOST=root@165.227.10.178 make deploy-droplet

# Deploy to US droplet (if exists)
ODOO_HOST=root@<US_IP> make deploy-droplet
```

---

## CI/CD Integration

### GitHub Actions Workflow

**Already configured:**
`.github/workflows/deploy-unified.yml`

**Triggers:**
- Automatic: Push to `main` branch
- Manual: `gh workflow run deploy-unified.yml`

**What it deploys:**
1. Supabase migrations
2. Supabase edge functions
3. Odoo Docker image to GHCR
4. DigitalOcean App Platform update

### Custom Workflow

```yaml
# .github/workflows/my-custom-deploy.yml
name: Custom Deploy
on:
  workflow_dispatch:
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: make deploy-now
```

---

## Performance Optimization

### Docker Build Cache

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Use cache from registry
docker build --cache-from ghcr.io/jgtolentino/insightpulse-odoo:latest-prod \
  -t ghcr.io/jgtolentino/insightpulse-odoo:latest-prod .
```

### Parallel Deployments

```bash
# Deploy Supabase and build image in parallel
make deploy-supabase & make deploy-odoo-image & wait
```

---

## Support & Resources

**Documentation:**
- Makefile: `make help`
- This file: `DEPLOYMENT_GUIDE.md`
- PH Localization: `scripts/setup-ph-localization.sh`

**Monitoring:**
- Odoo: https://erp.insightpulseai.net
- DO Console: https://cloud.digitalocean.com/apps/b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
- Supabase: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz

**Contact:**
- Email: jgtolentino_rn@yahoo.com
- GitHub: https://github.com/jgtolentino/insightpulse-odoo

---

**Status:** ✅ Production Ready
**Last Updated:** 2025-11-04
**Version:** 1.0.0
