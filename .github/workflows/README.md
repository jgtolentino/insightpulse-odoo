# GitHub Actions Workflows - Active Summary

**Last Updated:** 2025-11-09
**Purpose:** Document active workflows and their responsibilities

---

## Production Deployment Workflows

### cd-odoo-prod.yml ✅ **PRIMARY**
- **Trigger:** Push to main (paths: odoo/**, scripts/deploy/**, docker-compose*.yml)
- **Responsibility:** Pull-based production deployment
  - Docker: git pull → docker compose pull → docker compose up -d
  - Portal: Deploy unified SSO page to insightpulseai.net
  - Nginx: Update configuration for portal
  - Smoke tests: ERP + Portal + Auth endpoints
- **Status:** Active - canonical production deployment workflow

### deploy-canary.yml ✅
- **Trigger:** workflow_dispatch (manual)
- **Responsibility:** Canary deployments with progressive traffic shifting
- **Status:** Active - manual canary testing

### deploy-gates.yml ✅
- **Trigger:** pull_request to main, workflow_dispatch
- **Responsibility:** Pre-deployment quality gates and validation
- **Status:** Active - quality gate for PRs

---

## CI/CD Workflows (Spec-Kit)

### spec-guard.yml ✅
- **Trigger:** PR/push affecting spec/**, docs/**, .github/workflows/**
- **Responsibility:** Validate platform_spec.json schema and file existence
- **Status:** Active - spec validation

### ci-odoo.yml ✅
- **Trigger:** pull_request, push to main
- **Responsibility:** Build+test Odoo Docker image
- **Status:** Active - skeleton (to be implemented)

### ci-supabase.yml ✅
- **Trigger:** pull_request
- **Responsibility:** Apply Supabase migrations against ephemeral DB
- **Status:** Active - skeleton (to be implemented)

### ci-superset.yml ✅
- **Trigger:** pull_request
- **Responsibility:** Import dashboards and validate Superset config
- **Status:** Active - skeleton (to be implemented)

### docs-ci.yml ✅
- **Trigger:** push to main, pull_request
- **Responsibility:** Validate docs links and structure
- **Status:** Active - skeleton (to be implemented)

### pages-deploy.yml ✅
- **Trigger:** push to main
- **Responsibility:** Build and deploy GitHub Pages site from docs/
- **Status:** Active - skeleton (to be implemented)

---

## Service-Specific Deployments

### deploy-ocr.yml ✅
- **Trigger:** push to main (paths: services/ocr/**)
- **Responsibility:** Deploy OCR service to DigitalOcean
- **Status:** Active

### deploy-superset.yml ✅
- **Trigger:** push to main (paths: superset/**)
- **Responsibility:** Deploy Superset to DigitalOcean
- **Status:** Active

### superset-deploy.yml ✅
- **Trigger:** push to main, workflow_dispatch
- **Responsibility:** Superset deployment with health checks
- **Status:** Active

### deploy-mcp.yml ✅
- **Trigger:** push to main (paths: mcp/**)
- **Responsibility:** Deploy MCP services
- **Status:** Active

---

## Testing & Quality

### ci-unified.yml ✅
- **Trigger:** pull_request, push to main
- **Responsibility:** Unified CI pipeline
- **Status:** Active

### ci-consolidated.yml ✅
- **Trigger:** pull_request, push to main
- **Responsibility:** Consolidated CI checks
- **Status:** Active

### odoo-unified.yml ✅
- **Trigger:** push to main/develop (paths: addons/**, odoo_addons/**)
- **Responsibility:** Odoo module validation and testing
- **Status:** Active

### integration-tests.yml ✅
- **Trigger:** push to main, pull_request
- **Responsibility:** Integration tests across services
- **Status:** Active

---

## Automation & Maintenance

### automation-health.yml ✅
- **Trigger:** schedule (cron), workflow_dispatch
- **Responsibility:** Monitor automation infrastructure health
- **Status:** Active

### health-monitor.yml ✅
- **Trigger:** schedule, workflow_dispatch
- **Responsibility:** Service health monitoring
- **Status:** Active

### backup-scheduler.yml ✅
- **Trigger:** schedule (cron)
- **Responsibility:** Automated database backups
- **Status:** Active

### doc-automation.yml ✅
- **Trigger:** push to main, schedule
- **Responsibility:** Automated documentation generation
- **Status:** Active

---

## BIR & Compliance

### bir-compliance-automation.yml ✅
- **Trigger:** schedule, workflow_dispatch
- **Responsibility:** BIR tax form generation and compliance
- **Status:** Active

### month-end-task-automation.yml ✅
- **Trigger:** schedule (monthly)
- **Responsibility:** Month-end closing tasks
- **Status:** Active

---

## Disabled/Deprecated Workflows

### odoo-deploy.yml ❌ DISABLED
- **Reason:** Replaced by cd-odoo-prod.yml (pull-based deployment)
- **Disabled:** 2025-11-09
- **File:** odoo-deploy.yml.disabled

### deploy-consolidated.yml ❌ DISABLED
- **Reason:** Replaced by cd-odoo-prod.yml (streamlined deployment)
- **Disabled:** 2025-11-09
- **File:** deploy-consolidated.yml.disabled

### Other .disabled/.deprecated files
- See `.github/workflows/*.disabled` and `*.deprecated` for historical workflows

---

## Required Checks for Branch Protection

To enable PR #377 to merge safely, configure the following **required status checks** on the `main` branch:

### Core CI/CD Checks (Required):
- `CI - Code Quality & Tests / Odoo Module Tests`
- `CI Unified / ci-summary`
- `CI Unified / quality-checks`
- `CI Unified / python-tests`
- `CI Unified / security-scan`
- `Spec Guard / Validate Platform Specification`
- `Deploy Gates / gates`

### Supporting Checks (Optional - Informational):
- `Dependency Scanning` (all jobs) - set to `continue-on-error: true`
- `Automation Health Check` - non-blocking for PRs, fails only on schedule
- `Documentation Automation` - informational only

### Deployment Checks (Post-Merge):
- `CD - Odoo Production` - only runs after merge to main

## Workflow Trigger Matrix

| Workflow | push:main | pull_request | schedule | workflow_dispatch | Required for Merge |
|----------|-----------|--------------|----------|-------------------|-------------------|
| cd-odoo-prod.yml | ✅ | ❌ | ❌ | ❌ | ❌ (post-merge) |
| spec-guard.yml | ✅ | ✅ | ❌ | ❌ | ✅ **CORE** |
| ci-odoo.yml | ✅ | ✅ | ❌ | ❌ | ✅ **CORE** |
| ci-supabase.yml | ❌ | ✅ | ❌ | ❌ | ⚠️ (skeleton) |
| ci-superset.yml | ❌ | ✅ | ❌ | ❌ | ⚠️ (skeleton) |
| docs-ci.yml | ✅ | ✅ | ❌ | ❌ | ⚠️ (skeleton) |
| pages-deploy.yml | ✅ | ❌ | ❌ | ❌ | ❌ (post-merge) |
| deploy-canary.yml | ❌ | ❌ | ❌ | ✅ | ❌ (manual) |
| deploy-gates.yml | ❌ | ✅ | ❌ | ✅ | ✅ **CORE** |
| ci-unified.yml | ✅ | ✅ | ❌ | ✅ | ✅ **CORE** |
| ci-consolidated.yml | ✅ | ✅ | ❌ | ✅ | ✅ **CORE** |
| dependency-scanning.yml | ✅ | ✅ | ⏰ | ❌ | ⚠️ (informational) |
| automation-health.yml | ✅ | ✅ | ⏰ | ✅ | ⚠️ (non-blocking for PRs) |

---

## PR #377 Deployment Hardening - Changes Summary

### Added Workflows:
- ✅ `cd-odoo-prod.yml` - **Single source of truth** for production ERP + portal deployment
- ✅ `spec-guard.yml` - Validates `spec/platform_spec.json` against schema
- ✅ `ci-odoo.yml`, `ci-supabase.yml`, `ci-superset.yml` - Spec-kit CI workflows (skeletons)
- ✅ `docs-ci.yml`, `pages-deploy.yml` - Documentation workflows

### Disabled Workflows:
- ❌ `odoo-deploy.yml.disabled` - Replaced by `cd-odoo-prod.yml`
- ❌ `deploy-consolidated.yml.disabled` - Replaced by `cd-odoo-prod.yml`

### Enhanced Workflows:
- 🔧 `dependency-scanning.yml` - Made resilient to missing files/tokens
- 🔧 `automation-health.yml` - Non-blocking for PRs, fails only on schedule

## Conflict Prevention Rules

1. **Only ONE workflow per deployment target**
   - Production Odoo: cd-odoo-prod.yml only ✅
   - OCR service: deploy-ocr.yml only
   - Superset: deploy-superset.yml (or superset-deploy.yml - consolidate later)

2. **CI/CD workflows should NOT deploy**
   - CI workflows: build, test, validate only
   - CD workflows: deploy only (after CI passes)

3. **Disable conflicting workflows immediately**
   - Rename to `.disabled` extension
   - Document reason and date in this README

4. **Spec-kit workflows are canonical**
   - workflows defined in spec/platform_spec.json are authoritative ✅
   - Non-spec workflows should have clear justification

5. **Graceful degradation for missing dependencies**
   - Workflows check for file existence before running
   - Secrets/tokens checked conditionally
   - `continue-on-error: true` for informational scans

---

## Maintenance

**Review Frequency:** Monthly
**Owner:** DevOps team
**Contact:** jgtolentino_rn@yahoo.com

**Cleanup Checklist:**
- [ ] Remove .disabled files older than 90 days
- [ ] Consolidate duplicate workflows (e.g., superset-deploy.yml variants)
- [ ] Update this README when workflows change
- [ ] Validate spec/platform_spec.json workflow list matches active workflows

---

## References

- [Platform Spec](../../spec/platform_spec.json) - Canonical workflow definitions
- [Workflow Consolidation Plan](../../docs/workflows/consolidation-plan.md) - Future improvements
- [CI/CD Guide](../../docs/guides/workflows-ci-cd.md) - Usage documentation
