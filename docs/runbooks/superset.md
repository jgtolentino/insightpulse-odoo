# Superset Runbook

## Query Timeout

**Severity**: P1
**Symptoms**: Dashboard panels show timeout errors, slow dashboard load, user complaints

### Detect
- Alert `SupersetQueryTimeout` fired
- Dashboard charts showing "Query timeout" error
- User reports of slow loading

### Check
```bash
# 1. Check recent query logs
docker compose logs superset | grep -i "timeout\|slow" | tail -50

# 2. Check database slow query log
psql "$POSTGRES_URL" -c "
  SELECT
    calls,
    total_time,
    mean_time,
    max_time,
    query
  FROM pg_stat_statements
  WHERE mean_time > 5000  -- 5 seconds
  ORDER BY mean_time DESC
  LIMIT 10;
"

# 3. Check missing indexes
psql "$POSTGRES_URL" -c "
  SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
  FROM pg_stats
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    AND n_distinct > 100
    AND correlation < 0.1
  ORDER BY n_distinct DESC;
"

# 4. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(superset_sql_query_seconds_bucket[5m]))by(le))' | jq .
```

### Heal
```bash
# Run auto-heal handler (warms cache)
./auto-healing/handlers/warm_superset_cache.sh

# Or manually warm specific dashboards
curl -X POST "http://localhost:8088/api/v1/dashboard/{id}/warm" \
  -H "Authorization: Bearer $SUPERSET_API_KEY"
```

### Verify
```bash
# 1. Test dashboard load time
time curl -s "http://localhost:8088/api/v1/dashboard/{id}" \
  -H "Authorization: Bearer $SUPERSET_API_KEY" > /dev/null

# Should complete in <3s

# 2. Check cache hit rate
# Navigate to: Superset UI > Settings > Stats
# Cache hit rate should be >70%

# 3. Monitor for 15 minutes
watch -n 60 'docker compose logs superset --tail 20 | grep -c timeout'
# Should return 0
```

### Prevent
- Add database indexes on filtered/joined columns
- Use materialized views for complex aggregations
- Set query timeout limits (sync and async)
- Enable async query execution for long-running queries
- Implement query result caching
- Pre-warm cache for popular dashboards
- Optimize SQL queries (avoid SELECT *, use LIMIT)

---

## Metadata Database Deadlock

**Severity**: P1
**Symptoms**: Dashboard save failures, chart edit errors, 502 Bad Gateway

### Detect
- Alert `SupersetMetadataDbDeadlock` fired
- Users unable to save dashboard changes
- Superset UI unresponsive

### Check
```bash
# 1. Check Superset metadata DB locks
psql "$SUPERSET_METADATA_DB_URL" -c "
  SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement
  FROM pg_catalog.pg_locks blocked_locks
  JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
  JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.pid != blocked_locks.pid
  JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
  WHERE NOT blocked_locks.granted;
"

# 2. Check long-running metadata queries
psql "$SUPERSET_METADATA_DB_URL" -c "
  SELECT pid, now() - query_start AS duration, query, state
  FROM pg_stat_activity
  WHERE datname = 'superset'
    AND state = 'active'
    AND query_start < now() - interval '10 seconds'
  ORDER BY duration DESC;
"

# 3. Check Superset logs for deadlock errors
docker compose logs superset | grep -i "deadlock\|lock timeout" | tail -20
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/restart_superset.sh

# Or manually restart
docker compose restart superset superset-worker superset-beat
```

### Verify
```bash
# 1. Test dashboard save
# Open Superset UI, edit and save a dashboard
# Should succeed without errors

# 2. Check no locks present
psql "$SUPERSET_METADATA_DB_URL" -c "
  SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock';
"
# Should return 0

# 3. Monitor for 10 minutes
docker compose logs superset --follow | grep -i "deadlock"
# Should see no new deadlocks
```

### Prevent
- Upgrade metadata database (increase resources)
- Tune connection pool size
- Serialize critical metadata writes
- Use optimistic locking for concurrent updates
- Monitor metadata DB performance
- Regular metadata DB maintenance (VACUUM, ANALYZE)

