# Finance Stack Health Check System

Comprehensive health monitoring and alerting system for the InsightPulse Finance Stack.

## Overview

The health check system validates all critical components of the finance infrastructure:
- Odoo service and database
- Finance projects and tasks
- n8n workflows
- Supabase integration
- OCR services
- System workers

## Components

### 1. `scripts/check_project_tasks.py`

UI-domain health validator that verifies finance projects are accessible via Odoo's JSON-RPC API.

**Purpose:**
- Validates projects 6, 10, 11 exist and are active
- Verifies task counts match database reality
- Detects broken UI filters/domains before they impact users

**Usage:**
```bash
export ODOO_URL=https://erp.insightpulseai.net
export ODOO_DB=odoo
export ODOO_LOGIN=jgtolentino_rn@yahoo.com
export ODOO_PASSWORD=your_password

python3 scripts/check_project_tasks.py
```

**Expected Output:**
```
✅ Authenticated as UID=2

▶ Checking finance projects (6, 10, 11)…
  ✅ Project 6: Month-end Closing - Template
     Active: True | Visibility: employees | Tasks: 36
  ✅ Project 10: Tax Filing & BIR Compliance
     Active: True | Visibility: employees | Tasks: 17
  ✅ Project 11: Monthly Closing - November 2025
     Active: True | Visibility: employees | Tasks: 36

▶ Checking task counts & domains…
  ✅ Project 6: DB=36, Expected=36, UI_accessible=True
  ✅ Project 10: DB=17, Expected=17, UI_accessible=True
  ✅ Project 11: DB=36, Expected=36, UI_accessible=True

============================================================
✅ W150_UI_DOMAIN_OK: All finance projects and task domains are healthy.
============================================================
```

**Exit Codes:**
- `0` - All checks passed
- `1` - UI domain / project visibility problems detected
- `2` - Configuration error (missing credentials)

### 2. `notion-n8n-monthly-close/scripts/verify_finance_stack.sh`

Comprehensive health check script with 10 validation gates.

**Features:**
- Multi-environment support (`--env prod|dev|staging`)
- Auto-remediation mode (`--fix`)
- Verbose output (`--verbose`)
- JSON output for CI/CD (`--json`)
- Supabase logging integration

**Usage:**
```bash
# Production validation (default)
./notion-n8n-monthly-close/scripts/verify_finance_stack.sh

# Staging with auto-fix
./notion-n8n-monthly-close/scripts/verify_finance_stack.sh --env staging --fix

# Verbose output for debugging
./notion-n8n-monthly-close/scripts/verify_finance_stack.sh --env dev --verbose

# CI/CD mode (JSON output)
./notion-n8n-monthly-close/scripts/verify_finance_stack.sh --json
```

**Validation Gates:**

| Gate # | Name | Purpose | Fix Available |
|--------|------|---------|---------------|
| 1 | SSH Connectivity | Verify SSH access to Odoo server | No |
| 2 | Odoo Service | Check Odoo container running | Yes |
| 3 | Database | Verify PostgreSQL connectivity | No |
| 4 | Finance Projects | Ensure projects 6, 10, 11 exist | No |
| 5 | Finance Tasks | Verify task counts | No |
| 6 | UI Domain | Run check_project_tasks.py | No |
| 7 | n8n Workflows | Check n8n API accessibility | No |
| 8 | Supabase | Verify Supabase connectivity | No |
| 9 | OCR Service | Check OCR backend health | No |
| 10 | Workers | Verify Odoo workers alive | No |

**Environment Variables:**
```bash
# Required for Supabase logging
export SUPABASE_SERVICE_ROLE_KEY=sbp_...

# Required for n8n check
export N8N_API_KEY=n8n_api_...

# Required for UI domain check
export ODOO_PASSWORD=your_password
```

**Exit Codes:**
- `0` - All gates passed
- `1` - One or more gates failed
- `2` - Invalid environment specified

### 3. Supabase Health Check Table

Stores historical health check results for monitoring and alerting.

**Schema:**
```sql
CREATE TABLE public.health_check (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  check_time TIMESTAMPTZ DEFAULT NOW(),
  environment TEXT NOT NULL CHECK (environment IN ('prod', 'dev', 'staging')),
  gate_name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL', 'WARN')),
  duration_ms INTEGER CHECK (duration_ms >= 0),
  details JSONB DEFAULT '{}'::jsonb,
  fixed BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Helper Views:**
- `health_check_latest` - Latest result per environment and gate
- `health_check_summary` - Summary by environment (last 24 hours)
- `health_check_recent_failures` - Recent failures (last 24 hours)

**Helper Functions:**
- `get_environment_health(p_environment TEXT)` - Get latest status
- `mark_health_check_fixed(p_id UUID)` - Mark issue as fixed
- `clean_old_health_checks()` - Clean data >30 days old

**Queries:**
```sql
-- Get latest health status for production
SELECT * FROM public.get_environment_health('prod');

-- Get summary for all environments
SELECT * FROM public.health_check_summary;

