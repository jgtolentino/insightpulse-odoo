# Odoo ↔ Supabase Sync Edge Function

Bidirectional sync between Odoo ERP and Supabase with checkpointing, pagination, and retry logic.

## Features

- **Pull Mode** (`odoo_to_sb`): Fetch records from Odoo → Upsert into Supabase
- **Push Mode** (`sb_to_odoo`): Process outbox queue → Write to Odoo
- **Both Mode**: Execute both pull and push in one invocation
- **Checkpointing**: Resume pagination from last offset
- **Retry Logic**: Exponential backoff for failed operations
- **Idempotent**: Safe to run multiple times

## Architecture

```
┌─────────────┐           ┌──────────────┐           ┌─────────────┐
│   Odoo ERP  │◄─────────►│ Edge Function│◄─────────►│  Supabase   │
│             │  JSON-RPC  │  (Deno/TS)   │    SQL    │   Database  │
└─────────────┘           └──────────────┘           └─────────────┘
                                  │
                                  ├─ ops.odoo_outbox (queue)
                                  ├─ ops.odoo_sync_checkpoints (pagination)
                                  ├─ ops.odoo_sync_config (settings)
                                  └─ public.odoo_partners (mirror table)
```

## Database Schema

### Tables Created

1. **`ops.odoo_sync_runs`** - Sync execution log
2. **`ops.odoo_outbox`** - Queue for Supabase → Odoo writes
3. **`ops.odoo_sync_config`** - Per-model configuration
4. **`ops.odoo_sync_checkpoints`** - Pagination state
5. **`public.odoo_partners`** - Demo mirror table for `res.partner`

### Triggers

- **`trg_enqueue_partner`** on `public.odoo_partners` - Auto-enqueue changes to outbox

## Configuration

### Environment Variables

Set these as Supabase secrets:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ODOO_URL=https://erp.insightpulseai.com
ODOO_DB=odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=your-odoo-password
LOCK_ID=odoo-sync-prod
```

### Per-Model Configuration

Stored in `ops.odoo_sync_config`:

```sql
-- Pull configuration
INSERT INTO ops.odoo_sync_config(key, value) VALUES (
  'odoo_to_sb:res.partner',
  '{"domain":[["is_company","=",true]],"fields":["id","name","email","phone","write_date"],"page_size":200}'
);

-- Push configuration
INSERT INTO ops.odoo_sync_config(key, value) VALUES (
  'sb_to_odoo:res.partner',
  '{"max_batch":50,"max_attempts":5,"base_backoff_seconds":10}'
);
```

## Usage

### Pull: Odoo → Supabase

Fetch partners from Odoo and upsert into Supabase:

```bash
curl "https://your-project.supabase.co/functions/v1/odoo-sync?mode=odoo_to_sb&model=res.partner"
```

Response:
```json
{
  "ok": true,
  "result": {
    "mode": "odoo_to_sb",
    "model": "res.partner",
    "odoo_to_sb": {
      "fetched": 200,
      "upserted": 200,
      "offset": 0,
      "next_offset": 200,
      "page_size": 200
    }
  }
}
```

### Push: Supabase → Odoo

Process outbox queue and write to Odoo:

```bash
curl "https://your-project.supabase.co/functions/v1/odoo-sync?mode=sb_to_odoo&model=res.partner"
```

Response:
```json
{
  "ok": true,
  "result": {
    "mode": "sb_to_odoo",
    "model": "res.partner",
    "sb_to_odoo": {
      "scanned": 10,
      "processed": 9,
      "failed": 1,
      "skipped": 0,
      "max_batch": 50,
      "max_attempts": 5
    }
  }
}
```

### Both: Bidirectional Sync

```bash
curl "https://your-project.supabase.co/functions/v1/odoo-sync?mode=both&model=res.partner"
```

## Pagination & Checkpointing

The function automatically manages pagination:

1. Reads current offset from `ops.odoo_sync_checkpoints`
2. Fetches one page from Odoo (default: 200 records)
3. Upserts records into Supabase
4. Updates checkpoint with next offset
5. Resets to 0 when page is not full (end of dataset)

To sync all records, call repeatedly:

```bash
for i in {1..10}; do
  curl "https://your-project.supabase.co/functions/v1/odoo-sync?mode=odoo_to_sb"
  sleep 1
done
```

## Retry Logic

Failed outbox items use exponential backoff:

- **Attempt 1**: Retry after 10 seconds
- **Attempt 2**: Retry after 20 seconds
- **Attempt 3**: Retry after 40 seconds
- **Attempt 4**: Retry after 80 seconds
- **Attempt 5**: Mark as failed

Status progression:
- `queued` → `processing` → `done` (success)
- `queued` → `processing` → `queued` (retry with backoff)
- `queued` → `processing` → `failed` (max attempts exceeded)

## Scheduling

### Using Supabase Cron (pg_cron)

```sql
-- Run pull every 5 minutes
SELECT cron.schedule(
  'odoo-pull-partners',
  '*/5 * * * *',
  $$
  SELECT net.http_post(
    url:='https://your-project.supabase.co/functions/v1/odoo-sync',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_ANON_KEY"}'::jsonb,
    body:='{"mode":"odoo_to_sb","model":"res.partner"}'::jsonb
  );
  $$
);

