# Disaster Recovery Plan - InsightPulse AI

**Version**: 1.0
**Last Updated**: 2025-01-06
**Owner**: DevOps Team
**Review Cycle**: Quarterly

## 📋 Executive Summary

This document outlines the disaster recovery (DR) procedures for InsightPulse AI infrastructure, including Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), backup strategies, and step-by-step recovery procedures.

## 🎯 Objectives

### Recovery Time Objective (RTO)
- **Critical Services**: < 4 hours
- **Standard Services**: < 24 hours
- **Non-Critical Services**: < 72 hours

### Recovery Point Objective (RPO)
- **Database**: < 1 hour (automated hourly backups)
- **File Storage**: < 24 hours (daily backups)
- **Configuration**: < 1 hour (Git-versioned)

## 🏗️ Infrastructure Overview

### Critical Components
1. **Supabase PostgreSQL Database** (Primary data store)
2. **DigitalOcean App Platform Apps** (Odoo, Superset, MCP)
3. **Droplets** (OCR/LLM, Monitoring)
4. **DNS Configuration** (insightpulseai.net)
5. **SSL/TLS Certificates**

### Dependencies
- **External**: Supabase, DigitalOcean, GitHub, Domain Registrar
- **Internal**: Docker images, Configuration files, Terraform state

## 💾 Backup Strategy

### Automated Backups

#### 1. Database Backups (Supabase PostgreSQL)

**Frequency**: Hourly
**Retention**: 7 days point-in-time recovery
**Location**: Supabase managed backups

**Manual Backup**:
```bash
# Create database dump
export POSTGRES_URL="postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

pg_dump "$POSTGRES_URL" \
  --file="backup-$(date +%Y%m%d-%H%M%S).sql" \
  --format=custom \
  --verbose

# Upload to backup storage
aws s3 cp backup-*.sql s3://insightpulse-backups/database/
```

**Automated Script** (`scripts/backup-database.sh`):
```bash
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backups/database"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Create backup
pg_dump "$POSTGRES_URL" \
  --file="$BACKUP_DIR/db-backup-$DATE.sql" \
  --format=custom

# Compress backup
gzip "$BACKUP_DIR/db-backup-$DATE.sql"

# Upload to DigitalOcean Spaces
s3cmd put "$BACKUP_DIR/db-backup-$DATE.sql.gz" \
  s3://insightpulse-backups/database/

# Clean old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Database backup completed: db-backup-$DATE.sql.gz"
```

#### 2. Application Configuration Backups

**Frequency**: On every deployment
**Retention**: 90 days
**Location**: Git repository + DigitalOcean Spaces

**Backup Items**:
- Terraform state files
- Environment variables (encrypted)
- Docker compose files
- Odoo addons and custom modules
- Grafana dashboards
- Prometheus rules

**Automated Backup**:
```bash
#!/bin/bash
# scripts/backup-config.sh

DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/tmp/config-backup-$DATE"

mkdir -p $BACKUP_DIR

# Backup Terraform state
cp terraform/*.tfstate $BACKUP_DIR/

# Backup environment files (encrypted)
tar -czf $BACKUP_DIR/env-files.tar.gz .env* --exclude=".env.example"

# Backup Docker configs
cp -r docker-compose*.yml $BACKUP_DIR/
cp -r infra/do/*.yaml $BACKUP_DIR/

# Backup Odoo custom modules
tar -czf $BACKUP_DIR/odoo-custom-modules.tar.gz addons/custom/

# Backup monitoring configs
tar -czf $BACKUP_DIR/monitoring-config.tar.gz monitoring/

# Upload to Spaces
tar -czf "/tmp/config-backup-$DATE.tar.gz" -C /tmp "config-backup-$DATE"
s3cmd put "/tmp/config-backup-$DATE.tar.gz" s3://insightpulse-backups/config/

# Cleanup
rm -rf $BACKUP_DIR "/tmp/config-backup-$DATE.tar.gz"

echo "✅ Configuration backup completed"
```

#### 3. Droplet Snapshots

**Frequency**: Weekly
**Retention**: 4 weeks
**Location**: DigitalOcean

**Automated Snapshot**:
```bash
#!/bin/bash
# scripts/create-droplet-snapshots.sh

# Get droplet IDs
OCR_DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep "ocr-llm" | awk '{print $1}')
MONITORING_DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep "monitoring" | awk '{print $1}')

# Create snapshots
doctl compute droplet-action snapshot $OCR_DROPLET_ID \
  --snapshot-name "ocr-llm-$(date +%Y%m%d)"

doctl compute droplet-action snapshot $MONITORING_DROPLET_ID \
  --snapshot-name "monitoring-$(date +%Y%m%d)"

# Delete old snapshots (keep last 4)
doctl compute snapshot list --format ID,Name,CreatedAt | \
  grep "ocr-llm" | tail -n +5 | awk '{print $1}' | \
  xargs -I {} doctl compute snapshot delete {} --force

echo "✅ Droplet snapshots created"
```

