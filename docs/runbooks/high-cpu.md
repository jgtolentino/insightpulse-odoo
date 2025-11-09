# Runbook: High CPU Usage

## Overview
**Severity**: High
**Impact**: Performance degradation, potential service disruption
**Auto-Remediation**: Attempted (service restart)
**Manual Intervention**: May be required

## Symptoms
- CPU usage consistently above 80%
- Slow response times
- Timeout errors in logs
- System alerts triggered

## Automated Response
The monitoring system automatically:
1. Detects high CPU usage (>80%)
2. Attempts service restart via `scripts/ci/remediation/restart-services.sh`
3. Waits 30 seconds for recovery
4. Re-checks CPU usage
5. Creates GitHub issue if remediation fails

## Manual Investigation

### Step 1: Verify Current Status
```bash
# SSH into the server
ssh user@production-server

# Check current CPU usage
top -bn1 | head -20

# Identify top CPU consumers
ps aux --sort=-%cpu | head -10
```

### Step 2: Check Odoo Processes
```bash
# Check Odoo worker processes
ps aux | grep odoo | grep -v grep

# Check for runaway workers
# Look for processes with very high CPU time
ps -eo pid,user,%cpu,time,comm | grep odoo
```

### Step 3: Review Logs
```bash
# Check Odoo logs for errors
tail -f /var/log/odoo/odoo-server.log

# Check for database-related issues
tail -f /var/log/postgresql/postgresql.log

# Check nginx logs
tail -f /var/log/nginx/access.log
```

### Step 4: Database Performance
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Check for long-running queries
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' AND now() - query_start > interval '5 minutes';

# Check table locks
SELECT * FROM pg_locks WHERE NOT granted;

# Terminate problematic query if needed
SELECT pg_terminate_backend(PID);
```

## Remediation Steps

### Option 1: Restart Odoo Service (Low Risk)
```bash
# Graceful restart
sudo systemctl restart odoo

# Verify service is running
sudo systemctl status odoo

# Check logs for successful startup
tail -f /var/log/odoo/odoo-server.log
```

### Option 2: Restart PostgreSQL (Medium Risk)
```bash
# Only if database is the issue
sudo systemctl restart postgresql

# Verify database is accepting connections
sudo -u postgres psql -c "SELECT version();"

# Restart Odoo after database restart
sudo systemctl restart odoo
```

### Option 3: Clear Caches (Low Risk)
```bash
# Clear Odoo caches
# Login to Odoo as admin
# Go to Settings → Technical → Database Structure → Clear Cache

# Or via command line
echo "DELETE FROM ir_cache;" | sudo -u postgres psql odoo_production
```

### Option 4: Scale Resources (If Cloud-Hosted)
```bash
# DigitalOcean example
doctl compute droplet-action resize DROPLET_ID --size s-4vcpu-8gb

# Wait for resize to complete
doctl compute droplet-action get DROPLET_ID ACTION_ID
```

## Prevention

### Short-Term
- [ ] Identify and optimize slow queries
- [ ] Review recent code changes for performance issues
- [ ] Check for memory leaks in custom modules
- [ ] Verify cron jobs aren't overlapping

### Long-Term
- [ ] Implement query result caching
- [ ] Add database indexing for slow queries
- [ ] Set up connection pooling (pgBouncer)
- [ ] Optimize Odoo worker configuration
- [ ] Consider horizontal scaling

## Monitoring & Validation

### After Remediation
```bash
# Monitor CPU for 10 minutes
watch -n 10 'top -bn1 | head -20'

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com

# Verify worker pool health
# Check Odoo logs for worker activity
```

### Success Criteria
- [ ] CPU usage below 60%
- [ ] Response times < 500ms
- [ ] No error rate increase
- [ ] All workers responding
- [ ] No database locks

## Escalation

If manual remediation fails:
1. **Immediate**: Page on-call engineer
2. **1 hour**: Escalate to senior DevOps
3. **2 hours**: Consider rollback to last stable version
4. **4 hours**: Enable maintenance mode, full investigation

## Related Runbooks
- [High Memory Usage](high-memory.md)
- [Slow Response Times](slow-response.md)
- [Service Restart Procedure](service-restart.md)
- [Database Performance Tuning](database-tuning.md)

## Post-Incident

### Follow-Up Actions
1. Document root cause in incident report
2. Update monitoring thresholds if needed
3. Implement preventive measures
4. Review and update this runbook
5. Conduct team retrospective

### Incident Report Template
```markdown
## Incident Report: High CPU Usage

**Date**: YYYY-MM-DD
**Duration**: X hours
**Impact**: Service degradation / downtime
**Root Cause**: [Describe]
**Resolution**: [Describe]
**Prevention**: [Action items]
**Owner**: @username
```

---

**Last Updated**: 2024-11-09
**Runbook Version**: 1.0
**Owner**: DevOps Team
