# n8n CLI Management for InsightPulse ERP Finance Automation

**n8n Instance**: `odoo-ipa-1` on `erp.insightpulseai.net`
**Database**: PostgreSQL (odoo-n8n-postgres-1)
**Cache**: Redis (odoo-n8n-redis-1)

---

## Quick Reference

### Base CLI Pattern
```bash
ssh root@erp.insightpulseai.net
docker exec -u node -it odoo-ipa-1 n8n <command> [flags]
```

---

## Common Operations

### 1. Execute a Workflow Manually
```bash
# Get workflow ID from n8n UI (URL: /workflow/<ID>)
docker exec -u node -it odoo-ipa-1 n8n execute --id 25
```

**Use for**:
- Testing `closing_daily_digest` manually
- Smoke-testing finance flows after deploy
- Debugging workflow logic

---

### 2. Activate/Deactivate Workflows

**Deactivate all workflows**:
```bash
docker exec -u node -it odoo-ipa-1 n8n update:workflow --all --active=false
```

**Activate specific workflow**:
```bash
docker exec -u node -it odoo-ipa-1 n8n update:workflow --id=25 --active=true
```

**Activate all workflows**:
```bash
docker exec -u node -it odoo-ipa-1 n8n update:workflow --all --active=true
```

---

### 3. Backup Workflows & Credentials

**Export all workflows**:
```bash
ssh root@erp.insightpulseai.net "docker exec -u node -it odoo-ipa-1 \
  n8n export:workflow --all --output=/files/backups/workflows-$(date +%Y%m%d).json"
```

**Export all credentials** (sensitive!):
```bash
ssh root@erp.insightpulseai.net "docker exec -u node -it odoo-ipa-1 \
  n8n export:credentials --all --output=/files/backups/credentials.json"
```

**Download to local repo**:
```bash
scp root@erp.insightpulseai.net:/files/backups/workflows-*.json \
  backups/
```

---

### 4. Import Workflows/Credentials

**Import workflows from repo**:
```bash
# First upload JSON to server
scp backups/odoo-workflows.json root@erp.insightpulseai.net:/tmp/

# Then import
ssh root@erp.insightpulseai.net "docker exec -u node -it odoo-ipa-1 \
  n8n import:workflow --input=/tmp/odoo-workflows.json --separate"
```

**Import credentials**:
```bash
ssh root@erp.insightpulseai.net "docker exec -u node -it odoo-ipa-1 \
  n8n import:credentials --input=/tmp/credentials.json"
```

---

### 5. Full Entity Export/Import (DB Migration)

**Export all entities** (workflows + credentials + executions + users):
```bash
ssh root@erp.insightpulseai.net "docker exec -u node -it odoo-ipa-1 \
  n8n export:entities --outputDir /files/entities-export \
  --includeExecutionHistoryDataTables=true"
```

**Import on new instance**:
```bash
ssh root@NEW_INSTANCE "docker exec -u node -it odoo-ipa-1 \
  n8n import:entities --inputDir /files/entities-export \
  --truncateTables=true"
```

---

### 6. Security & User Management

**Run security audit**:
```bash
docker exec -u node -it odoo-ipa-1 n8n audit
```

**Reset user management** (wipe users, start clean):
```bash
docker exec -u node -it odoo-ipa-1 n8n user-management:reset
```

**Disable MFA for stuck user**:
```bash
docker exec -u node -it odoo-ipa-1 n8n mfa:disable \
  --email=finance.ops@insightpulseai.com
```

---

## Finance Workspace Workflows

### Workflow IDs & Purpose

| ID | Name | Purpose | Trigger | Integrations |
|----|------|---------|---------|--------------|
| 25 | `closing_daily_digest` | Daily overdue/due-soon tasks by cluster | Cron: 8 AM PHT | Odoo, Mattermost |
| 26 | `bir_calendar_alerts` | BIR deadline alerts (7 days before) | Cron: 9 AM PHT | Odoo, Mattermost |
| 30 | `supabase_close_state_snapshot` | Write monthly close state to Supabase | Cron: Daily 11 PM PHT | Odoo, Supabase |
| 31 | `supabase_error_events` | Log failed OCR/n8n executions | Webhook | Supabase |
| 40 | `superset_refresh_dashboards` | Refresh Superset closing dashboards | Cron: Daily 5 AM PHT | Superset API |
| 50 | `notion_close_sync` | Sync Notion DB with Odoo close state | Notion Trigger | Notion, Odoo |
| 51 | `notion_tasks_to_odoo` | Push Notion tasks into Odoo Finance | Notion Trigger | Notion, Odoo |

---

## Bootstrap Finance Automations (Fresh Install)

