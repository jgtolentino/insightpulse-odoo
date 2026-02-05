# ETL CLI Command Reference
**InsightPulse Odoo - ETL Operations Guide**

This document provides a comprehensive reference for all CLI commands related to ETL operations, data synchronization, and pipeline management.

---

## Quick Reference

| Command | Purpose | Risk Level |
|---------|---------|------------|
| `./scripts/check-etl-health.sh` | Health check all ETL components | 🟢 Safe |
| `./scripts/validate-airbyte-sync.sh` | Check Airbyte sync status | 🟢 Safe |
| `./scripts/outbox-worker.py --once` | Process outbox queue once | 🟡 Moderate |
| `cd dbt && dbt run` | Run all dbt transformations | 🟡 Moderate |
| `./scripts/trigger-full-sync.sh [table]` | Force full resync | 🔴 High Risk |
| `./scripts/rollback-warehouse.sh` | Rollback warehouse changes | 🔴 High Risk |

---

## 1. Health Checks & Monitoring

### Check All ETL Components
**Command:**
```bash
./scripts/check-etl-health.sh
```

**What it does:**
- Validates Airbyte configuration files
- Checks dbt project structure
- Tests Supabase connectivity
- Inspects outbox queue depth
- Verifies warehouse schema
- Checks environment variables

**Exit codes:**
- `0` - All checks passed
- `1` - Critical failures detected
- See output for warnings

**Example output:**
```
==========================================
ETL Health Check - InsightPulse Odoo
==========================================

1. Airbyte Configuration Checks
------------------------------------------
✓ Airbyte config file exists
✓ Odoo source configured
✓ Supabase destination configured
✓ 17 data streams configured
⚠ Airbyte containers not detected

2. dbt Project Checks
------------------------------------------
✓ dbt project file exists
⚠ No dbt models implemented yet

...

========================================
Health Check Summary
========================================
Passed:  12
Warnings: 8
Failed:  0

✅ ETL Health Check PASSED
```

**Troubleshooting:**
- If failed: Review output, check ETL_BLOCKERS_REPORT.md
- If warnings: Component may not be deployed yet (expected in dev)

---

### Validate Airbyte Sync Status
**Command:**
```bash
./scripts/validate-airbyte-sync.sh
```

**Status:** ⏳ To be implemented

**Planned functionality:**
- Check Airbyte API health endpoint
- Retrieve last sync timestamp for each stream
- Calculate sync lag (current time - last sync)
- Report failed syncs

**Example (planned):**
```bash
$ ./scripts/validate-airbyte-sync.sh

Airbyte Sync Status Report
---------------------------
Stream: res_partner
  Last Sync: 2 minutes ago
  Status: ✓ Success
  Records Synced: 1,247

Stream: account_move
  Last Sync: 5 minutes ago
  Status: ✓ Success
  Records Synced: 8,932

Overall Health: ✓ All streams healthy
```

---

### Check Outbox Queue Depth
**Command:**
```bash
psql "$SUPABASE_DB_URL" -c "SELECT COUNT(*) FROM ops.odoo_outbox WHERE status = 'queued';"
```

**What it does:**
- Counts pending changes waiting to sync to Odoo
- High count indicates worker may be stalled

**Healthy range:**
- `0-100` - Normal
- `100-1000` - Monitor closely
- `>1000` - Investigate worker health

**Alerts:**
- Queue growing over time = worker not processing
- Queue stuck at same number = possible deadlock

---

### View Failed Syncs
**Command:**
```bash
./scripts/view-failed-syncs.sh
```

**Status:** ⏳ To be implemented

**Planned query:**
```sql
SELECT 
  id,
  model,
  operation,
  attempts,
  last_error,
  created_at
FROM ops.odoo_outbox
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 20;
```

---

## 2. Manual Sync Operations

### Trigger Full Airbyte Sync
**Command:**
```bash
./scripts/trigger-full-sync.sh [table_name]
```

**Status:** ⏳ To be implemented  
**Risk Level:** 🔴 High - Can cause load on source database

**Purpose:**
- Force full refresh of a table (ignoring cursor)
- Use when incremental sync is stuck or data drift detected

**Prerequisites:**
- Airbyte must be deployed and running
- Airbyte API credentials must be set

**Example:**
```bash
# Full sync of all tables
./scripts/trigger-full-sync.sh

# Full sync of specific table
./scripts/trigger-full-sync.sh account_move
```