#### 4. Prometheus & Grafana Data

**Frequency**: Daily
**Retention**: 30 days
**Location**: Volume backups

```bash
#!/bin/bash
# scripts/backup-monitoring-data.sh

DATE=$(date +%Y%m%d)

# Backup Prometheus data
docker run --rm \
  -v monitoring_prometheus_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/prometheus-$DATE.tar.gz -C /data .

# Backup Grafana data
docker run --rm \
  -v monitoring_grafana_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/grafana-$DATE.tar.gz -C /data .

# Upload to Spaces
s3cmd put backups/prometheus-$DATE.tar.gz s3://insightpulse-backups/monitoring/
s3cmd put backups/grafana-$DATE.tar.gz s3://insightpulse-backups/monitoring/

echo "✅ Monitoring data backed up"
```

### Backup Verification

**Frequency**: Weekly
**Automated Test**: Restore to staging environment

```bash
#!/bin/bash
# scripts/test-backup-restore.sh

echo "🧪 Testing backup restoration..."

# Download latest backup
LATEST_BACKUP=$(s3cmd ls s3://insightpulse-backups/database/ | tail -1 | awk '{print $4}')
s3cmd get $LATEST_BACKUP /tmp/test-restore.sql.gz

# Decompress
gunzip /tmp/test-restore.sql.gz

# Create test database
psql "$STAGING_DB_URL" -c "CREATE DATABASE backup_test;"

# Restore backup
pg_restore -d backup_test /tmp/test-restore.sql

# Verify data
ROW_COUNT=$(psql "$STAGING_DB_URL/backup_test" -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname='public';")

if [ "$ROW_COUNT" -gt 0 ]; then
  echo "✅ Backup restore test PASSED ($ROW_COUNT tables)"
else
  echo "❌ Backup restore test FAILED"
  exit 1
fi

# Cleanup
psql "$STAGING_DB_URL" -c "DROP DATABASE backup_test;"
rm /tmp/test-restore.sql

echo "✅ Backup verification completed"
```

## 🚨 Disaster Scenarios & Recovery Procedures

### Scenario 1: Database Corruption/Loss

**Severity**: Critical
**RTO**: 2 hours
**RPO**: 1 hour

**Detection**:
- Database connection failures
- Data inconsistency reports
- Monitoring alerts

**Recovery Steps**:

1. **Assess Damage**
   ```bash
   # Check database connectivity
   psql "$POSTGRES_URL" -c "SELECT version();"

   # Check data integrity
   psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM pg_tables;"
   ```

2. **Stop All Applications**
   ```bash
   # Stop App Platform apps
   doctl apps list --format ID | xargs -I {} doctl apps update {} --spec /dev/null
   ```

3. **Restore from Backup**
   ```bash
   # Download latest backup
   LATEST_BACKUP=$(s3cmd ls s3://insightpulse-backups/database/ | tail -1 | awk '{print $4}')
   s3cmd get $LATEST_BACKUP /tmp/restore.sql.gz
   gunzip /tmp/restore.sql.gz

   # Drop existing database (CAUTION!)
   psql "$POSTGRES_URL" -c "DROP DATABASE postgres WITH (FORCE);"
   psql "$POSTGRES_URL" -c "CREATE DATABASE postgres;"

   # Restore backup
   pg_restore -d postgres /tmp/restore.sql -v
   ```

4. **Verify Data Integrity**
   ```bash
   # Run validation queries
   psql "$POSTGRES_URL" <<EOF
   SELECT COUNT(*) FROM res_users;
   SELECT COUNT(*) FROM res_partner;
   SELECT MAX(create_date) FROM account_move;
   EOF
   ```

5. **Restart Applications**
   ```bash
   # Redeploy apps
   doctl apps create-deployment <app-id>
   ```

6. **Validate Recovery**
   - Test user login
   - Verify recent transactions
   - Check all critical functions

**Estimated Recovery Time**: 2 hours

### Scenario 2: Complete App Platform Failure

**Severity**: Critical
**RTO**: 4 hours
**RPO**: 0 (stateless applications)

**Recovery Steps**:

1. **Deploy to Alternative Region**
   ```bash
   # Update region in Terraform
   cd terraform
   vim variables.tf  # Change region to 'nyc1' or 'sfo'

   # Apply changes
   terraform plan
   terraform apply
   ```

