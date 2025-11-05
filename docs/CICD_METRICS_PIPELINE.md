# CI/CD Metrics Pipeline

**Status**: ✅ Operational
**Date**: November 5, 2025
**Components**: GitHub Actions → Supabase → Superset

---

## Architecture

```
GitHub Actions Workflows
    ↓ (on workflow completion)
metrics-collector.yml
    ↓ (extracts metrics)
metrics.json
    ↓ (uploads via REST API)
Supabase ops.workflow_runs
    ↓ (queries)
Superset CI/CD Dashboard
```

---

## Components

### 1. Data Collection (GitHub Actions)

**File**: `.github/workflows/metrics-collector.yml`

**Trigger**:
- On workflow completion (any workflow)
- Every 6 hours (scheduled)

**Collects**:
- Workflow name
- Status (success/failure/cancelled)
- Duration (seconds)
- Created timestamp

**Output**: `metrics.json` → Uploaded to Supabase

### 2. Data Storage (Supabase)

**Schema**: `packages/db/sql/03_ci_cd_metrics.sql`

**Table**: `ops.workflow_runs`
```sql
CREATE TABLE ops.workflow_runs (
    id SERIAL PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    status TEXT NOT NULL,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**View**: `ops.workflow_success_rate`
- 30-day rolling success rate by workflow
- Average duration for successful runs
- Total run count

### 3. Visualization (Superset)

**Deployment Script**: `scripts/deploy-cicd-dashboard.py`

**Dashboards**:
1. **Overall Success Rate** - Big number showing % success
2. **Duration Trends** - Line chart of avg duration over time
3. **Status Distribution** - Pie chart of success/failure/cancelled
4. **Top Failing Workflows** - Table of most problematic workflows

---

## Deployment Guide

### Prerequisites

1. **Supabase**: Project running with credentials
2. **Superset**: Instance accessible (localhost:8088 or remote)
3. **GitHub Secrets**: Required secrets configured

### Step 1: Apply Database Schema

```bash
export POSTGRES_URL="postgresql://postgres.xxx:password@pooler.supabase.com:6543/postgres?sslmode=require"
psql "$POSTGRES_URL" -f packages/db/sql/03_ci_cd_metrics.sql
```

**Verify**:
```bash
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM ops.workflow_runs;"
# Should return: count = 0 (initially)
```

### Step 2: Configure GitHub Secrets

Navigate to: `Settings → Secrets and variables → Actions`

Add secrets:
- `SUPABASE_URL`: https://xxx.supabase.co
- `SUPABASE_SERVICE_ROLE_KEY`: sbp_xxx

**Verify**: Secrets exist with correct values

### Step 3: Trigger Metrics Collection

Two options:

**Option A: Manual Trigger**
```bash
gh workflow run metrics-collector.yml
```

**Option B: Wait for Next Workflow**
- Any workflow completion triggers collection
- Scheduled run every 6 hours

**Verify**:
```bash
psql "$POSTGRES_URL" -c "SELECT workflow_name, status, COUNT(*) FROM ops.workflow_runs GROUP BY workflow_name, status ORDER BY workflow_name;"
```

### Step 4: Deploy Superset Dashboard

```bash
# Set credentials
export SUPERSET_URL="http://localhost:8088"  # Or remote URL
export SUPERSET_USERNAME="admin"
export SUPERSET_PASSWORD="your_password"
export POSTGRES_URL="postgresql://..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="sbp_xxx"

# Run deployment
python scripts/deploy-cicd-dashboard.py
```

**Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 CI/CD Metrics Dashboard Deployment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 Authenticating with Superset...
✅ Authenticated successfully

🔗 Creating Supabase database connection...
✅ Database connection created (ID: 1)

📊 Creating workflow_runs dataset...
✅ Dataset created (ID: 1)

📈 Creating success rate chart...
✅ Success rate chart created (ID: 1)

⏱️  Creating duration trends chart...
✅ Duration chart created (ID: 2)

🥧 Creating status distribution chart...
✅ Status distribution chart created (ID: 3)

🎨 Assembling dashboard...
✅ Dashboard created (ID: 1)
🌐 Access at: http://localhost:8088/superset/dashboard/1/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Deployment Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 5: Access Dashboard

Navigate to: `http://localhost:8088/superset/dashboard/1/`

Login with Superset credentials (default: admin/admin)

---

## Monitoring

### Health Checks

**1. Data Collection**
```bash
# Check recent workflow runs uploaded
psql "$POSTGRES_URL" -c "
  SELECT
    workflow_name,
    COUNT(*) as runs,
    MAX(created_at) as last_run
  FROM ops.workflow_runs
  WHERE created_at > NOW() - INTERVAL '24 hours'
  GROUP BY workflow_name
  ORDER BY last_run DESC;
"
```

