# Finance Ops Workflows

This directory contains n8n workflow JSON files organized by domain and purpose.

## Directory Structure

```
workflows/
├── odoo/               # Odoo-centric workflows (W000-W099, W400-W599)
│   ├── W001_OD_MNTH_CLOSE_SYNC.json     # Daily closing digest
│   ├── W002_OD_BIR_ALERTS.json          # BIR deadline alerts
│   ├── W401_CC_EXPENSE_IMPORT.json      # SAP Concur-equivalent: Expense import
│   ├── W402_CC_TRAVEL_APPROVAL.json     # SAP Concur-equivalent: Travel approval
│   ├── W501_EQ_BOOKING_SYNC.json        # Cheqroom-equivalent: Equipment booking
│   └── W502_EQ_OVERDUE_ALERTS.json      # Cheqroom-equivalent: Overdue alerts
├── supabase/           # Supabase data pipelines (W100-W199)
│   ├── W101_SB_CLOSE_SNAPSHOT.json      # Monthly close state snapshot
│   └── W102_SB_ERROR_EVENTS.json        # Error event logging
├── superset/           # Superset BI dashboards (W200-W299)
│   └── W201_SS_REFRESH_DASHBOARDS.json  # Dashboard refresh automation
├── notion/             # Notion workspace mirror (W300-W399)
│   ├── W301_NO_CLOSE_MIRROR.json        # Sync Notion with Odoo closing
│   └── W302_NO_TASKS_TO_ODOO.json       # Push Notion tasks to Odoo
├── backups/            # Time-stamped workflow backups
│   └── finance-workflows-YYYYMMDD-HHMMSS.json
└── index.yaml          # Single source of truth for all workflows
```

## Workflow Domains

### Odoo (OD)
Core finance operations integrated with Odoo CE 18.0:
- **W001-W099**: Core closing and BIR workflows
- **W400-W499**: SAP Concur-equivalent (expenses & travel)
- **W500-W599**: Cheqroom-equivalent (equipment management)

**Key Workflows**:
- **W001_OD_MNTH_CLOSE_SYNC**: Daily digest of overdue/due-soon closing tasks by cluster
- **W002_OD_BIR_ALERTS**: 7-day advance alerts for BIR filing deadlines
- **W401_CC_EXPENSE_IMPORT**: OCR receipt parsing → Odoo expense creation
- **W501_EQ_BOOKING_SYNC**: Equipment booking requests → Odoo equipment.booking records

### Supabase (SB)
Data pipeline workflows for analytics and logging:
- **W100-W199**: Snapshots, ETL, event logging

**Key Workflows**:
- **W101_SB_CLOSE_SNAPSHOT**: Nightly snapshot of closing state to Supabase for BI
- **W102_SB_ERROR_EVENTS**: Log failed OCR/workflow executions for debugging

### Superset (SS)
BI dashboard automation:
- **W200-W299**: Dashboard refreshes and data updates

**Key Workflows**:
- **W201_SS_REFRESH_DASHBOARDS**: Daily refresh of closing performance dashboards

### Notion (NO)
Workspace mirroring (optional - Odoo is canonical):
- **W300-W399**: Notion database sync and task import

**Key Workflows**:
- **W301_NO_CLOSE_MIRROR**: Mirror Odoo closing tasks to Notion for users who prefer Notion UI
- **W302_NO_TASKS_TO_ODOO**: Push Notion-created tasks into Odoo finance projects

## Naming Convention

All workflow files follow this pattern:

```
WNNN_DD_SHORT_DESCRIPTION.json
```

- `W`: Workflow prefix (literal)
- `NNN`: 3-digit sequence number (by domain)
- `DD`: 2-letter domain code (OD, SB, SS, NO, CC, EQ)
- `SHORT_DESCRIPTION`: UPPER_SNAKE summary

**Examples**:
- `W001_OD_MNTH_CLOSE_SYNC` → Workflow 001, Odoo domain, Monthly Closing Sync
- `W101_SB_CLOSE_SNAPSHOT` → Workflow 101, Supabase domain, Closing Snapshot
- `W401_CC_EXPENSE_IMPORT` → Workflow 401, Concur-equivalent, Expense Import

