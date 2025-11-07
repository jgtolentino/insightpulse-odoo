# DigitalOcean App Platform Runbook

## Deploy Failures

**Severity**: P1
**Symptoms**: Deployment fails, app stuck in deploying state, rollback triggered

### Detect
- Alert `DODeployFailed` fired
- GitHub Actions deploy job failing
- App Platform shows "Failed" status

### Check
```bash
# 1. Check recent deployments
doctl apps list-deployments <app-id>

# 2. Get deployment details
doctl apps get-deployment <app-id> <deployment-id>

# 3. Check deployment logs
doctl apps logs <app-id> --type build --follow

# 4. Check runtime logs
doctl apps logs <app-id> --type run --follow

# 5. Check app health
doctl apps get <app-id> --format ID,Tier,Phase,LiveURL

# 6. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=increase(do_deploy_failures_total[15m])' | jq .
```

### Heal
```bash
# Run auto-heal handler (rollback)
./auto-healing/handlers/rollback_do_app.sh <app-id>

# Or manually rollback via CLI
doctl apps create-deployment <app-id> --force-rebuild

# Or via Dashboard
# Navigate to: Apps > <app> > Settings > Rollback
```

### Verify
```bash
# 1. Check app is active
doctl apps get <app-id> --format Phase
# Should show "ACTIVE"

# 2. Check health endpoint
curl -f https://<app-url>/health
# Should return 200 OK

# 3. Monitor logs for errors
doctl apps logs <app-id> --type run --tail 50
# Should show normal operation
```

### Prevent
- Test builds locally before deploying
- Validate health check configuration
- Implement staged rollouts (canary)
- Use CI/CD with automated testing
- Monitor build duration trends
- Set appropriate timeouts
- Review build logs regularly

---

## App Health Check Failing

**Severity**: P0
**Symptoms**: App marked unhealthy, traffic not routed, automatic restarts

### Detect
- Alert `DOAppHealthCheckFailing` fired
- App Platform dashboard shows red health status
- Users unable to access application

### Check
```bash
# 1. Check app details
doctl apps get <app-id> --format ID,Phase,Health

# 2. Check health check configuration
doctl apps get <app-id> --format HealthCheck

# 3. Test health endpoint manually
curl -v https://<app-url>/health

# 4. Check logs for startup errors
doctl apps logs <app-id> --type run --tail 100 | grep -i "error\|exception\|failed"

# 5. Check if app is listening on correct port
doctl apps logs <app-id> --type run | grep -i "listening\|port"

# 6. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=do_app_health_check_failures' | jq .
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/restart_do_app.sh <app-id>

# Or manually restart
doctl apps create-deployment <app-id>

# If health check config is wrong, update via App Spec
# Edit .do/app.yaml:
# health_check:
#   http_path: /health
#   initial_delay_seconds: 30
#   period_seconds: 10
#   timeout_seconds: 5
#   success_threshold: 1
#   failure_threshold: 3

# Apply changes
doctl apps update <app-id> --spec .do/app.yaml
```

### Verify
```bash
# 1. Check health status
doctl apps get <app-id> --format Health
# Should show "HEALTHY"

# 2. Test health endpoint
curl -f https://<app-url>/health
# Should return 200 OK quickly

# 3. Monitor for 10 minutes
for i in {1..60}; do
  sleep 10
  curl -sf https://<app-url>/health && echo "OK" || echo "FAIL"
done
# Should consistently return OK
```

### Prevent
- Increase health check timeout if app has slow startup
- Validate health endpoint returns 200 OK
- Implement graceful shutdown
- Test health checks locally
- Monitor health check trends
- Use `initial_delay_seconds` for slow startups
- Ensure app binds to correct port (PORT env var)

---

## Scaling Stuck

**Severity**: P2
**Symptoms**: App not scaling up despite load, autoscaler inactive, manual scale fails

### Detect
- Alert `DOScalingStuck` fired
- App Platform dashboard shows fewer instances than expected
- High CPU/memory despite autoscaling enabled

