# Cron Jobs & Edge Function Webhook Review

**Date**: 2025-11-10
**Reviewer**: Claude Code
**Status**: Analysis Complete

---

## Executive Summary

- **GitHub Actions Cron Jobs**: 26 workflows with scheduled triggers
- **Supabase Edge Functions**: 15 functions (4 webhook-based)
- **Celery Beat Schedules**: Not yet deployed (planned for Visual KG)
- **Issues Found**: 8 workflows with syntax errors, 15+ redundant cron jobs

---

## 1. GitHub Actions Cron Jobs (26 Total)

### Daily (2 AM UTC) - 11 Workflows ⚠️ TOO MANY

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `auto-patch.yml` | 0 2 * * * | Auto-patch dependencies | ❌ Redundant | DELETE - covered by `scheduled.yml` |
| `automation-health.yml` | 0 2 * * * | Health monitoring | ✅ Keep | Core monitoring |
| `backup-scheduler.yml` | 0 2 * * * | Daily backups | ✅ Keep | Critical |
| `oca-intel-sync.yml` | 0 2 * * * | Sync OCA module catalog | ✅ Keep | Important |
| `odoo-module-update.yml` | 0 2 * * * | Update Odoo modules | ❌ Redundant | DELETE - manual only |
| `scheduled.yml` | 0 2 * * * | Generic scheduled tasks | ✅ Keep | Consolidation target |
| `skillsmith-integration.yml` | 0 2 * * * | Skill mining | ✅ Keep | AI automation |
| `superset-health.yml` | 0 2 * * * | Superset health check | ❌ Redundant | DELETE - covered by `automation-health.yml` |
| `superset-postgres-guard.yml` | 0 2 * * * | DB drift detection | ✅ Keep | Data integrity |
| `doc-automation.yml` | 0 3 * * * | Doc automation | ❌ Redundant | DELETE - covered by `docs-validation.yml` |
| `assistant-context-freshness.yml` | 0 3 * * * | Claude.md freshness | ✅ Keep | AI context validation |

**Recommendation**: Consolidate 11 daily jobs → 6 (delete 5 redundant)

### Every 30 Minutes - 1 Workflow ⚠️ EXCESSIVE

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `health-monitor.yml` | */30 * * * * | Issue spam monitoring | ⚠️ Excessive | REDUCE to hourly or on-demand |

**Recommendation**: Change to hourly (0 * * * *) or workflow_dispatch only

### Every 6 Hours - 3 Workflows ✅ REASONABLE

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `integration-tests.yml` | 0 */6 * * * | Integration testing | ✅ Keep | Good cadence |
| `odoo-knowledge-scraper.yml` | 0 */6 * * * | Scrape Odoo forums | ✅ Keep | Knowledge building |
| `skillsmith.yml` | 0 */6 * * * | Skill generation | ❌ Redundant | DELETE - covered by `skillsmith-integration.yml` |

**Recommendation**: Keep 2, delete 1 duplicate

### Daily (Morning UTC) - 4 Workflows ✅ GOOD

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `parity-live-sync.yml` | 0 18 * * * | Live parity sync | ✅ Keep | Deployment validation |
| `ph-tax-canary.yml` | 0 9 * * * | BIR tax validation | ❌ Broken YAML | FIX or DELETE |
| `visual-compliance-agent.yml` | 0 9 * * 1 | Visual KG weekly run | ✅ Keep | AI validation |
| `wiki-alignment.yml` | 0 9 * * 1 | Wiki sync check | ❌ Redundant | DELETE - covered by `docs-validation.yml` |

### Weekly (Monday) - 5 Workflows ✅ GOOD CADENCE

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `dast-security.yml` | 0 3 * * 1 | Security scanning | ✅ Keep | Important security |
| `dependency-scanning.yml` | 0 0 * * 1 | Dependency audit | ✅ Keep | Security |
| `performance-testing.yml` | 0 2 * * 1 | Performance benchmarks | ❌ Not used | DELETE |

