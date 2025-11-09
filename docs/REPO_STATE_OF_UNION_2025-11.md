# Repository-wide CI/CD, SRE, and AI-Agent Modernization Update

**Date**: November 2025
**Status**: Current State of the Repository
**Last Updated**: 2025-11-09

---

This update captures the current end-to-end state of the **insightpulse-odoo** repository, with a focus on:

* CI/CD & deployment hardening
* SRE & health monitoring noise reduction
* AI agent / skills infrastructure (ALK)
* Workflow documentation & governance

## 1. CI/CD & Deployment Architecture

We've aligned the repo on a clearer, safer deployment strategy:

### Canonical production deploy

* `cd-odoo-prod.yml` is the **single source of truth** for production ERP + portal deploys.
* Implements **pull-based** deployments (git pull + docker compose pull + up -d) for faster, safer rollouts.
* Runs **triple smoke tests**:
  * ERP: `https://erp.insightpulseai.net/web/login`
  * Portal: `https://insightpulseai.net`
  * Auth: `/web/database/list` endpoint
* Deployment fails if any smoke check is non-200.

### Legacy deployment workflows

* `odoo-deploy.yml` and `deploy-consolidated.yml` are kept in sync with `main` and documented as:
  * `odoo-deploy.yml`: Odoo-only pipeline.
  * `deploy-consolidated.yml`: full-stack/infra changes when needed.
* Conflicts in recent PRs are resolved by **deferring to the main branch versions** so feature PRs don't unintentionally change production deploy behaviour.

### CI unification

* **Primary CI gates**:
  * `CI - Code Quality & Tests` (black, isort, flake8, pre-commit, pylint, Python tests, Odoo module tests, security scans)
  * `CI Unified` (summary + core tests + security)
  * `CI – Spec-Driven Build / spec-regen` (spec verification)
* Older / duplicate workflows (standalone flake8/pre-commit/legacy Odoo CI) are treated as **legacy** and are being either:
  * folded into the unified CI, or
  * disabled / made non-blocking where they duplicate coverage.

### Branch protection (recommended required checks)

* `CI Unified / ci-summary`
* `CI Unified / python-tests`
* `CI Unified / quality-checks`
* `CI Unified / security-scan`
* `CI - Code Quality & Tests / Odoo Module Tests`
* `Spec Guard / Validate Platform Specification`
* `Deploy Gates / gates`
* Optionally: `cd-odoo-prod.yml` if we want "merge = deploy".

---

## 2. Platform Spec & Guardrails

We introduced a **canonical platform spec** and guard workflows:

### Files

* `spec/platform_spec.json` – single source of truth for platform configuration.
* `spec/platform_spec.schema.json` – JSON Schema for validation.
* `scripts/validate_spec.py` – validation script used by CI.

### Workflows

* `spec-guard.yml`:
  * Runs `python3 scripts/validate_spec.py`.
  * Triggers on changes to `spec/**`, related `docs/**`, and deployment workflows that depend on the spec.
  * Fails fast with clear error messages when the spec is invalid.

This gives us a consistent spec-driven pipeline that both **Deploy Gates** and other quality checks can rely on.

---

## 3. SRE & Health Monitoring Improvements

We cleaned up noisy health monitoring and brought SRE hygiene back under control:

### Health monitor tuning (`health-monitor.yml`)

* Schedule reduced: **every 5 minutes → every 30 minutes**
  * Issue volume reduced from ~288/day to ~48/day.
* **Issue creation cooldown:**
  * After an issue is closed, a new one will not be created for a defined cooldown window (2+ hours), preventing issue storms.
* **Comment cooldown (fixed)**
  * Correctly uses `issues.listComments` to fetch the **latest** comment and enforces a **1-hour cooldown** before posting another "still failing" update.
  * This prevents comment spam on long-running incidents.

### Health issue clean-up & documentation

