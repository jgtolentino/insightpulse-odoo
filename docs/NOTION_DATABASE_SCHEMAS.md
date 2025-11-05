# Notion Database Schemas

Notion database schemas for Finance SSC automation workflows.

## Required Environment Variables

```bash
export NOTION_API_TOKEN="secret_xxx"          # Notion API integration token
export NOTION_BIR_DB_ID="db_bir_xxx"          # BIR Compliance database ID
export NOTION_MONTHEND_DB_ID="db_monthend_xxx" # Month-End Tasks database ID
export NOTION_FIELDS_DB_ID="db_fields_xxx"    # Field Documentation database ID
export NOTION_SOP_DB_ID="db_sop_xxx"          # SOPs database ID
```

## Database 1: BIR Compliance Calendar

**Purpose:** Track BIR form filing deadlines for all agencies

**Schema:**
| Property | Type | Description |
|----------|------|-------------|
| Form Code | Title | BIR form code with name (e.g., "1601-C - Monthly Withholding Tax") |
| Agency | Select | Agency code (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB) |
| Deadline | Date | Filing deadline |
| Reminder Date | Date | Reminder date (3 days before deadline) |
| Status | Select | Pending, In Progress, Completed, Overdue |
| Priority | Select | Critical, High, Medium, Low |
| External ID | Rich Text | Unique ID (bir_{form}_{agency}_{year}_{month}) |
| Last Synced | Date | Last sync timestamp |

**Checklist Template:**
- Gather supporting documents
- Prepare {form_code} form
- Review with Finance Officer
- Submit to BIR
- File copy in agency folder

## Database 2: Month-End Closing Tasks

**Purpose:** Track month-end closing tasks for all agencies

**Schema:**
| Property | Type | Description |
|----------|------|-------------|
| Task | Title | Task name with priority emoji and agency |
| Agency | Select | Agency code |
| Month | Rich Text | Month and year (e.g., "January 2025") |
| Deadline | Date | Task deadline |
| Priority | Select | Critical, High, Medium, Low |
| Status | Select | Pending, In Progress, Completed |
| External ID | Rich Text | Unique ID (monthend_{agency}_{task}_{year}_{month}) |
| Last Synced | Date | Last sync timestamp |

**Task Categories:**
1. Bank Reconciliation (Critical, +3 days)
2. Accounts Payable Review (High, +4 days)
3. Accounts Receivable Review (High, +4 days)
4. Expense Report Processing (High, +5 days)
5. General Ledger Review (Critical, +5 days)
6. Fixed Assets Review (Medium, +6 days)
7. Payroll Reconciliation (High, +5 days)
8. Financial Reports Generation (Critical, +7 days)

## Database 3: Field Documentation

**Purpose:** Document Odoo model fields

**Schema:**
| Property | Type | Description |
|----------|------|-------------|
| Field Name | Title | Model.field format |
| Model | Rich Text | Odoo model name |
| Field Type | Select | fields.Char, fields.Integer, fields.Many2one, etc. |
| Label | Rich Text | Field label (string parameter) |
| Help Text | Rich Text | Field help text |
| Required | Checkbox | Is field required? |
| Readonly | Checkbox | Is field readonly? |
| Source File | Rich Text | Python file path |
| External ID | Rich Text | Unique ID (field_{module}_{model}_{field}) |
| Last Synced | Date | Last sync timestamp |

## Database 4: Standard Operating Procedures (SOPs)

**Purpose:** Document procedures extracted from docstrings

**Schema:**
| Property | Type | Description |
|----------|------|-------------|
| SOP Name | Title | Module and procedure name |
| Module | Select | Odoo module name |
| Type | Select | Procedure, Process, Checklist |
| External ID | Rich Text | Unique ID (sop_{module}_{sop_name}) |
| Last Synced | Date | Last sync timestamp |

## External ID Pattern Benefits

**Idempotent Operations:**
- Workflows can run multiple times without creating duplicates
- Updates existing entries instead of creating new ones
- Ensures data consistency across workflow re-runs

**Format Examples:**
```
bir_1601-C_RIM_2025_01           # BIR entry
monthend_RIM_BankReconciliation_2025_01  # Month-end task
field_hr_payroll_hr.employee_salary       # Field documentation
sop_hr_payroll_month_end_closing          # SOP
```

## Setup Instructions

1. **Create Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Name: "InsightPulse Finance SSC Automation"
   - Submit and copy the API token

2. **Create Databases:**
   - Create 4 databases in your Notion workspace
   - Apply schemas from this document
   - Share each database with your integration

3. **Configure GitHub Secrets:**
   ```bash
   gh secret set NOTION_API_TOKEN --body "secret_xxx"
   gh secret set NOTION_BIR_DB_ID --body "db_bir_xxx"
   gh secret set NOTION_MONTHEND_DB_ID --body "db_monthend_xxx"
   gh secret set NOTION_FIELDS_DB_ID --body "db_fields_xxx"
   gh secret set NOTION_SOP_DB_ID --body "db_sop_xxx"
   ```

4. **Test Connection:**
   ```bash
   python scripts/bir_notion_sync.py \
     --calendar docs/bir_calendar_2025_01.json \
     --database-id "db_bir_xxx"
   ```

## Workflow Integration

**Workflows that sync to Notion:**
- `.github/workflows/bir-compliance-automation.yml` - Syncs BIR calendar
- `.github/workflows/month-end-task-automation.yml` - Syncs month-end tasks
- `.github/workflows/field-doc-sync.yml` - Syncs field documentation
- `.github/workflows/sop-generator.yml` - Syncs SOPs

**Sync Frequency:**
- BIR: Monthly (1st of each month)
- Month-End: Monthly (25th of each month)
- Fields: On push to `addons/**/models/*.py`
- SOPs: On push to `addons/**/*.py`

## Data Retention

**Notion Free Tier Limits:**
- 1,000 blocks per workspace
- Unlimited pages
- 5MB file upload limit

**Estimated Usage:**
- BIR: ~80 entries/year (4 forms × 8 agencies × 3-12 months)
- Month-End: ~64 entries/month (8 agencies × 8 tasks)
- Fields: ~500-1000 fields (depending on module count)
- SOPs: ~50-100 procedures

**Total:** ~2,000-3,000 Notion pages/year (within free tier)
