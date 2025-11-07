# Supabase Runbook

## Database Connection Saturation

**Severity**: P0
**Symptoms**: Connection refused errors, timeouts on new connections, 504 Gateway Timeout

### Detect
- Alert `SupabaseDBConnectionsHigh` fired
- Applications unable to connect to database
- PgBouncer connection pool exhausted

### Check
```bash
# 1. Check current connections vs limit
psql "$POSTGRES_URL" -c "
  SELECT
    count(*) as current_connections,
    (SELECT setting::int FROM pg_settings WHERE name='max_connections') as max_connections,
    round(100.0 * count(*) / (SELECT setting::int FROM pg_settings WHERE name='max_connections'), 2) as pct
  FROM pg_stat_activity;
"

# 2. Check idle connections
psql "$POSTGRES_URL" -c "
  SELECT state, count(*)
  FROM pg_stat_activity
  GROUP BY state
  ORDER BY count(*) DESC;
"

# 3. Check connections by application
psql "$POSTGRES_URL" -c "
  SELECT application_name, state, count(*)
  FROM pg_stat_activity
  GROUP BY application_name, state
  ORDER BY count(*) DESC;
"

# 4. Check PgBouncer status (if using pooler)
psql "postgresql://postgres.spdtwktxdalcfigzeqrz@aws-1-us-east-1.pooler.supabase.com:6543/pgbouncer" -c "SHOW POOLS;"
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/kill_idle_connections.sh

# Or manually kill idle connections
psql "$POSTGRES_URL" -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle'
    AND state_change < now() - interval '10 minutes'
    AND pid <> pg_backend_pid();
"
```

### Verify
```bash
# Check connections dropped below 80%
psql "$POSTGRES_URL" -c "
  SELECT
    count(*) as current,
    (SELECT setting::int FROM pg_settings WHERE name='max_connections') as max,
    round(100.0 * count(*) / (SELECT setting::int FROM pg_settings WHERE name='max_connections'), 2) as pct
  FROM pg_stat_activity;
"

# Monitor for 10 minutes
watch -n 30 "psql '$POSTGRES_URL' -c 'SELECT count(*) FROM pg_stat_activity;'"
```

### Prevent
- Tune PgBouncer `pool_mode` (transaction vs session)
- Set connection limits per application
- Implement connection retry logic with exponential backoff
- Use connection pooling in application code
- Monitor connection trends
- Set appropriate `max_connections` in postgresql.conf

---

## Storage Full

**Severity**: P0
**Symptoms**: Write errors, unable to upload files, backup failures

### Detect
- Alert `SupabaseStorageFull` fired
- Upload errors in application logs
- Backup jobs failing

### Check
```bash
# 1. Check storage usage via Supabase Dashboard
# Navigate to: Project Settings > Usage

# 2. Check bucket sizes
psql "$POSTGRES_URL" -c "
  SELECT
    bucket_id,
    count(*) as file_count,
    pg_size_pretty(sum(length(metadata))::bigint) as metadata_size
  FROM storage.objects
  GROUP BY bucket_id
  ORDER BY count(*) DESC;
"

# 3. Check for large files
psql "$POSTGRES_URL" -c "
  SELECT
    bucket_id,
    name,
    pg_size_pretty(metadata->>'size'::bigint) as size,
    created_at
  FROM storage.objects
  WHERE (metadata->>'size')::bigint > 100000000  -- 100MB
  ORDER BY (metadata->>'size')::bigint DESC
  LIMIT 20;
"

# 4. Check for old files
psql "$POSTGRES_URL" -c "
  SELECT
    bucket_id,
    count(*) as old_files
  FROM storage.objects
  WHERE created_at < now() - interval '180 days'
  GROUP BY bucket_id;
"
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/prune_old_storage.sh

# Or manually delete old files
psql "$POSTGRES_URL" <<EOF
-- Delete files older than 180 days in temp bucket
DELETE FROM storage.objects
WHERE bucket_id = 'temp'
  AND created_at < now() - interval '180 days';

-- Delete orphaned files (no references)
-- TODO: Add application-specific logic
EOF
```

### Verify
```bash
# Check storage usage dropped
psql "$POSTGRES_URL" -c "
  SELECT
    bucket_id,
    count(*) as file_count,
    pg_size_pretty(sum((metadata->>'size')::bigint)) as total_size
  FROM storage.objects
  GROUP BY bucket_id;
"

# Should show reduction in file count and size
```

