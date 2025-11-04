# Odoo SaaS to Self-Hosted Migration Plan

**Status:** Planning Phase
**Target:** Full parity migration from Odoo.com SaaS to erp.insightpulseai.net
**Estimated Timeline:** 2-3 days
**Risk Level:** Medium (reversible with rollback plan)

---

## Current State Assessment

### Odoo SaaS Instance
- **URL:** (Need to confirm - likely odoo.com subdomain)
- **Version:** (Need to confirm - likely Odoo 16 or 17)
- **Database Size:** (Need to assess)
- **Active Users:** 8 agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- **Active Modules:** (Need full audit)

### Self-Hosted Instance (Current)
- **URL:** https://erp.insightpulseai.net
- **Version:** Odoo 16
- **Status:** Fresh install, no database yet
- **Infrastructure:** DigitalOcean droplet (165.227.10.178)
- **TLS:** Valid until 2026-02-02
- **Resources:** 4GB RAM, 2 vCPUs, 120GB SSD

---

## Migration Strategy

### Phase 1: Discovery and Planning (Day 1 Morning)

**Objectives:**
- Complete inventory of SaaS configuration
- Identify all installed modules
- Document customizations
- Map data dependencies
- Assess database size

**Actions:**
1. **Access SaaS Admin Panel**
   - Get full module list (Apps → Installed)
   - Export module dependency tree
   - Document custom fields/models
   - Check for Studio customizations

2. **Data Inventory**
   - Count records per model (res.partner, sale.order, account.move, etc.)
   - Identify data volume per agency
   - Check for attachments/binary data
   - Document external integrations

3. **User Access Audit**
   - List all users and groups
   - Document permissions per agency
   - Identify admin users
   - Check for API keys/external accesses

**Deliverables:**
- `SAAS_INVENTORY.md` - Complete module and data inventory
- `MIGRATION_CHECKLIST.md` - Step-by-step migration tasks

---

### Phase 2: Self-Hosted Preparation (Day 1 Afternoon)

**Objectives:**
- Match SaaS module configuration
- Install all required dependencies
- Configure system parameters
- Prepare for data import

**Actions:**

1. **Create Production Database**
   ```bash
   # Via web interface
   URL: https://erp.insightpulseai.net/web/database/manager
   Master Password: 2ca2a768b7c9016f52364921bb78ab2a359da05a23dd0bf1

   Database: insightpulse_prod
   Admin Email: jgtolentino_rn@yahoo.com
   Language: English (US)
   Country: Philippines
   Demo Data: NO
   ```

2. **Install Core Modules (Match SaaS)**
   - Base modules (sales, accounting, inventory, HR, etc.)
   - Industry-specific (if any)
   - Custom modules (ipai_agent, slack_bridge)

3. **Configure System Parameters**
   - Multi-company setup (8 agencies)
   - Fiscal positions (Philippine BIR)
   - Chart of accounts
   - Payment terms
   - Warehouses/locations

4. **Security Configuration**
   - User groups per agency
   - Record rules (multi-company)
   - Field-level security
   - RLS policies

**Deliverables:**
- Production database ready
- All modules installed
- System parameters configured

---

### Phase 3: Data Export from SaaS (Day 2 Morning)

**Objectives:**
- Export complete database backup
- Verify data integrity
- Prepare for import

**Methods:**

#### Method A: Database Dump (Recommended)
```python
# Via Odoo SaaS Database Manager
1. Login to SaaS admin panel
2. Database Manager → Backup Database
3. Select: Include filestore (YES)
4. Format: ZIP (with filestore) or PG_DUMP
5. Download backup file

Expected file: saas_backup_YYYY-MM-DD.zip
```

#### Method B: CSV/Excel Export (Fallback)
If database dump not accessible:
- Export data per model via List Views
- Export attachments separately
- Document export order (master data first, transactions last)

**Data Export Order:**
1. **Master Data:**
   - res.partner (contacts, customers, vendors)
   - res.users (users and permissions)
   - product.product (products/services)
   - account.account (chart of accounts)

2. **Configuration:**
   - account.journal (journals)
   - stock.warehouse (warehouses)
   - res.company (companies/agencies)

3. **Transactional Data:**
   - sale.order (sales)
   - account.move (invoices, bills, journal entries)
   - stock.picking (deliveries)
   - hr.expense (expenses)

