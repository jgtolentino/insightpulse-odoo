# Supabase Deployment Guide

**Project**: Finance Automation (spdtwktxdalcfigzeqrz)
**Components**: Edge Function + Migration for W101 closing snapshots

---

## Prerequisites

```bash
# Install Supabase CLI (if not already installed)
brew install supabase/tap/supabase

# Login to Supabase
supabase login

# Link to project
supabase link --project-ref spdtwktxdalcfigzeqrz
```

---

## Step 1: Apply Database Migration

**Migration**: `202511210001_finance_closing_snapshots.sql`

```bash
cd /Users/tbwa/odoo-ce/notion-n8n-monthly-close/supabase

# Apply migration to production
supabase db push --include-all

# Verify table created
psql "$POSTGRES_URL" -c "\d finance_closing_snapshots"
```

**Expected Output**:
```
Table "public.finance_closing_snapshots"
Column         | Type                   | Modifiers
---------------+------------------------+-----------
id             | uuid                   | primary key
captured_at    | timestamp with time zone | not null
source         | text                   | not null
odoo_db        | text                   | not null
period_label   | text                   | not null
total_tasks    | integer                | not null
...
```

---

## Step 2: Deploy Edge Function

**Function**: `closing-snapshot`

### 2.1 Set Environment Secrets

```bash
# Set secrets for Edge Function
supabase secrets set \
  SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co" \
  SUPABASE_SERVICE_ROLE_KEY="<service_role_key>"

# Verify secrets set
supabase secrets list
```

### 2.2 Deploy Function

```bash
cd /Users/tbwa/odoo-ce/notion-n8n-monthly-close/supabase

# Deploy function
supabase functions deploy closing-snapshot

# Verify deployment
supabase functions list
```

**Expected Output**:
```
┌─────────────────┬────────────┬──────────────────────────────────────────────────────┬─────────┐
│ NAME            │ VERSION    │ ENTRYPOINT                                           │ STATUS  │
├─────────────────┼────────────┼──────────────────────────────────────────────────────┼─────────┤
│ closing-snapshot│ v1.0.0     │ /functions/closing-snapshot/index.ts                 │ active  │
└─────────────────┴────────────┴──────────────────────────────────────────────────────┴─────────┘
```

---

## Step 3: Test Edge Function

### 3.1 Test with curl

```bash
curl -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/closing-snapshot" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "manual_test",
    "odoo_db": "odoo",
    "period_label": "2025-11",
    "total_tasks": 24,
    "open_tasks": 8,
    "blocked_tasks": 2,
    "done_tasks": 14,
    "cluster_a_open": 3,
    "cluster_b_open": 2,
    "cluster_c_open": 2,
    "cluster_d_open": 1
  }'
```

**Expected Response**:
```json
{
  "status": "ok",
  "message": "Closing snapshot saved successfully",
  "snapshot_id": "uuid-here",
  "captured_at": "2025-11-21T15:00:00.000Z",
  "period_label": "2025-11",
  "total_tasks": 24,
  "open_tasks": 8,
  "blocked_tasks": 2,
  "done_tasks": 14
}
```

### 3.2 Verify in Database

```bash
psql "$POSTGRES_URL" -c "SELECT * FROM finance_closing_snapshots ORDER BY captured_at DESC LIMIT 1;"
```

---

## Step 4: Monitor Function Logs

```bash
# Follow function logs in real-time
supabase functions logs closing-snapshot --follow

# View recent logs
supabase functions logs closing-snapshot --limit 50
```

---

## Rollback Procedure

If deployment fails or issues arise:

### Rollback Migration

```bash
# Drop table (warning: data loss!)
psql "$POSTGRES_URL" -c "DROP TABLE IF EXISTS finance_closing_snapshots CASCADE;"

# Or disable RLS policies
psql "$POSTGRES_URL" -c "ALTER TABLE finance_closing_snapshots DISABLE ROW LEVEL SECURITY;"
```

### Rollback Edge Function

```bash
# Delete function
supabase functions delete closing-snapshot

# Or deploy previous version
supabase functions deploy closing-snapshot --import-map import_map_old.json
```

---

## Integration with n8n W101

After successful deployment, update n8n workflow:

**File**: `workflows/supabase/W101_SB_CLOSE_SNAPSHOT.json`

**Edge Function URL**:
```
https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/closing-snapshot
```

**Required Headers**:
```yaml
Authorization: Bearer <service_role_key>
Content-Type: application/json
```

**Required Payload**:
```json
{
  "source": "n8n",
  "odoo_db": "odoo",
  "period_label": "YYYY-MM",
  "total_tasks": 0,
  "open_tasks": 0,
  "blocked_tasks": 0,
  "done_tasks": 0,
  "cluster_a_open": 0,
  "cluster_b_open": 0,
  "cluster_c_open": 0,
  "cluster_d_open": 0
}
```

---

## Troubleshooting

### Function Returns 400

**Cause**: Missing required fields
**Solution**: Verify payload includes `odoo_db` and `period_label`

### Function Returns 500

**Cause**: Database connection error or RLS policy issue
**Solution**:
1. Check secrets: `supabase secrets list`
2. Verify RLS policies: `psql "$POSTGRES_URL" -c "\d+ finance_closing_snapshots"`
3. Check function logs: `supabase functions logs closing-snapshot`

### No Data in Table

**Cause**: RLS policies blocking insert
**Solution**: Verify service role policy exists:
```sql
SELECT * FROM pg_policies WHERE tablename = 'finance_closing_snapshots';
```

---

**Last Updated**: 2025-11-21
**Maintained By**: Finance SSC Team - InsightPulse AI
