# Runbook: Slow Response Times

## Overview
**Severity**: Medium to High
**Impact**: Poor user experience, potential timeouts
**Auto-Remediation**: Attempted (resource scaling)
**Manual Intervention**: Usually required

## Symptoms
- Response times > 2000ms (2 seconds)
- User complaints about slowness
- Timeout errors (502, 504)
- Database query timeouts
- System alerts triggered

## Automated Response
The monitoring system automatically:
1. Detects high response times (>2000ms)
2. Initiates resource scaling if cloud-hosted
3. Monitors for improvement
4. Creates GitHub issue if remediation fails

## Quick Diagnostics

### Check Current Response Times
```bash
# Test from external location
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com

# curl-format.txt contents:
cat > curl-format.txt << 'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF

# Multiple samples
for i in {1..10}; do
  curl -w "Request $i: %{time_total}s\n" -o /dev/null -s https://your-domain.com
  sleep 2
done
```

## Investigation Steps

### Step 1: Identify Bottleneck Layer

#### Network Layer
```bash
# Check network latency
ping your-domain.com

# Traceroute to identify network issues
traceroute your-domain.com

# Check DNS resolution time
dig your-domain.com
```

#### Application Layer (Nginx)
```bash
# Check nginx error logs
tail -f /var/log/nginx/error.log

# Check access logs for slow requests
awk '{if ($NF > 1.0) print $0}' /var/log/nginx/access.log

# Check nginx status
curl http://localhost/nginx_status
```

#### Application Layer (Odoo)
```bash
# Check Odoo logs for slow requests
grep "slow\|timeout" /var/log/odoo/odoo-server.log

# Enable Odoo profiling temporarily
# Add to odoo.conf: log_level = debug

# Check worker availability
curl http://localhost:8069/web/health

# Check number of active requests
netstat -an | grep :8069 | grep ESTABLISHED | wc -l
```

#### Database Layer (PostgreSQL)
```bash
# Find slow queries (>1 second)
sudo -u postgres psql << EOF
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
AND now() - query_start > interval '1 second'
ORDER BY duration DESC;
EOF

# Check for table bloat
sudo -u postgres psql odoo_production << EOF
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
LIMIT 10;
EOF
```

### Step 2: Check Resource Utilization
```bash
# CPU, memory, disk I/O
htop

# I/O wait times
iostat -x 1 10

# Network bandwidth
iftop

# Disk space
df -h
```

## Remediation Steps

### Quick Wins (Immediate)

#### 1. Restart Services
```bash
# If worker pool is exhausted
sudo systemctl restart odoo

# If too many database connections
sudo systemctl restart postgresql
```

#### 2. Clear Caches
```bash
# Clear Odoo caches
echo "DELETE FROM ir_cache;" | sudo -u postgres psql odoo_production

# Clear web browser caches (via Odoo UI)
# Settings → Technical → Database Structure → Clear Assets Bundle

# Clear Redis if used
redis-cli FLUSHALL
```

#### 3. Increase Workers (Temporary)
```bash
# Edit odoo.conf
sudo nano /etc/odoo/odoo.conf

# Increase workers (be careful with memory)
workers = 8  # was 4

sudo systemctl restart odoo
```

### Database Optimization

#### 1. Analyze Slow Queries
```bash
# Enable slow query log
sudo nano /etc/postgresql/16/main/postgresql.conf

# Add or uncomment:
log_min_duration_statement = 1000  # Log queries > 1 second
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d '

sudo systemctl restart postgresql

# Review logs
tail -f /var/log/postgresql/postgresql-16-main.log
```

#### 2. Add Missing Indexes
```sql
-- Find missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
AND n_distinct > 100
ORDER BY n_distinct DESC;

-- Example: Add index for frequent searches
CREATE INDEX CONCURRENTLY idx_res_partner_name 
ON res_partner(name);

-- Reindex if needed
REINDEX TABLE res_partner;
```

#### 3. Vacuum and Analyze
```bash
# Vacuum all tables
sudo -u postgres vacuumdb -a -z -v

# Analyze specific table
sudo -u postgres psql odoo_production -c "VACUUM ANALYZE res_partner;"
```

### Application-Level Optimization

#### 1. Enable Odoo Caching
```python
# In custom modules, use @api.ormcache decorator
from odoo import api, models

class MyModel(models.Model):
    _name = 'my.model'
    
    @api.ormcache('arg1', 'arg2')
    def expensive_computation(self, arg1, arg2):
        # This will be cached
        return result
```

#### 2. Optimize Views
```bash
# Find views with many records
sudo -u postgres psql odoo_production << EOF
SELECT 
    relname AS table_name,
    n_tup_ins AS inserts,
    n_tup_upd AS updates,
    n_tup_del AS deletes,
    n_live_tup AS live_rows
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC
LIMIT 20;
EOF

# Add filters to reduce result sets
# Add pagination to list views
# Use search domains efficiently
```

### Infrastructure Scaling

#### 1. Vertical Scaling
```bash
# Upgrade server resources
doctl compute droplet-action resize DROPLET_ID --size s-8vcpu-16gb
```

#### 2. Horizontal Scaling
```bash
# Set up load balancer
# Add more Odoo worker nodes
# Configure sticky sessions
```

#### 3. Database Read Replicas
```bash
# Set up PostgreSQL read replica
# Route read-only queries to replica
# Keep writes on primary
```

## Prevention

### Monitoring
```bash
# Set up continuous response time monitoring
# Tools: New Relic, Datadog, Prometheus + Grafana

# Example with curl monitoring
*/5 * * * * /usr/local/bin/check-response-time.sh >> /var/log/response-time.log
```

### Regular Maintenance
- [ ] Weekly: VACUUM ANALYZE database
- [ ] Monthly: Review slow query logs
- [ ] Quarterly: Performance audit
- [ ] Yearly: Capacity planning review

### Code Review
- [ ] Review N+1 query patterns
- [ ] Implement lazy loading where appropriate
- [ ] Use bulk operations for data imports
- [ ] Optimize search domains

## Validation

### Success Criteria
- [ ] Response times < 500ms for 95th percentile
- [ ] No timeout errors
- [ ] Database queries < 100ms average
- [ ] Worker utilization < 70%

### Monitoring Script
```bash
#!/bin/bash
# monitor-response-times.sh

for i in {1..60}; do
  TIME=$(curl -w "%{time_total}" -o /dev/null -s https://your-domain.com)
  echo "$(date): ${TIME}s"
  
  # Alert if > 2 seconds
  if (( $(echo "$TIME > 2.0" | bc -l) )); then
    echo "ALERT: Response time exceeded threshold: ${TIME}s"
  fi
  
  sleep 60
done
```

## Related Runbooks
- [High CPU Usage](high-cpu.md)
- [Database Performance Tuning](database-tuning.md)
- [Service Restart Procedure](service-restart.md)

---

**Last Updated**: 2024-11-09
**Runbook Version**: 1.0
**Owner**: DevOps Team