**Deliverables:**
- Complete database backup file
- Backup verification report
- Data integrity checksum

---

### Phase 4: Data Import to Self-Hosted (Day 2 Afternoon)

**Objectives:**
- Restore database backup
- Resolve import conflicts
- Validate data integrity

**Actions:**

#### Import Method A: Database Restore (If dump available)
```bash
# On ERP droplet
ssh root@165.227.10.178

# Stop Odoo
systemctl stop odoo16

# Drop and recreate database
su - postgres
psql -c "DROP DATABASE IF EXISTS insightpulse_prod;"
psql -c "CREATE DATABASE insightpulse_prod OWNER odoo16;"

# Restore from dump
pg_restore -d insightpulse_prod /path/to/saas_backup.dump

# Or from SQL dump
psql insightpulse_prod < /path/to/saas_backup.sql

# Restore filestore
cp -r /path/to/filestore/* /opt/odoo16/.local/share/Odoo/filestore/insightpulse_prod/

# Update database UUID (important!)
psql insightpulse_prod -c "UPDATE ir_config_parameter SET value='NEW_UUID' WHERE key='database.uuid';"

# Start Odoo
systemctl start odoo16
```

#### Import Method B: Module-Based Import (If dump unavailable)
```python
# Use Odoo's import wizard
# Settings → Technical → Database Structure → Import

# Or via odoo-bin CLI
./odoo-bin -d insightpulse_prod -i base --load-language=en_US --stop-after-init

# Then import CSVs per model
./odoo-bin shell -d insightpulse_prod <<EOF
import csv
env['res.partner'].load(['name', 'email', 'phone'], [
    ['Customer 1', 'test@example.com', '123456']
])
EOF
```

**Validation Steps:**
1. Check record counts match SaaS
2. Verify user access and permissions
3. Test critical workflows (SO → Invoice → Payment)
4. Validate multi-company data separation
5. Check all attachments restored

**Deliverables:**
- Fully restored database
- Data validation report
- List of any import errors/warnings

---

### Phase 5: Configuration Sync (Day 3 Morning)

**Objectives:**
- Match SaaS configuration exactly
- Sync external integrations
- Configure email/SMS gateways

**Actions:**

1. **System Parameters Sync**
   ```python
   # Compare and sync all ir.config_parameter
   # Settings → Technical → Parameters → System Parameters

   Critical parameters:
   - web.base.url → https://erp.insightpulseai.net
   - mail.catchall.domain → insightpulseai.net
   - mail.default.from → noreply@insightpulseai.net
   - database.uuid → (keep self-hosted UUID)
   ```

2. **Email Configuration**
   ```yaml
   Outgoing Mail Servers:
   - SMTP: (copy from SaaS settings)
   - From: noreply@insightpulseai.net
   - Authentication: OAuth or App Password

   Incoming Mail Servers:
   - IMAP/POP3: (copy from SaaS)
   - Aliases per agency
   ```

3. **External Integrations**
   - Payment gateways (if any)
   - Shipping carriers
   - Banking APIs
   - BIR eFPS integration
   - Slack bridge (new)
   - AI agent (new)

4. **Scheduled Actions (Cron Jobs)**
   ```python
   # Settings → Technical → Automation → Scheduled Actions

   Verify all cron jobs migrated:
   - Email queue processor
   - Invoice auto-send
   - Report generation
   - Data cleanup tasks
   ```

5. **Custom Modules Installation**
   ```bash
   # Install our custom modules
   # Apps → Update Apps List → Search → Install

   - ipai_agent (AI bot with Gradient fallback)
   - slack_bridge (Slack integration)
   ```

**Deliverables:**
- Configuration parity achieved
- All integrations functional
- Custom modules installed

---

### Phase 6: Testing and Validation (Day 3 Afternoon)

**Objectives:**
- Comprehensive workflow testing
- User acceptance testing
- Performance validation

**Test Scenarios:**

1. **Sales Workflow**
   - Create quotation → Send to customer
   - Confirm sale order
   - Create invoice
   - Register payment
   - Validate accounting entries

2. **Purchase Workflow**
   - Create RFQ → Send to vendor
   - Receive products
   - Create vendor bill
   - Register payment

3. **Expense Management**
   - Submit expense
   - Manager approval
   - Accounting validation
   - Payment processing

