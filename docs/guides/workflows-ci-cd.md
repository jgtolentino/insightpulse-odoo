# CI/CD Workflows

GitHub Actions workflows for InsightPulse Odoo platform.

## Workflow Overview

**CI Workflows** (Pull Requests):
- `ci-odoo.yml` - Build+test Odoo Docker image
- `ci-supabase.yml` - Apply Supabase migrations against ephemeral DB
- `ci-superset.yml` - Import dashboards and validate Superset config
- `docs-ci.yml` - Validate docs links and structure

**CD Workflows** (Push to main):
- `cd-odoo-prod.yml` - Deploy to production droplet
- `pages-deploy.yml` - Build and deploy GitHub Pages

**Spec Guard** (PR + Push):
- `spec-guard.yml` - Validate platform_spec.json and file existence

## CI Workflow Details

### ci-odoo.yml
- **Triggers**: PR, push to main
- **Responsibility**: Build+test Odoo Docker image and run tests
- **Steps**:
  1. Checkout code
  2. Build Docker image
  3. Run Odoo tests
  4. Validate module structure

### ci-supabase.yml
- **Triggers**: PR on supabase/**, warehouse/**
- **Responsibility**: Apply Supabase migrations against ephemeral DB
- **Steps**:
  1. Checkout code
  2. Setup ephemeral Supabase instance
  3. Apply migrations
  4. Validate schema

### ci-superset.yml
- **Triggers**: PR on apps/superset/**, superset/**
- **Responsibility**: Import dashboards and validate Superset config
- **Steps**:
  1. Checkout code
  2. Setup Superset
  3. Import dashboards
  4. Validate configuration

### docs-ci.yml
- **Triggers**: PR + push on docs/**, spec/**
- **Responsibility**: Validate docs links and structure
- **Steps**:
  1. Checkout code
  2. Validate internal links
  3. Check broken references
  4. Verify spec-kit compliance

## CD Workflow Details

### cd-odoo-prod.yml
- **Triggers**: Push to main on odoo/**, scripts/deploy/**, docker-compose*.yml
- **Responsibility**: Deploy to production droplet using scripts/deploy/deploy-all.sh
- **Target**: DigitalOcean droplet ipai-odoo-erp (165.227.10.178, SFO2)
- **Steps**:
  1. Checkout code
  2. Build production Docker image
  3. Deploy to droplet via SSH
  4. Run health checks
  5. Notify on success/failure

### pages-deploy.yml
- **Triggers**: Push to main on docs/**
- **Responsibility**: Build and deploy GitHub Pages site from docs
- **Steps**:
  1. Checkout code
  2. Build Jekyll site
  3. Deploy to gh-pages branch
  4. Verify deployment

## Spec Guard Workflow

### spec-guard.yml
- **Triggers**: PR + push on spec/**, docs/**, .github/workflows/**
- **Responsibility**: Validate platform_spec.json and ensure referenced files exist
- **Steps**:
  1. Checkout code
  2. Install jsonschema
  3. Run scripts/validate_spec.py
  4. Fail if validation errors

**Exit Codes**:
- 0: All validations passed
- 1: Schema validation failed
- 2: Referenced files missing
- 3: JSON parsing error

## Local Testing

```bash
# Validate spec
python scripts/validate_spec.py

# Run specific workflow
act -j ci-odoo  # requires act CLI

# Test Docker build
docker compose build odoo

# Test Supabase migrations
supabase db reset
```

## Best Practices

1. **Always validate locally** before pushing
2. **Keep workflows minimal** - skeleton first, enhance iteratively
3. **Never weaken guardrails** - spec-guard must always pass
4. **CD only on main** - no branch deployments
5. **Follow Odoo.sh policy** - reference_only, never step-by-step guides

## References

- [Platform Spec](../spec-kit/PRD_PLATFORM.md)
- [Deployment Guide](../deployments/overview.md)
- [Docker Compose Guide](docker-compose.md)
