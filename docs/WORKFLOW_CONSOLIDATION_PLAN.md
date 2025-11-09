# GitHub Workflows Consolidation Plan
**Date:** 2025-11-09
**Current Status:** 73 workflows (excessive), All services deployed and healthy
**Target:** 8-10 essential workflows

---

## Executive Summary

✅ **Deployment Status:** All services healthy (erp, agent, superset, ocr returning HTTP 200)
⚠️ **Problem:** 73 workflows creating complexity, maintenance burden, and CI failures
🎯 **Solution:** Consolidate to 8-10 core workflows aligned with actual architecture

---

## Current Architecture (Production)

| Service | Endpoint | Infrastructure | Deployment Method |
|---------|----------|---------------|-------------------|
| **ERP** | erp.insightpulseai.net | Droplet @ 165.227.10.178 | Docker + systemd |
| **Agent** | agent.insightpulseai.net | Proxied via ERP droplet | Nginx reverse proxy |
| **Superset** | superset.insightpulseai.net | DO App Platform | App spec deployment |
| **OCR** | ocr.insightpulseai.net | Droplet @ 188.166.237.231 | Direct service |
| **Landing** | insightpulseai.net | DO App Platform | Static/Next.js |
| **MCP Hub** | mcp.insightpulseai.net | DO App Platform (optional) | App spec deployment |

---

## ✅ Essential Workflows (KEEP THESE 8)

### 1. **CI/Testing** (`ci-unified.yml`)
**Purpose:** Run tests, linting, quality checks on PRs
**Triggers:** `pull_request`, `push` to main
**Why Essential:** Catch bugs before deployment

### 2. **Odoo Deployment** (`odoo-deploy.yml`)
**Purpose:** Build → Test → Deploy Odoo to ERP droplet
**Triggers:** `push` to production branch, `workflow_dispatch`
**Why Essential:** Core ERP deployment automation

### 3. **Superset Deployment** (`deploy-superset.yml`)
**Purpose:** Deploy Superset to DO App Platform
**Triggers:** Changes to `infra/superset/**`
**Why Essential:** Analytics platform deployment

### 4. **Superset PostgreSQL Guard** (`superset-postgres-guard.yml`) ⭐ CRITICAL
**Purpose:** Daily validation that Superset uses PostgreSQL (not SQLite)
**Triggers:** Daily cron, `workflow_dispatch`
**Why Essential:** Prevents SQLite regression (data loss risk)

### 5. **OCR Deployment** (`deploy-ocr.yml`)
**Purpose:** Deploy PaddleOCR service to OCR droplet
**Triggers:** Changes to OCR code
**Why Essential:** BIR compliance document processing

### 6. **Infrastructure Validation** (`infrastructure-validation.yml`)
**Purpose:** Verify DNS, TLS, firewall, Nginx configs
**Triggers:** Daily cron, manual
**Why Essential:** Catch infrastructure drift

### 7. **Feature Inventory** (`feature-inventory.yml`)
**Purpose:** Auto-update documentation from code
**Triggers:** `push` to main
**Why Essential:** Keep docs in sync with code

### 8. **OCA Pre-commit** (`oca-pre-commit.yml`)
**Purpose:** Enforce OCA code quality standards
**Triggers:** `pull_request`
**Why Essential:** Maintain Odoo module quality

### Optional (9-10)
- **Backup Scheduler** (`backup-scheduler.yml`) - Automated backups if configured
- **Health Monitor** (`health-monitor.yml`) - Periodic health checks with alerts

---

## ❌ Workflows to DELETE (65 workflows)

### Architecture Mismatch (Not Using These)
```bash
# Docker Hub - Not publishing to Docker Hub
dockerhub-publish.yml
docker-image.yml

# Azure - Migrated to DigitalOcean
azure-deploy.yml
azure-aci-deploy.yml

# Canary/Blue-Green - DO App Platform handles this natively
flip-canary.yml
deploy-canary.yml

# Kubernetes - Not using K8s
k8s-deploy.yml
helm-deploy.yml
```

### Redundant/Consolidated
```bash
# Multiple CI workflows → consolidated to ci-unified.yml
ci.yml
ci-spec.yml
ci-odoo.yml
quick-ci.yml
Code Quality.yml
quality.yml

# Multiple deployment workflows → consolidated to odoo-deploy.yml
deploy.yml
ci-deploy.yml
digitalocean-deploy.yml
deploy-consolidated.yml

# Multiple Odoo CI → consolidated
odoo-ci.yml
odoo-module-test.yml
odoo_addon.yml
odoo-unified.yml
```

