# n8n Workflow Conventions – Finance Ops / Closing Stack

**Status**: Canonical
**Scope**: Odoo CE · Supabase · Superset · Notion · SAP Concur-equivalent · Cheqroom-equivalent

This document defines how we **name, store, and operate** n8n workflows for the Finance Ops workspace so they can be:

- moved between environments with CLI,
- restored after rebuilds, and
- extended without breaking IDs.

All workflows used for closing, BIR, and ERP automations **must follow these conventions**.

---

## 1. Directory Layout

Repo root (excerpt):

```text
notion-n8n-monthly-close/
  workflows/
    odoo/
      W001_OD_MNTH_CLOSE_SYNC.json
      W002_OD_BIR_ALERTS.json
      W401_CC_EXPENSE_IMPORT.json
      W402_CC_TRAVEL_APPROVAL.json
      W501_EQ_BOOKING_SYNC.json
      W502_EQ_OVERDUE_ALERTS.json
    supabase/
      W101_SB_CLOSE_SNAPSHOT.json
      W102_SB_ERROR_EVENTS.json
    superset/
      W201_SS_REFRESH_DASHBOARDS.json
    notion/
      W301_NO_CLOSE_MIRROR.json
      W302_NO_TASKS_TO_ODOO.json
    backups/
      finance-workflows-YYYYMMDD-HHMMSS.json
    index.yaml
  scripts/
    n8n-sync.sh
  docs/
  WORKFLOW_CONVENTIONS.md
  N8N_CLI_README.md
```

**Rules:**

* Every workflow JSON you care about lives under `workflows/<domain>/`.
* Every JSON file must be referenced in `workflows/index.yaml`.
* No "random exports" outside `workflows/` – if it's important, it gets an ID and an entry.

---

## 2. Workflow Code & File Naming

Each workflow has a **stable code** and a corresponding filename:

```text
WNNN_DD_SHORT_DESCRIPTION.json
```

* `W` – literal prefix (Workflow).
* `NNN` – 3-digit sequence number **within the domain**.
* `DD` – 2-letter domain code.
* `SHORT_DESCRIPTION` – UPPER_SNAKE summary.

### Domain Codes

| Domain         | Code | Example                                                 |
| -------------- | ---- | ------------------------------------------------------- |
| Odoo           | `OD` | `W001_OD_MNTH_CLOSE_SYNC` (month-end closing sync)      |
| Supabase       | `SB` | `W101_SB_CLOSE_SNAPSHOT` (closing data snapshot)        |
| Superset       | `SS` | `W201_SS_REFRESH_DASHBOARDS` (refresh BI dashboards)    |
| Notion         | `NO` | `W301_NO_CLOSE_MIRROR` (Notion mirror of closing board) |
| SAP Concur-eqv | `CC` | `W401_CC_EXPENSE_IMPORT` (import expenses into Odoo)    |
| Cheqroom-eqv   | `EQ` | `W501_EQ_BOOKING_SYNC` (equipment booking sync)   |

**Sequence guidelines:**

* `000–099`: Odoo (OD) core finance & closing
* `100–199`: Supabase (SB) data pipelines / snapshots
* `200–299`: Superset (SS) dashboards & refreshes
* `300–399`: Notion (NO) parity / migration / mirror
* `400–499`: Concur-equivalent (CC) expense/travel flows
* `500–599`: Cheqroom-equivalent (EQ) equipment flows

**Examples:**

* `workflows/odoo/W001_OD_MNTH_CLOSE_SYNC.json` - Daily closing digest
* `workflows/odoo/W002_OD_BIR_ALERTS.json` - BIR deadline alerts
* `workflows/supabase/W101_SB_CLOSE_SNAPSHOT.json` - Monthly close state snapshot
* `workflows/notion/W301_NO_CLOSE_MIRROR.json` - Notion closing board mirror
* `workflows/notion/W302_NO_TASKS_TO_ODOO.json` - Push Notion tasks to Odoo
* `workflows/odoo/W401_CC_EXPENSE_IMPORT.json` - SAP Concur-equivalent expense import
* `workflows/odoo/W402_CC_TRAVEL_APPROVAL.json` - SAP Concur-equivalent travel approval
* `workflows/odoo/W501_EQ_BOOKING_SYNC.json` - Cheqroom-equivalent equipment booking
* `workflows/odoo/W502_EQ_OVERDUE_ALERTS.json` - Cheqroom-equivalent overdue alerts