Run this on a fresh n8n instance:

```bash
./scripts/bootstrap_finance_automations.sh
```

This script:
1. Imports all canonical workflows (Odoo + Supabase + Superset + Notion)
2. Imports credentials (Odoo, Supabase, Notion, Mattermost, Superset)
3. Activates only finance workflows by ID

---

## Daily Operations

### Morning Check (9 AM PHT)
```bash
# Check if workflows ran successfully
ssh root@erp.insightpulseai.net "docker logs odoo-ipa-1 --tail 50 | grep -E '(closing_daily_digest|bir_calendar_alerts)'"
```

### Manual Trigger (If Needed)
```bash
# Closing digest
docker exec -u node -it odoo-ipa-1 n8n execute --id 25

# BIR alerts
docker exec -u node -it odoo-ipa-1 n8n execute --id 26
```

### Weekly Backup (Automated via Cron)
```bash
# /etc/cron.d/n8n-backup on erp.insightpulseai.net
5 3 * * * root docker exec -u node odoo-ipa-1 n8n export:workflow --all --output=/files/backups/workflows-$(date +\%F).json
```

---

## Troubleshooting

### Workflow Not Running
1. **Check if active**:
   ```bash
   # In n8n UI: Workflows → check "Active" toggle
   # Or via CLI:
   docker exec -u node -it odoo-ipa-1 n8n update:workflow --id=25 --active=true
   ```

2. **Check logs**:
   ```bash
   docker logs odoo-ipa-1 --tail 100 | grep "ERROR"
   ```

3. **Check credentials**:
   ```bash
   # In n8n UI: Credentials → verify Odoo/Supabase/Mattermost
   ```

### Connection Errors

**Odoo connection failed**:
- Verify URL: `https://erp.insightpulseai.net`
- Verify API key: Check Odoo user settings
- Test: `curl https://erp.insightpulseai.net/web/database/selector`

**Supabase connection failed**:
- Verify project URL: `https://xkxyvboeubffxxbebsll.supabase.co`
- Verify service role key in credentials

**Mattermost connection failed**:
- Verify webhook URL format
- Check Mattermost channel permissions

### Credentials Not Found
```bash
# Re-import credentials
scp backups/credentials.json root@erp.insightpulseai.net:/tmp/
ssh root@erp.insightpulseai.net "docker exec -u node -it odoo-ipa-1 \
  n8n import:credentials --input=/tmp/credentials.json"
```

---

## Security Best Practices

### Credentials Management
- ❌ **NEVER** commit `credentials.json` to Git (contains secrets)
- ✅ Store credentials in 1Password or encrypted vault
- ✅ Use `.gitignore` for `backups/credentials*.json`
- ✅ Rotate API keys quarterly

### Access Control
- Only finance ops team has n8n UI access
- Use separate credentials per environment (dev/prod)
- Enable MFA for n8n admin users

### Audit Trail
- Monthly review of workflow execution logs
- Alert on failed executions (via `supabase_error_events`)
- Quarterly security audit: `docker exec -u node -it odoo-ipa-1 n8n audit`

---

## Development Workflow

### 1. Create/Edit Workflow in UI
1. Login to n8n UI at https://ipa.insightpulseai.net
2. Create/edit workflow with visual editor
3. Test with sample data
4. Save and activate

### 2. Export to Repo
```bash
# Export single workflow by ID
ssh root@erp.insightpulseai.net "docker exec -u node -it odoo-ipa-1 \
  n8n export:workflow --id=25 --output=/files/backups/closing_daily_digest.json"

# Download to local repo
scp root@erp.insightpulseai.net:/files/backups/closing_daily_digest.json \
  workflows/
```

### 3. Commit to Git
```bash
git add workflows/closing_daily_digest.json
git commit -m "Update closing digest workflow - add cluster filtering"
git push origin main
```

### 4. Deploy to Prod (If Separate)
```bash
scp workflows/closing_daily_digest.json root@PROD_SERVER:/tmp/
ssh root@PROD_SERVER "docker exec -u node -it odoo-ipa-1 \
  n8n import:workflow --input=/tmp/closing_daily_digest.json"
```

---

## Reference Links

- **n8n Documentation**: https://docs.n8n.io/
- **n8n CLI Reference**: https://docs.n8n.io/hosting/cli-commands/
- **Odoo XML-RPC**: https://www.odoo.com/documentation/18.0/developer/reference/external_api.html
- **Supabase API**: https://supabase.com/docs/reference/javascript/introduction
- **InsightPulse ERP**: https://erp.insightpulseai.net

---

**Last Updated**: 2025-11-21
**Maintained By**: Finance SSC Team - InsightPulse AI
