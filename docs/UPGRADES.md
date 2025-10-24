# Upgrade Guide

## Upgrade Strategy

### Version Compatibility
- **Odoo 19**: Current stable version
- **PostgreSQL 14**: Supported version
- **Redis 6**: Cache and session storage
- **Caddy 2.8**: Reverse proxy and SSL

### Upgrade Types
1. **Patch Updates**: Security fixes and bug patches
2. **Minor Updates**: Feature additions and improvements
3. **Major Updates**: Breaking changes (careful planning required)

## Pre-Upgrade Checklist

### Before Any Upgrade

**Backup Everything**
```bash
# Database backup
./scripts/backup_db.sh

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz env/.env odoo/odoo.conf caddy/Caddyfile

# Custom modules backup
tar -czf custom_modules_$(date +%Y%m%d).tar.gz addons/ --exclude='addons/oca'
```

**Health Check**
```bash
# Verify current system health
docker compose ps
docker compose logs --tail=50

# Database health
docker compose exec postgres psql -U odoo -d odoo -c "SELECT version();"
docker compose exec postgres psql -U odoo -d odoo -c "VACUUM ANALYZE;"
```

**Document Current State**
```bash
# List installed modules
docker compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo --no-http --stop-after-init -e "
print('Installed modules:', env['ir.module.module'].search([('state','=','installed')]).mapped('name'))
"

# System parameters
docker compose exec postgres psql -U odoo -d odoo -c "SELECT key, value FROM ir_config_parameter ORDER BY key;"
```

## Upgrade Procedures

### Odoo Version Upgrade

**Step 1: Prepare for Upgrade**
```bash
# Stop services
docker compose down

# Backup database
docker compose run --rm postgres pg_dump -U odoo odoo > pre_upgrade_backup_$(date +%Y%m%d).sql
```

**Step 2: Update Docker Images**
```bash
# Pull new Odoo image
docker compose pull odoo
docker compose pull odoo-longpoll

# Verify new version
docker images | grep odoo
```

**Step 3: Test Upgrade**
```bash
# Start services with new version
docker compose up -d

# Check logs for errors
docker compose logs -f odoo | tail -100
```

**Step 4: Run Database Upgrade**
```bash
# Update all modules
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u all --stop-after-init

# Check for upgrade errors
docker compose logs odoo | grep -i "error\|warning\|traceback"
```

**Step 5: Verify Upgrade**
```bash
# Check Odoo version
curl -s https://your-domain.com/odoo/web/login | grep "Odoo"

# Verify modules are working
docker compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo --no-http --stop-after-init -e "
print('Odoo version:', env['ir.module.module'].search([('name','=','base')]).odoo_version)
"
```

### OCA Module Updates

**Update OCA Repositories**
```bash
# Update all OCA repositories
cd addons/oca
for repo in */; do
  echo "Updating $repo"
  cd "$repo"
  git pull origin main
  cd ..
done
cd ../..
```

**Install Updated Modules**
```bash
# Update specific modules
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u module1,module2 --stop-after-init

# Or update all modules
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u all --stop-after-init
```

### Custom Module Updates

**Backup Custom Modules**
```bash
# Backup before changes
cp -r addons/custom_module addons/custom_module_backup_$(date +%Y%m%d)
```

**Update Process**
```bash
# Stop Odoo services
docker compose stop odoo odoo-longpoll

# Replace custom modules
# (Copy updated modules to addons/)

# Update modules
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -u custom_module --stop-after-init

# Restart services
docker compose start odoo odoo-longpoll
```

## Post-Upgrade Verification

### Functional Testing

**Core Module Testing**
```bash
# Verify key modules are working
docker compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo --no-http --stop-after-init -e "
modules = ['base', 'web', 'mail', 'knowledge_notion_clone', 'bi_superset_agent']
for module in modules:
    mod = env['ir.module.module'].search([('name','=',module)])
    if mod and mod.state == 'installed':
        print(f'✓ {module}: OK')
    else:
        print(f'✗ {module}: Not installed or error')
"
```

**Database Integrity Check**
```bash
# Check for database inconsistencies
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo --init=base --update=all --stop-after-init --test-enable
```

