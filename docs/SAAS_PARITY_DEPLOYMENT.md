# SaaS Parity Deployment Guide

Complete checklist to bring self-hosted Odoo 19 to full parity with official Odoo SaaS.

## Phase 1: Dashboard Consolidation ✅

### 1.1 Uninstall Native Dashboards Module

```bash
# Option A: Via Docker (production)
docker compose exec odoo odoo -d odoo --stop-after-init --uninstall dashboards

# Option B: Via UI
# Navigate to: Apps → Search "Dashboards" → Uninstall
```

### 1.2 Install Superset Menu Integration

```bash
# The module is already in addons/custom/superset_menu/
# Install via UI: Apps → Update Apps List → Search "Superset BI Integration" → Install
```

**Expected Result**:
- Odoo "Dashboards" menu disappears
- New "BI & Analytics" menu appears with 3 sub-items:
  - Sales Dashboard → Opens Superset in new tab
  - Finance Dashboard → Opens Superset in new tab
  - HR Dashboard → Opens Superset in new tab

---

## Phase 2: Module Installation

### 2.1 Already Discovered (Install via UI)

Navigate to: **Apps → Update Apps List → Search → Install**

1. **web_environment_ribbon** (OCA)
   - Shows colored ribbon indicating environment (dev/staging/prod)

2. **web_favicon** (OCA)
   - Custom favicon support for branding

3. **insightpulse_app_sources** (Custom)
   - InsightPulse-specific app integrations

### 2.2 Security & Compliance

4. **auth_totp** (Core Odoo)
   ```bash
   # Install via UI: Apps → Search "Two-Factor Authentication" → Install
   ```
   - Enables 2FA/TOTP for all users
   - Required for: Settings → Users → Enforce 2FA

### 2.3 Reporting & Export

5. **report_xlsx** (OCA)
   ```bash
   # Install via UI: Apps → Search "Excel Export" → Install
   # Or via CLI:
   docker compose exec odoo odoo -d odoo -i report_xlsx --stop-after-init
   ```
   - Excel export capability for reports

6. **server_environment** (OCA)
   ```bash
   # Install via UI: Apps → Search "Server Environment" → Install
   ```
   - Environment-specific configuration management
   - Config file: `config/odoo/server_environment_files.d/`

---

## Phase 3: Email Stack Configuration

### 3.1 Outgoing Mail Servers (SMTP)

**Settings → Technical → Outgoing Mail Servers**

| Field | Value | Notes |
|-------|-------|-------|
| Description | Primary SMTP | |
| SMTP Server | smtp.gmail.com | Or your provider |
| SMTP Port | 587 | TLS |
| Security | STARTTLS | |
| Username | your-email@domain.com | |
| Password | app-specific password | |
| Priority | 10 | Lower = higher priority |

**Test Configuration**: Click "Test Connection" button

### 3.2 Incoming Mail Servers

**Settings → Technical → Incoming Mail Servers**

| Field | Value |
|-------|-------|
| Name | Support Inbox |
| Server Type | IMAP |
| Server | imap.gmail.com |
| Port | 993 |
| SSL/TLS | Yes |
| Username | support@insightpulseai.net |
| Password | app-specific password |

**Fetch Interval**: 5 minutes (default)

### 3.3 Alias Domains

**Settings → Technical → Alias Domains**

Add your domain: `insightpulseai.net`

**Purpose**: Email routing and catch-all support

### 3.4 Email Aliases

**Settings → Technical → Aliases**

Create aliases for key workflows:
- `sales@insightpulseai.net` → Creates leads in CRM
- `support@insightpulseai.net` → Creates helpdesk tickets
- `hr@insightpulseai.net` → Routes to HR department

---

## Phase 4: BI Read-Only User

### 4.1 Create BI User

**Settings → Users → Create**

| Field | Value |
|-------|-------|
| Name | BI_READONLY |
| Login | bi_readonly@insightpulseai.net |
| Password | [Generate strong password] |
| Groups | **Employee** (minimal access) |
| Access Rights | Read-only on all models |

### 4.2 Configure Superset Connection

```python
# Superset Database Connection
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://bi_readonly:password@odoo-db:5432/odoo"

# Connection Extras (JSON)
{
  "engine_params": {
    "pool_size": 5,
    "pool_recycle": 3600
  },
  "metadata_params": {
    "schema": "public"
  }
}
```

### 4.3 RLS Configuration

**Settings → Technical → Record Rules**