### Weekly (Sunday) - 3 Workflows ✅ GOOD CADENCE

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `generate-docs.yml` | 0 0 * * 0 | Weekly doc generation | ❌ Redundant | DELETE - covered by `gittodoc-cron.yml` |
| `openupgrade-test.yml` | 0 2 * * 0 | OpenUpgrade tests | ❌ Not used | DELETE |
| `validate-structure.yml` | 0 0 * * 0 | Structure validation | ❌ Broken YAML | FIX or DELETE |

### Monthly - 1 Workflow ✅ GOOD

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `bir-compliance-automation.yml` | 0 0 1 * * | BIR monthly reports | ❌ Broken YAML | FIX - critical for PH compliance |

### Other - 2 Workflows

| Workflow | Schedule | Purpose | Status | Action |
|----------|----------|---------|--------|--------|
| `claude-daily-cron.yml` | 17 3 * * * | Claude daily tasks | ❌ Redundant | DELETE - merge into `scheduled.yml` |
| `gittodoc-cron.yml` | 17 2 * * * | Git-to-doc daily | ✅ Keep | Important automation |

---

## 2. Supabase Edge Functions (15 Total)

### Webhook-Based Functions (4)

| Function | Trigger | Purpose | Deployment | Status |
|----------|---------|---------|------------|--------|
| `github-webhook` | GitHub webhook | PR/issue events | Production | ✅ Active |
| `drain_webhooks` | Task queue | Process webhook backlog | Production | ✅ Active |
| `notify-odoo` | Supabase DB trigger | Notify Odoo on changes | Production | ✅ Active |
| `odoo_sync_dispatcher` | Supabase DB trigger | Dispatch sync tasks | Production | ✅ Active |

### OAuth/Authentication Functions (3)

| Function | Trigger | Purpose | Deployment | Status |
|----------|---------|---------|------------|--------|
| `github-oauth` | HTTP request | OAuth flow | Production | ✅ Active |
| `github-app-install` | GitHub App install | App installation | Production | ✅ Active |
| `github-mint-token` | HTTP request | JWT token generation | Production | ✅ Active |

### Scheduled Functions (3) ⚠️ NO CRON CONFIGURED

| Function | Expected Schedule | Purpose | Deployment | Status |
|----------|-------------------|---------|------------|--------|
| `health_heartbeat` | Every 5 minutes? | Health monitoring | ❌ Not scheduled | NEEDS CRON |
| `superset_cache_warm` | Daily at 6 AM? | Warm Superset cache | ❌ Not scheduled | NEEDS CRON |
| `synthetic_order_flow` | Hourly? | Generate test data | ❌ Not scheduled | NEEDS CRON |

### Notification Functions (3)

| Function | Trigger | Purpose | Deployment | Status |
|----------|---------|---------|------------|--------|
| `notion-edge` | HTTP request | Notion integration | ⚠️ Deprecated | DELETE |
| `notion-escalation` | Notion webhook | Escalate tasks | ⚠️ Deprecated | DELETE |
| `notion-overdue` | Notion webhook | Overdue alerts | ⚠️ Deprecated | DELETE |

### Incident Management (2)

| Function | Trigger | Purpose | Deployment | Status |
|----------|---------|---------|------------|--------|
| `escalate_incidents` | Database trigger | Incident escalation | Production | ✅ Active |
| `drain_webhooks` | Task queue | Webhook processing | Production | ✅ Active |

---

## 3. Celery Beat Schedules (Visual KG)

### Current Status: ❌ NOT DEPLOYED

**Documented in** `visual_kg_spec.json`:

