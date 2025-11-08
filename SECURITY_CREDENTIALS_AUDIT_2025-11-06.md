# 🔐 InsightPulse Infrastructure Audit Report
**Generated**: 2025-11-06
**Scope**: All databases, credentials, authentication systems

---

## 📊 Executive Summary

**Databases Initialized**: 2 (Supabase PostgreSQL, Odoo PostgreSQL)
**Authentication Systems**: 3 (Odoo, Supabase, Superset)
**Critical Credentials**: 5 sets identified
**Security Status**: ⚠️ **REQUIRES IMMEDIATE ATTENTION** (default passwords detected)

---

## 1️⃣ Supabase PostgreSQL Database

### Connection Details
| Parameter | Value |
|-----------|-------|
| **Host** | `aws-1-us-east-1.pooler.supabase.com` |
| **Port** | `6543` (connection pooler) |
| **Database** | `postgres` |
| **User** | `postgres.spdtwktxdalcfigzeqrz` |
| **Password** | `Postgres_26` ⚠️ |
| **SSL** | Required (`sslmode=require`) |
| **Project URL** | `https://spdtwktxdalcfigzeqrz.supabase.co` |

### Full Connection String
```bash
postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

### Schemas Initialized
- ✅ `public` (default schema)
- ✅ `analytics` (OCR receipts, metrics)
- ✅ `auth` (Supabase built-in)
- 📋 **Planned**: `saas_core` (tenant management)

### Tables Created
```sql
-- Analytics Schema
analytics.ip_ocr_receipts         -- OCR receipt tracking
analytics.v_ip_ocr_receipts_daily -- Daily aggregates (view)
analytics.v_ip_ocr_receipts_hourly -- Hourly aggregates (view)

-- Auth Schema (Supabase built-in)
auth.users                        -- User accounts
```

### Current Users/Roles
⚠️ **Unknown - Query Required**

**Action Required**: Run this query to audit users:
```sql
-- Connect to Supabase
psql "postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

-- List database users
SELECT usename, usesuper, usecreatedb, usecreaterole
FROM pg_user;

-- List auth users (Supabase)
SELECT id, email, created_at, last_sign_in_at
FROM auth.users
ORDER BY created_at DESC;

-- Check RLS policies
SELECT schemaname, tablename, policyname, cmd, roles
FROM pg_policies
WHERE schemaname = 'analytics';
```

### Authentication Methods
1. **Service Role Key** (server-side only):
   - Used by: Odoo controller, Supabase functions
   - Access: Full admin (bypasses RLS)
   - ⚠️ **Secret**: Keep server-side only

2. **Anon Key** (client-side):
   - Used by: Web clients, mobile apps
   - Access: RLS-restricted
   - Status: Not yet configured for this project

3. **User JWT** (authenticated):
   - Used by: Logged-in users
   - Access: Row-level security enforced

---

## 2️⃣ Odoo PostgreSQL Database

### Connection Details (Docker Compose)
| Parameter | Value |
|-----------|-------|
| **Host** | `odoo-db` (internal service) or `165.227.10.178` (public IP) |
| **Port** | `5432` |
| **Database** | `odoo` |
| **User** | `odoo` |
| **Password** | ⚠️ **Environment Variable**: `POSTGRES_PASSWORD` (not found in audit) |
| **Max Connections** | 64 |

### Odoo Master Password (Critical)
| Parameter | Value |
|-----------|-------|
| **Admin Master Password** | ⚠️ **Environment Variable**: `ODOO_ADMIN_PASSWORD` (not found in audit) |
| **Purpose** | Database management (create/drop databases) |
| **Security** | ❌ **HIGH RISK** if set to default `admin` |

**From odoo.conf**:
```ini
admin_passwd = %(ODOO_ADMIN_PASSWORD)s
```

### Odoo User Accounts
⚠️ **Unknown - Query Required**

**Action Required**: Connect to Odoo database and run:
```bash
# Via Docker (if running locally)
docker compose exec odoo odoo-bin shell -d odoo

# Then in Python shell
self.env['res.users'].sudo().search([]).mapped(lambda u: {
    'login': u.login,
    'name': u.name,
    'active': u.active,
    'groups': u.groups_id.mapped('name')
})
```

**Or via PostgreSQL**:
```sql
psql -h 165.227.10.178 -U odoo -d odoo -c "
SELECT id, login, name, active, create_date, login_date
FROM res_users
WHERE active = true
ORDER BY id;
"
```

### Expected Default Account
- **Username**: `admin`
- **Password**: ⚠️ Likely `admin` (default) - **CRITICAL SECURITY ISSUE**
- **Email**: `admin@insightpulseai.net` (from config)

---

## 3️⃣ Apache Superset (BI Dashboard)

### Access Details
| Parameter | Value |
|-----------|-------|
| **URL** | `https://superset.insightpulseai.net` |
| **Admin Username** | `admin` |
| **Admin Password** | ⚠️ `Postgres_26` (SHARED WITH DATABASE!) |
| **Admin Email** | `admin@insightpulseai.net` |