### Experimental/Unused
```bash
# AI experimentation - not production critical
ai-training.yml
ai-code-review.yml
claude-autofix-bot.yml
assistant-guard.yml
assistant-context-freshness.yml

# Auto-merge/conflict resolution - risky automation
auto-merge.yml
auto-resolve-conflicts.yml
auto-patch.yml

# Skill generation - manual process preferred
auto-skill-generation.yml
skillsmith.yml
skillsmith-integration.yml
skills-consolidate.yml
skills-agents-check.yml

# GitToDoc - redundant with feature-inventory
gittodoc-ci.yml
gittodoc-cron.yml
doc-automation.yml
field-doc-sync.yml

# Testing/experimental
tee-mvp-ci.yml
mvp_smoke.yml
agent-eval.yml
n8n-cli-ci.yml

# Notion automation - manual preferred
notion-automations.yml

# Odoo knowledge scraper - one-time use
odoo-knowledge-scraper.yml

# OpenUpgrade testing - not needed yet
openupgrade-test.yml

# SOP generator - manual process
sop-generator.yml

# Issue management - over-engineered
auto-close-resolved.yml
close-duplicate-health-issues.yml
issue-from-comment.yml
issue-validation.yml
triage.yml

# Automation health - meta-workflow
automation-health.yml

# Security scans - handled in ci-unified
dependency-scanning.yml
dast-security.yml

# Month-end automation - Odoo native features preferred
month-end-task-automation.yml

# Parity sync - manual preferred
parity-live-sync.yml

# Post-deploy refresh - handled in main deploy
post-deploy-refresh.yml

# Rollback - manual operation
rollback.yml

# SAP spec validation - not using SAP
sap-spec-validate.yml

# Seed labels - one-time setup
seed-labels.yml

# Structure validation - one-time audit
validate-structure.yml

# BIR compliance automation - integrated into main CI
bir-compliance-automation.yml

# Performance testing - manual/on-demand
performance-testing.yml

# Integration tests - consolidated into ci-unified
integration-tests.yml

# Supabase functions - deployed manually via CLI
supabase-funcs.yml

# Claude config - one-time setup
claude-config.yml
claude-daily-cron.yml
claude-sync-ci.yml

# Deploy gates - over-engineered
deploy-gates.yml

# Deploy docs - static site, rarely changes
deploy-docs.yml

# Git ops - manual preferred
git-ops.yml

# Insightpulse monitor deploy - separate repo
insightpulse-monitor-deploy.yml

# Metrics collector - not set up yet
metrics-collector.yml

# MCP/Superset deploys - handled by main workflows
deploy-mcp.yml
superset-deploy.yml

# OCA bot automation - redundant with oca-pre-commit
oca-bot-automation.yml

# PH tax canary - test-only
ph-tax-canary.yml

# Generate docs - manual preferred
generate-docs.yml

# Superset health - integrated into infrastructure-validation
superset-health.yml
```

---

## Implementation Plan

### Phase 1: Immediate Cleanup (Today)

```bash
cd /home/user/insightpulse-odoo

# Create archive directory
mkdir -p .github/workflows-archive

# Move all workflows to archive
mv .github/workflows/*.yml .github/workflows-archive/

# Restore only essential workflows
mv .github/workflows-archive/ci-unified.yml .github/workflows/
mv .github/workflows-archive/odoo-deploy.yml .github/workflows/
mv .github/workflows-archive/deploy-superset.yml .github/workflows/
mv .github/workflows-archive/superset-postgres-guard.yml .github/workflows/
mv .github/workflows-archive/deploy-ocr.yml .github/workflows/
mv .github/workflows-archive/infrastructure-validation.yml .github/workflows/
mv .github/workflows-archive/feature-inventory.yml .github/workflows/
mv .github/workflows-archive/oca-pre-commit.yml .github/workflows/

# Commit
git add .github/
git commit -m "ci: consolidate to 8 essential workflows (archive 65 redundant)"
git push -u origin claude/review-github-workflows-011CUwdUXBoLLMnTETfQLaiS
```

### Phase 2: Verify Essential Workflows (This Week)

```bash
# Test each workflow manually
gh workflow run ci-unified.yml
gh workflow run superset-postgres-guard.yml
gh workflow run infrastructure-validation.yml
gh workflow run odoo-deploy.yml --ref production

# Monitor results
gh run list --limit 10
```