---

## 3. `index.yaml` – Single Source of Truth

`workflows/index.yaml` tracks **which workflows matter**, their IDs in n8n, and how critical they are.

Example:

```yaml
n8n_container: odoo-ipa-1   # Docker container name

workflows:
  - code: W001_OD_MNTH_CLOSE_SYNC
    id: 25
    file: workflows/odoo/W001_OD_MNTH_CLOSE_SYNC.json
    name: "closing_daily_digest"
    description: "Daily overdue/due-soon tasks by cluster"
    trigger: "Cron: 8 AM PHT"
    integrations: ["Odoo", "Mattermost"]
    critical: true
    envs: [dev, prod]

  - code: W002_OD_BIR_ALERTS
    id: 26
    file: workflows/odoo/W002_OD_BIR_ALERTS.json
    name: "bir_calendar_alerts"
    description: "BIR deadline alerts (7 days before)"
    trigger: "Cron: 9 AM PHT"
    integrations: ["Odoo", "Mattermost"]
    critical: true
    envs: [dev, prod]

  - code: W101_SB_CLOSE_SNAPSHOT
    id: 30
    file: workflows/supabase/W101_SB_CLOSE_SNAPSHOT.json
    name: "supabase_close_state_snapshot"
    description: "Write monthly close state to Supabase"
    trigger: "Cron: Daily 11 PM PHT"
    integrations: ["Odoo", "Supabase"]
    critical: true
    envs: [dev, prod]

  - code: W201_SS_REFRESH_DASHBOARDS
    id: 40
    file: workflows/superset/W201_SS_REFRESH_DASHBOARDS.json
    name: "superset_refresh_dashboards"
    description: "Refresh Superset closing dashboards"
    trigger: "Cron: Daily 5 AM PHT"
    integrations: ["Superset API"]
    critical: false
    envs: [prod]

  - code: W301_NO_CLOSE_MIRROR
    id: 50
    file: workflows/notion/W301_NO_CLOSE_MIRROR.json
    name: "notion_close_sync"
    description: "Sync Notion DB with Odoo close state"
    trigger: "Notion Trigger"
    integrations: ["Notion", "Odoo"]
    critical: true
    envs: [dev, prod]

  - code: W401_CC_EXPENSE_IMPORT
    id: 60
    file: workflows/odoo/W401_CC_EXPENSE_IMPORT.json
    name: "concur_expense_import"
    description: "Import expenses from OCR/CSV into Odoo"
    trigger: "Webhook / Schedule"
    integrations: ["Odoo", "OCR", "Supabase"]
    critical: true
    envs: [prod]

  - code: W501_EQ_BOOKING_SYNC
    id: 70
    file: workflows/odoo/W501_EQ_BOOKING_SYNC.json
    name: "equipment_booking_sync"
    description: "Sync booking requests → Odoo equipment.booking"
    trigger: "Webhook / Schedule"
    integrations: ["Odoo", "Supabase"]
    critical: true
    envs: [prod]
```

**Fields:**

* `code` – stable human code (`W001_OD_MNTH_CLOSE_SYNC`).
* `id` – numeric **n8n workflow ID** from the instance where it was first created.
* `file` – path to JSON file in the repo.
* `name` – internal n8n workflow name.
* `description` – human-readable purpose.
* `trigger` – how the workflow is activated.
* `integrations` – external services used.
* `critical` – `true` → must be working for Finance Ops to be "green".
* `envs` – allowed environments (`dev`, `prod`, etc.). For now, informational.

**Rules:**

1. When you create a **new** workflow in the n8n UI:

   * Name it clearly (same as `code` or close).
   * Note its numeric ID from n8n.
   * Export JSON and drop it into the correct domain folder.
   * Add an entry to `index.yaml` with `code`, `id`, `file`, `name`, `description`, `trigger`, `integrations`, `critical`, `envs`.