4. **BIR Compliance**
   - Generate 1601-C report
   - Generate 1702-RT report
   - Export to BIR format
   - Validate calculations

5. **Multi-Agency Testing**
   - Switch companies (agencies)
   - Verify data isolation
   - Test inter-company transactions
   - Check permission boundaries

6. **Integration Testing**
   - Send email from Odoo
   - Slack notifications
   - AI agent queries (@ipai-bot)
   - External API calls

7. **Performance Testing**
   - Dashboard load times
   - Report generation speed
   - Search performance
   - Concurrent user handling

**Test Deliverables:**
- Test execution report
- Bug/issue log (if any)
- Performance benchmarks
- User acceptance sign-off

---

### Phase 7: Go-Live Planning (Day 3 Evening)

**Objectives:**
- Plan cutover window
- Prepare communication
- Set up monitoring

**Cutover Plan:**

1. **Pre-Cutover (1 hour before)**
   - Announce maintenance window to users
   - Take final SaaS backup
   - Sync any last-minute data changes
   - Prepare rollback scripts

2. **Cutover Window (15-30 minutes)**
   ```bash
   # 1. Set SaaS to read-only (or disable)
   # 2. Export final incremental data
   # 3. Import to self-hosted
   # 4. Update DNS (if using custom domain)
   # 5. Enable self-hosted
   # 6. Notify users
   ```

3. **Post-Cutover (1 hour after)**
   - Monitor system logs
   - Check user access
   - Validate critical operations
   - Address immediate issues

**Rollback Plan:**
```yaml
If critical issues within first 24 hours:

1. Revert DNS to SaaS (5 minutes)
2. Re-enable SaaS access
3. Notify users of rollback
4. Investigate and fix issues
5. Reschedule cutover

Rollback window: 24 hours
Rollback decision maker: Jake Tolentino
```

**Communication Plan:**
```
T-7 days: Announce migration to all agencies
T-3 days: Detailed migration timeline
T-1 day: Final reminder and cutover window
T-0: "System in maintenance" message
T+15min: "System live on new platform" message
T+1 day: Check-in and feedback collection
```

---

## Module Parity Matrix

### Core Odoo Modules (Verify Installation)
| Module | SaaS | Self-Hosted | Notes |
|--------|------|-------------|-------|
| Sales Management | ✓ | ⏳ | Install on Day 2 |
| Accounting | ✓ | ⏳ | Configure PH localization |
| Inventory | ✓ | ⏳ | Multi-warehouse setup |
| Purchase | ✓ | ⏳ | Vendor management |
| HR | ✓ | ⏳ | Employee records |
| HR Expenses | ✓ | ⏳ | Expense workflows |
| Invoicing | ✓ | ⏳ | BIR compliance |
| Contacts | ✓ | ⏳ | CRM data |
| Discuss | ✓ | ⏳ | Internal chat |
| Calendar | ✓ | ⏳ | Scheduling |
| Helpdesk | ? | ⏳ | If used on SaaS |
| Project | ? | ⏳ | If used on SaaS |
| Timesheet | ? | ⏳ | If used on SaaS |
| Studio | ? | ❌ | Enterprise only (alternative: custom modules) |

### Custom/Additional Modules
| Module | Purpose | Status |
|--------|---------|--------|
| ipai_agent | AI bot with Gradient API | ✅ Created |
| slack_bridge | Slack integration | ✅ Created |
| l10n_ph_bir | Philippine BIR forms | ⏳ Check if needed |

---

## Data Migration Checklist

### Master Data
- [ ] Companies (8 agencies)
- [ ] Users and permissions
- [ ] Customers and contacts
- [ ] Vendors and suppliers
- [ ] Products and services
- [ ] Chart of accounts
- [ ] Tax configurations
- [ ] Payment terms
- [ ] Fiscal positions

### Transactional Data
- [ ] Sale orders (all statuses)
- [ ] Purchase orders
- [ ] Invoices (customer/vendor)
- [ ] Payments
- [ ] Journal entries
- [ ] Bank statements
- [ ] Inventory moves
- [ ] Expenses (submitted/approved/paid)

### Attachments
- [ ] Invoice PDFs
- [ ] Expense receipts
- [ ] Document uploads
- [ ] Email attachments

### Configuration
- [ ] Email templates
- [ ] Report layouts
- [ ] Dashboard configurations
- [ ] Scheduled actions
- [ ] Webhooks/integrations
- [ ] Access rights and record rules

