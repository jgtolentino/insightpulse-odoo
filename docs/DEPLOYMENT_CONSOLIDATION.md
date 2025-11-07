# Deployment Workflow Consolidation

**Date**: 2025-11-06
**Issue**: #305 - Consolidate 3 Odoo Deployment Workflows

## Summary

Three redundant deployment workflows have been consolidated into a single, unified deployment pipeline.

## Changes

### Deprecated Workflows ❌

These workflows are no longer active and have been renamed with `.deprecated` suffix:

1. **deploy-odoo.yml** → `deploy-odoo.yml.deprecated`
   - Single-purpose Odoo deployment to droplet
   - Used DigitalOcean Container Registry
   - SSH-based deployment

2. **deploy-unified.yml** → `deploy-unified.yml.deprecated`
   - Full-stack deployment
   - Included Supabase, Odoo, and Superset
   - Used GitHub Container Registry

3. **production-deploy.yml** → `production-deploy.yml.deprecated`
   - Production-only deployment
   - Triggered after dockerhub-publish
   - Included rollback capability

### New Consolidated Workflow ✅

**File**: `.github/workflows/deploy-consolidated.yml`

**Features**:
- ✅ Single workflow for all deployment needs
- ✅ Environment selection (production/staging)
- ✅ Component selection (full-stack, odoo-only, supabase-only, superset-only)
- ✅ Automatic and manual triggers
- ✅ Health checks and smoke tests
- ✅ Database backup before deployment
- ✅ Slack notifications
- ✅ Comprehensive deployment summary

## Usage

### Automatic Deployment

The workflow automatically triggers on:
- Push to `main` branch → Production deployment
- Push to `staging` branch → Staging deployment
- Changes to: `services/**`, `ops/**`, `infra/**`

### Manual Deployment

```bash
# Full stack production deployment
gh workflow run deploy-consolidated.yml \
  -f environment=production \
  -f deployment_type=full-stack

# Odoo-only deployment to staging
gh workflow run deploy-consolidated.yml \
  -f environment=staging \
  -f deployment_type=odoo-only

# Deploy with specific image tag
gh workflow run deploy-consolidated.yml \
  -f environment=production \
  -f deployment_type=odoo-only \
  -f image_tag=prod-abc1234

# Deploy and skip smoke tests
gh workflow run deploy-consolidated.yml \
  -f environment=staging \
  -f deployment_type=full-stack \
  -f skip_tests=true
```

## Deployment Types

### Full Stack (`full-stack`)
Deploys all components:
- Supabase migrations and edge functions
- Odoo ERP application
- Superset dashboards

**Use when**: Deploying comprehensive updates affecting multiple services

### Odoo Only (`odoo-only`)
Deploys only:
- Odoo Docker image build
- Odoo container deployment
- Health checks

**Use when**: Making Odoo-specific changes without affecting other services

### Supabase Only (`supabase-only`)
Deploys only:
- Database migrations
- Edge functions

**Use when**: Database schema changes or edge function updates

### Superset Only (`superset-only`)
Deploys only:
- Superset dashboards

**Use when**: Dashboard configuration updates

## Migration Guide

### If you were using `deploy-odoo.yml`:

**Before**:
```yaml
# Automatically deployed on push to services/odoo/**
```

**After**:
```bash
# Automatically deployed on push to services/**
# Or manually trigger:
gh workflow run deploy-consolidated.yml -f deployment_type=odoo-only
```

### If you were using `deploy-unified.yml`:

**Before**:
```bash
gh workflow run deploy-unified.yml -f env=prod
```

**After**:
```bash
gh workflow run deploy-consolidated.yml \
  -f environment=production \
  -f deployment_type=full-stack
```

### If you were using `production-deploy.yml`:

**Before**:
```bash
# Triggered automatically after dockerhub-publish
gh workflow run production-deploy.yml -f image_tag=latest
```

**After**:
```bash
gh workflow run deploy-consolidated.yml \
  -f environment=production \
  -f deployment_type=odoo-only \
  -f image_tag=latest
```

## Benefits

### Before Consolidation
- ❌ 3 separate workflows to maintain
- ❌ Inconsistent deployment logic
- ❌ Duplicate code and configuration
- ❌ Confusion about which workflow to use
- ❌ No component selection flexibility

### After Consolidation
- ✅ Single source of truth for deployments
- ✅ Consistent deployment logic across environments
- ✅ Flexible component selection
- ✅ Reduced maintenance burden
- ✅ Clear deployment parameters
- ✅ Better testing and validation

## Workflow Architecture

```
deploy-consolidated.yml
├── setup (determine parameters)
├── build-odoo (conditional)
├── deploy-supabase (conditional)
├── deploy-odoo (conditional)
├── deploy-superset (conditional)
└── summary (always runs)
```

## Configuration

### Environment Variables

| Variable | Description | Production | Staging |
|----------|-------------|------------|---------|
| `DROPLET_IP` | Droplet IP address | `165.227.10.178` | Same |
| `DO_APP_ID` | DigitalOcean App ID | `b1bb1b07...` | `7f7b673b...` |
| `DO_REGISTRY` | Container registry | `registry.digitalocean.com/insightpulse` | Same |

### Required Secrets

- `DIGITALOCEAN_ACCESS_TOKEN` - DigitalOcean API token
- `DROPLET_SSH_KEY` - SSH private key for droplet access
- `ODOO_DB_PASSWORD` - PostgreSQL password
- `SUPABASE_ACCESS_TOKEN` - Supabase CLI token
- `SUPABASE_PROJECT_REF` - Supabase project reference
- `SUPERSET_PASSWORD` - Superset admin password
- `SLACK_WEBHOOK_URL` - (Optional) Slack notifications

## Rollback

For rollback, use the dedicated rollback workflow:

```bash
gh workflow run rollback.yml \
  -f environment=production \
  -f deployment_id=<previous-deployment-id>
```

Or redeploy a previous image tag:

```bash
gh workflow run deploy-consolidated.yml \
  -f environment=production \
  -f deployment_type=odoo-only \
  -f image_tag=prod-abc1234
```

## Monitoring

After deployment, monitor:
- Health endpoints: https://erp.insightpulseai.net/web/login
- Deployment logs: GitHub Actions workflow run
- Container logs: `docker logs odoo` on droplet
- Slack notifications (if configured)

## Cleanup

The deprecated workflows can be safely deleted after verifying the new consolidated workflow works correctly. We recommend:

1. **Keep for 30 days** to ensure no disruption
2. **Monitor the new workflow** in production and staging
3. **Delete deprecated files** after successful validation

```bash
# After 30 days of successful use:
rm .github/workflows/deploy-odoo.yml.deprecated
rm .github/workflows/deploy-unified.yml.deprecated
rm .github/workflows/production-deploy.yml.deprecated
```

## Related Issues
- Issue #305: Consolidate 3 Odoo Deployment Workflows ✅ Completed
- Issue #308: Implement Canary Deployment Strategy (future enhancement)