2. If you **change** a workflow in the Editor:

   * Export it again from n8n.
   * Overwrite the existing JSON file.
   * Keep `id` and `code` **unchanged**.

3. IDs move **with** the workflow:

   * `n8n import:workflow` keeps the ID.
   * `index.yaml` is your contract between Git and n8n.

---

## 4. CLI Wrapper – `scripts/n8n-sync.sh`

We use a single script to manage everything via CLI:

```bash
./scripts/n8n-sync.sh backup
./scripts/n8n-sync.sh restore
./scripts/n8n-sync.sh activate
./scripts/n8n-sync.sh execute W001_OD_MNTH_CLOSE_SYNC
./scripts/n8n-sync.sh list
./scripts/n8n-sync.sh status
```

### 4.1 Commands

* `backup`

  * Runs `n8n export:workflow --all` inside the container on production.
  * Copies JSON export into `workflows/backups/finance-workflows-YYYYMMDD-HHMMSS.json`.

* `restore`

  * Reads `workflows/index.yaml`.
  * For each entry, imports the corresponding JSON into n8n via `n8n import:workflow --input=-`.
  * Use after a fresh n8n install or DB reset.

* `activate`

  * Reads `index.yaml` and runs `n8n update:workflow --id=<ID> --active=true` for each.
  * You may need to restart n8n for active states to fully apply.

* `execute <CODE>`

  * Looks up ID in `index.yaml` and runs `n8n execute --id <ID>`.
  * Use for one-shot flows like:

    * `W001_OD_MNTH_CLOSE_SYNC` - Daily closing digest
    * `W101_SB_CLOSE_SNAPSHOT` - Monthly close snapshot
    * `W201_SS_REFRESH_DASHBOARDS` - Refresh BI dashboards

* `list`

  * Shows all workflows from `index.yaml` with their IDs and critical status.

* `status`

  * Checks active/inactive status of all workflows in production.

### 4.2 Environment Variables

* `N8N_CONTAINER` – default `odoo-ipa-1`; override for other hosts/containers.
* `N8N_HOST` – default `root@erp.insightpulseai.net`; SSH host for production.
* `BACKUP_DIR` – default `workflows/backups`.

Example:

```bash
N8N_CONTAINER=finance-n8n ./scripts/n8n-sync.sh backup
N8N_HOST=user@dev-server ./scripts/n8n-sync.sh execute W001_OD_MNTH_CLOSE_SYNC
```

---

## 5. Concur / Cheqroom / Notion Specific Notes

### 5.1 SAP Concur-Equivalent (CC*)

Handled via Odoo + n8n:

* **Odoo modules**: `ipai_expense`, `ipai_ocr_expense`, `ipai_finance_monthly_closing`.
* **n8n flows (examples):**

  * `W401_CC_EXPENSE_IMPORT` – Pulls expense records (e.g. CSV/API) → writes into Odoo CE.
  * `W402_CC_TRAVEL_APPROVAL` – Keeps travel requests in sync with Odoo project/tasks.

Pattern:

* Use **Odoo node** for CRUD into CE.
* Use **Supabase node** if you need staging tables before Odoo.
* Use **OCR adapter** at `ocr.insightpulseai.net` for receipt parsing.

### 5.2 Cheqroom-Equivalent (EQ*)

Handled via Odoo equipment + n8n:

* **Odoo modules**: `ipai_equipment` + base `stock` / `maintenance`.
* **n8n flows (examples):**

  * `W501_EQ_BOOKING_SYNC` – Syncs booking JSON / Supabase tables → Odoo `equipment.booking`.
  * `W502_EQ_OVERDUE_ALERTS` – Nightly job: emails + Mattermost messages for overdue returns.

### 5.3 Notion (NO*)

Notion is **optional UI**, Odoo is canonical.

* `W301_NO_CLOSE_MIRROR` – Mirror Odoo closing tasks into a Notion DB for users still living in Notion.
* `W302_NO_TASKS_TO_ODOO` – Push Notion tasks into Odoo Finance project.