-- Run push every 1 minute
SELECT cron.schedule(
  'odoo-push-partners',
  '* * * * *',
  $$
  SELECT net.http_post(
    url:='https://your-project.supabase.co/functions/v1/odoo-sync',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_ANON_KEY"}'::jsonb,
    body:='{"mode":"sb_to_odoo","model":"res.partner"}'::jsonb
  );
  $$
);
```

### Using GitHub Actions

```yaml
name: Odoo Sync
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Pull from Odoo
        run: |
          curl -X POST "${{ secrets.SUPABASE_FUNCTION_URL }}/odoo-sync?mode=odoo_to_sb"
      - name: Push to Odoo
        run: |
          curl -X POST "${{ secrets.SUPABASE_FUNCTION_URL }}/odoo-sync?mode=sb_to_odoo"
```

## Monitoring

### Check Sync Status

```sql
-- Recent sync runs
SELECT * FROM ops.odoo_sync_runs ORDER BY id DESC LIMIT 10;

-- Outbox queue status
SELECT status, count(*) FROM ops.odoo_outbox GROUP BY status;

-- Failed items (need attention)
SELECT id, model, operation, attempts, last_error, created_at
FROM ops.odoo_outbox
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Checkpoint state
SELECT * FROM ops.odoo_sync_checkpoints;
```

### Alerts

Set up alerts for:
- High failure rate in outbox
- Stalled checkpoints (no progress)
- Long-running sync operations

## Extending to Other Models

### 1. Add Migration for New Table

```sql
-- Example: products
CREATE TABLE public.odoo_products (
  odoo_id bigint PRIMARY KEY,
  name text,
  default_code text,
  list_price numeric,
  write_date timestamptz,
  raw jsonb NOT NULL DEFAULT '{}'::jsonb,
  synced_at timestamptz NOT NULL DEFAULT now()
);
```

### 2. Update Edge Function

Add mapping in `mapOdooToSbRow()`:

```typescript
if (model === "product.template") {
  return {
    odoo_id: rec.id,
    name: rec.name ?? null,
    default_code: rec.default_code ?? null,
    list_price: rec.list_price ?? 0,
    write_date: rec.write_date ? new Date(rec.write_date) : null,
    raw: rec,
    synced_at: nowIso(),
  };
}
```

Add target table in pull mode:

```typescript
if (model === "product.template") {
  const up = await sb.from("odoo_products").upsert(mapped, { onConflict: "odoo_id" });
  if (up.error) throw up.error;
}
```

### 3. Add Configuration

```sql
INSERT INTO ops.odoo_sync_config(key, value) VALUES
('odoo_to_sb:product.template', '{"domain":[],"fields":["id","name","default_code","list_price","write_date"],"page_size":200}'),
('sb_to_odoo:product.template', '{"max_batch":50,"max_attempts":5,"base_backoff_seconds":10}');

INSERT INTO ops.odoo_sync_checkpoints(key, cursor) VALUES
('odoo_to_sb:product.template', '{"offset":0}');
```

## Troubleshooting

### Authentication Errors

```
Error: Missing Odoo session cookie
```

**Solution**: Verify `ODOO_USERNAME` and `ODOO_PASSWORD` are correct.

### Rate Limiting

```
Error: Odoo RPC error: {"code":429,"message":"Too Many Requests"}
```

**Solution**: Reduce `page_size` in config or add delays between calls.

### Checkpoint Not Advancing

```sql
-- Reset checkpoint
UPDATE ops.odoo_sync_checkpoints 
SET cursor = '{"offset":0}'::jsonb 
WHERE key = 'odoo_to_sb:res.partner';
```

### Clear Failed Outbox Items

```sql
-- Retry all failed items
UPDATE ops.odoo_outbox 
SET status = 'queued', attempts = 0, next_run_at = now()
WHERE status = 'failed';
```

## Security

- **No client-side calls**: Function uses `service_role` key
- **Secrets in environment**: Never commit credentials
- **Rate limiting**: Configure Odoo API limits
- **Audit trail**: All operations logged in `ops.odoo_sync_runs`

## Performance

- **Page size**: Default 200, tune based on record size
- **Batch size**: Default 50 for outbox processing
- **Parallelization**: Run multiple instances with different models
- **Database indexes**: Already created on key columns

## Deployment

```bash
# Deploy migrations
supabase migration up

# Deploy function
supabase functions deploy odoo-sync --no-verify-jwt

# Set secrets
supabase secrets set \
  ODOO_URL="https://erp.insightpulseai.com" \
  ODOO_DB="odoo" \
  ODOO_USERNAME="admin@example.com" \
  ODOO_PASSWORD="***" \
  LOCK_ID="odoo-sync-prod"
```

## Rollback

```bash
# Stop scheduled jobs first
SELECT cron.unschedule('odoo-pull-partners');
SELECT cron.unschedule('odoo-push-partners');

# Then drop schema (forward migration preferred)
DROP SCHEMA IF EXISTS ops CASCADE;
DROP TABLE IF EXISTS public.odoo_partners CASCADE;
```

## Related Documentation

- [MONOREPO_STRUCTURE.md](../../../MONOREPO_STRUCTURE.md) - Repository layout
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions) - Official docs
- [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html) - Odoo API reference