### Prevent
- Implement lifecycle policies for old files
- Set file size limits in storage policies
- Regular cleanup jobs for temp files
- Monitor storage quota usage
- Use CDN for large static assets
- Implement file compression

---

## RLS Policy Leak

**Severity**: P1
**Symptoms**: Unauthorized data access, users seeing others' data, security audit failures

### Detect
- Alert `SupabaseRLSPolicyLeak` fired (if audit logging enabled)
- User reports seeing unauthorized data
- Security audit findings

### Check
```bash
# 1. List tables without RLS enabled
psql "$POSTGRES_URL" -c "
  SELECT schemaname, tablename
  FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'storage', 'auth')
    AND tablename NOT IN (
      SELECT tablename
      FROM pg_tables t
      JOIN pg_class c ON c.relname = t.tablename
      WHERE c.relrowsecurity = true
    );
"

# 2. Check RLS policies per table
psql "$POSTGRES_URL" -c "
  SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
  FROM pg_policies
  ORDER BY schemaname, tablename;
"

# 3. Test policy as user
# TODO: Add application-specific test queries with test user credentials

# 4. Check for exposed service_role usage
grep -r "SUPABASE_SERVICE_ROLE_KEY" . --exclude-dir=node_modules --exclude-dir=.git
```

### Heal
```bash
# No auto-heal - requires manual policy creation
# This is intentional for security

# 1. Enable RLS on table
psql "$POSTGRES_URL" -c "ALTER TABLE <schema>.<table> ENABLE ROW LEVEL SECURITY;"

# 2. Create appropriate policies
psql "$POSTGRES_URL" <<EOF
-- Example: User can only see their own rows
CREATE POLICY user_select_own ON <schema>.<table>
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY user_insert_own ON <schema>.<table>
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_update_own ON <schema>.<table>
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_delete_own ON <schema>.<table>
  FOR DELETE
  USING (auth.uid() = user_id);
EOF
```

### Verify
```bash
# 1. Confirm RLS enabled
psql "$POSTGRES_URL" -c "
  SELECT
    schemaname,
    tablename,
    rowsecurity
  FROM pg_tables t
  JOIN pg_class c ON c.relname = t.tablename
  WHERE schemaname = '<your_schema>'
    AND c.relrowsecurity = true;
"

# 2. Test with test user (use anon or authenticated role)
# Attempt to access other users' data - should fail

# 3. Run policy test suite
# TODO: Add automated policy tests
```

### Prevent
- Enable RLS on ALL user tables
- Test policies for each role (anon, authenticated, service_role)
- Never expose `service_role` key to client
- Code review all policy changes
- Regular security audits
- Use policy templates/generators

---

## Edge Function Timeout

**Severity**: P2
**Symptoms**: Function timeouts after 60s, incomplete processing, client-side errors

### Detect
- Alert `SupabaseEdgeFunctionTimeout` fired
- Users see timeout errors
- Incomplete background jobs

### Check
```bash
# 1. Check function logs
supabase functions logs <function-name> --tail 100

# 2. Check function duration in dashboard
# Navigate to: Edge Functions > <function> > Logs

# 3. Identify slow external calls
# Review function code for:
# - Database queries without timeout
# - External API calls without timeout
# - CPU-intensive operations

# 4. Check Prometheus (if metrics exported)
curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(edge_function_duration_seconds_bucket[5m]))by(function,le))' | jq .
```

### Heal
```bash
# Run auto-heal handler (restarts function)
./auto-healing/handlers/restart_edge_function.sh <function-name>

# Or manually redeploy
supabase functions deploy <function-name>
```

### Verify
```bash
# 1. Test function execution
curl -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/<function-name>" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -d '{"test": true}'

# 2. Monitor execution time
# Should complete in <30s

# 3. Check logs for errors
supabase functions logs <function-name> --tail 20
```

### Prevent
- Break long operations into chunks
- Use async background jobs for heavy processing
- Set client timeout expectations
- Add timeouts to external API calls
- Optimize database queries
- Use streaming for large responses
- Consider Cloud Functions for CPU-intensive tasks

---

## Additional Resources

- Error Catalog: [ops/error-catalog/supabase.yaml](../../ops/error-catalog/supabase.yaml)
- Prometheus Alerts: [monitoring/prometheus/alerts_supabase.yml](../../monitoring/prometheus/alerts_supabase.yml)
- Auto-heal Handlers: [auto-healing/handlers/](../../auto-healing/handlers/)
- Supabase Docs: https://supabase.com/docs
