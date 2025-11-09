# Issue Resolution Summary

**Last Updated**: 2025-11-09
**Purpose**: Document resolution paths for historic and recurring issues

---

## Overview

This document provides guidance for resolving historic issues, particularly those created by automated workflows before improvements were implemented. It serves as a reference for cleanup operations and prevents confusion about older issue patterns.

---

## 1. Health Check Issue Cleanup

### Background

Between early October and November 2025, the `health-monitor.yml` workflow created numerous duplicate health check issues due to:

* Running every 5 minutes (288 times/day)
* No cooldown period after issue closure
* No comment cooldown, leading to spam on long-running incidents
* Issues: #254–#277 and related

### Resolution Path

**Status**: ✅ **RESOLVED** (as of 2025-11-09)

**Improvements Made**:

1. **Schedule reduced**: Every 5 minutes → Every 30 minutes
   * Reduces potential daily issues from ~288 to ~48
2. **Issue creation cooldown**: 2+ hours after closure
   * Prevents issue storms when services flap
3. **Comment cooldown**: 1 hour between "still failing" updates
   * Fixed to use `issues.listComments` properly
   * Prevents comment spam during extended outages

**Cleanup Procedure**:

For historic duplicate health check issues (#254–#277):

```bash
# Option 1: Manual review and close
# Review each issue individually and close with comment:
# "Closing duplicate/historic health check issue.
#  Health monitoring has been improved (cooldowns, reduced frequency).
#  See docs/REPO_STATE_OF_UNION_2025-11.md for details."

# Option 2: Use bulk cleanup workflow
# Run: .github/workflows/close-duplicate-health-issues.yml
# This workflow can be manually triggered to close batches of historic issues
```

**Prevention**:

* Health monitoring now includes smart cooldowns
* Issue creation is throttled
* Comment frequency is limited
* See `.github/workflows/health-monitor.yml` for current configuration

---

## 2. Workflow Trigger Audit Issues

### Background

Issue #306 tracked the need to audit all workflow triggers to ensure proper configuration and avoid unintended workflow runs.

### Resolution Path

**Status**: ✅ **RESOLVED**

**Improvements Made**:

1. Created comprehensive workflow documentation in `.github/workflows/README.md`
2. Documented all ~76 workflows with:
   * Trigger types (push, pull_request, schedule, workflow_dispatch, etc.)
   * Purpose and scope
   * Dependencies and relationships
3. Standardized trigger patterns across similar workflows

**Prevention**:

* All new workflows must be documented in `.github/workflows/README.md`
* Workflow trigger changes require documentation updates
* See [Workflow README](../.github/workflows/README.md) for current inventory

---

## 3. Deployment Workflow Consolidation

### Background

Issue #305 tracked confusion around multiple deployment workflows:
* `cd-odoo-prod.yml`
* `odoo-deploy.yml`
* `deploy-consolidated.yml`
* `deploy-canary.yml`

### Resolution Path

**Status**: ✅ **RESOLVED**

**Clarity Achieved**:

1. **`cd-odoo-prod.yml`**: Single source of truth for production ERP + portal
   * Pull-based deployment
   * Triple smoke tests (ERP, Portal, Auth)
   * Should be used for standard production deployments

2. **`odoo-deploy.yml`**: Odoo-only pipeline
   * Legacy/specialized Odoo deployments
   * Kept in sync with main branch

3. **`deploy-consolidated.yml`**: Full-stack/infrastructure changes
   * When changes span beyond Odoo (database, networking, etc.)
   * Kept in sync with main branch

4. **`deploy-canary.yml`**: Canary deployments
   * For risky changes requiring gradual rollout
   * See `docs/CANARY_DEPLOYMENT_GUIDE.md`

**Prevention**:

* Deployment strategy is now documented in `.github/workflows/README.md`
* PRs that modify deployment workflows are reviewed for alignment with strategy
* See [Deployment Documentation](DEPLOYMENT.md) for detailed procedures

---

## 4. Canary Deployment Story

### Background

Issue #308 requested clear documentation of the canary deployment process and when to use it.

### Resolution Path

**Status**: ✅ **RESOLVED**

**Documentation Created**:

1. `docs/CANARY_DEPLOYMENT_GUIDE.md` – Complete canary deployment guide
2. `.github/workflows/README.md` – Workflow trigger and usage documentation
3. Canary workflow (`deploy-canary.yml`) is documented and tested

**When to Use Canary**:

* Database schema changes
* Major dependency updates
* Critical business logic changes
* New module deployments
* Changes to authentication/authorization

**Prevention**:

* Canary process is now standard for risky changes
* Documentation is linked from workflow README
* See [Canary Deployment Guide](CANARY_DEPLOYMENT_GUIDE.md)

---

## 5. Skills Registry & Evals Alignment

### Background

As AI skills and agents became first-class citizens in the repo, we needed validation that:
* All skills are properly registered
* Evals exist or are explicitly exempted
* Registry metadata is complete and accurate

### Resolution Path

**Status**: 🔄 **IN PROGRESS** (monitored)

**Improvements Made**:

1. Created `Skills & Agents Inventory Check` workflow
   * Validates registry completeness
   * Checks for orphaned skills
   * Ensures metadata quality

2. Enhanced `tee-mvp-ci / evals` workflow
   * Enforces eval coverage
   * Allows explicit exemptions
   * Fails on missing evals without exemption

**Ongoing Work**:

* Keep skills under `docs/claude-code-skills/community/**`
* Maintain relative symlinks under `.claude/skills/**`
* Update registry when adding new skills
* Add evals or document exemptions

**Prevention**:

* CI checks enforce registry and eval requirements
* See [Skills Documentation](CLAUDE_CODE_WEB_SKILLS_SETUP.md)

---

## 6. Branch Protection Tightening

### Background

Branch protection rules need to match the recommended required checks from the CI/CD modernization.

### Resolution Path

**Status**: 📋 **PLANNED** (not yet implemented)

**Recommended Required Checks**:

* `CI Unified / ci-summary`
* `CI Unified / python-tests`
* `CI Unified / quality-checks`
* `CI Unified / security-scan`
* `CI - Code Quality & Tests / Odoo Module Tests`
* `Spec Guard / Validate Platform Specification`
* `Deploy Gates / gates`
* Optionally: `cd-odoo-prod.yml` (if "merge = deploy" is desired)

**Next Steps**:

1. Review current branch protection rules
2. Update GitHub branch protection settings
3. Test with a non-critical PR
4. Roll out to main branch
5. Document in repository settings

---

## 7. Documentation Validation Pipeline

### Background

Issue #369 tracks the need to verify the GitToDoc pipeline and ensure docs workflows are properly integrated.

### Resolution Path

**Status**: 🔄 **IN PROGRESS** (verification pending)

**Components**:

1. GitToDoc pipeline for automated documentation generation
2. Docs workflow integration
3. Documentation validation in CI

**Next Steps**:

1. Complete verification of GitToDoc pipeline
2. Ensure docs are generated correctly
3. Add documentation quality checks to CI
4. Update workflow documentation

---

## Cleanup Workflows

### Available Bulk Cleanup Tools

1. **`close-duplicate-health-issues.yml`**
   * Closes historic health check issues in batches
   * Requires manual trigger with issue number range
   * Adds closure comment with context

2. **`close-stale-issues.yml`** (if exists)
   * Closes issues with no activity after N days
   * Can be configured to skip certain labels

### Manual Cleanup Template

For closing individual historic issues:

```markdown
Closing [duplicate/historic/resolved] issue.

**Context**: [Brief explanation of why this is being closed]

**Resolution**: [What was done to prevent recurrence]

**Reference**: See docs/REPO_STATE_OF_UNION_2025-11.md and docs/ISSUE_RESOLUTION_SUMMARY.md for details.
```

---

## References

* [Repository State of Union](REPO_STATE_OF_UNION_2025-11.md) – Current state overview
* [Workflow Documentation](../.github/workflows/README.md) – Complete workflow reference
* [CI/CD Fixes Summary](CI_CD_FIXES_SUMMARY.md) – Recent CI/CD improvements
* [Deployment Guide](DEPLOYMENT.md) – Deployment procedures
* [Canary Deployment Guide](CANARY_DEPLOYMENT_GUIDE.md) – Canary deployment strategy

---

## Contact

For questions about issue resolution or cleanup procedures, refer to the [Workflow README](../.github/workflows/README.md) or consult the platform team.