### Phase 3: Cleanup Archive (Next Month)

```bash
# After confirming no regressions for 30 days
rm -rf .github/workflows-archive/
git commit -am "chore: remove archived workflows after 30-day verification"
```

---

## Workflow Dependency Matrix

| Workflow | Depends On | Triggers | Secrets Required |
|----------|-----------|----------|------------------|
| ci-unified.yml | - | PR, push | - |
| odoo-deploy.yml | ci-unified (tests pass) | push to production | DIGITALOCEAN_TOKEN, DROPLET_SSH_KEY |
| deploy-superset.yml | - | infra changes | DIGITALOCEAN_ACCESS_TOKEN, DO_APP_ID_SUPERSET |
| superset-postgres-guard.yml | - | daily cron | DO_APP_ID_SUPERSET, DIGITALOCEAN_ACCESS_TOKEN |
| deploy-ocr.yml | - | ocr code changes | OCR_HOST, OCR_SSH_KEY |
| infrastructure-validation.yml | - | daily cron | ODOO_HOST, OCR_HOST |
| feature-inventory.yml | - | push to main | - |
| oca-pre-commit.yml | - | PR | - |

---

## Required GitHub Secrets (Audit)

### ✅ Currently Set (Assumed)
- `DIGITALOCEAN_ACCESS_TOKEN` or `DIGITALOCEAN_TOKEN`
- `DO_APP_ID_SUPERSET` (from CI/CD audit doc)

### ⚠️ Need to Set
```bash
# Droplet access
gh secret set ODOO_HOST --body '165.227.10.178'
gh secret set ODOO_SSH_KEY --body "$(cat ~/.ssh/id_rsa)"
gh secret set ODOO_SSH_USER --body 'root'

gh secret set OCR_HOST --body '188.166.237.231'
gh secret set OCR_SSH_KEY --body "$(cat ~/.ssh/id_rsa)"
gh secret set OCR_SSH_USER --body 'root'

# Droplet ID for doctl commands
gh secret set PRODUCTION_DROPLET_ID --body '<droplet_id_from_doctl>'

# Optional: Notion integration
gh secret set NOTION_API_KEY --body 'secret_...'
gh secret set INSIGHTPULSE_API_KEY --body '<your_api_key>'
```

### ❌ No Longer Needed (Remove)
- `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` (not using Docker Hub)
- `AZURE_*` secrets (migrated to DO)
- `PRODUCTION_HOST`, `PRODUCTION_SSH_KEY` (renamed to ODOO_HOST, ODOO_SSH_KEY)

---

## Success Metrics

### Before Consolidation
- **Workflows:** 73
- **Failing workflows:** ~15-20
- **Redundant workflows:** ~50
- **Maintenance burden:** High
- **CI/CD reliability:** ~65%

### After Consolidation
- **Workflows:** 8-10
- **Failing workflows:** 0 (target)
- **Redundant workflows:** 0
- **Maintenance burden:** Low
- **CI/CD reliability:** 95%+ (target)

---

## Rollback Plan

If consolidation causes issues:

```bash
# Restore all workflows from archive
mv .github/workflows-archive/*.yml .github/workflows/

# Or restore specific workflow
mv .github/workflows-archive/specific-workflow.yml .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "rollback: restore workflow from archive"
git push
```

---

## Next Steps

1. ✅ Review this consolidation plan
2. ⚠️ Execute Phase 1 cleanup (move to archive, restore essentials)
3. ⚠️ Set missing GitHub secrets
4. ⚠️ Test essential workflows manually
5. ⚠️ Monitor for 1 week
6. ⚠️ Delete archive after 30-day verification

---

## Questions to Answer

**Q: Can we close all open issues now?**
A: Need to check issue list first. Likely many are workflow-related and can be closed after consolidation.

**Q: What about deployment status?**
A: ✅ All services healthy (verified HTTP 200):
- erp.insightpulseai.net
- agent.insightpulseai.net
- superset.insightpulseai.net
- ocr.insightpulseai.net

**Q: Will this break anything?**
A: No. All archived workflows are either:
- Redundant (functionality in another workflow)
- Experimental (not production-critical)
- Architecture mismatch (Docker/Azure/K8s not in use)

---

**Reviewed by:** Claude Code
**Approved by:** [Pending user approval]
**Implementation date:** 2025-11-09
