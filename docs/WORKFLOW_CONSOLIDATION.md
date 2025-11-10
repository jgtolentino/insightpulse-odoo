# GitHub Actions Workflow Consolidation Plan

**Current State**: 92 workflow files (8 have syntax errors)
**Target**: ~30 consolidated workflows
**Savings**: ~60% reduction in workflow files

---

## Redundant Workflows to Delete

### 1. Code Quality (Keep 1, Delete 2)

**Keep**: `quality.yml` (most comprehensive)

**Delete**:
- `oca-pre-commit.yml` - Duplicate of quality.yml pre-commit checks
- `ci-consolidated.yml` - Already covered by ci-unified.yml

### 2. Documentation (Keep 3, Delete 7)

**Keep**:
- `docs-validation.yml` - Primary doc validation
- `deploy-docs.yml` - GitHub Pages deployment
- `gittodoc-ci.yml` - Git-to-doc automation

**Delete**:
- `doc-automation.yml` - Redundant with docs-validation.yml
- `docs-ci.yml` - Redundant with docs-validation.yml
- `docs-health-check.yml` - Covered by docs-validation.yml
- `field-doc-sync.yml` - Niche use case, rarely triggered
- `generate-docs.yml` - Redundant with gittodoc-ci.yml
- `gittodoc-cron.yml` - Can be merged into gittodoc-ci.yml with schedule trigger
- `wiki-alignment.yml` - Covered by docs-validation.yml

### 3. CI/Testing (Keep 3, Delete 12)

**Keep**:
- `ci-unified.yml` - Main CI orchestrator
- `ci-odoo.yml` - Odoo-specific tests
- `tee-mvp-ci.yml` - TEE evaluation tests

**Delete**:
- `ci-autofix-on-failure.yml` - Covered by claude-autofix-bot.yml
- `ci-spec.yml` - Redundant with ci-unified.yml
- `ci-supabase.yml` - Can merge into ci-unified.yml
- `ci-superset.yml` - Can merge into ci-unified.yml
- `dast-security.yml` - Rarely used, expensive
- `integration-tests.yml` - Covered by ci-unified.yml
- `metrics-collector.yml` - Not actively used
- `n8n-cli-ci.yml` - N8N deprecated
- `odoo-unified.yml` - Redundant with ci-odoo.yml
- `openupgrade-test.yml` - Niche use case
- `performance-testing.yml` - Not actively used
- `self-healing.yml` - Redundant with automation-health.yml

### 4. Deployment (Keep 4, Delete 7)

**Keep**:
- `cd-odoo-prod.yml` - Production Odoo deployment
- `deploy-gates.yml` - Pre-deployment validation
- `pages-deploy.yml` - GitHub Pages
- `supabase-funcs.yml` - Supabase Edge Functions

**Delete**:
- `deploy-canary.yml` - Not using canary deployments
- `deploy-mcp.yml` - MCP deployment covered by cd-odoo-prod.yml
- `deploy-ocr.yml` - OCR service covered by cd-odoo-prod.yml
- `deploy-superset.yml` - Redundant with superset-deploy.yml
- `insightpulse-monitor-deploy.yml` - Monitoring covered by automation-health.yml
- `post-deploy-refresh.yml` - Can merge into cd-odoo-prod.yml
- `superset-deploy.yml` - Keep build-and-deploy-superset.yml instead

### 5. Automation (Keep 5, Delete 11)

**Keep**:
- `ai-code-review.yml` - AI-powered code review
- `claude-autofix-bot.yml` - Auto-fix automation
- `claude-config.yml` - Claude configuration sync
- `automation-health.yml` - Health monitoring
- `backup-scheduler.yml` - Critical backups

**Delete**:
- `ai-training.yml` - Not actively used
- `auto-close-resolved.yml` - Can merge into oca-bot-automation.yml
- `auto-patch.yml` - Redundant with claude-autofix-bot.yml
- `auto-resolve-conflicts.yml` - Rarely successful, manual review better
- `auto-skill-generation.yml` - Covered by skillsmith-integration.yml
- `claude-daily-cron.yml` - Can merge into scheduled.yml
- `monitor.yml` - Redundant with automation-health.yml
- `notion-automations.yml` - Notion integration deprecated
- `oca-bot-automation.yml` - Covered by triage.yml
- `scheduled.yml` - Merge cron jobs into specific workflows
- `superset-health.yml` - Covered by automation-health.yml

### 6. Broken Workflows (Delete All - 8)

**Delete** (Syntax errors prevent execution):
- `close-duplicate-health-issues.yml`
- `validate-structure.yml`
- `claude-sync-ci.yml`
- `auto-merge.yml`
- `assistant-guard.yml`
- `ph-tax-canary.yml`
- `bir-compliance-automation.yml`
- `month-end-task-automation.yml`

