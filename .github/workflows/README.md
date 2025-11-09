# GitHub Actions Workflows Documentation

This document provides a comprehensive overview of all GitHub Actions workflows in this repository, organized by purpose and trigger type.

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
- [Workflow Naming Conventions](#workflow-naming-conventions)
- [Branch Protection](#branch-protection)
- [Troubleshooting](#troubleshooting)

---

## Overview

This repository uses GitHub Actions for:
- **Continuous Integration** - Automated testing, linting, and validation
- **Continuous Deployment** - Automated deployments to DigitalOcean infrastructure
- **Health Monitoring** - Continuous monitoring of production services
- **Automation** - Document generation, dependency management, and maintenance tasks

---

## Workflow Categories

### CI/CD Workflows

These workflows run automatically on `push` and/or `pull_request` events to validate code changes.

| Workflow | Triggers | Purpose |
|----------|----------|---------|
| `ci-consolidated.yml` | push, pull_request, workflow_dispatch | Consolidated CI pipeline with tests, linting, and validation |
| `ci-odoo.yml` | push, pull_request | Odoo module testing and validation |
| `ci-spec.yml` | push, pull_request | Specification validation |
| `ci-unified.yml` | push, pull_request, workflow_dispatch | Unified CI checks across all services |
| `odoo-unified.yml` | push, pull_request, workflow_dispatch | Odoo module structure validation, linting, XML validation |
| `gittodoc-ci.yml` | push, pull_request | GitToDoc service smoke tests |
| `ai-code-review.yml` | pull_request | AI-powered code review on PRs |
| `auto-resolve-conflicts.yml` | pull_request, workflow_dispatch | Automatic conflict resolution |
| `assistant-guard.yml` | pull_request, push (main) | Validates assistant configuration files |
| `n8n-cli-ci.yml` | push, pull_request | n8n workflow validation |
| `tee-mvp-ci.yml` | push, pull_request | TEE MVP testing |
| `mvp_smoke.yml` | push, pull_request | Smoke tests for MVP features |
| `claude-config.yml` | push, pull_request, workflow_dispatch | Claude configuration validation |

### Scheduled/Monitoring Workflows

These workflows run on a schedule to monitor services, generate reports, and perform maintenance.

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `health-monitor.yml` | Every 30 minutes | **Production health monitoring** - Checks ERP, MCP, Superset, OCR endpoints. Creates GitHub issues on failure. |
| `automation-health.yml` | Daily at 02:00 UTC | Comprehensive automation validation across all layers |
| `backup-scheduler.yml` | schedule, workflow_dispatch | Automated backup scheduling |
| `claude-daily-cron.yml` | schedule, workflow_dispatch | Daily Claude maintenance tasks |
| `doc-automation.yml` | schedule, push, pull_request, workflow_dispatch | Automated documentation generation |
| `gittodoc-cron.yml` | schedule, workflow_dispatch, push | GitToDoc scheduled updates |
| `skills-consolidate.yml` | schedule, workflow_dispatch | Consolidate skills definitions |
| `metrics-collector.yml` | schedule, workflow_dispatch | Collect system and usage metrics |
| `parity-live-sync.yml` | schedule, workflow_dispatch | Sync parity data |
| `dast-security.yml` | workflow_dispatch, schedule | Dynamic Application Security Testing |
| `dependency-scanning.yml` | push, pull_request, schedule | Security scanning of dependencies |
| `assistant-context-freshness.yml` | schedule, push, pull_request, workflow_dispatch | Validates assistant context freshness |

**Note on `health-monitor.yml`:**
- Reduced from every 5 minutes to every 30 minutes to prevent issue spam
- Implements deduplication: only updates existing issues every 60+ minutes
- Implements cooldown: won't create new issue for 2 hours after last issue closed
- Auto-closes issues when health is restored

### Deployment Workflows

These workflows handle deployments to various environments.

#### Production Deployments

| Workflow | Purpose | Deployment Target |
|----------|---------|-------------------|
| `odoo-deploy.yml` | **Canonical Odoo deployment** - Full test → build → push → deploy → health check pipeline | DigitalOcean Droplet (production) |
| `deploy-consolidated.yml` | **Multi-service deployment** - Deploys Odoo + Supabase + Superset with configurable options | DigitalOcean (production/staging) |
| `deploy-docs.yml` | Documentation deployment | GitHub Pages |
| `deploy-mcp.yml` | MCP server deployment | DigitalOcean |
| `deploy-ocr.yml` | OCR service deployment | DigitalOcean |
| `deploy-superset.yml` | Superset deployment | DigitalOcean |
| `supabase-funcs.yml` | Supabase Edge Functions deployment | Supabase |
| `superset-deploy.yml` | Superset dashboards deployment | DigitalOcean |
| `insightpulse-monitor-deploy.yml` | Monitoring stack deployment | DigitalOcean |

#### Canary/Progressive Deployments

| Workflow | Purpose |
|----------|---------|
| `deploy-canary.yml` | **Canary deployment with traffic splitting** - Supports 10%/25%/50% traffic, automatic monitoring, rollback on errors, and auto-promotion |
| `ph-tax-canary.yml` | Philippines tax module canary deployment |

**Odoo Deployment Strategy:**
- **Primary:** `odoo-deploy.yml` - Use for Odoo-specific changes
- **Secondary:** `deploy-consolidated.yml` - Use for full-stack deployments
- **Testing:** `deploy-canary.yml` - Use for risky changes that need gradual rollout

### Manual/On-Demand Workflows

These workflows are triggered manually via `workflow_dispatch` or by specific events.

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `rollback.yml` | workflow_dispatch | Emergency rollback to previous deployment |
| `git-ops.yml` | workflow_dispatch, repository_dispatch | GitOps operations |
| `post-deploy-refresh.yml` | workflow_dispatch, workflow_run | Post-deployment cache refresh and verification |
| `deploy-gates.yml` | workflow_dispatch | Deployment gating and approval |
| `close-duplicate-health-issues.yml` | workflow_dispatch | **Bulk close duplicate health check issues** - Run this after health-monitor updates to clean up historical spam |
| `auto-close-resolved.yml` | workflow_run, workflow_dispatch | Auto-close resolved issues |
| `seed-labels.yml` | workflow_dispatch | Initialize repository labels |
| `generate-docs.yml` | push, workflow_dispatch, schedule | Generate documentation on demand |

### Event-Driven Workflows

These workflows respond to specific GitHub events.

| Workflow | Event | Purpose |
|----------|-------|---------|
| `ci-autofix-on-failure.yml` | workflow_run | Auto-fix CI failures |
| `claude-autofix-bot.yml` | issue_comment | Claude-powered auto-fix on issue comments |
| `issue-from-comment.yml` | issue_comment | Create issues from PR comments |
| `auto-patch.yml` | push, schedule, workflow_dispatch | Auto-patch dependencies |
| `auto-skill-generation.yml` | push, workflow_dispatch | Auto-generate skill definitions |
| `ai-training.yml` | push, workflow_dispatch | AI model training |
| `triage.yml` | issues, pull_request | Auto-triage and label issues/PRs |

### Specialized Workflows

| Workflow | Purpose |
|----------|---------|
| `feature-inventory.yml` | Tracks and documents implemented features |
| `field-doc-sync.yml` | Syncs field documentation |
| `bir-compliance-automation.yml` | BIR (Philippines tax) compliance automation |
| `month-end-task-automation.yml` | Month-end closing automation |
| `notion-automations.yml` | Notion integration and sync |
| `oca-bot-automation.yml` | OCA (Odoo Community Association) bot |
| `oca-pre-commit.yml` | OCA pre-commit hooks |
| `odoo-knowledge-scraper.yml` | Scrapes Odoo knowledge base |
| `odoo-module-update.yml` | Updates Odoo modules |
| `openupgrade-test.yml` | Tests Odoo upgrade paths |
| `performance-testing.yml` | Performance benchmarks |
| `quality.yml` | Code quality checks |
| `sap-spec-validate.yml` | SAP specification validation |
| `skillsmith.yml` / `skillsmith-integration.yml` | Skill management and integration |
| `skills-agents-check.yml` | Validates skill agents |
| `sop-generator.yml` | Generates Standard Operating Procedures |
| `superset-health.yml` | Superset-specific health checks |
| `superset-postgres-guard.yml` | Superset database guardrails |
| `integration-tests.yml` | Cross-service integration tests |
| `infrastructure-validation.yml` | Infrastructure configuration validation |
| `issue-validation.yml` | Issue template validation |

---

## Workflow Naming Conventions

- `ci-*.yml` - Continuous Integration workflows
- `deploy-*.yml` - Deployment workflows
- `auto-*.yml` - Automated maintenance/fix workflows
- `*-health.yml` - Health monitoring workflows
- `*-validation.yml` - Validation workflows
- `*-automation.yml` - Automation workflows

---

## Branch Protection

### Recommended Required Checks for `main` Branch

Based on the current workflow configuration, the following checks should be required:

#### Core CI Checks
- `ci-consolidated` - Primary CI pipeline
- `ci-odoo` - Odoo module validation
- `ci-unified` - Unified cross-service checks

#### Security & Quality
- `dependency-scanning` - Dependency vulnerabilities
- `quality` - Code quality gates

#### Service-Specific Checks
- `gittodoc-ci` - GitToDoc smoke tests (if using GitToDoc)
- `odoo-unified / module-validation` - Odoo module structure
- `odoo-unified / xml-validation` - Odoo XML validation

#### Documentation
- `assistant-guard` - Assistant config validation

**Note:** Do NOT require:
- `health-monitor` (scheduled, not PR-triggered)
- `automation-health` (scheduled)
- Any `deploy-*` workflows (post-merge only)
- Any workflows with `workflow_dispatch` only

---

## Troubleshooting

### Health Check Issues Spamming

**Problem:** Many duplicate health check issues (e.g., issues #254-#277)

**Solution:**
1. The `health-monitor.yml` workflow has been updated (Nov 2025) with:
   - Reduced frequency: 5 min → 30 min
   - Comment deduplication: Only updates every 60+ minutes
   - Cooldown period: Won't create new issue for 2 hours after closure
2. Run `close-duplicate-health-issues.yml` workflow manually to bulk-close duplicates

### Deployment Failures

**Problem:** Deployment failed or needs rollback

**Solution:**
1. Check deployment logs in Actions tab
2. Review health check results
3. Run `rollback.yml` workflow if needed
4. Check `odoo-deploy.yml` automatic rollback logic

### CI Failures

**Problem:** CI checks failing on PR

**Solution:**
1. Check specific workflow logs for details
2. For auto-fixable issues, add comment: `/fix` (triggers `claude-autofix-bot.yml`)
3. For conflicts, `auto-resolve-conflicts.yml` may automatically resolve

### Missing Workflow Triggers

**Problem:** Workflow not running when expected

**Solution:**
1. Check this README for trigger configuration
2. Verify `paths:` filters if workflow should trigger on specific files
3. For manual workflows, use "Run workflow" button in Actions tab
4. Check branch filters (`branches:` in `on:` section)

---

## Contributing

When adding new workflows:

1. Follow naming conventions above
2. Add appropriate triggers (avoid `on: push` to all branches for expensive workflows)
3. Add workflow to this README in the appropriate category
4. Consider using `paths:` filters to limit unnecessary runs
5. For reusable workflows, use `workflow_call` trigger
6. Always include `workflow_dispatch` for manual testing
7. Document required secrets in the workflow file

---

## Related Documentation

- [CI/CD Architecture](../../docs/ci-cd-architecture.md)
- [Deployment Guide](../../docs/deployment-guide.md)
- [Health Monitoring](../../docs/health-monitoring.md)
- [Odoo Development](../../docs/odoo-development.md)

---

**Maintained by:** DevOps Team
**Questions?** Open an issue with label `infrastructure`
