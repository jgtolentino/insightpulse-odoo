# Runbook: Service Restart Procedure

## Overview
**Severity**: Low to Medium (during restart)
**Impact**: Brief service interruption
**Risk Level**: Low (if done correctly)
**Downtime**: ~30-60 seconds

## When to Use This Runbook
- After configuration changes
- When services become unresponsive
- During deployment of updates
- As part of remediation procedures
- For routine maintenance

## Prerequisites
```bash
# Verify you have:
# - SSH access to production server
# - Sudo privileges
# - Backup of critical data (if major change)
# - Notification sent to users (for planned maintenance)
```

## Pre-Restart Checklist
- [ ] Notify users of impending restart (if planned)
- [ ] Take database backup (for safety)
- [ ] Check current system status
- [ ] Verify no critical operations in progress
- [ ] Have rollback plan ready

## Safe Restart Procedures

### 1. Odoo Service Restart (Standard)

#### Health Check Before Restart
```bash
# Check service status
sudo systemctl status odoo

# Check active users
sudo -u postgres psql odoo_production -c \
  "SELECT count(DISTINCT res_id) FROM res_users_log WHERE create_date > now() - interval '5 minutes';"

# Check running jobs/cron tasks
sudo -u postgres psql odoo_production -c \
  "SELECT name, state FROM ir_cron WHERE active = true AND nextcall < now();"
```

#### Graceful Restart
```bash
# Method 1: Systemd restart (preferred)
sudo systemctl restart odoo

# Wait for service to stabilize
sleep 10

# Verify service is running
sudo systemctl status odoo

# Check logs for errors
tail -n 50 /var/log/odoo/odoo-server.log
```

#### Force Restart (If Graceful Fails)
```bash
# Stop service
sudo systemctl stop odoo

# Verify all processes stopped
ps aux | grep odoo

# Kill any hanging processes
sudo pkill -9 -f odoo-bin

# Start service
sudo systemctl start odoo

# Verify startup
sudo systemctl status odoo
```

### 2. PostgreSQL Restart (Use with Caution)

#### Pre-Restart Checks
```bash
# Check active connections
sudo -u postgres psql -c \
  "SELECT count(*) as total, state FROM pg_stat_activity GROUP BY state;"

# Check for long-running queries
sudo -u postgres psql -c \
  "SELECT pid, now() - query_start AS duration, query FROM pg_stat_activity 
   WHERE state = 'active' AND now() - query_start > interval '1 minute';"
```

#### Graceful Restart
```bash
# Stop Odoo first to prevent connection errors
sudo systemctl stop odoo

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify PostgreSQL is accepting connections
sudo -u postgres psql -c "SELECT version();"

# Restart Odoo
sudo systemctl start odoo

# Full verification
sudo systemctl status odoo
sudo systemctl status postgresql
```

### 3. Nginx Restart (Safe - No Downtime)

```bash
# Test configuration before restart
sudo nginx -t

# If test passes, reload (zero downtime)
sudo systemctl reload nginx

# Or restart if needed
sudo systemctl restart nginx

# Verify
sudo systemctl status nginx
curl -I https://your-domain.com
```

### 4. Full Stack Restart (Maximum Disruption)

Only use when necessary (major issues or updates).

```bash
#!/bin/bash
# full-restart.sh

echo "Starting full stack restart..."

# 1. Stop services in reverse dependency order
echo "Stopping Nginx..."
sudo systemctl stop nginx

echo "Stopping Odoo..."
sudo systemctl stop odoo

echo "Stopping PostgreSQL..."
sudo systemctl stop postgresql

# Wait for clean shutdown
sleep 5

# 2. Verify all stopped
ps aux | grep -E "nginx|odoo|postgres" | grep -v grep

# 3. Start services in dependency order
echo "Starting PostgreSQL..."
sudo systemctl start postgresql
sleep 5

echo "Starting Odoo..."
sudo systemctl start odoo
sleep 10

echo "Starting Nginx..."
sudo systemctl start nginx
sleep 5

# 4. Verify all services
echo "Verifying services..."
sudo systemctl status postgresql --no-pager
sudo systemctl status odoo --no-pager
sudo systemctl status nginx --no-pager

echo "Full restart complete!"
```

## Post-Restart Verification