-- Get recent failures
SELECT * FROM public.health_check_recent_failures;
```

### 4. n8n W150 Workflow

Automated health monitoring with Mattermost alerts.

**Schedule:** Daily at 7:30 AM PHT (23:30 UTC previous day)

**Workflow:**
1. Cron trigger
2. Run `verify_finance_stack.sh` via SSH
3. Run `check_project_tasks.py` via SSH
4. Merge results
5. Check for failures
6. Send Mattermost alert (success or failure)

**Setup:**
1. Import `W150_FINANCE_HEALTH_CHECK.json` into n8n
2. Configure environment variables in n8n:
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `N8N_API_KEY`
   - `ODOO_PASSWORD`
   - `MATTERMOST_WEBHOOK_URL`
3. Test manually before enabling cron

### 5. GitHub Actions Workflow

CI/CD integration for automated health checks.

**Triggers:**
- **Schedule:** Daily at 2 AM UTC (10 AM PHT)
- **Manual:** Via workflow_dispatch with parameters

**Features:**
- Runs both health scripts via SSH
- Combines reports into markdown
- Uploads artifacts (30-day retention)
- Triggers n8n alerts on failure
- Comments on PRs if health check fails

**Required Secrets:**
- `SSH_PRIVATE_KEY` - SSH key for erp.insightpulseai.net
- `SSH_KNOWN_HOSTS` - Known hosts entry
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `N8N_API_KEY` - n8n API key
- `ODOO_PASSWORD` - Odoo password
- `N8N_WEBHOOK_URL` - n8n webhook for alerts

**Manual Trigger:**
```bash
# Via GitHub UI: Actions → Finance Stack Health Check → Run workflow
# Or via gh CLI:
gh workflow run health-check.yml \
  -f environment=prod \
  -f fix_mode=false
```

## Troubleshooting

### Common Issues

#### 1. "SSH connection failed"

**Cause:** SSH key not configured or host unreachable

**Fix:**
```bash
# Test SSH connection
ssh -v root@erp.insightpulseai.net echo "test"

# Verify SSH key permissions
chmod 600 ~/.ssh/id_rsa

# Add host to known_hosts
ssh-keyscan erp.insightpulseai.net >> ~/.ssh/known_hosts
```

#### 2. "Odoo container not running"

**Cause:** Docker container stopped

**Fix:**
```bash
# Check container status
ssh root@erp.insightpulseai.net "docker ps | grep odoo"

# Restart if needed
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1"

# Or run with --fix flag
./verify_finance_stack.sh --env prod --fix
```

#### 3. "UI domain check failed"

**Cause:** Broken filters, invalid fields, or RLS issues

**Fix:**
1. Check Odoo logs:
   ```bash
   ssh root@erp.insightpulseai.net "docker logs --tail 100 odoo-odoo-1"
   ```

2. Run check_project_tasks.py with verbose output:
   ```bash
   ODOO_PASSWORD=xxx python3 scripts/check_project_tasks.py
   ```

3. Clear problematic filters in Odoo:
   - Go to Projects → List view
   - Clear all saved filters
   - Reset "Group By" to default

#### 4. "Supabase API unreachable"

**Cause:** Invalid service role key or network issue

**Fix:**
```bash
# Test Supabase connection
curl -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  https://xkxyvboeubffxxbebsll.supabase.co/rest/v1/

# Verify service role key is set
echo ${SUPABASE_SERVICE_ROLE_KEY:0:15}
```

#### 5. "n8n API unreachable"

**Cause:** n8n down or invalid API key

**Fix:**
```bash
# Test n8n API
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  https://ipa.insightpulseai.net/api/v1/workflows

# Check n8n service status
ssh root@ipa.insightpulseai.net "docker ps | grep n8n"
```

### Monitoring Best Practices

1. **Daily Review:** Check Mattermost #finance-alerts for health reports
2. **Supabase Dashboard:** Monitor trends in health_check table
3. **GitHub Actions:** Review artifact reports weekly
4. **Proactive Alerts:** Don't wait for failures - review warnings

### Maintenance

**Weekly:**
- Review health check trends in Supabase
- Address warnings before they become failures
- Update expected task counts if projects change

**Monthly:**
- Clean old health check data (auto-cleaned at 30 days)
- Review and update validation gates
- Update documentation with new insights

**Quarterly:**
- Audit all health check integrations
- Test auto-fix functionality on staging
- Review and optimize alert thresholds

## Integration with Other Systems

### Mattermost

Alerts sent to:
- `#finance-alerts` - Health check failures and warnings
- `#finance-ssc` - Expense OCR notifications
- `#finance-knowledge` - Knowledge page updates

### Supabase

Tables used:
- `health_check` - Health check results
- `knowledge_embeddings` - RAG embeddings (from Knowledge Gov workflow)

### DigitalOcean

Services monitored:
- `ade-ocr-backend` - OCR service health endpoint

## Future Enhancements

- [ ] Slack integration as alternative to Mattermost
- [ ] Email alerts for critical failures
- [ ] Grafana dashboard for health metrics
- [ ] Predictive alerts based on trend analysis
- [ ] Integration with Odoo notification system
- [ ] Mobile app push notifications