```json
{
  "celery_beat_schedule": {
    "refresh_knowledge_graph_daily": {
      "task": "visual_compliance.tasks.refresh_knowledge_graph",
      "schedule": "crontab(hour=2, minute=0)",
      "description": "Daily refresh of all knowledge graph repos"
    },
    "update_quality_metrics_6h": {
      "task": "visual_compliance.tasks.update_quality_metrics",
      "schedule": "crontab(minute=0, hour='*/6')",
      "description": "Update chunk quality scores every 6 hours"
    },
    "deduplicate_embeddings_weekly": {
      "task": "visual_compliance.tasks.deduplicate_embeddings",
      "schedule": "crontab(day_of_week=1, hour=3, minute=0)",
      "description": "Weekly deduplication cleanup"
    }
  }
}
```

**Action Required**: Deploy Celery Beat service:

```yaml
# Add to docker-compose.yml
celery-beat:
  build: .
  command: celery -A visual_compliance.celery_app beat --loglevel=info
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
    - VISUAL_KG_SUPABASE_URL=${VISUAL_KG_SUPABASE_URL}
  depends_on:
    - redis
  restart: unless-stopped
```

---

## 4. Issues Found

### Broken YAML Files (8) ❌

These workflows have syntax errors and cannot run:

1. `close-duplicate-health-issues.yml` - YAML parsing error line 45
2. `validate-structure.yml` - YAML parsing error line 66
3. `claude-sync-ci.yml` - Flow mapping error line 28
4. `auto-merge.yml` - Simple key error line 82
5. `assistant-guard.yml` - Simple key error line 25
6. `ph-tax-canary.yml` - Alias error line 132
7. `bir-compliance-automation.yml` - Alias error line 170 ⚠️ CRITICAL - BIR compliance
8. `month-end-task-automation.yml` - Alias error line 225

**Action**: Fix `bir-compliance-automation.yml` (critical), delete others

### Redundant Cron Jobs (15) ⚠️

Same 2 AM UTC time slot:
- 11 workflows all running at 2 AM UTC
- Creates resource contention
- Makes debugging harder

**Action**: Stagger schedules:
- Critical backups: 2 AM
- Health checks: 3 AM
- Maintenance: 4 AM
- Docs/sync: 5 AM

### Missing Cron for Edge Functions (3) ❌

Edge Functions that should be scheduled but aren't:
- `health_heartbeat` - Should run every 5 minutes
- `superset_cache_warm` - Should run daily at 6 AM
- `synthetic_order_flow` - Should run hourly (if needed for testing)

**Action**: Add Supabase cron jobs via SQL:

```sql
-- Add cron jobs for Edge Functions
SELECT cron.schedule(
  'health-heartbeat',
  '*/5 * * * *',
  $$
  SELECT net.http_post(
    url:='https://xkxyvboeubffxxbebsll.supabase.co/functions/v1/health_heartbeat',
    headers:='{"Authorization": "Bearer ' || current_setting('app.service_role_key') || '"}'::jsonb
  );
  $$
);

SELECT cron.schedule(
  'superset-cache-warm',
  '0 6 * * *',
  $$
  SELECT net.http_post(
    url:='https://xkxyvboeubffxxbebsll.supabase.co/functions/v1/superset_cache_warm',
    headers:='{"Authorization": "Bearer ' || current_setting('app.service_role_key') || '"}'::jsonb
  );
  $$
);
```

### Deprecated Functions (3) ⚠️

Notion integration is deprecated:
- `notion-edge`
- `notion-escalation`
- `notion-overdue`

**Action**: Delete these functions

---

## 5. Recommendations

### Immediate Actions (High Priority)

1. **Fix BIR Compliance Workflow** ❗ CRITICAL
   ```bash
   # Fix YAML syntax in bir-compliance-automation.yml
   # This is legally required for Philippine tax compliance
   ```

2. **Delete Redundant Workflows** (Save $$ on GitHub Actions minutes)
   ```bash
   rm .github/workflows/auto-patch.yml
   rm .github/workflows/odoo-module-update.yml
   rm .github/workflows/superset-health.yml
   rm .github/workflows/doc-automation.yml
   rm .github/workflows/skillsmith.yml
   rm .github/workflows/wiki-alignment.yml
   rm .github/workflows/performance-testing.yml
   rm .github/workflows/generate-docs.yml
   rm .github/workflows/openupgrade-test.yml
   rm .github/workflows/claude-daily-cron.yml
   ```