**Requirement:**

* All Notion workflows use the Notion node + **internal integration**.
* n8n remains the glue; Odoo remains source of truth for closing/BIR status.

---

## 6. Secrets & Credentials

* **Never** store API keys or secrets in this repo.
* n8n credentials must be managed via:

  * n8n UI (encrypted in the DB), or
  * a separate secrets management layer (Vault, Docker secrets, etc.).
* CLI exports:

  * `n8n export:credentials --all --output=/files/backups/creds.json` should go into a **private backup location**, not Git.
  * If you must move between instances, use `--decrypted` once, then secure and delete after import.

---

## 7. How to Add a New Workflow (Checklist)

1. Build & test in n8n Editor UI.
2. Note its numeric ID from the n8n UI.
3. Export workflow JSON from n8n (editor "Download" or `export:workflow`).
4. Save it as `workflows/<domain>/WNNN_DD_SHORT_DESCRIPTION.json`.
5. Add an entry to `workflows/index.yaml`:

   * `code`, `id`, `file`, `name`, `description`, `trigger`, `integrations`, `critical`, `envs`.
6. Commit & push.
7. On server:

   * `git pull`
   * `./scripts/n8n-sync.sh restore`
   * `./scripts/n8n-sync.sh activate` (if it should be live)
8. (Optional) One-shot: `./scripts/n8n-sync.sh execute <CODE>`.

Once it's in `index.yaml`, it's part of the **Finance Ops automation surface** and will survive rebuilds.

---

## 8. Testing & Validation

### Local Testing

Before deploying to production:

1. Test workflow in n8n UI with sample data
2. Export JSON and validate structure
3. Test import/export cycle:
   ```bash
   ./scripts/n8n-sync.sh backup
   ./scripts/n8n-sync.sh restore
   ```

### Production Deployment

1. Create feature branch for workflow changes
2. Update `index.yaml` with new workflow details
3. Commit and push to GitHub
4. Pull on production server
5. Run restore and activate:
   ```bash
   cd /path/to/notion-n8n-monthly-close
   git pull origin main
   ./scripts/n8n-sync.sh restore
   ./scripts/n8n-sync.sh activate
   ```
6. Verify with status check:
   ```bash
   ./scripts/n8n-sync.sh status
   ```

### Monitoring

* Check n8n UI execution history for errors
* Monitor Mattermost notifications for workflow failures
* Review Supabase error_events table for logged exceptions

---

## 9. Maintenance & Backup Schedule

### Daily

* Automated workflow executions (per cron schedules)
* Error monitoring via `W102_SB_ERROR_EVENTS`

### Weekly

* Manual backup of all workflows:
  ```bash
  ./scripts/n8n-sync.sh backup
  ```
* Review workflow execution logs in n8n UI

### Monthly

* Full system backup including:
  * n8n database
  * Workflow JSONs
  * Credentials (encrypted)
* Update workflow documentation as needed
* Review and optimize workflow performance

---

## 10. Troubleshooting

### Workflow Not Executing

1. Check if workflow is active:
   ```bash
   ./scripts/n8n-sync.sh status
   ```
2. Activate if needed:
   ```bash
   ./scripts/n8n-sync.sh activate
   ```
3. Check n8n logs:
   ```bash
   ssh root@erp.insightpulseai.net "docker logs odoo-ipa-1 --tail 100"
   ```

### Import/Export Failures

1. Verify SSH connectivity:
   ```bash
   ssh root@erp.insightpulseai.net "echo 'Connection OK'"
   ```
2. Check n8n container status:
   ```bash
   ssh root@erp.insightpulseai.net "docker ps | grep odoo-ipa-1"
   ```
3. Verify file paths in `index.yaml`

### Credential Issues

1. Check credentials in n8n UI: Settings → Credentials
2. Re-create missing credentials
3. Update workflow to use correct credential names

---

**Last Updated**: 2025-11-21
**Maintained By**: Finance SSC Team - InsightPulse AI
**Production Instance**: `odoo-ipa-1` on `erp.insightpulseai.net`