* Historic "🚨 Health Check Failed – …" issues (#254–#277 and related) have a documented resolution path in `ISSUE_RESOLUTION_SUMMARY.md`.
* Added guidance for when to run bulk-cleanup workflows (e.g., `close-duplicate-health-issues.yml`).

**Result**: health monitoring still catches real incidents, but **no longer floods GitHub** with duplicate issues or comments.

---

## 4. Workflow Documentation & Governance

We now have a **single, human-readable map** of all workflows:

### `.github/workflows/README.md`

* Documents ~76 workflows, organized by:
  * CI/CD
  * Scheduled / monitoring
  * Deployment
  * Manual / on-demand
  * Event-driven / specialized
* Includes:
  * Trigger types and high-level purpose for each workflow.
  * Deployment strategy (when to use `cd-odoo-prod.yml` vs `odoo-deploy.yml` vs `deploy-consolidated.yml` vs canary).
  * Canary deployment notes (`deploy-canary.yml`).
  * Branch protection & troubleshooting guidance.

This file is now the **canonical reference** for understanding automation in the repo and for deciding where new workflows should be added.

---

## 5. AI Learning & Knowledge (ALK) Skills & Agents

We've started treating AI agents and skills as **first-class citizens** in the repo:

### Skills layout

* New skills live under:
  * `docs/claude-code-skills/community/**`
* They are exposed to AI agents via symlinks under:
  * `.claude/skills/**`

### Symlink hardening

* Replaced absolute symlinks like:
  * `/home/user/insightpulse-odoo/docs/...`
* With **relative symlinks** that work in:
  * local clones,
  * CI containers,
  * and any workspace path.

### Checks & registries

* `Skills & Agents Inventory Check / Validate Skills & Agents Registry` validates that:
  * Every skill has a proper registry entry (id, path, owner, category, etc.).
* `tee-mvp-ci / evals` enforces:
  * eval coverage and/or explicit exemptions for skills.

### ALK focus areas

* DevOps & CI/CD optimization (e.g., CI audit skills, IaC executors/planners/security auditors).
* Future agents will plug into:
  * GitHub Actions,
  * deployment workflows,
  * and documentation automation as "first-class" automation components.

---

## 6. Issue Resolution & Open Items

### Resolved / documented

* Health check issue spam (#254–#277).
* Workflow trigger audit (#306) with documentation of all configured triggers.
* Odoo deployment workflow consolidation / clarity (#305).
* Canary deployment story (#308), now documented and wired into the workflow docs.

### In progress / watchlist

* Skills registry / evals alignment:
  * `Skills & Agents Inventory Check` and `tee-mvp-ci / evals` will be kept in sync as new ALK skills are added.
* Branch protection tightening:
  * We still need to formally update GitHub branch protection rules to match the recommended required checks list.
* Documentation validation (#369):
  * Pending final verification of the GitToDoc pipeline and its interaction with docs workflows.

---

## 7. How to Work in This Repo Going Forward

### For application or module changes

* Rely on `CI - Code Quality & Tests` and `CI Unified`.
* Ensure specs, docs, and tests are updated; spec-guard and deploy-gates will enforce this.

### For production changes

* Target `cd-odoo-prod.yml` for ERP + portal deploys.
* Use canary deploys (`deploy-canary.yml`) for risky changes.
* Treat health-monitor alerts as the primary signal; use the cooldown-aware issues/comments as the incident log.

### For AI agent / skills changes

* Add skills under `docs/claude-code-skills/**`.
* Expose them via relative symlinks under `.claude/skills/**`.
* Register them in the skills registry and (if applicable) add or link evals so that:
  * `Skills & Agents Inventory Check` and `tee-mvp-ci / evals` stay green.

---

## Related Documentation

* [Workflow Documentation](.github/workflows/README.md) – Complete workflow reference
* [Issue Resolution Summary](ISSUE_RESOLUTION_SUMMARY.md) – Historic issue cleanup guidance
* [CI/CD Fixes Summary](CI_CD_FIXES_SUMMARY.md) – Recent CI/CD improvements
* [Deployment Guide](DEPLOYMENT.md) – Deployment procedures
* [Canary Deployment Guide](CANARY_DEPLOYMENT_GUIDE.md) – Canary deployment strategy
* [Planning](../PLANNING.md) – Sprint planning and roadmap
* [Architecture](../ARCHITECTURE.md) – System architecture

---

## TL;DR

* **CI/CD**: Unified on `cd-odoo-prod.yml` for production, with spec-guard validation and comprehensive quality gates.
* **SRE**: Health monitoring now runs every 30min with smart cooldowns – no more issue/comment spam.
* **Workflows**: ~76 workflows fully documented in `.github/workflows/README.md`.
* **AI/Skills**: Relative symlinks, registry validation, and eval coverage for all Claude Code skills.
* **Next Steps**: Tighten branch protection, align skills/evals, complete documentation validation.

---

**For questions or clarifications**, see the [Workflow README](.github/workflows/README.md) or reach out to the platform team.
