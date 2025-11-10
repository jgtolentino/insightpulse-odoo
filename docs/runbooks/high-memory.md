# Runbook: High Memory Usage

## Overview
**Severity**: High
**Impact**: Performance degradation, potential OOM kills
**Auto-Remediation**: Attempted (cache clearing)
**Manual Intervention**: May be required

## Symptoms
- Memory usage consistently above 85%
- Swap usage increasing
- OOM killer activating
- Service crashes or restarts
- System alerts triggered

## Automated Response
The monitoring system automatically:
1. Detects high memory usage (>85%)
2. Attempts cache clearing via `scripts/ci/remediation/clear-caches.sh`
3. Waits 30 seconds for recovery
4. Re-checks memory usage
5. Creates GitHub issue if remediation fails

## Manual Investigation

### Step 1: Verify Current Status
```bash
# Check memory usage
free -h

# Detailed memory breakdown
cat /proc/meminfo

# Check swap usage
swapon -s

# Top memory consumers
ps aux --sort=-%mem | head -10
```

### Step 2: Check for Memory Leaks
```bash
# Monitor Odoo processes over time
watch -n 5 'ps aux | grep odoo | grep -v grep'

# Check for growing processes
# Compare VSZ/RSS columns over time

# Use pmap for detailed memory mapping
pmap -x $(pgrep -f odoo-bin | head -1)
```

### Step 3: Database Memory Usage
```bash
# PostgreSQL memory settings
sudo -u postgres psql -c "SHOW shared_buffers;"
sudo -u postgres psql -c "SHOW work_mem;"

# Active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Memory used by PostgreSQL
ps aux | grep postgres | awk '{sum+=$6} END {print sum/1024 " MB"}'
```

### Step 4: Application-Level Checks
```bash
# Check Odoo logs for memory-related issues
grep -i "memory\|oom" /var/log/odoo/odoo-server.log

# Check kernel logs for OOM killer activity
dmesg | grep -i "killed process\|out of memory"

# System logs
journalctl -u odoo -p err --since "1 hour ago"
```

## Remediation Steps

### Option 1: Clear Application Caches (Low Risk)
```bash
# Clear Redis cache (if used)
redis-cli FLUSHALL

# Clear Odoo caches via database
echo "DELETE FROM ir_cache; DELETE FROM ir_attachment WHERE name LIKE '%cache%';" | \
  sudo -u postgres psql odoo_production

# Restart Odoo to release memory
sudo systemctl restart odoo
```

### Option 2: Reduce Database Connections (Low Risk)
```bash
# Check current connections
sudo -u postgres psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Kill idle connections
sudo -u postgres psql << EOF
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND query_start < now() - interval '30 minutes';
EOF
```

### Option 3: Adjust Odoo Configuration (Medium Risk)
```bash
# Edit odoo.conf
sudo nano /etc/odoo/odoo.conf

# Reduce worker limits
limit_memory_hard = 2684354560  # 2.5GB (reduce from default)
limit_memory_soft = 2147483648  # 2GB (reduce from default)
limit_time_cpu = 60             # CPU time limit
limit_time_real = 120           # Real time limit

# Restart to apply changes
sudo systemctl restart odoo
```

### Option 4: Emergency Memory Recovery (High Risk)
```bash
# Drop filesystem caches (frees page cache but safe)
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

# Check freed memory
free -h

# If desperate: restart PostgreSQL (causes brief downtime)
sudo systemctl restart postgresql
sudo systemctl restart odoo
```

### Option 5: Scale Resources (If Cloud-Hosted)
```bash
# DigitalOcean: Resize droplet
doctl compute droplet-action resize DROPLET_ID --size s-4vcpu-8gb

# AWS: Modify instance type
aws ec2 modify-instance-attribute --instance-id i-xxxxx --instance-type t3.large
```

## Prevention

### Immediate Actions
- [ ] Identify memory leak source (check recent deployments)
- [ ] Review custom modules for inefficient queries
- [ ] Check for large file uploads or attachments
- [ ] Verify proper session cleanup

### Configuration Tuning
```bash
# PostgreSQL optimizations
sudo nano /etc/postgresql/16/main/postgresql.conf

# Adjust based on available RAM (example for 8GB server)
shared_buffers = 2GB          # 25% of RAM
work_mem = 16MB               # Per operation
maintenance_work_mem = 512MB  # For maintenance tasks
effective_cache_size = 6GB    # 75% of RAM

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Odoo Worker Configuration
```ini
# /etc/odoo/odoo.conf
workers = 4                    # 2 * CPU cores + 1
max_cron_threads = 2          # Dedicated cron workers
limit_memory_hard = 2684354560 # 2.5GB
limit_memory_soft = 2147483648 # 2GB
limit_time_cpu = 60
limit_time_real = 120
```

### Long-Term Solutions
- [ ] Implement connection pooling (pgBouncer)
- [ ] Set up memory monitoring alerts
- [ ] Regular cleanup of old sessions/logs
- [ ] Archive old data
- [ ] Consider Redis for session storage
- [ ] Review and optimize large queries

## Monitoring & Validation

### After Remediation
```bash
# Monitor memory for 15 minutes
watch -n 30 'free -h'

# Check for memory leaks
# Run for 1 hour and compare
ps aux --sort=-%mem | head -10 > /tmp/mem_before.txt
# ... wait 1 hour ...
ps aux --sort=-%mem | head -10 > /tmp/mem_after.txt
diff /tmp/mem_before.txt /tmp/mem_after.txt
```

### Success Criteria
- [ ] Memory usage below 75%
- [ ] No swap usage or decreasing
- [ ] No OOM killer activity
- [ ] Stable process memory footprint
- [ ] No service crashes

## Escalation

### Escalation Path
1. **Immediate**: If OOM killer active, page on-call engineer
2. **30 minutes**: If memory continues to grow, escalate to senior DevOps
3. **1 hour**: Consider enabling maintenance mode for investigation
4. **2 hours**: Plan for emergency scaling or rollback

### Critical Threshold
If memory usage exceeds 95%:
```bash
# Emergency response
sudo systemctl restart odoo
# Monitor closely for next 30 minutes
```

## Related Runbooks
- [High CPU Usage](high-cpu.md)
- [Service Restart Procedure](service-restart.md)
- [Database Performance Tuning](database-tuning.md)
- [OOM Killer Investigation](oom-investigation.md)

## Post-Incident

### Root Cause Analysis Questions
1. What triggered the memory spike?
2. Was there a recent deployment or configuration change?
3. Are there memory leaks in custom code?
4. Is the server properly sized for the workload?
5. Are there opportunities for optimization?

### Documentation
```markdown
## Memory Incident Report

**Date**: YYYY-MM-DD
**Peak Memory Usage**: XX%
**Duration**: X hours
**Root Cause**: [Memory leak in module X / Insufficient resources / etc]
**Resolution**: [Cleared caches / Restarted services / Scaled resources]
**Prevention**: [Code fix / Config change / Resource upgrade]
**Action Items**:
- [ ] Fix memory leak in module X
- [ ] Upgrade to 16GB RAM
- [ ] Implement connection pooling
```

---

**Last Updated**: 2024-11-09
**Runbook Version**: 1.0
**Owner**: DevOps Team