### Check
```bash
# 1. Check current instance count
doctl apps get <app-id> --format InstanceCount

# 2. Check autoscaling config
doctl apps get <app-id> --format Autoscaling

# 3. Check resource usage
doctl apps get <app-id> --format Resources

# 4. Check account resource quotas
doctl account get --format DropletLimit,FloatingIPLimit

# 5. Check region capacity
# Navigate to: DigitalOcean Status Page
# https://status.digitalocean.com/

# 6. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=do_app_instance_count' | jq .
curl -s 'http://localhost:9090/api/v1/query?query=avg(container_cpu_usage_percent)by(app)' | jq .
```

### Heal
```bash
# No auto-heal - may require quota increase or manual intervention

# 1. Try manual scale
doctl apps update <app-id> --spec .do/app.yaml

# 2. Check if quota increase needed
# Contact DigitalOcean support if hitting limits

# 3. Consider multi-region deployment
# Edit .do/app.yaml to add regions
```

### Verify
```bash
# 1. Check instance count increased
doctl apps get <app-id> --format InstanceCount
# Should match target

# 2. Check CPU normalized
doctl apps logs <app-id> --type run | grep -i cpu
# Or check metrics in dashboard

# 3. Test application performance
ab -n 1000 -c 10 https://<app-url>/
# Should handle load without errors
```

### Prevent
- Monitor resource quotas
- Test autoscaling in staging
- Set appropriate scaling thresholds
- Implement multi-region deployment for high availability
- Monitor scaling events
- Have plan for rapid scale (contact support for limit increases)
- Use load testing to validate scaling

---

## Database Connection Limit

**Severity**: P1
**Symptoms**: Connection errors from app, database refusing connections, 504 errors

### Detect
- Alert `DODatabaseConnectionLimit` fired
- Application logs showing connection errors
- Database dashboard shows connections near limit

### Check
```bash
# 1. Check managed database info
doctl databases get <db-id> --format NumConnections,MaxConnections

# 2. Check current connections
doctl databases connection <db-id>

# 3. Check connection pool settings
# Review App Spec connection string

# 4. Connect to database and check
psql "$(doctl databases connection <db-id> --format URI --no-header)" -c "
  SELECT
    count(*) as current_connections,
    (SELECT setting::int FROM pg_settings WHERE name='max_connections') as max_connections
  FROM pg_stat_activity;
"

# 5. Check idle connections
psql "$(doctl databases connection <db-id> --format URI --no-header)" -c "
  SELECT state, count(*)
  FROM pg_stat_activity
  GROUP BY state;
"

# 6. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=do_managed_db_connections/do_managed_db_connection_limit' | jq .
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/kill_idle_db_connections.sh

# Or manually kill idle connections
psql "$(doctl databases connection <db-id> --format URI --no-header)" -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle'
    AND state_change < now() - interval '10 minutes'
    AND pid <> pg_backend_pid();
"

# Or upgrade database plan (if limit too low)
doctl databases resize <db-id> --size db-s-2vcpu-4gb
```

### Verify
```bash
# Check connections dropped
psql "$(doctl databases connection <db-id> --format URI --no-header)" -c "
  SELECT count(*) FROM pg_stat_activity;
"
# Should be <80% of max

# Test application connectivity
curl -f https://<app-url>/health
# Should return 200 OK
```

### Prevent
- Use PgBouncer for connection pooling
- Set connection limits per application
- Tune connection timeout settings
- Monitor connection trends
- Size database appropriately
- Implement connection retry logic
- Use managed connection pooler

---

## Additional Resources

- Error Catalog: [ops/error-catalog/do.yaml](../../ops/error-catalog/do.yaml)
- Prometheus Alerts: [monitoring/prometheus/alerts_do.yml](../../monitoring/prometheus/alerts_do.yml)
- Auto-heal Handlers: [auto-healing/handlers/](../../auto-healing/handlers/)
- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/
- DigitalOcean Status: https://status.digitalocean.com/
