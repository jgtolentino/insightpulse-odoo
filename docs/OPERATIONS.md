# Operations Guide

## Daily Operations

### Service Management

**Start Services**
```bash
docker compose up -d
```

**Stop Services**
```bash
docker compose down
```

**Restart Services**
```bash
docker compose restart
```

**View Service Status**
```bash
docker compose ps
docker compose logs [service_name]
```

### Database Operations

**Backup Database**
```bash
# Full database backup
docker compose exec postgres pg_dump -U odoo odoo > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker compose exec postgres pg_dump -U odoo odoo | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Restore Database**
```bash
# From SQL file
docker compose exec -T postgres psql -U odoo odoo < backup_file.sql

# From compressed file
gunzip -c backup_file.sql.gz | docker compose exec -T postgres psql -U odoo odoo
```

**Database Maintenance**
```bash
# Vacuum and analyze
docker compose exec postgres psql -U odoo -d odoo -c "VACUUM ANALYZE;"

# Check database size
docker compose exec postgres psql -U odoo -d odoo -c "SELECT pg_size_pretty(pg_database_size('odoo'));"
```

### Log Management

**View Real-time Logs**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f odoo
docker compose logs -f postgres
docker compose logs -f caddy
```

**Log Rotation**
```bash
# Clear logs (be careful with this)
docker compose logs --tail=100 > recent_logs.txt
docker compose restart odoo  # This will clear container logs
```

## Monitoring

### Health Checks

**Service Health**
```bash
# Check if services are running
docker compose ps

# Check service health
curl -f https://your-domain.com/odoo/web/login
curl -f https://your-domain.com/health
```

**Database Health**
```bash
# Check database connections
docker compose exec postgres psql -U odoo -d odoo -c "SELECT count(*) FROM pg_stat_activity;"

# Check long-running queries
docker compose exec postgres psql -U odoo -d odoo -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

**Performance Monitoring**
```bash
# Check Odoo worker status
docker compose exec odoo ps aux | grep odoo

# Check memory usage
docker stats
```

### Resource Monitoring

**Disk Space**
```bash
# Check volume sizes
docker system df
docker volume ls

# Check specific volume
docker volume inspect insightpulse-odoo_pgdata
```

**CPU and Memory**
```bash
# Real-time resource usage
docker stats --no-stream

# Historical resource usage
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

## Maintenance Tasks

### Weekly Tasks

**Database Optimization**
```bash
# Run vacuum and analyze
docker compose exec postgres psql -U odoo -d odoo -c "VACUUM ANALYZE;"

# Check for table bloat
docker compose exec postgres psql -U odoo -d odoo -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
       n_dead_tup as dead_tuples
FROM pg_stat_all_tables 
WHERE n_dead_tup > 1000 
ORDER BY n_dead_tup DESC;"
```

**Log Rotation**
```bash
# Archive and clear old logs
docker compose logs --tail=1000 > logs/odoo_$(date +%Y%m%d).log
docker compose restart odoo
```

### Monthly Tasks

**Full Backup**
```bash
# Complete system backup
./scripts/backup_db.sh
tar -czf system_backup_$(date +%Y%m).tar.gz backup_*.sql logs/ env/.env
```

**Security Audit**
```bash
# Check for security updates
docker compose pull
docker images | grep odoo

# Review user access logs
docker compose logs odoo | grep -i "login\|failed\|error"
```

## Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check for port conflicts
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :8069

# Check disk space
df -h

# Check Docker daemon
docker info
```

**Database Connection Issues**
```bash
# Test database connectivity
docker compose exec postgres pg_isready -U odoo -d odoo

# Check PostgreSQL logs
docker compose logs postgres | tail -50

# Check Odoo database configuration
docker compose exec odoo cat /etc/odoo/odoo.conf | grep db_
```

**SSL Certificate Problems**
```bash
# Check Caddy status
docker compose logs caddy | grep -i "certificate\|ssl\|tls"

# Verify domain configuration
cat env/.env | grep DOMAIN

# Test SSL
curl -I https://your-domain.com
```

**Performance Issues**
```bash
# Check Odoo workers
docker compose exec odoo ps aux | grep odoo

# Check database performance
docker compose exec postgres psql -U odoo -d odoo -c "
SELECT query, calls, total_time, mean_time, rows 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"
```

### Emergency Procedures

**Service Recovery**
```bash
# Complete service restart
docker compose down
docker compose up -d

# Database recovery
docker compose stop odoo
docker compose exec postgres pg_ctl restart
docker compose start odoo
```

**Data Recovery**
```bash
# From latest backup
docker compose stop odoo
gunzip -c latest_backup.sql.gz | docker compose exec -T postgres psql -U odoo odoo
docker compose start odoo
```

## Security Operations

### User Management

**Add New User**
```bash
# Through Odoo interface is preferred
# Or via database (emergency only)
docker compose exec postgres psql -U odoo -d odoo -c "
INSERT INTO res_users (login, password, active, company_id) 
VALUES ('newuser@company.com', 'encrypted_password', true, 1);"
```

**Password Reset**
```bash
# Emergency password reset
docker compose exec postgres psql -U odoo -d odoo -c "
UPDATE res_users SET password = 'new_encrypted_password' WHERE login = 'admin';"
```

### Access Control

**Review User Sessions**
```bash
docker compose exec postgres psql -U odoo -d odoo -c "
SELECT login, create_date, last_update 
FROM res_users 
WHERE active = true 
ORDER BY last_update DESC;"
```

**Audit Log Review**
```bash
# Check audit logs if auditlog module is installed
docker compose exec postgres psql -U odoo -d odoo -c "
SELECT name, model, method, user_id, create_date 
FROM auditlog_log 
ORDER BY create_date DESC 
LIMIT 20;"
```

## Backup Strategy

### Automated Backups

Create a cron job for automated backups:
```bash
# Add to crontab -e
0 2 * * * /path/to/insightpulse-odoo/scripts/backup_db.sh
0 3 * * 0 /path/to/insightpulse-odoo/scripts/full_system_backup.sh
```

### Backup Verification

**Test Backup Restoration**
```bash
# Create test database
docker compose exec postgres createdb -U odoo test_restore

# Test restore
gunzip -c backup_file.sql.gz | docker compose exec -T postgres psql -U odoo test_restore

# Verify data
docker compose exec postgres psql -U odoo -d test_restore -c "SELECT count(*) FROM res_users;"

# Cleanup
docker compose exec postgres dropdb -U odoo test_restore
```

## Performance Tuning

### Odoo Configuration

**Worker Configuration**
```ini
# In odoo/odoo.conf
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
```

### Database Configuration

**PostgreSQL Tuning**
```sql
-- Consider adding to postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB
```

## Support Procedures

### Issue Reporting

When reporting issues, include:
- Service logs: `docker compose logs [service]`
- Configuration: `cat env/.env` (redact passwords)
- Error messages from Odoo interface
- Steps to reproduce the issue

### Emergency Contacts

- **System Administrator**: [Contact Info]
- **Database Administrator**: [Contact Info]
- **Security Officer**: [Contact Info]