Verify company-scoped RLS for BI-exposed models:
- `res.partner` (Contacts)
- `sale.order` (Sales Orders)
- `account.move` (Invoices)
- `hr.employee` (Employees)

**Rule Example**:
```python
[('company_id', 'in', user.company_ids.ids)]
```

---

## Phase 5: Security Hardening

### 5.1 Enable 2FA Enforcement

**Settings → Users**

For each admin user:
1. Edit user
2. Check "Use 2FA (Two-Factor Authentication)"
3. Scan QR code with authenticator app
4. Save

**System-Wide Enforcement** (Optional):
```python
# config/odoo/odoo.conf
[options]
auth_2fa_required = True
```

### 5.2 Session Security

**Settings → Technical → System Parameters**

Add/update:
- `session.timeout`: 1800 (30 minutes)
- `session.timeout_idle`: 900 (15 minutes)
- `session.cookie_httponly`: True
- `session.cookie_secure`: True (HTTPS only)

### 5.3 Password Policy

**Settings → Technical → System Parameters**

Add/update:
- `auth_password_policy.minlength`: 12
- `auth_password_policy.minlower`: 1
- `auth_password_policy.minupper`: 1
- `auth_password_policy.mindigit`: 1
- `auth_password_policy.minsymbol`: 1

---

## Phase 6: Document Branding

### 6.1 Company Settings

**Settings → General Settings → Company**