**2. Success Rate**
```bash
# Check overall success rate
psql "$POSTGRES_URL" -c "
  SELECT
    COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*) AS success_rate,
    COUNT(*) AS total_runs,
    AVG(duration_seconds) FILTER (WHERE status = 'success') AS avg_duration_sec
  FROM ops.workflow_runs
  WHERE created_at > NOW() - INTERVAL '7 days';
"
```

**3. Failing Workflows**
```bash
# Identify problematic workflows
psql "$POSTGRES_URL" -c "
  SELECT
    workflow_name,
    COUNT(*) FILTER (WHERE status = 'failure') AS failures,
    COUNT(*) AS total_runs,
    COUNT(*) FILTER (WHERE status = 'failure') * 100.0 / COUNT(*) AS failure_rate
  FROM ops.workflow_runs
  WHERE created_at > NOW() - INTERVAL '7 days'
  GROUP BY workflow_name
  HAVING COUNT(*) FILTER (WHERE status = 'failure') > 0
  ORDER BY failure_rate DESC
  LIMIT 10;
"
```

### Alerts

**Recommended Thresholds**:
- Success rate < 80% → Investigate failing workflows
- Average duration > 10 minutes → Optimize slow workflows
- No data collected in 12 hours → Check metrics-collector.yml

---

## Troubleshooting

### Issue: No Metrics Appearing in Supabase

**Check**:
1. GitHub Secrets exist: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
2. Workflow logs: `gh run list --workflow=metrics-collector.yml`
3. Database schema applied: `psql "$POSTGRES_URL" -c "\dt ops.*"`

**Fix**:
```bash
# Re-apply schema
psql "$POSTGRES_URL" -f packages/db/sql/03_ci_cd_metrics.sql

# Trigger manual collection
gh workflow run metrics-collector.yml

# Check logs
gh run view $(gh run list --workflow=metrics-collector.yml --limit 1 --json databaseId -q ".[0].databaseId")
```

### Issue: Superset Dashboard Deployment Fails

**Check**:
1. Superset accessible: `curl -I http://localhost:8088/health`
2. Credentials correct: `SUPERSET_USERNAME`, `SUPERSET_PASSWORD`
3. Database connection valid: Test in Superset UI

**Fix**:
```bash
# Test authentication
curl -X POST http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password","provider":"db","refresh":true}'

# Re-run deployment with verbose logging
python scripts/deploy-cicd-dashboard.py
```

### Issue: Charts Not Showing Data

**Check**:
1. Data exists in `ops.workflow_runs`: Run SQL queries above
2. Dataset refreshed: Click "Refresh metadata" in Superset
3. Query executes: Check SQL Lab in Superset

**Fix**:
```bash
# Verify dataset exists and has columns
psql "$POSTGRES_URL" -c "\d ops.workflow_runs"

# Refresh Superset dataset metadata
# (Navigate to: Data → Datasets → workflow_runs → Edit → Columns)
```

---

## Maintenance

### Daily

- **Monitor success rate**: Should be ≥ 80%
- **Check failing workflows**: Investigate failures
- **Verify data collection**: Recent workflows should appear

### Weekly

- **Review trends**: Identify patterns in failures
- **Optimize slow workflows**: Durations increasing?
- **Clean old data** (optional):
  ```sql
  DELETE FROM ops.workflow_runs WHERE created_at < NOW() - INTERVAL '90 days';
  ```

### Monthly

- **Dashboard updates**: Add new charts as needed
- **Query optimization**: Add indexes if slow
- **Storage review**: Check Supabase usage

---

## Cost Analysis

**Before** (Manual process):
- Time: 2 hours/week reviewing workflow logs
- Cost: $200/month (engineer time)

**After** (Automated):
- Time: 5 minutes/week dashboard review
- Cost: $0/month (included in existing Supabase/Superset)

**ROI**: $2,400/year savings + faster insights

---

## Future Enhancements

**Phase 2**:
- [ ] Failure root cause classification (via LLM analysis)
- [ ] Predictive failure alerts (ML model on historical data)
- [ ] Cross-repository metrics (compare repos)
- [ ] Cost tracking per workflow (GitHub Actions minutes)

**Phase 3**:
- [ ] Real-time alerting (Slack/email on failures)
- [ ] Workflow optimization suggestions
- [ ] Historical trend analysis (year-over-year)
- [ ] Integration with DORA metrics (deployment frequency, lead time)

---

**Last Updated**: November 5, 2025
**Maintained By**: DevOps Team
**Status**: Production Ready ✅