---

## Risk Assessment and Mitigation

### High Risk: Data Loss
**Mitigation:**
- Multiple backup copies before migration
- Checksum verification of all exports
- Row count validation before/after
- Test restore on staging first

### Medium Risk: Downtime > Expected
**Mitigation:**
- Detailed step-by-step runbook
- Pre-tested import scripts
- Rollback plan ready
- Communication plan prepared

### Medium Risk: Integration Failures
**Mitigation:**
- Test all integrations in staging
- Document all API endpoints
- Prepare fallback procedures
- Keep SaaS active during testing window

### Low Risk: User Adoption
**Mitigation:**
- User training sessions
- Quick reference guides
- Dedicated support during first week
- Slack channel for questions

---

## Success Criteria

### Technical Success
- [ ] 100% data migrated (verified by row counts)
- [ ] All attachments present and accessible
- [ ] All modules functional
- [ ] No critical bugs
- [ ] Performance acceptable (page loads < 3s)
- [ ] All integrations working

### Business Success
- [ ] All agencies can access their data
- [ ] Critical workflows operational (SO → Invoice → Payment)
- [ ] BIR compliance maintained
- [ ] No user complaints about missing data
- [ ] Zero unplanned downtime

### User Acceptance
- [ ] Users can login successfully
- [ ] Users find their historical data
- [ ] Users can complete daily tasks
- [ ] User satisfaction > 80%

---

## Post-Migration Tasks

### Week 1
- Daily monitoring and support
- Address user issues immediately
- Fine-tune performance
- Validate all reports

### Week 2
- Complete integration testing
- Optimize database queries
- Review and optimize cron jobs
- User feedback collection

### Month 1
- Full system audit
- Security review
- Performance optimization
- Documentation completion
- Cancel SaaS subscription (if all good)

---

## Resource Requirements

### Infrastructure
- ✅ ERP Droplet (165.227.10.178) - Already provisioned
- ✅ TLS Certificate - Already configured
- ⏳ Database backup storage (100GB+ recommended)
- ⏳ Staging environment (optional but recommended)

### Tools Needed
- PostgreSQL client (psql)
- Odoo backup/restore tools
- Data validation scripts
- Migration monitoring dashboard

### Personnel
- Migration Lead: Jake Tolentino
- Technical Support: On-call during cutover
- User Support: First week post-migration
- Backup/Rollback Authority: Jake Tolentino

---

## Next Immediate Actions

1. **Confirm SaaS Details** (30 minutes)
   - SaaS instance URL
   - Odoo version
   - Admin access credentials
   - Module list

2. **Create Staging Database** (1 hour)
   - Test migration process end-to-end
   - Validate import procedures
   - Time the migration steps

3. **Schedule Cutover Window** (coordinate with agencies)
   - Proposed: Weekend or off-hours
   - Duration: 2-4 hours
   - Notify all users 1 week in advance

---

## Questions to Answer Before Starting

1. **SaaS Instance Details:**
   - What is the exact SaaS URL?
   - What Odoo version is running?
   - Do you have admin access to Database Manager?
   - Are there any custom developments via Studio?

2. **Data Scope:**
   - How much historical data to migrate? (All time or recent only?)
   - Any data to exclude/archive?
   - Any sensitive data requiring special handling?

3. **Integrations:**
   - What external systems connect to Odoo SaaS?
   - Any payment gateways configured?
   - Any shipping integrations?
   - Banking sync active?

4. **Timeline:**
   - What is your preferred go-live date?
   - Any blackout dates to avoid?
   - What is acceptable downtime window?

5. **Resources:**
   - Need additional server resources?
   - Need staging environment?
   - Budget for migration tools/services?

---

## Contact and Support

**Migration Lead:** Jake Tolentino (jgtolentino_rn@yahoo.com)
**Technical Documentation:** This file + runbooks in `/docs/migration/`
**Emergency Rollback:** See "Rollback Plan" section above
**Status Updates:** Daily during migration week

**Slack Channels:**
- #migration-updates (status and announcements)
- #migration-support (questions and issues)
- #migration-team (internal coordination)

---

**Status:** Ready to begin Phase 1 (Discovery) upon confirmation
**Last Updated:** 2025-11-04
**Document Owner:** Jake Tolentino
