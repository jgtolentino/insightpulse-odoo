# 🚀 Deployment Guide: Notion Enterprise → Odoo CE/OCA

**Version:** 1.0
**Target:** Finance SSC Multi-Agency Operations
**Timeline:** 12 weeks
**Last Updated:** 2025-11-05

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Core Infrastructure](#phase-1-core-infrastructure-week-1-2)
4. [Phase 2: Security & Compliance](#phase-2-security--compliance-week-3-4)
5. [Phase 3: Finance SSC Workflows](#phase-3-finance-ssc-workflows-week-5-8)
6. [Phase 4: Analytics & BI](#phase-4-analytics--bi-week-9-10)
7. [Phase 5: Integration](#phase-5-integration-week-11-12)
8. [Post-Deployment](#post-deployment)
9. [Rollback Plan](#rollback-plan)
10. [Support](#support)

---

## Executive Summary

This guide provides step-by-step instructions for deploying Odoo 19 CE with OCA modules as a complete replacement for Notion Enterprise, specifically tailored for Finance Shared Service Center operations managing multiple agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB).

### Cost Savings
- **Notion Enterprise (50 users):** $1,000/month = $12,000/year
- **Odoo CE + OCA (self-hosted):** ~$200/month = $2,400/year
- **Total 3-Year Savings:** $28,000

### Technology Stack
```
┌─────────────────────────────────────────────┐
│  📊 Frontend: Odoo Web UI + Custom Views    │
├─────────────────────────────────────────────┤
│  🔧 Backend: Odoo 19 CE + OCA Modules       │
├─────────────────────────────────────────────┤
│  🗄️ Database: PostgreSQL 16 + pgvector      │
├─────────────────────────────────────────────┤
│  🤖 AI Layer: InsightPulse AI (PaddleOCR)   │
├─────────────────────────────────────────────┤
│  📈 Analytics: Apache Superset              │
├─────────────────────────────────────────────┤
│  🚀 Infrastructure: DigitalOcean Droplet    │
└─────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Infrastructure Requirements

**Server Specifications (DigitalOcean Droplet):**
- CPU: 8 vCPUs (Premium Intel or AMD)
- RAM: 16 GB
- Storage: 320 GB SSD
- Bandwidth: 6 TB transfer
- Cost: ~$144/month

**Alternative (for smaller deployments):**
- CPU: 4 vCPUs
- RAM: 8 GB
- Storage: 160 GB SSD
- Cost: ~$72/month

### 2. Domain & SSL
- Domain name (e.g., `erp.insightpulseai.net`)
- SSL certificate (Let's Encrypt recommended)

### 3. Required Accounts
- DigitalOcean account
- GitHub account (for repository access)
- Docker Hub account (optional, for custom images)

### 4. Local Development Tools
- Git
- Docker & Docker Compose
- SSH client
- Text editor (VS Code recommended)

---

## Phase 1: Core Infrastructure (Week 1-2)

### Day 1-2: Server Provisioning

#### 1.1 Create DigitalOcean Droplet

```bash
# Using doctl CLI
doctl compute droplet create insightpulse-odoo-prod \
  --region sgp1 \
  --size s-8vcpu-16gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys <your-ssh-key-id>

# Or use DigitalOcean web interface
# Navigate to: Create > Droplets > Choose plan > Create Droplet
```

#### 1.2 Initial Server Setup

```bash
# SSH into server
ssh root@<droplet-ip>

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Create deployment user
adduser odoo
usermod -aG docker odoo
su - odoo
```

#### 1.3 Clone Repository

```bash
# As odoo user
cd /home/odoo
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
git checkout claude/notion-to-odoo-mapping-011CUpkKA5LugAkD5mKLr66J
```

### Day 3-5: OCA Module Installation

#### 1.4 Install OCA Modules

```bash
# Make installation script executable
chmod +x scripts/install_oca_modules.sh

# Run installation
./scripts/install_oca_modules.sh

# Review installation log
cat logs/oca_installation_*.log
```

Expected output:
```
====================================
 OCA Module Installation Script
 InsightPulse Odoo Finance SSC
====================================

Odoo Version: 19.0
Target Directory: ./addons/oca

[INFO] Installing Python dependencies...
[SUCCESS] Python dependencies installed
[INFO] Cloning OCA repositories...
[SUCCESS] Successfully cloned server-auth
[SUCCESS] Successfully cloned server-backend
...
[SUCCESS] OCA module installation complete!
```

### Day 6-7: Environment Configuration

#### 1.5 Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

**Required Environment Variables:**

```bash
# PostgreSQL Configuration
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=odoo19

# Odoo Configuration
ODOO_ADMIN_PASSWORD=<strong-admin-password>
ODOO_WORKERS=8
ODOO_DB_FILTER=^odoo19$

# Redis Configuration
REDIS_PASSWORD=<redis-password>

# Superset Configuration
SUPERSET_SECRET_KEY=<superset-secret>
SUPERSET_DB=superset

# AI Services
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>

# InsightPulse AI
INSIGHTPULSE_OCR_URL=http://paddleocr:8000
INSIGHTPULSE_AI_URL=http://insightpulse-ai:8001
```

#### 1.6 PostgreSQL Initialization Script

Create extension initialization script:

```bash
mkdir -p scripts/postgres
cat > scripts/postgres/init-extensions.sql <<EOF
-- Enable required PostgreSQL extensions

-- pgvector for AI semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- pg_stat_statements for performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create database for Superset if not exists
SELECT 'CREATE DATABASE superset'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'superset')\gexec

EOF
```

### Day 8-10: Initial Deployment

#### 1.7 Deploy Services

```bash
# Build and start services
docker-compose -f docker-compose.oca.yml up -d --build

# Check service status
docker-compose -f docker-compose.oca.yml ps

# View logs
docker-compose -f docker-compose.oca.yml logs -f odoo
```

Expected services:
```
NAME                        STATUS    PORTS
insightpulse-db-oca         Up        5432/tcp
insightpulse-redis-oca      Up        6379/tcp
insightpulse-odoo-oca       Up        8069/tcp, 8072/tcp
insightpulse-paddleocr      Up        8000/tcp
insightpulse-ai-nlp         Up        8001/tcp
insightpulse-superset       Up        8088/tcp
insightpulse-nginx          Up        80/tcp, 443/tcp
```

#### 1.8 Create Odoo Database

```bash
# Access Odoo container
docker-compose -f docker-compose.oca.yml exec odoo bash

# Create database with base modules
/opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoo19 -i base,web --stop-after-init

# Verify database creation
psql -h db -U odoo -d odoo19 -c "\dt"
```

### Day 11-14: Multi-Company Setup

#### 1.9 Configure Companies (Agencies)

Access Odoo UI at `http://<droplet-ip>:8069` and:

1. **Login as admin**
   - Database: odoo19
   - Email: admin
   - Password: <ODOO_ADMIN_PASSWORD>

2. **Create Companies:**
   - Go to Settings > Companies > Manage Companies
   - Create each agency:

   ```
   Company Name: Razon Industries Management
   Short Name: RIM
   Tax ID: 123-456-789-000
   Currency: PHP

   Company Name: CK Venture Capital
   Short Name: CKVC
   Tax ID: 123-456-790-000
   Currency: PHP

   ... (repeat for BOM, JPAL, JLI, JAP, LAS, RMQB)
   ```

3. **Configure Company Settings:**
   - Set fiscal year start date
   - Configure chart of accounts
   - Set default taxes
   - Configure BIR TIN for each company

---

## Phase 2: Security & Compliance (Week 3-4)

### Week 3: Authentication & Authorization

#### 2.1 Install Security Modules

```bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo19 \
  -i auth_totp,password_security,auth_session_timeout \
  --stop-after-init
```

#### 2.2 Configure Password Policies

1. Go to Settings > Technical > Parameters > System Parameters
2. Create parameters:
   ```
   auth_password_policy.minlength = 12
   auth_password_policy.uppercase = 1
   auth_password_policy.lowercase = 1
   auth_password_policy.numeric = 1
   auth_password_policy.special = 1
   password_expiration_days = 90
   ```

#### 2.3 Enable 2FA for Admins

1. Go to Settings > Users
2. For each admin user:
   - Edit user
   - Check "2FA Required"
   - Save

#### 2.4 Configure Session Timeout

```bash
# Update odoo.conf
cat >> config/odoo/odoo.oca.conf <<EOF

# Session timeout (30 minutes)
session_timeout = 1800

# Maximum inactive time (2 hours)
max_inactive_time = 7200
EOF

# Restart Odoo
docker-compose -f docker-compose.oca.yml restart odoo
```

### Week 4: Audit & Compliance

#### 2.5 Install Audit Logging

```bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo19 \
  -i auditlog \
  --stop-after-init
```

#### 2.6 Configure Audit Rules

1. Go to Settings > Technical > Audit > Rules
2. Create audit rules for:
   - `res.users` - User changes
   - `res.company` - Company changes
   - `account.move` - Journal entries
   - `finance.closing.period` - Closing periods
   - `finance.closing.task` - Closing tasks
   - `finance.bir.compliance.task` - BIR filings

Example rule:
```
Name: Audit Journal Entries
Model: account.move
Log Reads: No
Log Writes: Yes
Log Creates: Yes
Log Deletes: Yes
Log Workflow: Yes
State: Subscribed
```

#### 2.7 Install GDPR Compliance Modules

```bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo19 \
  -i privacy,privacy_consent \
  --stop-after-init
```

---

## Phase 3: Finance SSC Workflows (Week 5-8)

### Week 5-6: Install Finance Modules

#### 3.1 Install Finance SSC Closing Module

```bash
# The module is already in addons/custom/finance_ssc_closing/
# Install via Odoo UI

# Or via CLI:
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo19 \
  -i finance_ssc_closing \
  --stop-after-init
```

#### 3.2 Install OCA Approval Module

```bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo19 \
  -i approval_request \
  --stop-after-init
```

#### 3.3 Configure Task Templates

1. Go to Finance SSC > Configuration > Task Templates
2. Create templates for each agency's closing process
3. Import from CSV (if provided)

### Week 7: BIR Compliance Setup

#### 3.4 Configure BIR Forms

1. Review BIR forms in Finance SSC > Configuration > BIR Forms
2. Update filing frequencies based on agency requirements
3. Set default assignees for each form type

#### 3.5 Configure Filing Deadlines

Create scheduled actions for automatic deadline calculation:
1. Go to Settings > Technical > Automation > Scheduled Actions
2. Create action:
   ```
   Name: Generate Monthly BIR Tasks
   Model: finance.bir.compliance.task
   Execute Every: 1 Months
   Next Execution Date: <first day of next month>
   Python Code:
   ```
   ```python
   # Auto-generate BIR tasks for next period
   ClosingPeriod = env['finance.closing.period']
   next_period = ClosingPeriod.search([
       ('start_date', '>', fields.Date.today())
   ], limit=1)

   if next_period:
       next_period.action_generate_bir_tasks()
   ```

### Week 8: Workflow Testing

#### 3.6 Create Test Closing Period

1. Create period: "2025-TEST"
2. Generate tasks from templates
3. Assign to test users
4. Walk through complete workflow:
   - Open period
   - Start tasks
   - Submit for review
   - Approve tasks
   - Close period

#### 3.7 Performance Testing

```bash
# Run performance tests
docker-compose -f docker-compose.oca.yml exec odoo python3 -m pytest tests/test_performance.py -v

# Check database performance
docker-compose -f docker-compose.oca.yml exec db psql -U odoo -d odoo19 -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
"
```

---

## Phase 4: Analytics & BI (Week 9-10)

### Week 9: Superset Setup

#### 4.1 Initialize Superset

```bash
# Access Superset container
docker-compose -f docker-compose.oca.yml exec superset bash

# Initialize database
superset db upgrade

# Create admin user
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@insightpulse.ai \
  --password <strong-password>

# Initialize Superset
superset init
```

#### 4.2 Connect to Odoo Database

1. Access Superset at `http://<droplet-ip>:8088`
2. Login as admin
3. Go to Data > Databases > + Database
4. Configure connection:
   ```
   Database: PostgreSQL
   Host: db
   Port: 5432
   Database: odoo19
   Username: odoo
   Password: <postgres-password>
   Display Name: Odoo Finance SSC
   ```

#### 4.3 Create Finance SSC Dashboards

Import pre-built dashboards:
```bash
# Copy dashboard definitions
cp superset/dashboards/finance_ssc_*.json /tmp/

# Import dashboards
superset import-dashboards -p /tmp/finance_ssc_closing_dashboard.json
superset import-dashboards -p /tmp/finance_ssc_bir_compliance.json
```

### Week 10: Reporting

#### 4.4 Install Reporting Modules

```bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo19 \
  -i report_xlsx,report_py3o,mis_builder \
  --stop-after-init
```

#### 4.5 Configure MIS Builder Reports

1. Go to Reporting > MIS Builder > MIS Report Templates
2. Create reports:
   - Month-End Closing Summary
   - BIR Compliance Report
   - Multi-Agency Consolidation
   - Variance Analysis

---

## Phase 5: Integration (Week 11-12)

### Week 11: REST API Setup

#### 5.1 Install REST Framework

```bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo19 \
  -i base_rest,base_rest_auth_jwt,base_rest_datamodel \
  --stop-after-init
```

#### 5.2 Configure API Endpoints

Create custom REST controller:
```python
# addons/custom/finance_ssc_api/controllers/api.py
from odoo.addons.base_rest.controllers import main

class FinanceSSCApiController(main.RestController):
    _root_path = '/api/finance_ssc/'
    _collection_name = 'finance.ssc.services'
    _default_auth = 'jwt'
```

### Week 12: InsightPulse AI Integration

#### 5.3 Configure PaddleOCR Service

```bash
# Test PaddleOCR service
curl http://localhost:8000/health

# Test OCR endpoint
curl -X POST http://localhost:8000/ocr \
  -F "file=@test_bir_form.pdf" \
  -H "Content-Type: multipart/form-data"
```

#### 5.4 Configure Webhooks

1. Go to Settings > Technical > Automation > Webhooks
2. Create webhooks for:
   - Period state changes
   - Task completion
   - BIR form filing
   - Overdue notifications

---

## Post-Deployment

### 1. User Training

Schedule training sessions:
- **Week 13:** Admin training (2 days)
- **Week 14:** Accountant training (3 days)
- **Week 15:** End-user training (2 days)

### 2. Data Migration

If migrating from Notion:
```bash
# Use custom migration script
python3 scripts/migrate_from_notion.py \
  --notion-token <notion-token> \
  --database-id <database-id> \
  --odoo-url http://localhost:8069 \
  --odoo-db odoo19 \
  --odoo-user admin \
  --odoo-password <password>
```

### 3. Go-Live Checklist

- [ ] All OCA modules installed and configured
- [ ] Multi-company setup complete
- [ ] User accounts created and access rights assigned
- [ ] 2FA enabled for all users
- [ ] Audit logging active
- [ ] Task templates configured
- [ ] BIR forms configured
- [ ] Superset dashboards created
- [ ] API endpoints tested
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] SSL certificate installed
- [ ] DNS configured
- [ ] Training completed
- [ ] Documentation updated

### 4. Backup Configuration

```bash
# Create backup script
cat > scripts/backup_odoo.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/home/odoo/backups

# Backup PostgreSQL
docker-compose exec -T db pg_dump -U odoo odoo19 | gzip > $BACKUP_DIR/odoo19_$DATE.sql.gz

# Backup filestore
tar -czf $BACKUP_DIR/filestore_$DATE.tar.gz -C /var/lib/docker/volumes/insightpulse-odoo_odoo_filestore_oca/_data .

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

chmod +x scripts/backup_odoo.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/odoo/insightpulse-odoo/scripts/backup_odoo.sh
```

### 5. Monitoring Setup

```bash
# Install monitoring tools
docker-compose -f docker-compose.monitoring.yml up -d

# Services:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000
# - AlertManager: http://localhost:9093
```

---

## Rollback Plan

In case of critical issues:

### 1. Database Rollback

```bash
# Stop Odoo
docker-compose -f docker-compose.oca.yml stop odoo

# Restore database
gunzip < /home/odoo/backups/odoo19_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose exec -T db psql -U odoo -d odoo19

# Restore filestore
tar -xzf /home/odoo/backups/filestore_YYYYMMDD_HHMMSS.tar.gz \
  -C /var/lib/docker/volumes/insightpulse-odoo_odoo_filestore_oca/_data

# Start Odoo
docker-compose -f docker-compose.oca.yml start odoo
```

### 2. Notion Fallback

If complete rollback to Notion is needed:
1. Re-enable Notion workspace
2. Export Odoo data to CSV
3. Import to Notion databases
4. Update team on status

---

## Support

### Resources

- **Documentation:** `/docs/NOTION_TO_ODOO_MAPPING.md`
- **OCA Documentation:** https://odoo-community.org/
- **Odoo Documentation:** https://www.odoo.com/documentation/19.0/
- **GitHub Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues

### Contact

- **Technical Lead:** jgtolentino
- **Finance SSC Team:** finance-ssc@insightpulse.ai
- **Emergency Support:** Available 24/7 for critical issues

---

**Deployment Guide Version:** 1.0
**Last Updated:** 2025-11-05
**Next Review:** 2025-12-05