2. **Update DNS Records**
   ```bash
   # Update A/CNAME records
   doctl compute domain records update insightpulseai.net \
     <record-id> --record-data <new-ip>
   ```

3. **Deploy Applications**
   ```bash
   # Deploy via Terraform
   terraform apply -target=digitalocean_app.odoo_saas
   terraform apply -target=digitalocean_app.superset
   terraform apply -target=digitalocean_app.mcp_server
   ```

4. **Verify Services**
   ```bash
   # Health checks
   curl https://erp.insightpulseai.net/web/health
   curl https://superset.insightpulseai.net/health
   curl https://mcp.insightpulseai.net/health
   ```

**Estimated Recovery Time**: 4 hours

### Scenario 3: Droplet Failure (OCR/LLM or Monitoring)

**Severity**: High
**RTO**: 1 hour
**RPO**: 0 (can rebuild)

**Recovery Steps**:

1. **Create New Droplet from Snapshot**
   ```bash
   # List available snapshots
   doctl compute snapshot list

   # Create droplet from snapshot
   doctl compute droplet create insightpulse-ocr-llm-restored \
     --image <snapshot-id> \
     --size s-1vcpu-1gb \
     --region sgp1 \
     --vpc-uuid <vpc-id>
   ```

2. **Update DNS**
   ```bash
   # Get new droplet IP
   NEW_IP=$(doctl compute droplet get insightpulse-ocr-llm-restored --format PublicIPv4 --no-header)

   # Update DNS records
   doctl compute domain records update insightpulseai.net \
     <ocr-record-id> --record-data $NEW_IP
   ```

3. **Verify Services**
   ```bash
   curl https://ocr.insightpulseai.net/health
   curl https://llm.insightpulseai.net/health
   ```

**Estimated Recovery Time**: 1 hour

### Scenario 4: Data Center Outage (Regional Failure)

**Severity**: Critical
**RTO**: 8 hours
**RPO**: 1 hour

**Recovery Steps**:

1. **Activate DR Region**
   ```bash
   cd terraform
   terraform workspace new dr-region
   terraform apply -var="region=nyc1"
   ```

2. **Restore Database in New Region**
   - Supabase: Create new project in alternative region
   - Restore from backup (see Scenario 1)

3. **Deploy All Services**
   ```bash
   terraform apply
   ```

4. **Update Global DNS**
   - Update all A/CNAME records to new region IPs

5. **Communicate to Users**
   - Send status update emails
   - Update status page

**Estimated Recovery Time**: 8 hours

## 🔄 Recovery Validation Checklist

After any recovery procedure:

- [ ] Database connectivity verified
- [ ] All applications responding to health checks
- [ ] User authentication working
- [ ] Critical business functions tested
- [ ] Monitoring and alerting operational
- [ ] DNS propagation completed (wait 5-10 minutes)
- [ ] SSL certificates valid
- [ ] Backup jobs re-enabled
- [ ] Post-mortem scheduled
- [ ] Documentation updated

## 📞 Emergency Contacts

| Role | Name | Contact | Availability |
|------|------|---------|--------------|
| DevOps Lead | [Name] | [Email/Phone] | 24/7 |
| Database Admin | [Name] | [Email/Phone] | Business hours |
| Infrastructure | [Name] | [Email/Phone] | 24/7 on-call |
| Management | [Name] | [Email/Phone] | Business hours |

## 📊 DR Testing Schedule

| Test Type | Frequency | Last Performed | Next Scheduled |
|-----------|-----------|----------------|----------------|
| Backup Restore | Weekly | 2025-01-05 | 2025-01-12 |
| Failover Test | Quarterly | 2024-12-15 | 2025-03-15 |
| Full DR Drill | Annually | 2024-11-01 | 2025-11-01 |

## 📝 Post-Incident Procedures

1. **Document the Incident**
   - What happened?
   - When was it detected?
   - What was the impact?
   - How was it resolved?

2. **Root Cause Analysis**
   - Conduct within 48 hours
   - Identify root cause
   - Document contributing factors

3. **Action Items**
   - Create tickets for improvements
   - Update runbooks
   - Implement preventive measures

4. **Communication**
   - Internal stakeholders notification
   - Customer communication (if needed)
   - Post-mortem report

## 🔗 Related Documentation

- [Operational Runbooks](./OPERATIONAL_RUNBOOKS.md)
- [Network Security](./NETWORK_SECURITY.md)
- [Monitoring Guide](../monitoring/README.md)
- [Terraform Infrastructure](../terraform/README.md)

## 📄 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-01-06 | 1.0 | Initial disaster recovery plan | DevOps Team |