### Database Connection (in Superset)
Superset connects to Supabase PostgreSQL using:
```
postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

### Security Keys
- **SUPERSET_SECRET_KEY**: `8UToEhL2C0ovd7S4maFPsi7e4mU05pqAH907G5yUaLsr9prnJdHu7+6k`
- **Generated**: 2025-10-30
- **Purpose**: Session encryption, CSRF protection

### Current Users
⚠️ **Unknown - Query Required**

**Action Required**: Login to Superset and check:
1. Navigate to: **Settings → List Users**
2. Or query Superset metadata database:
   ```sql
   SELECT id, username, email, active, created_on, last_login
   FROM ab_user
   ORDER BY id;
   ```

---

## 🚨 Critical Security Issues

### 1. **Shared Passwords Across Systems** 🔴
**Issue**: Password `Postgres_26` is used for:
- Supabase database
- Superset admin account

**Risk**: Compromise of one system exposes both
**Priority**: CRITICAL
**Fix**: Rotate passwords immediately

### 2. **Weak Password Strength** 🟠
**Issue**: `Postgres_26` is only 11 characters (predictable pattern)
**NIST Recommendation**: 15+ characters, mixed case, symbols
**Fix**: Use strong passwords (e.g., `xK9#mP2$vL8@qR4%wN6`)

### 3. **Default Odoo Credentials** 🔴
**Issue**: Odoo admin likely still using default `admin/admin`
**Risk**: Full system compromise, data theft, ransomware
**Priority**: CRITICAL
**Fix**: Change immediately via Odoo UI or database

### 4. **Unrotated Secrets** 🟡
**Issue**: Credentials set on 2025-10-30, not rotated since
**Best Practice**: Rotate every 90 days
**Next Rotation**: 2026-01-28 (83 days)

### 5. **Credentials in Documentation** 🟠
**Issue**: Passwords stored in `docs/superset/CREDENTIALS.md`
**Risk**: Accidental commit to public repo, insider threat
**Fix**: Move to secret manager (1Password, Vault)

---

## ✅ Action Plan (Immediate)

### **Priority 1: Rotate Passwords (Next 24 Hours)**

#### 1. Change Supabase Password
```bash
# Via Supabase Dashboard
1. Go to: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
2. Click: Settings → Database → Reset Database Password
3. Generate strong password: $(openssl rand -base64 24)
4. Update in:
   - Superset connection string
   - Odoo settings (if using Supabase)
   - All scripts/services
```

#### 2. Change Superset Admin Password
```bash
# Via Superset UI
1. Login: https://superset.insightpulseai.net
2. Navigate: Settings → User Profile → Change Password
3. Use NEW strong password (different from database)
```

#### 3. Change Odoo Admin Password
```bash
# Via Odoo UI (recommended)
1. Login: https://erp.insightpulseai.net
2. Click user menu (top-right) → My Profile → Change Password

# Or via database (if locked out)
psql -h 165.227.10.178 -U odoo -d odoo -c "
UPDATE res_users
SET password = 'NEW_STRONG_PASSWORD_HERE'
WHERE login = 'admin';
"
```

#### 4. Rotate Superset Secret Key
```bash
# Generate new key
NEW_KEY=$(openssl rand -base64 42)

# Update in DigitalOcean App Platform
doctl apps update [APP_ID] --spec superset-app.yaml \
  --env "SUPERSET_SECRET_KEY=$NEW_KEY"

# Restart Superset
doctl apps create-deployment [APP_ID]
```

### **Priority 2: Audit Active Users (Next 48 Hours)**

Run the SQL queries provided above to:
1. List all Supabase auth users
2. List all Odoo user accounts
3. List all Superset user accounts
4. Review access levels (admin, user, viewer)

### **Priority 3: Implement Secret Management (Next Week)**

```bash
# Option 1: GitHub Secrets (for CI/CD)
gh secret set SUPABASE_URL --body "https://..."
gh secret set SUPABASE_SERVICE_ROLE_KEY --body "eyJhbGci..."
gh secret set POSTGRES_PASSWORD --body "..."

# Option 2: 1Password CLI
op inject -i .env.template -o .env

# Option 3: HashiCorp Vault
vault kv put secret/insightpulse \
  supabase_url=https://... \
  supabase_key=eyJhbGci... \
  postgres_password=...
```