---

## Cache Miss

**Severity**: P2
**Symptoms**: Slow dashboard loads despite warm cache, high DB load, cache hit ratio <50%

### Detect
- Alert `SupersetCacheMiss` fired
- Dashboard load times inconsistent
- High database query volume

### Check
```bash
# 1. Check cache configuration
docker compose exec superset cat /app/pythonpath/superset_config.py | grep -A 10 "CACHE_CONFIG"

# 2. Check cache stats
# Navigate to: Superset UI > Settings > Database > Cache Stat

# 3. Check Redis (if using Redis cache)
docker compose exec redis redis-cli INFO stats | grep -i "hit\|miss"

# 4. Check cache keys
docker compose exec redis redis-cli KEYS "superset:*" | wc -l

# 5. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(superset_cache_hits[5m]))/(sum(rate(superset_cache_hits[5m]))+sum(rate(superset_cache_misses[5m])))' | jq .
```

### Heal
```bash
# Run auto-heal handler (warms cache)
./auto-healing/handlers/warm_superset_cache.sh

# Or manually warm dashboards
for id in {1..20}; do
  curl -X POST "http://localhost:8088/api/v1/dashboard/$id/warm" \
    -H "Authorization: Bearer $SUPERSET_API_KEY"
done
```

### Verify
```bash
# Check cache hit rate improved
# Navigate to: Superset UI > Settings > Database > Cache Stat
# Should show >70% hit rate

# Monitor for 30 minutes
watch -n 60 'docker compose exec redis redis-cli INFO stats | grep keyspace_hits'
```

### Prevent
- Increase cache size (memory allocation)
- Tune cache TTL (not too short)
- Pre-warm cache for popular dashboards (scheduled job)
- Use consistent cache key generation
- Enable query result caching
- Monitor cache eviction rate
- Consider distributed cache (Redis Cluster)

---

## Worker Overload

**Severity**: P2
**Symptoms**: Slow async query execution, email reports delayed, Celery queue growing

### Detect
- Alert `SupersetWorkerOverload` fired
- Users complaining about slow reports
- Email reports delayed

### Check
```bash
# 1. Check Celery queue length
docker compose exec superset-worker celery -A superset.tasks.celery_app:app inspect active | jq 'to_entries | .[].value | length'

# 2. Check worker CPU and memory
docker stats --no-stream | grep superset-worker

# 3. Check worker logs for errors
docker compose logs superset-worker --tail 100 | grep -i "error\|timeout"

# 4. Check task duration
docker compose exec superset-worker celery -A superset.tasks.celery_app:app inspect stats

# 5. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=sum(celery_queue_length)by(queue)' | jq .
```

### Heal
```bash
# Run auto-heal handler (scales workers)
./auto-healing/handlers/scale_superset_workers.sh

# Or manually scale
docker compose up -d --scale superset-worker=4
```

### Verify
```bash
# 1. Check queue length decreased
docker compose exec superset-worker celery -A superset.tasks.celery_app:app inspect active | jq 'to_entries | .[].value | length'
# Should be <50

# 2. Check CPU usage normalized
docker stats --no-stream | grep superset-worker
# Should be <80%

# 3. Test async query
# Run a long query, check it completes within expected time
```

### Prevent
- Scale workers horizontally (add more containers)
- Set task timeouts (soft and hard)
- Prioritize queues (separate urgent/bulk)
- Monitor worker health
- Implement task retry logic
- Use task routing for specialized workers
- Regular worker restarts to prevent memory leaks

---

## Additional Resources

- Error Catalog: [ops/error-catalog/superset.yaml](../../ops/error-catalog/superset.yaml)
- Prometheus Alerts: [monitoring/prometheus/alerts_superset.yml](../../monitoring/prometheus/alerts_superset.yml)
- Auto-heal Handlers: [auto-healing/handlers/](../../auto-healing/handlers/)
- Superset Docs: https://superset.apache.org/docs/