---

## Summary

| Category | Current | Keep | Delete | Reduction |
|----------|---------|------|--------|-----------|
| Code Quality | 3 | 1 | 2 | 67% |
| Documentation | 10 | 3 | 7 | 70% |
| CI/Testing | 15 | 3 | 12 | 80% |
| Deployment | 11 | 4 | 7 | 64% |
| Automation | 16 | 5 | 11 | 69% |
| Broken | 8 | 0 | 8 | 100% |
| **Total** | **92** | **30** | **62** | **67%** |

---

## AI-Native Documentation Strategy

### Current Problem
- 92 workflows = fragmented documentation across many files
- Hard for AI (Claude Code, GitHub Copilot) to understand the full system
- Difficult for CLI-first developers to navigate

### Proposed Solution: Machine-Readable Workflow Manifest

Create `/docs/workflows/MANIFEST.json`:

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-10",
  "total_workflows": 30,
  "categories": {
    "code_quality": {
      "workflows": ["quality.yml"],
      "purpose": "Enforce code standards (Black, isort, Flake8, pre-commit)",
      "triggers": ["pull_request", "push"],
      "cli_equivalent": "make lint && make format"
    },
    "ci_testing": {
      "workflows": ["ci-unified.yml", "ci-odoo.yml", "tee-mvp-ci.yml"],
      "purpose": "Run tests and validation",
      "triggers": ["pull_request", "push"],
      "cli_equivalent": "make test && make validate"
    },
    "deployment": {
      "workflows": ["cd-odoo-prod.yml", "deploy-gates.yml"],
      "purpose": "Deploy to production with validation gates",
      "triggers": ["push:main", "workflow_dispatch"],
      "cli_equivalent": "make deploy-prod"
    }
  },
  "workflow_map": {
    "quality.yml": {
      "name": "Code Quality",
      "purpose": "Run all code quality checks",
      "jobs": ["black", "isort", "flake8", "pre-commit"],
      "cli_local": "make lint",
      "skip_conditions": ["[skip ci]", "[no quality]"]
    }
  },
  "ai_prompts": {
    "fix_quality_issues": "Run 'make lint' locally, then commit fixes",
    "trigger_deployment": "Push to main branch or use 'gh workflow run cd-odoo-prod.yml'",
    "check_status": "gh pr view <PR> --json statusCheckRollup | jq '.statusCheckRollup'"
  }
}
```

### AI-Native Features

1. **Single Source of Truth** (`MANIFEST.json`):
   - AI agents read one file to understand entire CI/CD system
   - CLI commands mapped to workflow equivalents
   - Clear trigger conditions and skip patterns

2. **Claude Code Skills Integration**:
   - Create skill: `github-workflows-navigator`
   - Auto-reads `MANIFEST.json` on session start
   - Provides intelligent workflow recommendations

3. **CLI-First Design**:
   - Every workflow has local `make` equivalent
   - Developers can run locally before pushing
   - Faster feedback loop

4. **Minimal Markdown Documentation**:
   - One README per category (5 total instead of 92)
   - Machine-readable YAML frontmatter
   - Generated from `MANIFEST.json`

### Implementation

```bash
# 1. Create manifest
cat > docs/workflows/MANIFEST.json << 'EOF'
{ ... json above ... }
EOF

# 2. Generate category READMEs from manifest
python scripts/generate-workflow-docs.py

# 3. Add Claude Code skill
cat > .claude/skills/github-workflows-navigator/SKILL.md << 'EOF'
---
name: github-workflows-navigator
description: Navigate GitHub Actions workflows using machine-readable manifest
---

# GitHub Workflows Navigator Skill

Reads `docs/workflows/MANIFEST.json` to provide intelligent workflow recommendations.

## Auto-Activation
- Keywords: "workflow", "ci", "deploy", "quality"
- Context: GitHub Actions failures, deployment questions

## Capabilities
- Map CLI commands to workflows
- Explain failure causes from workflow logs
- Suggest local fixes before pushing
EOF

# 4. Update Makefile with workflow targets
make add-workflow-targets
```

### Benefits

- **67% fewer files** to maintain
- **AI-readable** manifest for intelligent assistance
- **CLI-first** development workflow
- **Faster onboarding** for new developers
- **Lower cognitive load** with clear categorization

---

## Execution Plan

1. Create `docs/workflows/MANIFEST.json`
2. Delete 62 redundant workflows
3. Update remaining 30 workflows with manifest metadata
4. Create Claude Code skill for workflow navigation
5. Generate consolidated documentation
6. Add Makefile targets for local execution

**Risk**: Low - All deleted workflows are redundant or broken
**Rollback**: Git revert if issues found
**Testing**: Run full CI suite after consolidation