1. **Logo**: Upload 512x512 PNG with transparent background
2. **Document Layout**: Click "Configure Document Layout"
   - Company Name
   - Company Logo
   - Header Colors: Primary (#0969da), Secondary (#2ea043)
   - Footer: Company address, phone, email

### 6.2 Favicon Configuration

**Requires**: `web_favicon` module installed

1. Navigate to: **Settings → Technical → System Parameters**
2. Add parameter:
   - Key: `web.favicon`
   - Value: `/web/image/res.company/1/favicon`

3. Upload favicon:
   **Settings → Companies → Your Company → Edit**
   - Upload 32x32 or 64x64 ICO/PNG file

### 6.3 Website Configuration (if using Website module)

**Website → Configuration → Settings**

- **Favicon**: Upload same 32x32 ICO/PNG
- **Social Media Preview**: Upload 1200x630 image for social sharing

---

## Phase 7: Validation & Smoke Tests

### 7.1 Module Installation Verification

```bash
# SSH to production server
ssh root@188.166.237.231

# Check installed modules
docker compose -f deploy/odoo.bundle.yml exec odoo \
  odoo shell -d odoo <<EOF
env['ir.module.module'].search([
    ('name', 'in', ['web_environment_ribbon', 'web_favicon',
                     'auth_totp', 'report_xlsx', 'server_environment',
                     'insightpulse_app_sources', 'superset_menu']),
    ('state', '=', 'installed')
]).mapped('name')
EOF
```

**Expected Output**: All 7 modules listed

### 7.2 Email Stack Verification

```bash
# Test outgoing email
# UI: Settings → Technical → Outgoing Mail Servers → Test Connection

# Check incoming mail
# UI: Settings → Technical → Incoming Mail Servers → Fetch Now
```

### 7.3 BI User Access Test

```sql
-- Connect as BI user
psql "postgresql://bi_readonly:password@188.166.237.231:5432/odoo"

-- Test read access
SELECT COUNT(*) FROM res_partner;
SELECT COUNT(*) FROM sale_order;

-- Test write protection (should fail)
INSERT INTO res_partner (name) VALUES ('Test'); -- Should error
```

### 7.4 2FA Login Test

1. Logout from Odoo
2. Login with admin user
3. Enter username/password
4. Should prompt for TOTP code
5. Enter code from authenticator app
6. Successful login

### 7.5 Dashboard Consolidation Test

1. Navigate to top menu
2. Verify "Dashboards" is gone
3. Click "BI & Analytics"
4. Click "Sales Dashboard" → Opens Superset in new tab
5. Verify Superset authentication via Odoo RLS

---

## Phase 8: Infrastructure Documentation

### 8.1 Update Status File

Edit: `infra/status.yaml`

```yaml
components:
  odoo:
    status: "healthy"
    version: "19.0"
    port: 8069
    commit: "<latest-git-sha>"
    deployment: "bundle"
    addons:
      oca:
        status: "ready"
        modules:
          - web_environment_ribbon
          - web_favicon
          - report_xlsx
          - server_environment
      insightpulse:
        status: "ready"
        modules:
          - insightpulse_app_sources
      custom:
        status: "ready"
        modules:
          - superset_menu
        count: 9
  superset:
    status: "healthy"
    port: 8088
    connection: "bi_readonly@odoo:5432/odoo"
    dashboards:
      - sales_main
      - finance_main
      - hr_main
  mindsdb:
    status: "pending"
    note: "Not yet configured"

security:
  2fa: "enabled"
  rls: "enforced"
  password_policy: "strong"
  session_timeout: "30min"

email:
  outgoing_smtp: "configured"
  incoming_imap: "configured"
  aliases: "configured"
  domains: "insightpulseai.net"

ports:
  odoo_http: 8069
  superset_http: 8088
```

### 8.2 Create Release Tag

```bash
# Tag the release
git tag -a v19.0.20251027-parity -m "Odoo 19 SaaS Parity Release

- Dashboard consolidation (Superset integration)
- Security hardening (2FA, RLS, password policy)
- Email stack (SMTP, IMAP, aliases)
- BI read-only user with proper RLS
- Document branding and favicon
- All OCA modules installed and configured"

# Push tag
git push origin v19.0.20251027-parity
```

---

## Post-Deployment Checklist

- [ ] Native Dashboards module uninstalled
- [ ] Superset menu module installed and visible
- [ ] All 6 modules installed: web_environment_ribbon, web_favicon, auth_totp, report_xlsx, server_environment, insightpulse_app_sources
- [ ] SMTP server configured and tested
- [ ] IMAP server configured and fetching mail
- [ ] Email aliases configured for sales/support/hr
- [ ] BI_READONLY user created with read-only access
- [ ] Superset connected to Odoo database via BI user
- [ ] 2FA enabled and enforced for all admin users
- [ ] Session security parameters configured
- [ ] Password policy enforced (12+ chars, mixed case, numbers, symbols)
- [ ] Company logo uploaded
- [ ] Document layout configured
- [ ] Favicon uploaded and visible
- [ ] infra/status.yaml updated
- [ ] Release tagged as v19.0.20251027-parity

---

## Troubleshooting

### Module Installation Fails

**Symptom**: Module shows "uninstalled" after installation attempt

**Fix**:
```bash
# Update module list first
docker compose -f deploy/odoo.bundle.yml exec odoo \
  odoo -d odoo -u base --stop-after-init

# Then install module
docker compose -f deploy/odoo.bundle.yml exec odoo \
  odoo -d odoo -i <module_name> --stop-after-init
```

### Email Sending Fails

**Symptom**: SMTP connection test fails

**Fixes**:
1. Check firewall: Port 587 must be open
2. Verify credentials: Use app-specific password (not account password)
3. Enable "Less Secure Apps" (Gmail legacy) or OAuth2 (recommended)
4. Check logs: `docker compose logs odoo | grep smtp`

### 2FA Not Prompting

**Symptom**: Login doesn't ask for TOTP code

**Fixes**:
1. Verify auth_totp module is installed
2. Check user settings: 2FA checkbox must be enabled
3. Clear browser cookies and cache
4. Verify user has scanned QR code and saved secret

### BI User Cannot Connect

**Symptom**: Superset connection fails with authentication error

**Fixes**:
1. Verify PostgreSQL user exists:
   ```sql
   \du bi_readonly
   ```
2. Grant read permissions:
   ```sql
   GRANT CONNECT ON DATABASE odoo TO bi_readonly;
   GRANT USAGE ON SCHEMA public TO bi_readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi_readonly;
   ```
3. Verify connection string format:
   ```
   postgresql://bi_readonly:password@host:5432/odoo
   ```

### Superset Dashboards Empty

**Symptom**: Dashboards load but show no data

**Fixes**:
1. Verify RLS policies in Odoo
2. Check BI user group assignments
3. Validate Superset dataset queries
4. Check PostgreSQL query logs:
   ```bash
   docker compose logs db | grep "bi_readonly"
   ```

---

## Next Steps

After completing SaaS parity:

1. **Performance Tuning**: Configure PostgreSQL connection pooling (pgBouncer)
2. **Backup Strategy**: Setup automated Supabase backups
3. **Monitoring**: Configure Prometheus metrics and Grafana dashboards
4. **CDN Setup**: Configure DigitalOcean Spaces for static asset delivery
5. **Load Testing**: Validate P95 latency < 200ms under 100 concurrent users