**Rollback:**
- Cannot rollback sync itself
- Restore from warehouse backup if data corrupted

**Data Loss Risk:**
- Low (destination tables use upsert mode)
- Ensure source data is clean before syncing

---

### Process Outbox Queue Manually
**Command:**
```bash
python scripts/outbox-worker.py --once
```

**Status:** ⏳ To be implemented  
**Risk Level:** 🟡 Moderate - Writes to Odoo

**Purpose:**
- Manually process pending changes in outbox
- Useful for debugging or one-time fixes

**Options:**
- `--once` - Process queue once and exit
- `--daemon` - Run continuously (production mode)
- `--batch-size N` - Process N records at a time (default: 100)
- `--dry-run` - Preview changes without writing

**Example:**
```bash
# Process once in dry-run mode
python scripts/outbox-worker.py --once --dry-run

# Process with custom batch size
python scripts/outbox-worker.py --once --batch-size 50
```

**Monitoring:**
```bash
# Watch queue depth decrease
watch -n 5 'psql "$SUPABASE_DB_URL" -t -c "SELECT COUNT(*) FROM ops.odoo_outbox WHERE status = '\''queued'\'';"'
```

---

## 3. dbt Operations

### Run All dbt Models
**Command:**
```bash
cd dbt && dbt run
```

**Risk Level:** 🟡 Moderate - Transforms data in warehouse

**Prerequisites:**
- dbt profiles configured (`~/.dbt/profiles.yml`)
- Database credentials set
- Models exist in `dbt/models/`

**Options:**
```bash
# Run specific model
dbt run --models staging.stg_partners

# Run models matching selector
dbt run --models tag:staging

# Full refresh (drop and recreate)
dbt run --full-refresh

# Run in specific target (dev/prod)
dbt run --target prod
```

**Example output:**
```
Running with dbt=1.5.0
Found 5 models, 12 tests, 0 snapshots

14:23:45 | Concurrency: 4 threads
14:23:45 | 
14:23:45 | 1 of 5 START sql table model staging.stg_partners............... [RUN]
14:23:46 | 1 of 5 OK created sql table model staging.stg_partners.......... [OK in 0.52s]
```

---

### Run dbt Tests
**Command:**
```bash
cd dbt && dbt test
```

**Purpose:**
- Validate data quality (not null, unique, etc.)
- Check referential integrity
- Custom business logic tests

**Example:**
```bash
# Test specific model
dbt test --models staging.stg_partners

# Test all staging models
dbt test --models tag:staging
```

---

### Generate dbt Documentation
**Command:**
```bash
cd dbt && dbt docs generate && dbt docs serve
```

**Purpose:**
- Create interactive documentation
- View data lineage
- Browse model descriptions

**Access:**
- Open browser to `http://localhost:8080`

---

## 4. Knowledge Pipeline Operations

### Ingest Knowledge Data
**Command:**
```bash
python scripts/ingest-knowledge.py [--source forum|docs|oca]
```

**Status:** ⏳ To be implemented  
**Risk Level:** 🟢 Safe - Read-only from external sources

**Purpose:**
- Scrape Odoo forum for Q&A
- Fetch platform documentation
- Index OCA GitHub repos

**Options:**
- `--source` - Limit to specific source
- `--limit N` - Max records to scrape
- `--quality-threshold 0.7` - Min quality score

**Example:**
```bash
# Ingest from all sources
python scripts/ingest-knowledge.py

# Only forum threads with quality > 0.8
python scripts/ingest-knowledge.py --source forum --quality-threshold 0.8
```

---

### Update Knowledge Quality Scores
**Command:**
```bash
psql "$SUPABASE_DB_URL" -c "SELECT update_quality_scores();"
```

**Purpose:**
- Recalculate quality scores for all knowledge records
- Based on views, votes, answers, stars

**Schedule:**
- Run daily via cron
- After bulk ingestion

---

### Search Knowledge Base
**Command:**
```bash
psql "$SUPABASE_DB_URL" -c "SELECT * FROM search_knowledge('odoo month end closing', 5);"
```

**Purpose:**
- Test RAG search function
- Validate knowledge ingestion
- Debug search relevance

**Parameters:**
- `query_text` - Search query
- `limit_count` - Number of results (default: 5)
- `source_filter` - Limit to source (optional)

---

## 5. Rollback & Recovery

