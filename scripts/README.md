# Scripts Directory

Deployment automation and health check scripts for the Finance Stack Health Monitoring system.

## Overview

This directory contains scripts to automate the deployment and operation of the finance stack health monitoring infrastructure.

## Deployment Scripts

### 1. `deploy-to-server.sh`

Deploys health check scripts to the production server (`erp.insightpulseai.net`).

**Usage:**
```bash
./scripts/deploy-to-server.sh [--env prod|staging|dev]
```

**What it does:**
- Creates remote directory structure
- Copies health check scripts to server
- Sets proper file permissions
- Validates deployment
- Displays next steps

**Prerequisites:**
- SSH access to `root@erp.insightpulseai.net`
- SSH key configured

**Example:**
```bash
# Deploy to production
./scripts/deploy-to-server.sh --env prod

# Deploy to staging
./scripts/deploy-to-server.sh --env staging
```

---

### 2. `apply-supabase-schema.sh`

Applies the Supabase health check database schema.

**Usage:**
```bash
./scripts/apply-supabase-schema.sh [--project-ref PROJECT_REF]
```

**What it does:**
- Validates Supabase connection
- Creates `health_check` table with RLS
- Creates helper views and functions
- Inserts test record for validation
- Displays next steps

**Prerequisites:**
- `SUPABASE_SERVICE_ROLE_KEY` environment variable set
- `SUPABASE_PROJECT_REF` environment variable set (or use `--project-ref` flag)
- `psql` command available

**Example:**
```bash
# Apply schema (using environment variables)
export SUPABASE_PROJECT_REF=xkxyvboeubffxxbebsll
export SUPABASE_SERVICE_ROLE_KEY=<your_service_role_key>
./scripts/apply-supabase-schema.sh

# Or specify project ref directly
./scripts/apply-supabase-schema.sh --project-ref xkxyvboeubffxxbebsll
```

---

### 3. `deployment-checklist.sh`

Interactive deployment progress tracker with validation.

**Usage:**
```bash
./scripts/deployment-checklist.sh [OPTIONS]
```

**Options:**
- `--env ENV` - Environment (prod|staging|dev) [default: prod]
- `--mark PHASE ITEM` - Mark item as complete
- `--reset` - Reset checklist
- `--help` - Display help

**What it does:**
- Displays deployment progress across 6 phases
- Auto-validates completed items where possible
- Tracks manual validation items
- Shows completion percentage and progress bar
- Saves state to `.deployment-checklist-{env}.txt`

**Example:**
```bash
# View deployment checklist for production
./scripts/deployment-checklist.sh --env prod

# Mark Supabase table creation as complete
./scripts/deployment-checklist.sh --mark 1 supabase_table

# Reset checklist
./scripts/deployment-checklist.sh --reset
```

**Deployment Phases:**
1. **Supabase Setup** (15 min) - Database schema and tables
2. **Server Deployment** (30 min) - Copy scripts to production server
3. **n8n Configuration** (45 min) - Credentials and workflow import
4. **GitHub Actions Setup** (20 min) - CI/CD configuration
5. **Odoo Integration** (30 min) - Webhook server actions
6. **Monitoring Setup** (15 min) - Mattermost channels and dashboards

---

## Health Check Scripts

### 4. `check_project_tasks.py`

UI domain health validator for Odoo finance projects.

**Usage:**
```bash
export ODOO_URL=https://erp.insightpulseai.net
export ODOO_DB=odoo
export ODOO_LOGIN=jgtolentino_rn@yahoo.com
export ODOO_PASSWORD=<your_password>

python3 scripts/check_project_tasks.py
```

**What it validates:**
- Finance projects (6, 10, 11) are accessible
- Project visibility settings are correct
- Task counts match database records
- UI domains and filters are working

**Exit Codes:**
- `0` - All checks passed
- `1` - UI domain / project visibility problems detected
- `2` - Configuration error (missing credentials)

**See also:** `docs/HEALTH_CHECK.md` for detailed documentation

---

## Data Import Scripts

### 5. `import_month_end_tasks.py`

Import and deduplicate month-end closing tasks from CSV.

**Usage:**
```bash
export POSTGRES_URL="postgres://postgres.xkxyvboeubffxxbebsll:${SUPABASE_SERVICE_ROLE_KEY}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

python3 scripts/import_month_end_tasks.py --csv data/month_end_tasks.csv --month-end 2025-01-31
```

**What it does:**
- Loads tasks from CSV file
- Deduplicates tasks by name (case-insensitive)
- Validates employee codes, cluster codes, and relative due dates
- Calculates actual due dates from month-end and relative dates (M-5, M+4, etc.)
- Inserts validated tasks into Supabase `month_end_tasks` table
- Provides detailed import summary with inserted/skipped counts

**CSV Format:**
```csv
Task Name,Owner,Reviewer,Approver,Cluster,Due Date
Create Google Drive folder,RIM,CKVC,CKVC,A,M-5
Month-end collection of receipts,RIM,CKVC,CKVC,A,M-5
```

**Options:**
- `--csv CSV_PATH` - Path to CSV file (required)
- `--month-end YYYY-MM-DD` - Month-end date for due date calculations (required)
- `--dry-run` - Validate without committing changes