## Management via CLI

Use `scripts/n8n-sync.sh` to manage workflows:

```bash
# List all workflows
./scripts/n8n-sync.sh list

# Backup all workflows from production
./scripts/n8n-sync.sh backup

# Restore workflows to production (after fresh install)
./scripts/n8n-sync.sh restore

# Activate all workflows
./scripts/n8n-sync.sh activate

# Check workflow status
./scripts/n8n-sync.sh status

# Execute a specific workflow manually
./scripts/n8n-sync.sh execute W001_OD_MNTH_CLOSE_SYNC
```

## Adding New Workflows

1. Create workflow in n8n UI
2. Export JSON from n8n
3. Save as `workflows/<domain>/WNNN_DD_SHORT_DESCRIPTION.json`
4. Add entry to `workflows/index.yaml`:
   ```yaml
   - code: WNNN_DD_SHORT_DESCRIPTION
     id: <n8n_workflow_id>
     file: workflows/<domain>/WNNN_DD_SHORT_DESCRIPTION.json
     name: "internal_n8n_name"
     description: "Human-readable purpose"
     trigger: "Cron/Webhook/Manual"
     integrations: ["Service1", "Service2"]
     critical: true/false
     envs: [dev, prod]
   ```
5. Commit and push to repository
6. Deploy to production:
   ```bash
   git pull
   ./scripts/n8n-sync.sh restore
   ./scripts/n8n-sync.sh activate
   ```

## Credentials Management

**IMPORTANT**: Credentials are NOT stored in this repository.

Credentials are managed via:
- n8n UI (encrypted in PostgreSQL)
- Supabase Vault (for sensitive keys)
- Environment variables on production server

When restoring workflows, you must manually recreate credentials in the n8n UI:
1. Settings → Credentials → Add New
2. Match credential names referenced in workflow JSONs
3. Test connection before activating workflows

## Backup Strategy

**Automated Backups** (via cron):
- Daily: `/etc/cron.d/n8n-backup` runs `./scripts/n8n-sync.sh backup` at 3 AM PHT
- Retention: Keep last 30 days of backups

**Manual Backups** (before major changes):
```bash
./scripts/n8n-sync.sh backup
```

**Backup Location**: `workflows/backups/finance-workflows-YYYYMMDD-HHMMSS.json`

## Production Environment

**n8n Instance**:
- Container: `odoo-ipa-1`
- Host: `erp.insightpulseai.net`
- Database: PostgreSQL 15 (`odoo-n8n-postgres-1`)
- Cache: Redis 7 (`odoo-n8n-redis-1`)

**Integration Endpoints**:
- Odoo: `https://erp.insightpulseai.net`
- OCR: `https://ocr.insightpulseai.net`
- Supabase: `https://xkxyvboeubffxxbebsll.supabase.co`
- Superset: `https://superset.insightpulseai.net`
- Mattermost: `https://mattermost.insightpulseai.net`

## Troubleshooting

### Workflow not executing
1. Check status: `./scripts/n8n-sync.sh status`
2. Activate if needed: `./scripts/n8n-sync.sh activate`
3. Check n8n logs: `docker logs odoo-ipa-1 --tail 100`

### Import/Export failures
1. Verify SSH connectivity: `ssh root@erp.insightpulseai.net "echo OK"`
2. Check container status: `docker ps | grep odoo-ipa-1`
3. Verify file paths in `index.yaml`

### Credential issues
1. Check credentials in n8n UI (Settings → Credentials)
2. Verify credential names match workflow references
3. Test connections before activating workflows

## Reference Documentation

- **Conventions**: `../WORKFLOW_CONVENTIONS.md` - Complete naming and organizational standards
- **CLI Guide**: `../N8N_CLI_README.md` - Detailed n8n CLI operations reference
- **Platform Matrix**: `../specs/MODULE_SERVICE_MATRIX.md` - How workflows fit into overall architecture

---

**Last Updated**: 2025-11-21
**Maintained By**: Finance SSC Team - InsightPulse AI