3. **Delete Broken Workflows** (Non-critical)
   ```bash
   rm .github/workflows/close-duplicate-health-issues.yml
   rm .github/workflows/validate-structure.yml
   rm .github/workflows/claude-sync-ci.yml
   rm .github/workflows/auto-merge.yml
   rm .github/workflows/assistant-guard.yml
   rm .github/workflows/ph-tax-canary.yml
   rm .github/workflows/month-end-task-automation.yml
   ```

4. **Delete Deprecated Edge Functions**
   ```bash
   rm -rf supabase/functions/notion-edge
   rm -rf supabase/functions/notion-escalation
   rm -rf supabase/functions/notion-overdue
   ```

5. **Add Missing Cron Jobs for Edge Functions**
   ```bash
   # Create migration: supabase/migrations/012_edge_function_cron.sql
   # Add cron.schedule() calls for health_heartbeat and superset_cache_warm
   ```

6. **Deploy Celery Beat for Visual KG**
   ```bash
   # Add celery-beat service to docker-compose.yml
   # Enable scheduled knowledge graph refresh
   ```

### Medium Priority

1. **Stagger Cron Schedules**
   - Avoid 11 workflows at 2 AM UTC
   - Spread across 2-6 AM for better resource distribution

2. **Reduce health-monitor.yml Frequency**
   - Change from */30 (every 30 min) to hourly
   - Or make it workflow_dispatch only

### Long-Term Improvements

1. **Consolidate into Makefile Targets**
   - All cron jobs should have `make` equivalents
   - Developers can test locally before CI

2. **Create Cron Dashboard**
   - Single page showing all scheduled jobs
   - Status, last run, next run
   - Link to logs

3. **Add Alerting for Failed Crons**
   - Critical: backup-scheduler, bir-compliance-automation
   - High: automation-health, superset-postgres-guard
   - Medium: docs, skillsmith

---

## 6. Cost Impact

**Current State**:
- 26 GitHub Actions cron jobs
- Many redundant/broken
- Unknown Edge Function invocation costs

**After Cleanup**:
- 15 GitHub Actions cron jobs (-42%)
- 12 Supabase Edge Functions (-20%)
- Estimated savings: ~$20-30/month in GitHub Actions minutes

---

## 7. Next Steps

Execute consolidation plan:

```bash
# 1. Fix critical BIR workflow
./scripts/fix-bir-workflow.sh

# 2. Delete redundant workflows (commit 1)
git rm .github/workflows/{auto-patch,odoo-module-update,superset-health,doc-automation,skillsmith,wiki-alignment,performance-testing,generate-docs,openupgrade-test,claude-daily-cron}.yml
git commit -m "refactor(ci): remove 10 redundant cron workflows"

# 3. Delete broken workflows (commit 2)
git rm .github/workflows/{close-duplicate-health-issues,validate-structure,claude-sync-ci,auto-merge,assistant-guard,ph-tax-canary,month-end-task-automation}.yml
git commit -m "fix(ci): remove 7 broken workflows with YAML syntax errors"

# 4. Delete deprecated Edge Functions (commit 3)
rm -rf supabase/functions/notion-*
git commit -m "refactor(edge-functions): remove deprecated Notion integration"

# 5. Add Edge Function cron jobs (commit 4)
cat > supabase/migrations/012_edge_function_cron.sql
git commit -m "feat(cron): add Supabase cron jobs for Edge Functions"

# 6. Deploy Celery Beat (commit 5)
# Edit docker-compose.yml to add celery-beat service
git commit -m "feat(visual-kg): deploy Celery Beat for scheduled tasks"

# 7. Push all changes
git push origin copilot/optimize-workflow-automation
```

---

**Review Date**: 2025-11-10
**Approver**: @jgtolentino
**Status**: Awaiting approval to execute cleanup