**Prerequisites:**
- `POSTGRES_URL` environment variable with Supabase service role key
- Python packages: `psycopg2-binary`, `python-dotenv`, `pandas`
- Install with: `pip install psycopg2-binary python-dotenv pandas`
- Supabase schema applied: `03_month_end_tasks.sql`

**Example:**
```bash
# Dry run (validate only)
python3 scripts/import_month_end_tasks.py \
  --csv data/month_end_tasks.csv \
  --month-end 2025-01-31 \
  --dry-run

# Live import
python3 scripts/import_month_end_tasks.py \
  --csv data/month_end_tasks.csv \
  --month-end 2025-01-31
```

**Output:**
```
[INFO] Step 1: Loading CSV data...
[SUCCESS] Loaded 36 tasks from CSV

[INFO] Step 2: Deduplicating tasks...
[WARNING] Duplicate task: Create Google Drive folder (Agency Name) M01
[INFO] Found 1 duplicate tasks
[SUCCESS] Kept 35 unique tasks

[INFO] Step 3: Connecting to Supabase...
[SUCCESS] Connected to Supabase

[INFO] Step 4: Fetching valid employee and cluster codes...
[INFO] Found 9 active employees: ['BOM', 'CKVC', 'JAP', 'JPAL', 'JPL', 'JRMO', 'LAS', 'RIM', 'RMQB']
[INFO] Found 4 active clusters: ['A', 'B', 'C', 'D']

[INFO] Step 5: Validating tasks...
[SUCCESS] 35 tasks are valid

[INFO] Step 6: Importing tasks...
[SUCCESS] Inserted: Create Google Drive folder (Owner: RIM, Due: 2025-01-26)
...
[SUCCESS] Changes committed to database

[INFO] ===============================================================================
[INFO] Import Summary
[INFO] ===============================================================================
[INFO] Total tasks in CSV: 36
[INFO] Duplicates found: 1
[INFO] Unique tasks: 35
[INFO] Valid tasks: 35
[INFO] Invalid tasks: 0
[SUCCESS] Tasks inserted: 35
[WARNING] Tasks skipped: 0
[INFO] ===============================================================================
```

**See also:** `packages/db/sql/03_month_end_tasks.sql` for database schema

---

## Quick Start Guide

### First-Time Deployment

1. **Apply Supabase Schema:**
   ```bash
   export SUPABASE_PROJECT_REF=xkxyvboeubffxxbebsll
   export SUPABASE_SERVICE_ROLE_KEY=<your_key>
   ./scripts/apply-supabase-schema.sh
   ```

2. **Deploy to Server:**
   ```bash
   ./scripts/deploy-to-server.sh --env staging
   ```

3. **Track Progress:**
   ```bash
   ./scripts/deployment-checklist.sh --env staging
   ```

4. **Test Health Checks:**
   ```bash
   # SSH to server
   ssh root@erp.insightpulseai.net

   # Test scripts
   cd /opt/odoo-ce
   python3 scripts/check_project_tasks.py
   cd notion-n8n-monthly-close
   ./scripts/verify_finance_stack.sh --env staging --verbose
   ```

5. **Continue with n8n Configuration:**
   - Follow Phase 3 in `deployment-checklist.sh`
   - See `docs/DEPLOYMENT_GUIDE.md` for detailed steps

---

## Troubleshooting

### SSH Connection Issues
```bash
# Test SSH connection
ssh -v root@erp.insightpulseai.net echo "test"

# Configure SSH key
ssh-copy-id root@erp.insightpulseai.net

# Add host to known_hosts
ssh-keyscan erp.insightpulseai.net >> ~/.ssh/known_hosts
```

### Supabase Connection Issues
```bash
# Test connection manually
export POSTGRES_URL="postgres://postgres.xkxyvboeubffxxbebsll:${SUPABASE_SERVICE_ROLE_KEY}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
psql "$POSTGRES_URL" -c "SELECT 1;"

# Verify credentials
echo "Project Ref: ${SUPABASE_PROJECT_REF}"
echo "Key prefix: ${SUPABASE_SERVICE_ROLE_KEY:0:10}"
```

### Script Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Verify permissions
ls -la scripts/*.sh
```

---

## Documentation

- **`docs/DEPLOYMENT_GUIDE.md`** - Complete step-by-step deployment guide
- **`docs/HEALTH_CHECK.md`** - Health check system documentation
- **`packages/db/sql/02_health_check_table.sql`** - Supabase schema

---

## Environment Variables

Required environment variables for deployment scripts:

```bash
# Odoo
export ODOO_URL=https://erp.insightpulseai.net
export ODOO_DB=odoo
export ODOO_LOGIN=jgtolentino_rn@yahoo.com
export ODOO_PASSWORD=<your_password>

# Supabase
export SUPABASE_PROJECT_REF=xkxyvboeubffxxbebsll
export SUPABASE_SERVICE_ROLE_KEY=<your_service_role_key>

# n8n
export N8N_API_KEY=<your_n8n_api_key>

# Optional: GitHub
export GITHUB_TOKEN=<your_github_token>
```

Add these to your `~/.zshrc` or `~/.bashrc` for persistence.

---

## Support

For issues or questions:
1. Check `docs/HEALTH_CHECK.md` for troubleshooting
2. Review deployment checklist status
3. Check script logs in `/tmp/`
4. Contact: jgtolentino_rn@yahoo.com
