# Odoo Runbook

## Bus/Longpoll Stalls

**Severity**: P0
**Symptoms**: UI freezes, chatbus unresponsive, delayed notifications

### Detect
- Alert `OdooLongpollLatencyHigh` fired
- User reports of frozen interface
- Longpoll endpoint timing out

### Check
```bash
# 1. Check gevent worker logs
docker compose logs odoo --tail 200 | grep -i "gevent\|longpoll\|bus"

# 2. Check CPU usage
docker stats --no-stream | grep odoo

# 3. Check database connections
docker compose exec odoo psql $PGDATABASE -c "
  SELECT count(*), state
  FROM pg_stat_activity
  GROUP BY state;
"

# 4. Check Prometheus metric
curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(odoo_longpoll_latency_seconds_bucket[5m]))by(le))' | jq .
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/restart_longpoll.sh

# Or manually restart
docker compose restart odoo
```

### Verify
```bash
# 1. Check latency returned to normal
# Should show p95 < 1s after 10 minutes

# 2. Test real-time updates
# Open Odoo UI, trigger notification (e.g., send message)
# Should appear immediately

# 3. Monitor for 10 minutes
watch -n 30 'docker stats --no-stream | grep odoo'
```

### Prevent
- Scale workers appropriately for CPU-bound load
- Separate longpoll worker class (dedicated workers)
- Monitor worker resource usage
- Set appropriate timeouts

---

## Cron Job Jam

**Severity**: P1
**Symptoms**: Scheduled jobs delayed >30m

### Detect
- Alert `OdooCronStuck` fired
- Scheduled reports not sent
- Automated tasks not running

### Check
```bash
# 1. Check cron job queue in Odoo
docker compose exec odoo odoo shell -d $ODOO_DB <<EOF
from odoo import api, SUPERUSER_ID
env = api.Environment(self.env.cr, SUPERUSER_ID, {})
jobs = env['ir.cron'].search([('active', '=', True)])
for job in jobs:
    if job.nextcall and (datetime.now() - job.nextcall).total_seconds() > 1800:
        print(f"DELAYED: {job.name} - next: {job.nextcall}")
EOF

# 2. Check for database locks
docker compose exec odoo psql $PGDATABASE -c "
  SELECT pid, usename, query, state, wait_event_type, wait_event
  FROM pg_stat_activity
  WHERE wait_event_type = 'Lock';
"

# 3. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=increase(odoo_cron_job_age_seconds_sum[10m])' | jq .
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/unlock_cron.sh

# Or manually unlock
docker compose exec odoo odoo -d $ODOO_DB -u base --stop-after-init --log-level=warning
```

### Verify
```bash
# Check pending jobs cleared
docker compose exec odoo odoo shell -d $ODOO_DB <<EOF
jobs = env['ir.cron'].search([('active', '=', True)])
delayed = [j for j in jobs if j.nextcall and (datetime.now() - j.nextcall).total_seconds() > 300]
print(f"Delayed jobs: {len(delayed)}")
EOF

# Should return 0 delayed jobs
```

### Prevent
- Set appropriate concurrency per job
- Make jobs idempotent with retries
- Monitor job execution time
- Use job priority/queues
- Set reasonable timeouts

---

## Database Deadlock

**Severity**: P1
**Symptoms**: Transaction timeouts, HTTP 504, workers hanging

### Detect
- Alert `OdooDbDeadlock` fired
- Users see "Database locked" errors
- Requests timing out

### Check
```bash
# 1. Check for locks
docker compose exec odoo psql $PGDATABASE -c "
  SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
  FROM pg_catalog.pg_locks blocked_locks
  JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
  JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
  JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
  WHERE NOT blocked_locks.granted;
"

# 2. Check long-running queries
docker compose exec odoo psql $PGDATABASE -c "
  SELECT pid, now() - query_start AS duration, query, state
  FROM pg_stat_activity
  WHERE state = 'active' AND query_start < now() - interval '30 seconds'
  ORDER BY duration DESC;
"
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/kill_slow_queries.sh

# Or manually kill blocking queries
# Get PID from above query, then:
docker compose exec odoo psql $PGDATABASE -c "SELECT pg_terminate_backend(<PID>);"
```

### Verify
```bash
# 1. Confirm no waiting locks
docker compose exec odoo psql $PGDATABASE -c "
  SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock';
"
# Should return 0

# 2. Monitor for 10 minutes
# Ensure no new deadlocks
```

### Prevent
- Optimize queries with proper indexes
- Set `statement_timeout` in postgresql.conf
- Use serializable isolation only when needed
- Review and optimize long transactions
- Use advisory locks for critical sections

---

## Memory Leak

**Severity**: P2
**Symptoms**: Workers OOMKilled, slow response times, container restarts

### Detect
- Alert `OdooMemoryLeak` fired
- Container restarts with OOMKilled status
- Gradual memory increase over time

### Check
```bash
# 1. Check container memory usage
docker stats --no-stream | grep odoo

# 2. Check for OOM kills
docker inspect odoo | jq '.[0].State.OOMKilled'

# 3. Check memory trends in Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=container_memory_usage_bytes{container="odoo"}/container_spec_memory_limit_bytes' | jq .

# 4. Profile memory in Odoo (if available)
docker compose exec odoo python3 -m memory_profiler /opt/odoo/odoo-bin --help
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/restart_odoo_workers.sh

# Or manually restart
docker compose restart odoo
```

### Verify
```bash
# Monitor memory for 30 minutes
watch -n 60 'docker stats --no-stream | grep odoo'

# Memory should stabilize below 80%
```

### Prevent
- Limit recordset size (pagination)
- Stream large attachments instead of loading in memory
- Paginate report generation
- Set `--limit-memory-hard` and `--limit-memory-soft`
- Use `@api.model` to avoid unnecessary recordset creation
- Clear caches periodically

---

## Additional Resources

- Error Catalog: [ops/error-catalog/odoo.yaml](../../ops/error-catalog/odoo.yaml)
- Prometheus Alerts: [monitoring/prometheus/alerts_odoo.yml](../../monitoring/prometheus/alerts_odoo.yml)
- Auto-heal Handlers: [auto-healing/handlers/](../../auto-healing/handlers/)
