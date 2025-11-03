# Deployment Consolidation Guide

**Date**: 2025-11-02
**Status**: ✅ Complete

## 🎯 Overview

This document tracks the consolidation of deployment configurations across the InsightPulse platform to eliminate duplication and provide a single source of truth.

---

## 📋 Changes Made

### 1. Unified Deployment Script

**Created**: `scripts/deploy-unified.sh`

Single master script that handles all deployment scenarios:
- Full platform deployment
- Individual service deployment (Odoo, Superset, PaddleOCR, Traefik)
- Environment selection (production, staging)
- Health checks and monitoring

**Usage**:
```bash
# Full deployment
./scripts/deploy-unified.sh full production

# Deploy individual services
./scripts/deploy-unified.sh odoo production
./scripts/deploy-unified.sh superset production
./scripts/deploy-unified.sh paddleocr production
./scripts/deploy-unified.sh traefik production

# Staging environment
./scripts/deploy-unified.sh odoo staging
```

### 2. Directory Structure (Consolidated)

**Before** (Duplicated):
```
deploy/
├── odoo.bundle.yml              # Duplicate
├── superset.compose.yml         # Duplicate
├── superset/
│   ├── deploy.sh               # Old script
│   └── traefik.yml             # Duplicate
└── sql/

infra/
├── do/
│   ├── odoo-saas-platform.yaml  # Canonical
│   └── deploy-production.sh    # Old script
├── superset/
│   ├── superset-app.yaml        # Canonical
│   ├── superset-official.yaml   # Duplicate
│   └── superset-single.yaml     # Duplicate
├── paddleocr/
│   └── deploy-droplet.sh        # Canonical
└── reverse-proxy/
    └── deploy.sh                # Canonical

scripts/
├── deploy-to-production.sh      # Old script
├── deploy-check.sh              # Keep (validation)
└── deploy-complete-architecture.sh  # Old script
```

**After** (Consolidated):
```
infra/                           # Single source of truth
├── do/
│   ├── odoo-saas-platform.yaml          # ✅ Canonical Odoo spec
│   └── odoo-saas-platform-staging.yaml  # ✅ Staging spec
├── superset/
│   └── superset-app.yaml                # ✅ Canonical Superset spec
├── paddleocr/
│   ├── deploy-droplet.sh                # ✅ PaddleOCR deployment
│   ├── setup-server.sh                  # ✅ Server setup
│   ├── docker-compose.yml               # ✅ Container config
│   └── app/                             # ✅ Application code
└── reverse-proxy/
    ├── deploy.sh                        # ✅ Traefik deployment
    ├── traefik.yml                      # ✅ Static config
    ├── dynamic.yml                      # ✅ Dynamic routing
    └── docker-compose.yml               # ✅ Container config

scripts/
├── deploy-unified.sh            # ✅ Master deployment script
└── deploy-check.sh              # ✅ Pre-deployment validation

.github/workflows/
└── ai-auto-commit.yml           # ✅ Automated deployments
```

### 3. Deprecated Files

The following files are now deprecated and should be removed:

**Old Deployment Scripts**:
- `scripts/deploy-to-production.sh` → Use `scripts/deploy-unified.sh odoo`
- `scripts/deploy-complete-architecture.sh` → Use `scripts/deploy-unified.sh full`
- `infra/do/deploy-production.sh` → Use `scripts/deploy-unified.sh odoo`
- `infra/do/deploy-staging.sh` → Use `scripts/deploy-unified.sh odoo staging`
- `deploy/superset/deploy.sh` → Use `scripts/deploy-unified.sh superset`

**Duplicate Configurations**:
- `deploy/odoo.bundle.yml` → Use `infra/do/odoo-saas-platform.yaml`
- `deploy/superset.compose.yml` → Use `infra/superset/superset-app.yaml`
- `infra/superset/superset-official.yaml` → Use `infra/superset/superset-app.yaml`
- `infra/superset/superset-single.yaml` → Use `infra/superset/superset-app.yaml`

**Old Reverse Proxy Config**:
- `deploy/superset/traefik.yml` → Use `infra/reverse-proxy/traefik.yml`

### 4. Archive Plan

Create an archive directory for old files:

```bash
# Create archive
mkdir -p archive/deploy-old
mkdir -p archive/scripts-old
mkdir -p archive/infra-old

# Move deprecated files
mv deploy/ archive/deploy-old/
mv scripts/deploy-to-production.sh archive/scripts-old/
mv scripts/deploy-complete-architecture.sh archive/scripts-old/
mv infra/do/deploy-*.sh archive/infra-old/
mv infra/superset/superset-official.yaml archive/infra-old/
mv infra/superset/superset-single.yaml archive/infra-old/
```