**Performance Verification**
```bash
# Check response times
time curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/odoo/web/login

# Check worker status
docker compose exec odoo ps aux | grep odoo
```

### Data Validation

**Critical Data Checks**
```bash
# Verify user accounts
docker compose exec postgres psql -U odoo -d odoo -c "SELECT count(*) FROM res_users WHERE active = true;"

# Verify company data
docker compose exec postgres psql -U odoo -d odoo -c "SELECT name FROM res_company;"

# Verify custom module data
docker compose exec postgres psql -U odoo -d odoo -c "SELECT count(*) FROM bi_analytics_dashboard;"
```

## Rollback Procedures

### Database Rollback

**From Backup**
```bash
# Stop Odoo services
docker compose stop odoo odoo-longpoll

# Restore database
docker compose exec -T postgres psql -U odoo -d odoo < pre_upgrade_backup.sql

# Restart with old version
docker compose up -d
```

### Configuration Rollback

**Restore Configuration**
```bash
# Restore configuration files
tar -xzf config_backup_$(date +%Y%m%d).tar.gz

# Restart services
docker compose restart
```

## Specific Upgrade Scenarios

### Odoo 18 to Odoo 19

**Major Changes to Consider**
- Python 3.10+ requirement
- Updated web client architecture
- New module dependencies
- Deprecated features removal

**Migration Steps**
```bash
# 1. Complete backup
./scripts/backup_db.sh

# 2. Update docker-compose.yml to use odoo:19
# 3. Update odoo.conf for new version
# 4. Test custom module compatibility
# 5. Follow standard upgrade procedure
```

### PostgreSQL Version Upgrade

**PostgreSQL 13 to 14**
```bash
# Dump and restore method
docker compose exec postgres pg_dump -U odoo odoo > migration_dump.sql
docker compose down
# Update docker-compose.yml to postgres:14
docker compose up -d postgres
docker compose exec -T postgres psql -U odoo -d odoo < migration_dump.sql
docker compose up -d
```

## Automated Upgrade Script

Create `scripts/upgrade_all.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Starting automated upgrade process..."

# Backup
./scripts/backup_db.sh

# Update OCA modules
cd addons/oca
for repo in */; do
  echo "Updating $repo"
  cd "$repo" && git pull origin main && cd ..
done
cd ../..

# Update Docker images
docker compose pull

# Restart services
docker compose up -d

# Update modules
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u all --stop-after-init

echo "Upgrade completed successfully!"
```

## Troubleshooting Upgrades

### Common Upgrade Issues

**Module Dependency Errors**
```bash
# Check module dependencies
docker compose logs odoo | grep -i "dependency\|missing\|conflict"

# Install missing dependencies
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -i missing_module --stop-after-init
```

**Database Migration Failures**
```bash
# Check migration logs
docker compose logs odoo | grep -i "migration\|upgrade\|error"

# Manual module update
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u problematic_module --stop-after-init
```

**Performance Degradation**
```bash
# Check for new performance issues
docker stats
docker compose exec postgres psql -U odoo -d odoo -c "EXPLAIN ANALYZE SELECT * FROM res_users;"

# Consider tuning parameters in odoo.conf
```

### Emergency Recovery

**Immediate Rollback**
```bash
# If upgrade fails catastrophically
docker compose down
docker compose run --rm postgres psql -U odoo -d odoo < latest_working_backup.sql
docker compose up -d
```

## Best Practices

### Testing Strategy

**Staging Environment**
- Maintain identical staging environment
- Test all upgrades in staging first
- Validate custom workflows and integrations

**User Acceptance Testing**
- Involve key users in testing
- Test critical business processes
- Document any workflow changes

### Communication Plan

**Pre-Upgrade**
- Notify users of maintenance window
- Document expected downtime
- Provide rollback timeline

**Post-Upgrade**
- Announce successful upgrade
- Provide updated documentation
- Collect user feedback

### Monitoring Post-Upgrade

**First 48 Hours**
- Monitor system performance
- Watch for error logs
- Track user-reported issues
- Verify automated processes

**First Week**
- Performance benchmarking
- User satisfaction survey
- Documentation updates
- Lessons learned review