### Rollback Warehouse Changes
**Command:**
```bash
./scripts/rollback-warehouse.sh [backup_file]
```

**Status:** ⏳ To be implemented  
**Risk Level:** 🔴 High - Replaces current data

**Purpose:**
- Restore warehouse to previous state
- Use after failed migration or data corruption

**Prerequisites:**
- Valid backup file from `pg_dump`
- Downtime window (read-only during restore)

**Process:**
1. Stop all writes to warehouse
2. Drop current warehouse schema
3. Restore from backup
4. Validate data integrity
5. Resume operations

**Example:**
```bash
# Restore from specific backup
./scripts/rollback-warehouse.sh backups/warehouse_20260205.sql

# Restore from latest backup
./scripts/rollback-warehouse.sh --latest
```

---

### Clear Outbox Queue (Emergency)
**Command:**
```bash
psql "$SUPABASE_DB_URL" -c "TRUNCATE ops.odoo_outbox;"
```

**Risk Level:** 🔴 CRITICAL - Deletes pending changes  
**Data Loss:** YES - All queued changes lost

**When to use:**
- Outbox corrupted beyond repair
- Need to reset sync state
- Only as last resort

**Before running:**
1. Export outbox contents for analysis
2. Notify stakeholders
3. Document decision
4. Have restore plan

**Alternative (safer):**
```sql
-- Mark all as failed instead of deleting
UPDATE ops.odoo_outbox 
SET status = 'failed', 
    last_error = 'Manually marked failed for investigation'
WHERE status = 'queued';
```

---

### Restore Odoo Database
**Command:**
```bash
pg_restore -h $ODOO_DB_HOST -U $ODOO_DB_USER -d odoo backup_file.dump
```

**Risk Level:** 🔴 CRITICAL - Replaces Odoo data  
**Downtime:** Required

**Process:**
1. Stop Odoo application
2. Create safety backup of current state
3. Drop current database
4. Restore from backup
5. Run migrations if needed
6. Start Odoo

---

## 6. Debugging & Troubleshooting

### View Sync Logs
**Command:**
```bash
./scripts/view-sync-logs.sh [--tail 100]
```

**Status:** ⏳ To be implemented

**What it shows:**
- Recent sync operations
- Error messages
- Performance metrics

---

### Test Database Connectivity
**Command:**
```bash
# Test Odoo DB
psql "postgresql://$ODOO_DB_USER:$ODOO_DB_PASSWORD@$ODOO_DB_HOST:5432/$ODOO_DB_NAME" -c "SELECT 1;"

# Test Supabase
psql "$SUPABASE_DB_URL" -c "SELECT 1;"
```

**Troubleshooting:**
- Connection refused: Check firewall, host, port
- Authentication failed: Verify credentials
- Database not found: Check database name

---

### Check Table Row Counts
**Command:**
```bash
# In Odoo (source)
psql "$ODOO_DB_URL" -c "
SELECT 
  relname AS table_name,
  n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname LIKE 'account_%'
ORDER BY n_live_tup DESC;
"

# In Supabase (destination)
psql "$SUPABASE_DB_URL" -c "
SELECT 
  table_name,
  (xpath('/row/cnt/text()', 
    query_to_xml('SELECT COUNT(*) AS cnt FROM odoo_raw.' || table_name, false, true, '')))[1]::text::int AS row_count
FROM information_schema.tables
WHERE table_schema = 'odoo_raw'
ORDER BY table_name;
"
```

**Purpose:**
- Validate sync completeness
- Detect data drift

---

### Inspect Failed Records
**Command:**
```bash
psql "$SUPABASE_DB_URL" -x -c "
SELECT * 
FROM ops.odoo_outbox 
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 1;
"
```

**Flags:**
- `-x` - Expanded display (easier to read)

---

## 7. Scheduled Operations

### Recommended Cron Jobs

**Daily (3 AM):**
```bash
# Update knowledge quality scores
0 3 * * * psql "$SUPABASE_DB_URL" -c "SELECT update_quality_scores();" >> /var/log/etl-quality.log 2>&1

# Ingest new knowledge
30 3 * * * python /path/to/scripts/ingest-knowledge.py >> /var/log/etl-ingest.log 2>&1

# Backup warehouse
0 4 * * * pg_dump "$SUPABASE_DB_URL" | gzip > /backups/warehouse_$(date +\%Y\%m\%d).sql.gz
```

