# GitHub Actions Workflows Documentation

This document provides a comprehensive overview of all GitHub Actions workflows in this repository, organized by purpose and trigger type, with emphasis on the **current production deployment model** (`cd-odoo-prod.yml`) and spec-driven CI.

**Last Updated:** 2025-11-09  
**Total Workflows:** 76

## Table of Contents

- [Overview](#overview)
- [Workflow Categories](#workflow-categories)
  - [CI/CD Workflows](#cicd-workflows)
  - [Scheduled/Monitoring Workflows](#scheduledmonitoring-workflows)
  - [Deployment Workflows](#deployment-workflows)
  - [Manual/On-Demand Workflows](#manualon-demand-workflows)
  - [Event-Driven Workflows](#event-driven-workflows)
  - [Specialized Workflows](#specialized-workflows)
- [Disabled / Historical Workflows](#disabled--historical-workflows)
- [Workflow Naming Conventions](#workflow-naming-conventions)
- [Branch Protection](#branch-protection)
- [Workflow Trigger Matrix](#workflow-trigger-matrix)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Maintenance](#maintenance)
- [Related Documentation](#related-documentation)
- [References](#references)

---

## Overview

This repository uses GitHub Actions for:

- **Continuous Integration** – Automated testing, linting, and validation
- **Continuous Deployment** – Automated deployments to DigitalOcean and related infrastructure
- **Health Monitoring** – Continuous monitoring of production services
- **Automation** – Documentation generation, dependency management, and maintenance tasks
- **Spec-Driven Governance** – Platform spec & guardrails for workflows, docs, and services

The **canonical production deployment workflow** is:

- `cd-odoo-prod.yml` – pull-based deployment for Odoo + unified portal + nginx, with triple smoke tests.

Legacy deployment workflows (`odoo-deploy.yml`, `deploy-consolidated.yml`) have been **disabled** in favor of the streamlined model and are documented below under [Disabled / Historical Workflows](#disabled--historical-workflows).

---

## Workflow Categories

### CI/CD Workflows

These workflows run automatically on `push` and/or `pull_request` events to validate code changes.

| Workflow | Triggers | Purpose | Notes |
|----------|----------|---------|-------|
| `ci-unified.yml` | push, pull_request, workflow_dispatch | Unified CI checks across all services | **Core** CI gate |
| `ci-consolidated.yml` | push, pull_request, workflow_dispatch | Consolidated CI pipeline with tests, linting, and validation | Legacy-style CI, still active |
| `ci-odoo.yml` | push, pull_request | Odoo build/test CI based on spec-kit | Skeleton to be fully wired |
| `ci-supabase.yml` | pull_request | Apply Supabase migrations against ephemeral DB | Skeleton |
| `ci-superset.yml` | pull_request | Import dashboards and validate Superset config | Skeleton |
| `ci-spec.yml` | push, pull_request | Specification validation (legacy) | Superseded by `spec-guard.yml` |
| `odoo-unified.yml` | push, pull_request, workflow_dispatch | Odoo module structure validation, linting, XML validation | Odoo-specific checks |
| `gittodoc-ci.yml` | push, pull_request | GitToDoc service build + smoke tests | Docs pipeline |
| `ai-code-review.yml` | pull_request | AI-powered code review on PRs | Non-blocking signal |
| `auto-resolve-conflicts.yml` | pull_request, workflow_dispatch | Automatic conflict resolution | Utility |
| `assistant-guard.yml` | pull_request, push (main) | Validates assistant configuration files | Required for assistant safety |
| `n8n-cli-ci.yml` | push, pull_request | n8n workflow validation | Service-specific |
| `tee-mvp-ci.yml` | push, pull_request | TEE MVP testing (spec + evals) | Experimental |
| `mvp_smoke.yml` | push, pull_request | Smoke tests for MVP features | Lightweight checks |
| `claude-config.yml` | push, pull_request, workflow_dispatch | Claude configuration validation | AI config guard |

#### Spec-Kit Guard

| Workflow | Triggers | Purpose |
|----------|----------|---------|
| `spec-guard.yml` | push, pull_request (affecting `spec/**`, relevant `docs/**`, `.github/workflows/**`) | Validates `spec/platform_spec.json` against `spec/platform_spec.schema.json` and ensures referenced files exist. **Core spec gate** for deployments. |

---

### Scheduled/Monitoring Workflows

These workflows run on a schedule to monitor services, generate reports, and perform maintenance.

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `health-monitor.yml` | Every 30 minutes | **Production health monitoring** – Checks ERP, MCP, Superset, OCR endpoints. Creates/updates GitHub issues on failure. |
| `automation-health.yml` | Daily at 02:00 UTC | Comprehensive automation validation across CI/CD, deploy, and monitoring layers |
| `backup-scheduler.yml` | schedule, workflow_dispatch | Automated backup scheduling |
| `claude-daily-cron.yml` | schedule, workflow_dispatch | Daily Claude maintenance tasks |
| `doc-automation.yml` | schedule, push, pull_request, workflow_dispatch | Automated documentation generation and checks |
| `gittodoc-cron.yml` | schedule, workflow_dispatch, push | GitToDoc scheduled builds/updates |
| `skills-consolidate.yml` | schedule, workflow_dispatch | Consolidate skills definitions into registry |
| `metrics-collector.yml` | schedule, workflow_dispatch | Collect system and usage metrics |
| `parity-live-sync.yml` | schedule, workflow_dispatch | Sync parity data |
| `dast-security.yml` | schedule, workflow_dispatch | Dynamic Application Security Testing |
| `dependency-scanning.yml` | push, pull_request, schedule | Dependency and container image vulnerability scanning |
| `assistant-context-freshness.yml` | schedule, push, pull_request, workflow_dispatch | Validates assistant context freshness and references |

**Note on `health-monitor.yml` (spam hardening):**

- Frequency reduced from **every 5 minutes → every 30 minutes** (288 → 48 runs/day)
- Implements **comment deduplication**: only posts a new comment if the last comment is older than 60 minutes
- Implements **issue creation cooldown**: will not create a new issue until at least 2 hours after the last related issue was closed
- Auto-closes health issues once services are healthy again
- Use `close-duplicate-health-issues.yml` (see Manual Workflows) to bulk close historical spam issues

---

### Deployment Workflows

These workflows handle deployments to various environments.

#### Production Deployments

| Workflow | Purpose | Deployment Target | Status |
|----------|---------|-------------------|--------|
| `cd-odoo-prod.yml` | **Canonical Odoo + Portal deployment** – Pull-based deploy from `main`. Runs triple smoke tests (ERP, Portal, Auth) and updates nginx config. | DigitalOcean Droplet (production) | ✅ **PRIMARY** |
| `deploy-ocr.yml` | OCR service deployment | DigitalOcean | ✅ |
| `deploy-superset.yml` | Superset deployment | DigitalOcean | ✅ |
| `superset-deploy.yml` | Superset dashboards deployment with health checks | DigitalOcean | ✅ |
| `deploy-mcp.yml` | MCP server deployment | DigitalOcean | ✅ |
| `deploy-docs.yml` | Documentation deployment | GitHub Pages | ✅ |
| `supabase-funcs.yml` | Supabase Edge Functions deployment | Supabase | ✅ |
| `insightpulse-monitor-deploy.yml` | Monitoring stack deployment | DigitalOcean | ✅ |

**Odoo Deployment Strategy (current):**

- **Primary (production):** `cd-odoo-prod.yml`  
  - Triggered on push to `main` for relevant paths (Odoo, deploy scripts, Docker compose, portal assets, nginx config).
  - Implements pull-based deploys: `git pull` → `docker compose pull` → `docker compose up -d`.
  - Runs smoke tests for:
    - ERP: `https://erp.insightpulseai.net/web/login`
    - Portal: `https://insightpulseai.net`
    - Auth: `/web/database/list` endpoint.
- **Canary / Progressive:** `deploy-canary.yml` (see below) for risky changes.

#### Canary / Progressive Deployments

| Workflow | Purpose | Status |
|----------|---------|--------|
| `deploy-canary.yml` | **Canary deployment with traffic splitting** – Supports 10%/25%/50% traffic, automatic monitoring, rollback on errors, and auto-promotion. | ✅ |
| `ph-tax-canary.yml` | Philippines tax module canary deployment | ✅ |

---

### Manual/On-Demand Workflows

These workflows are triggered manually via `workflow_dispatch` or via specific workflow events.

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `rollback.yml` | workflow_dispatch | Emergency rollback to previous deployment |
| `git-ops.yml` | workflow_dispatch, repository_dispatch | GitOps operations |
| `post-deploy-refresh.yml` | workflow_dispatch, workflow_run | Post-deployment cache refresh and verification |
| `deploy-gates.yml` | pull_request, workflow_dispatch | Deployment gating and approval based on tests/spec/docs | **Core gate** |
| `close-duplicate-health-issues.yml` | workflow_dispatch | **Bulk close duplicate health check issues** generated by `health-monitor.yml` |
| `auto-close-resolved.yml` | workflow_run, workflow_dispatch | Auto-close resolved issues based on health status |
| `seed-labels.yml` | workflow_dispatch | Initialize repository labels |
| `generate-docs.yml` | push, workflow_dispatch, schedule | Generate documentation on demand |

---

### Event-Driven Workflows

These workflows respond to specific GitHub events.

| Workflow | Event | Purpose |
|----------|-------|---------|
| `ci-autofix-on-failure.yml` | workflow_run | Auto-fix CI failures based on logs |
| `claude-autofix-bot.yml` | issue_comment | Claude-powered auto-fix on issue comments |
| `issue-from-comment.yml` | issue_comment | Create issues from PR comments |
| `auto-patch.yml` | push, schedule, workflow_dispatch | Auto-patch dependencies |
| `auto-skill-generation.yml` | push, workflow_dispatch | Auto-generate skill definitions from code/docs |
| `ai-training.yml` | push, workflow_dispatch | AI model training and eval orchestration |
| `triage.yml` | issues, pull_request | Auto-triage and label issues/PRs |

---

### Specialized Workflows

| Workflow | Purpose |
|----------|---------|
| `feature-inventory.yml` | Tracks and documents implemented features |
| `field-doc-sync.yml` | Syncs field documentation |
| `bir-compliance-automation.yml` | BIR (Philippines tax) compliance automation |
| `month-end-task-automation.yml` | Month-end closing automation |
| `notion-automations.yml` | Notion integration and sync |
| `oca-bot-automation.yml` | OCA (Odoo Community Association) bot integration |
| `oca-pre-commit.yml` | OCA pre-commit hooks |
| `odoo-knowledge-scraper.yml` | Scrapes Odoo knowledge base |
| `odoo-module-update.yml` | Updates Odoo modules |
| `openupgrade-test.yml` | Tests Odoo upgrade paths |
| `performance-testing.yml` | Performance benchmarks |
| `quality.yml` | Additional code quality checks |
| `sap-spec-validate.yml` | SAP specification validation |
| `skillsmith.yml` / `skillsmith-integration.yml` | Skill management and integration |
| `skills-agents-check.yml` | Validates skills & agents registry |
| `sop-generator.yml` | Generates Standard Operating Procedures |
| `superset-health.yml` | Superset-specific health checks |
| `superset-postgres-guard.yml` | Superset database guardrails |
| `integration-tests.yml` | Cross-service integration tests |
| `infrastructure-validation.yml` | Infrastructure configuration validation |
| `issue-validation.yml` | Issue template and label validation |

---

## Disabled / Historical Workflows

These workflows are kept for history but are **not** part of the active deployment path.

### Deployment Workflows

| Workflow | Reason | Status | Notes |
|----------|--------|--------|-------|
| `odoo-deploy.yml` → `odoo-deploy.yml.disabled` | Replaced by `cd-odoo-prod.yml` (pull-based deployment) | ❌ Disabled | Historical full test → build → push → deploy pipeline |
| `deploy-consolidated.yml` → `deploy-consolidated.yml.disabled` | Replaced by `cd-odoo-prod.yml` / spec-kit approach | ❌ Disabled | Historical multi-service deploy (Odoo + Supabase + Superset) |

**Rule of thumb:** There should be **only one** canonical workflow per deployment target. For Odoo production that is now **`cd-odoo-prod.yml`**.

---

## Workflow Naming Conventions

- `ci-*.yml` – Continuous Integration workflows
- `cd-*.yml` / `*-deploy.yml` – Continuous Deployment workflows
- `deploy-*.yml` – Service deployment workflows
- `auto-*.yml` – Automated maintenance/fix workflows
- `*-health.yml` – Health monitoring workflows
- `*-validation.yml` – Validation workflows (schema, spec, config)
- `*-automation.yml` – Automation workflows (docs, month-end, etc.)
- `*-cron.yml` – Scheduled cron-like jobs

When adding new workflows:

1. Use a clear, purpose-driven prefix (`ci-`, `cd-`, `deploy-`, `auto-`, etc.).
2. Prefer `workflow_call` for reusable components.
3. Add `workflow_dispatch` for manual testing where appropriate.

---

## Branch Protection

### Recommended Required Checks for `main` Branch

These should be configured as **required status checks** for merges into `main`:

#### Core CI & Quality

- `CI Unified / ci-summary`
- `CI Unified / python-tests`
- `CI Unified / quality-checks`
- `CI Unified / security-scan`
- `CI - Code Quality & Tests / Odoo Module Tests`
- `CI - Code Quality & Tests / Code Quality (black)`
- `CI - Code Quality & Tests / Code Quality (flake8)`
- `CI - Code Quality & Tests / Code Quality (isort)`
- `CI - Code Quality & Tests / Code Quality (pylint)`
- `CI - Code Quality & Tests / Python Tests`
- `CI - Code Quality & Tests / Security Scan (bandit)`
- `CI - Code Quality & Tests / Security Scan (safety)`

#### Spec & Deploy Gates

- `Spec Guard / Validate Platform Specification`
- `Deploy Gates / gates`
- `Assistant-Guard` (if exposed as a status check)

> **Note:** `cd-odoo-prod.yml` is **post-merge** and usually should not be required for merging (it runs on push to `main`). If you want “merge implies deploy”, you may optionally mark its status as required.

#### Checks that **should NOT** be required

- `health-monitor.yml` (scheduled only)
- `automation-health.yml` (scheduled)
- Most `dependency-scanning` jobs if configured as informational (`continue-on-error: true`)
- Any `workflow_dispatch`-only or purely manual workflows (e.g., `deploy-canary.yml`, `rollback.yml`)

---

## Workflow Trigger Matrix

(High-level summary – actual checks may contain more jobs.)

| Workflow | push:main | pull_request | schedule | workflow_dispatch | Required for Merge |
|----------|-----------|--------------|----------|-------------------|--------------------|
| `cd-odoo-prod.yml` | ✅ | ❌ | ❌ | ❌ | ❌ (post-merge deploy) |
| `spec-guard.yml` | ✅ | ✅ | ❌ | ❌ | ✅ **Core** |
| `ci-unified.yml` | ✅ | ✅ | ❌ | ✅ | ✅ **Core** |
| `ci-consolidated.yml` | ✅ | ✅ | ❌ | ✅ | ✅ (legacy but required until fully migrated) |
| `ci-odoo.yml` | ✅ | ✅ | ❌ | ❌ | ✅ (once fully wired) |
| `docs-ci.yml` | ✅ | ✅ | ❌ | ❌ | Optional (docs) |
| `pages-deploy.yml` | ✅ | ❌ | ❌ | ❌ | ❌ (post-merge docs deploy) |
| `dependency-scanning.yml` | ✅ | ✅ | ⏰ | ❌ | Optional / informational |
| `automation-health.yml` | ✅ | ✅ | ⏰ | ✅ | Non-blocking |
| `deploy-gates.yml` | ❌ | ✅ | ❌ | ✅ | ✅ **Core gate** |
| `deploy-canary.yml` | ❌ | ❌ | ❌ | ✅ | ❌ (manual) |
| `health-monitor.yml` | ❌ | ❌ | ⏰ | ✅ | ❌ (monitoring only) |

---

## Troubleshooting

### Health Check Issues Spamming

**Problem:** Multiple duplicate health check issues (e.g. `🚨 Health Check Failed - 2025-11-05T21:29:19.701Z` through `🚨 Health Check Failed - 2025-11-06T03:54:52.872Z`).

**Mitigation implemented:**

1. `health-monitor.yml` has been updated to:
   - Reduce frequency from 5 minutes to 30 minutes.
   - Deduplicate comments (min 60 minutes between comments).
   - Apply a 2-hour cooldown before creating a new issue after the last one is closed.
   - Auto-close issues once services are healthy.
2. Use `close-duplicate-health-issues.yml` to bulk-close historical duplicates.

### Deployment Failures

1. Check the failing `cd-odoo-prod.yml` run in the Actions tab.
2. Confirm which step failed (pull, docker, smoke tests).
3. If user-facing impact is severe, run `rollback.yml` to revert to previous release.
4. Review `Deploy Gates / gates` and `Spec Guard / Validate Platform Specification` for spec/docs issues.

### CI Failures

1. Open the failing CI job (CI Unified, CI - Code Quality & Tests, etc.).
2. For auto-fixable issues, comment with the appropriate bot command (e.g. `/fix`) to trigger `claude-autofix-bot.yml` or `ci-autofix-on-failure.yml`.
3. Re-run jobs as needed once fixes are pushed.

### Missing Workflow Triggers

1. Check this README to verify expected triggers.
2. Inspect `on:` and `paths:` filters in the workflow file.
3. Confirm branches (`branches:`) include `main` or the relevant feature branch.
4. For manual-only workflows, use the “Run workflow” button in the Actions tab.

---

## Contributing

When adding or modifying workflows:

1. Follow the naming conventions above.
2. Add appropriate triggers – avoid broad `on: push` to all branches for expensive workflows.
3. Use `paths:` filters to limit unnecessary runs.
4. Add new workflows to this README in the correct category.
5. Prefer reusable `workflow_call` building blocks where possible.
6. Include `workflow_dispatch` for manual testing.
7. Document required secrets and environment variables.

---

## Maintenance

**Review Frequency:** Monthly  
**Owner:** DevOps team  
**Contact:** jgtolentino_rn@yahoo.com

**Cleanup Checklist:**

- [ ] Remove `.disabled` workflow files older than 90 days.
- [ ] Consolidate duplicate workflows (e.g. multiple Superset deploy variants).
- [ ] Ensure this README matches the current set of active workflows.
- [ ] Validate that `spec/platform_spec.json` workflow list matches reality.
- [ ] Review branch protection required checks and adjust as CI evolves.

---

## Related Documentation

- [CI/CD Architecture](../../docs/ci-cd-architecture.md)
- [Deployment Guide](../../docs/deployment-guide.md)
- [Health Monitoring](../../docs/health-monitoring.md)
- [Odoo Development](../../docs/odoo-development.md)
- [Workflow Consolidation Plan](../../docs/workflows/consolidation-plan.md)
- [CI/CD Guide](../../docs/guides/workflows-ci-cd.md)
- [Platform Spec](../../spec/platform_spec.json)

---

## References

- `spec/platform_spec.json` – Canonical platform/workflow spec  
- `spec/platform_spec.schema.json` – JSON Schema for the platform spec  
- `scripts/validate_spec.py` – Validation script used by `spec-guard.yml`

**Maintained by:** DevOps Team  
**Questions?** Open an issue with label `infrastructure`.