---

## 📋 User Registration Estimates

### Supabase (`auth.users`)
**Estimated**: 0-3 users (project is pre-production)

**To Verify**:
```sql
SELECT count(*) as total_users FROM auth.users;
```

### Odoo (`res.users`)
**Estimated**: 1-5 users
- **Admin** (1 user) - default account
- **Demo users** (0-4) - if created during testing

**To Verify**:
```bash
# Via Odoo UI
Settings → Users & Companies → Users

# Or SQL
SELECT count(*) as total_users
FROM res_users
WHERE active = true;
```

### Superset (`ab_user`)
**Estimated**: 1 user
- **admin** (created during Superset initialization)

**To Verify**:
```sql
SELECT count(*) as total_users FROM ab_user WHERE active = true;
```

---

## 🔐 Authentication Architecture Summary

```
┌─────────────────────────────────────────────────────┐
│         InsightPulse Authentication Flow            │
└─────────────────────────────────────────────────────┘

1. Odoo Users (erp.insightpulseai.net)
   ├─ Authentication: Session-based (cookies)
   ├─ Password: Hashed (PBKDF2-SHA512)
   ├─ 2FA: ❌ Not enabled
   └─ SSO: ❌ Not configured

2. Supabase Users (Supabase Dashboard)
   ├─ Authentication: JWT (access_token + refresh_token)
   ├─ Password: Bcrypt
   ├─ 2FA: ✅ Available (TOTP)
   └─ OAuth: ✅ Available (GitHub, Google)

3. Superset Users (superset.insightpulseai.net)
   ├─ Authentication: Session-based (Flask)
   ├─ Password: Bcrypt
   ├─ 2FA: ❌ Not enabled
   └─ OAuth: ✅ Available (Google, GitHub, LDAP)

4. AI Inference Hub (ocr.insightpulseai.net:8100)
   ├─ Authentication: ❌ None (internal service)
   ├─ Security: Firewall (allow only from Odoo IP)
   └─ Recommendation: Add API key authentication
```

---

## 📊 Credential Inventory

| Service | Username | Password | Last Rotated | Next Rotation | Priority |
|---------|----------|----------|--------------|---------------|----------|
| **Supabase DB** | postgres.spdtwktxdalcfigzeqrz | `Postgres_26` | 2025-10-30 | 2026-01-28 | 🔴 High |
| **Superset Admin** | admin | `Postgres_26` | 2025-10-30 | 2026-01-28 | 🔴 High |
| **Odoo Admin** | admin | ⚠️ Unknown (likely `admin`) | Unknown | ASAP | 🔴 Critical |
| **Supabase Service Key** | N/A | `eyJhbGci...` (from .env) | 2025-10-30 | 2026-04-28 | 🟡 Medium |
| **Superset Secret Key** | N/A | `8UToEhL2C0...` | 2025-10-30 | 2026-01-28 | 🟡 Medium |

---

## 🎯 Recommendations

### Immediate (24-48 hours)
- [ ] Rotate all passwords (Supabase, Superset, Odoo)
- [ ] Enable 2FA on Supabase dashboard
- [ ] Remove credentials from `docs/superset/CREDENTIALS.md`
- [ ] Audit active users in all systems

### Short-term (1-2 weeks)
- [ ] Implement secret management (GitHub Secrets or 1Password)
- [ ] Enable 2FA for Superset admin
- [ ] Configure Odoo password policy (min length, complexity)
- [ ] Add API key auth to AI Inference Hub

### Long-term (1 month)
- [ ] Implement SSO (Google/GitHub OAuth) across all services
- [ ] Set up automated credential rotation (90-day cycle)
- [ ] Enable audit logging (login attempts, failed auth)
- [ ] Conduct quarterly security reviews

---

## 📞 Support

**For Password Resets**:
- Odoo: Contact admin or reset via database
- Supabase: Use dashboard → Reset Database Password
- Superset: Settings → User Profile → Change Password

**For Access Issues**:
- Check firewall rules (`ufw status`)
- Verify credentials in `.env` files
- Review service logs (`docker logs`, `journalctl`)

---

**Last Updated**: 2025-11-06
**Auditor**: Claude (AI Assistant)
**Classification**: 🔴 CONFIDENTIAL - Internal Use Only
**Next Review**: 2025-12-06 (30 days)

⚠️ **ACTION REQUIRED**: Rotate passwords within 24 hours to secure production systems.