### Immediate Checks (0-2 minutes)
```bash
# 1. Service status
sudo systemctl status odoo
sudo systemctl status postgresql
sudo systemctl status nginx

# 2. Process verification
ps aux | grep odoo | grep -v grep
ps aux | grep postgres | grep -v grep
ps aux | grep nginx | grep -v grep

# 3. Port listening
netstat -tuln | grep -E ":8069|:5432|:80|:443"
```

### Application Health (2-5 minutes)
```bash
# 1. HTTP response
curl -I https://your-domain.com

# 2. Odoo health endpoint
curl http://localhost:8069/web/health

# 3. Database connectivity
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# 4. Check logs for errors
tail -n 100 /var/log/odoo/odoo-server.log | grep -i error
tail -n 100 /var/log/postgresql/postgresql-16-main.log | grep -i error
tail -n 100 /var/log/nginx/error.log
```

### User Access Test (5-10 minutes)
```bash
# 1. Login test
curl -X POST https://your-domain.com/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"db":"odoo_production","login":"admin","password":"test"}}'

# 2. Dashboard load time
time curl -s https://your-domain.com/web > /dev/null

# 3. Check active users
sudo -u postgres psql odoo_production -c \
  "SELECT count(DISTINCT res_id) FROM res_users_log WHERE create_date > now() - interval '2 minutes';"
```

### Success Criteria Checklist
- [ ] All services show "active (running)" status
- [ ] No error messages in logs
- [ ] HTTP response code 200
- [ ] Database accepting connections
- [ ] Users can log in
- [ ] Response times normal (<2 seconds)
- [ ] No spike in error rates

## Rollback Procedure

If restart causes issues:

```bash
# 1. Immediate: Restore from backup if data corruption
sudo -u postgres pg_restore -d odoo_production /path/to/backup.dump

# 2. Revert configuration changes
sudo cp /etc/odoo/odoo.conf.backup /etc/odoo/odoo.conf

# 3. Restart with old configuration
sudo systemctl restart odoo

# 4. Verify rollback success
curl -I https://your-domain.com
```

## Common Issues & Solutions

### Issue: Odoo Won't Start
```bash
# Check logs
tail -f /var/log/odoo/odoo-server.log

# Common causes:
# - Database connection error → Check PostgreSQL is running
# - Port already in use → Kill process on port 8069
# - Configuration error → Validate odoo.conf
# - Permission error → Check file ownership

# Kill process on port 8069
sudo lsof -ti:8069 | xargs kill -9

# Fix permissions
sudo chown -R odoo:odoo /var/log/odoo
sudo chown odoo:odoo /etc/odoo/odoo.conf
```

### Issue: Database Connection Refused
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check pg_hba.conf for connection rules
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Verify listen address
sudo -u postgres psql -c "SHOW listen_addresses;"

# Test connection manually
sudo -u postgres psql odoo_production
```

### Issue: 502 Bad Gateway (Nginx)
```bash
# Check Odoo is running
sudo systemctl status odoo

# Check Nginx upstream configuration
sudo nginx -t

# Verify proxy_pass in nginx config
sudo nano /etc/nginx/sites-available/odoo

# Should have:
# proxy_pass http://127.0.0.1:8069;
```

## Monitoring After Restart

### Short-Term (First Hour)
```bash
# Monitor logs continuously
tail -f /var/log/odoo/odoo-server.log

# Watch resource usage
watch -n 5 'ps aux | grep odoo | grep -v grep'

# Monitor error rates
watch -n 10 'tail -20 /var/log/nginx/access.log | grep -c " 5[0-9][0-9] "'
```

### Medium-Term (First 24 Hours)
- Monitor response times
- Check error rates in logs
- Review user feedback
- Watch resource utilization trends

## Documentation

### Restart Log Template
```markdown
## Service Restart Log

**Date**: YYYY-MM-DD HH:MM UTC
**Performed By**: @username
**Reason**: [Configuration change / Unresponsive service / etc]
**Services Restarted**: [Odoo / PostgreSQL / Nginx / Full Stack]
**Downtime**: XX seconds
**Issues Encountered**: [None / List any issues]
**Resolution**: [Successful / Rolled back / etc]
**Follow-up Actions**: [None required / Monitor for X hours / etc]
```

## Related Runbooks
- [High CPU Usage](high-cpu.md)
- [High Memory Usage](high-memory.md)
- [Slow Response Times](slow-response.md)
- [Database Performance Tuning](database-tuning.md)

---

**Last Updated**: 2024-11-09
**Runbook Version**: 1.0
**Owner**: DevOps Team