**Hourly:**
```bash
# Health check
0 * * * * /path/to/scripts/check-etl-health.sh >> /var/log/etl-health.log 2>&1
```

**Every 5 minutes (if worker not running as daemon):**
```bash
*/5 * * * * python /path/to/scripts/outbox-worker.py --once >> /var/log/outbox-worker.log 2>&1
```

---

## 8. Performance Optimization

### Add Indexes for Sync Tables
**Command:**
```bash
psql "$SUPABASE_DB_URL" -f supabase/migrations/XXX_etl_indexes.sql
```

**Recommended indexes:**
```sql
-- Outbox queue processing
CREATE INDEX IF NOT EXISTS idx_outbox_status_created 
  ON ops.odoo_outbox(status, created_at);

-- Sync run lookups
CREATE INDEX IF NOT EXISTS idx_sync_runs_direction_status 
  ON ops.odoo_sync_runs(direction, status, created_at DESC);

-- Partner lookups
CREATE INDEX IF NOT EXISTS idx_partners_odoo_id 
  ON public.odoo_partners(odoo_id);

CREATE INDEX IF NOT EXISTS idx_partners_synced_at 
  ON public.odoo_partners(synced_at DESC);
```

---

### Vacuum and Analyze
**Command:**
```bash
# Reclaim space and update statistics
psql "$SUPABASE_DB_URL" -c "VACUUM ANALYZE ops.odoo_outbox;"
psql "$SUPABASE_DB_URL" -c "VACUUM ANALYZE ops.odoo_sync_runs;"
```

**When to run:**
- After large deletes
- Weekly maintenance
- Performance degradation

---

## 9. Security Best Practices

### Rotate Database Credentials
```bash
# 1. Create new credentials in Supabase dashboard
# 2. Update environment variables
export SUPABASE_DB_PASSWORD="new_password"

# 3. Update Airbyte connections
./scripts/update-airbyte-credentials.sh

# 4. Restart workers
docker-compose restart outbox-worker

# 5. Revoke old credentials in Supabase
```

---

### Audit Access Logs
**Command:**
```bash
# Query PostgreSQL logs
psql "$SUPABASE_DB_URL" -c "
SELECT 
  usename,
  application_name,
  client_addr,
  COUNT(*) as connection_count
FROM pg_stat_activity
WHERE datname = 'postgres'
GROUP BY usename, application_name, client_addr;
"
```

---

## 10. Emergency Procedures

### All ETL Down - Quick Recovery
```bash
# 1. Check health
./scripts/check-etl-health.sh

# 2. Restart all ETL services
docker-compose restart airbyte outbox-worker

# 3. Verify queue processing
watch -n 5 'psql "$SUPABASE_DB_URL" -t -c "SELECT COUNT(*) FROM ops.odoo_outbox WHERE status = '\''queued'\'';"'

# 4. Check for errors
docker-compose logs --tail=100 -f outbox-worker
```

---

### Data Corruption Detected
```bash
# 1. STOP ALL WRITES
docker-compose stop outbox-worker airbyte

# 2. Assess scope
./scripts/assess-data-integrity.sh

# 3. Restore from backup (if needed)
./scripts/rollback-warehouse.sh --latest

# 4. Verify integrity
./scripts/validate-data-quality.sh

# 5. Resume operations
docker-compose up -d
```

---

## Appendix: Environment Variables

Required for ETL operations:

```bash
# Odoo Source
export ODOO_DB_HOST="odoo-db.internal"
export ODOO_DB_NAME="odoo"
export ODOO_DB_USER="odoo"
export ODOO_DB_PASSWORD="***"

# Supabase Destination
export SUPABASE_PROJECT_URL="https://xxx.supabase.co"
export SUPABASE_ANON_KEY="***"
export SUPABASE_SERVICE_KEY="***"
export SUPABASE_DB_HOST="db.xxx.supabase.co"
export SUPABASE_DB_NAME="postgres"
export SUPABASE_DB_USER="postgres"
export SUPABASE_DB_PASSWORD="***"
export SUPABASE_DB_URL="postgresql://postgres:***@db.xxx.supabase.co:5432/postgres"

# Airbyte (if deployed)
export AIRBYTE_API_URL="http://localhost:8000"
export AIRBYTE_API_KEY="***"
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-05  
**Maintained By:** DevOps Team

For issues or improvements, open a GitHub issue with label `etl` or `documentation`.