---

## 🗺️ Canonical Deployment Paths

### Production Deployment

**Full Platform**:
```bash
./scripts/deploy-unified.sh full production
```

**Individual Services**:
```bash
# Odoo ERP
./scripts/deploy-unified.sh odoo production

# Superset Dashboard
./scripts/deploy-unified.sh superset production

# PaddleOCR Service
./scripts/deploy-unified.sh paddleocr production

# Traefik Reverse Proxy
./scripts/deploy-unified.sh traefik production
```

### CI/CD Deployment

**GitHub Actions Workflow**:
`.github/workflows/ai-auto-commit.yml`

Automatically triggers deployments on push to `main`:
- Odoo ERP deployment
- Superset deployment
- Creates deployment notifications

### Manual Deployment

**Direct doctl Commands**:
```bash
# Odoo
doctl apps create --spec infra/do/odoo-saas-platform.yaml
doctl apps create-deployment <APP_ID> --force-rebuild

# Superset
doctl apps create --spec infra/superset/superset-app.yaml
doctl apps create-deployment <APP_ID> --force-rebuild
```

---

## 📚 Documentation Updates

### Updated Documentation

1. **`infra/UNIFIED_DEPLOYMENT_ARCHITECTURE.md`**
   - Complete platform architecture
   - Deployment procedures
   - Cost breakdown
   - Security considerations

2. **`.github/workflows/README.md`**
   - CI/CD workflow setup
   - GitHub App configuration
   - Automated deployments

3. **`infra/mobile/MOBILE_APP_SPECIFICATION.md`**
   - Mobile app architecture
   - Integration with backend services
   - Deployment to App Store/Play Store

4. **This file (`DEPLOYMENT_CONSOLIDATION.md`)**
   - Consolidation changes
   - Migration guide
   - Deprecation notices

---

## 🔄 Migration Guide

### For Developers

**Old Command** → **New Command**:

```bash
# Old: Deploy to production droplet
./scripts/deploy-to-production.sh
# New: Use unified script
./scripts/deploy-unified.sh odoo production

# Old: Deploy complete architecture
./scripts/deploy-complete-architecture.sh
# New: Use unified script
./scripts/deploy-unified.sh full production

# Old: Deploy Superset
cd deploy/superset && ./deploy.sh
# New: Use unified script
./scripts/deploy-unified.sh superset production

# Old: Deploy with blue-green
./infra/do/deploy-production.sh
# New: Use DO App Platform automatic blue-green
./scripts/deploy-unified.sh odoo production
```

### For CI/CD Pipelines

**Update your automation**:
- Replace individual deployment scripts with `scripts/deploy-unified.sh`
- Or use `.github/workflows/ai-auto-commit.yml` for automated deployments

### For New Team Members

**Single entry point**:
```bash
# Read the docs
cat infra/UNIFIED_DEPLOYMENT_ARCHITECTURE.md

# Deploy everything
./scripts/deploy-unified.sh full production

# Done!
```

---

## ✅ Validation Checklist

- [x] Created unified deployment script (`scripts/deploy-unified.sh`)
- [x] Consolidated infra configs to `infra/` directory
- [x] Identified duplicate files for removal
- [x] Documented canonical deployment paths
- [x] Created migration guide
- [x] Updated CI/CD workflows
- [x] Added comprehensive documentation

---

## 🔮 Future Improvements

### Phase 1: Cleanup (This PR)
- [x] Create unified deployment script
- [x] Document consolidation
- [ ] Archive old files
- [ ] Update references in code

### Phase 2: Automation
- [ ] Add deployment rollback command
- [ ] Implement automatic health checks
- [ ] Add deployment notifications (Slack/Email)
- [ ] Create deployment dashboard

### Phase 3: Kubernetes (Future)
- [ ] Helm charts for Odoo
- [ ] Helm charts for Superset
- [ ] Kubernetes deployment scripts
- [ ] Auto-scaling configurations

---

## 📞 Support

For deployment questions or issues:

1. **Documentation**: Review `infra/UNIFIED_DEPLOYMENT_ARCHITECTURE.md`
2. **Unified Script**: Run `./scripts/deploy-unified.sh` (shows usage)
3. **CI/CD**: Check `.github/workflows/README.md`
4. **Team**: Contact DevOps at devops@insightpulseai.net

---

## 📝 Changelog

### 2025-11-02 - Initial Consolidation
- Created unified deployment script
- Documented all duplicate files
- Established canonical deployment paths
- Created migration guide
- Updated documentation

---

**Maintained By**: InsightPulse DevOps Team
**Last Updated**: 2025-11-02
**Version**: 2.0.0
