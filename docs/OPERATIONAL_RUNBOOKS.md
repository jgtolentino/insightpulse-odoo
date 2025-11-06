# Operational Runbooks - InsightPulse AI

**Version**: 1.0
**Last Updated**: 2025-01-06

## 📚 Table of Contents

1. [Service Restart Procedures](#service-restart-procedures)
2. [Deployment Procedures](#deployment-procedures)
3. [Database Operations](#database-operations)
4. [Scaling Operations](#scaling-operations)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance Windows](#maintenance-windows)

---

## 🔄 Service Restart Procedures

### Restart Odoo ERP Application

**When to use**: Application errors, high memory usage, configuration changes

```bash
# Via DigitalOcean CLI
doctl apps create-deployment <odoo-app-id>

# Wait for deployment
doctl apps get-deployment <odoo-app-id> <deployment-id>

# Verify health
curl https://erp.insightpulseai.net/web/health

# Expected: {"status": "healthy"}
```

**Rollback if needed**:
```bash
# List deployments
doctl apps list-deployments <odoo-app-id>

# Rollback to previous
doctl apps create-rollback <odoo-app-id> <previous-deployment-id>
```

### Restart Superset Analytics

```bash
# Restart app
doctl apps create-deployment <superset-app-id>

# Verify
curl https://superset.insightpulseai.net/health
```

### Restart MCP Server

```bash
# Restart
doctl apps create-deployment <mcp-app-id>

# Test webhook
curl -X POST https://mcp.insightpulseai.net/mcp/github/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Restart Monitoring Stack

```bash
cd monitoring

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart prometheus
docker-compose restart grafana

# Verify
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
```

---

## 🚀 Deployment Procedures

### Standard Deployment (via GitHub Actions)

**Trigger**: Push to main branch

1. **Pre-deployment Checks**
   ```bash
   # Run tests locally
   make test

   # Check deployment readiness
   ./scripts/pre-deploy-check.sh
   ```

2. **Create Deployment**
   ```bash
   git checkout main
   git pull origin main
   git push origin main  # Triggers CI/CD
   ```

3. **Monitor Deployment**
   - Watch GitHub Actions workflow
   - Check application logs
   - Verify health endpoints

4. **Post-deployment Validation**
   ```bash
   # Health checks
   curl https://erp.insightpulseai.net/web/health
   curl https://superset.insightpulseai.net/health
   curl https://mcp.insightpulseai.net/health

   # Smoke tests
   ./scripts/smoke-tests.sh
   ```

### Manual Deployment (Emergency)

```bash
# 1. Build Docker image
docker build -t insightpulse-odoo:emergency -f Dockerfile .

# 2. Tag for registry
docker tag insightpulse-odoo:emergency registry.digitalocean.com/insightpulse/odoo:emergency

# 3. Push to registry
docker push registry.digitalocean.com/insightpulse/odoo:emergency

# 4. Update app spec
vim infra/do/odoo-saas-platform.yaml
# Update image tag to 'emergency'

# 5. Apply update
doctl apps update <app-id> --spec infra/do/odoo-saas-platform.yaml
```

### Rollback Procedure

```bash
# Quick rollback
doctl apps list-deployments <app-id>
doctl apps create-rollback <app-id> <previous-deployment-id>

# Via GitHub
gh run list --workflow=deploy-unified.yml --limit 10
gh run rerun <previous-successful-run-id>

# Verify rollback
curl https://erp.insightpulseai.net/web/health
```

---

## 💾 Database Operations

### Create Manual Backup

```bash
# Full database backup
export POSTGRES_URL="postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

pg_dump "$POSTGRES_URL" \
  --file="manual-backup-$(date +%Y%m%d-%H%M%S).sql" \
  --format=custom \
  --verbose

# Compress
gzip manual-backup-*.sql

# Upload to backup storage
s3cmd put manual-backup-*.sql.gz s3://insightpulse-backups/database/manual/
```

### Restore from Backup

**⚠️ CAUTION: This will overwrite existing data!**

```bash
# Download backup
s3cmd get s3://insightpulse-backups/database/backup-20250106.sql.gz

# Decompress
gunzip backup-20250106.sql.gz

# Stop applications first
doctl apps update <app-id> --spec /dev/null

# Restore
pg_restore -d postgres backup-20250106.sql -v

# Restart applications
doctl apps create-deployment <app-id>
```

### Database Maintenance

**Vacuum and Analyze**:
```bash
psql "$POSTGRES_URL" <<EOF
VACUUM ANALYZE;
EOF
```

**Check Database Size**:
```bash
psql "$POSTGRES_URL" -c "SELECT pg_size_pretty(pg_database_size('postgres'));"
```

**Check Table Sizes**:
```bash
psql "$POSTGRES_URL" <<EOF
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
EOF
```

### Optimize Slow Queries

```bash
# Enable query logging
psql "$POSTGRES_URL" -c "ALTER DATABASE postgres SET log_min_duration_statement = 1000;"

# Find slow queries
psql "$POSTGRES_URL" <<EOF
SELECT
    calls,
    mean_exec_time,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
EOF

# Create indexes for slow queries
psql "$POSTGRES_URL" -c "CREATE INDEX idx_partner_name ON res_partner(name);"
```

---

## 📈 Scaling Operations

### Vertical Scaling (Increase Resources)

**App Platform**:
```bash
# Update instance size
vim terraform/variables.tf
# Change app_instance_size to "professional-xs" or higher

terraform plan
terraform apply
```

**Droplets**:
```bash
# Resize droplet
doctl compute droplet-action resize <droplet-id> \
  --size s-2vcpu-4gb \
  --resize-disk
```

### Horizontal Scaling (Add Instances)

```bash
# Increase instance count
vim terraform/variables.tf
# Change app_instance_count to 2 or more

terraform apply

# Load will be automatically balanced
```

### Database Connection Pool Adjustment

```bash
# Increase max connections
psql "$POSTGRES_URL" -c "ALTER SYSTEM SET max_connections = 200;"
psql "$POSTGRES_URL" -c "SELECT pg_reload_conf();"

# Update application config
vim infra/do/odoo-saas-platform.yaml
# Increase ODOO_DB_MAXCONN
```

---

## 🔍 Troubleshooting

### Application Not Responding

**Symptoms**: 502/504 errors, timeouts

**Diagnosis**:
```bash
# Check app status
doctl apps get <app-id>

# Check logs
doctl apps logs <app-id> --type=run

# Check health endpoint
curl -v https://erp.insightpulseai.net/web/health
```

**Resolution**:
```bash
# Restart application
doctl apps create-deployment <app-id>

# If persists, check database
psql "$POSTGRES_URL" -c "SELECT 1;"

# Check resource usage
doctl apps get <app-id> --format ID,ActiveDeployment.MemoryUsage,ActiveDeployment.CPUUsage
```

### High Memory Usage

**Diagnosis**:
```bash
# Check Odoo workers
ps aux | grep odoo

# Check memory per process
top -o %MEM
```

**Resolution**:
```bash
# Reduce Odoo workers
vim infra/do/odoo-saas-platform.yaml
# Set ODOO_WORKERS=1

# Restart with new config
doctl apps update <app-id> --spec infra/do/odoo-saas-platform.yaml
```

### Database Connection Errors

**Symptoms**: "Too many connections", "Connection refused"

**Diagnosis**:
```bash
# Check active connections
psql "$POSTGRES_URL" <<EOF
SELECT count(*) FROM pg_stat_activity;
SELECT max_connections FROM pg_settings WHERE name='max_connections';
EOF
```

**Resolution**:
```bash
# Kill idle connections
psql "$POSTGRES_URL" <<EOF
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < now() - interval '10 minutes';
EOF

# Restart connection pooler
# (Contact Supabase support if needed)
```

### SSL Certificate Issues

**Symptoms**: Certificate expired warnings

**Diagnosis**:
```bash
# Check certificate expiry
echo | openssl s_client -servername erp.insightpulseai.net \
  -connect erp.insightpulseai.net:443 2>/dev/null | \
  openssl x509 -noout -dates
```

**Resolution**:
```bash
# Force certificate renewal (Caddy)
ssh user@droplet-ip
systemctl restart caddy

# Verify renewal
curl -I https://erp.insightpulseai.net
```

---

## 🛠️ Maintenance Windows

### Weekly Maintenance (Sunday 2 AM UTC)

**Tasks**:
- Database vacuum
- Log rotation
- Backup verification
- Security updates

**Procedure**:
```bash
#!/bin/bash
# Weekly maintenance script

echo "=== Weekly Maintenance Started ==="

# 1. Database maintenance
psql "$POSTGRES_URL" -c "VACUUM ANALYZE;"

# 2. Rotate logs
docker-compose -f monitoring/docker-compose.yml exec prometheus \
  wget -O - http://localhost:9090/api/v1/admin/tsdb/clean_tombstones

# 3. Verify backups
./scripts/test-backup-restore.sh

# 4. Security updates
apt-get update
apt-get upgrade -y

echo "=== Weekly Maintenance Completed ==="
```

### Monthly Maintenance (First Sunday 2 AM UTC)

**Additional Tasks**:
- Full infrastructure audit
- Performance optimization
- Dependency updates
- SSL certificate check

---

## 📞 Escalation Procedures

### Severity Levels

**P0 - Critical** (Service Down):
- Immediate response required
- Contact: DevOps on-call
- Escalate to: Engineering Lead if not resolved in 30 minutes

**P1 - High** (Degraded Performance):
- Response within 1 hour
- Contact: DevOps team
- Escalate to: Engineering Lead if not resolved in 4 hours

**P2 - Medium** (Minor Issues):
- Response within 4 hours
- Contact: DevOps team
- No escalation needed

**P3 - Low** (Enhancement/Question):
- Response within 24 hours
- Create ticket
- No escalation needed

---

## 📋 Checklists

### Pre-Deployment Checklist
- [ ] Tests passing
- [ ] Security scan completed
- [ ] Backup created
- [ ] Rollback plan ready
- [ ] Stakeholders notified

### Post-Deployment Checklist
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Monitoring active
- [ ] Logs reviewed
- [ ] Documentation updated

### Incident Response Checklist
- [ ] Incident logged
- [ ] Severity assessed
- [ ] Team notified
- [ ] Mitigation started
- [ ] Root cause identified
- [ ] Post-mortem scheduled

---

## 🔗 Quick Links

- [Disaster Recovery](./DISASTER_RECOVERY.md)
- [Network Security](./NETWORK_SECURITY.md)
- [Monitoring Dashboards](https://monitoring.insightpulseai.net)
- [Status Page](https://status.insightpulseai.net)

## 📄 Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-01-06 | 1.0 | Initial runbooks | DevOps Team |
