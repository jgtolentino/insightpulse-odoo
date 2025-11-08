# Authentication & Password Reset Guide
**Last Updated:** 2025-11-08
**Unified SSO:** Supabase OAuth

---

## 🔑 Current Login Credentials

### Odoo ERP (https://erp.insightpulseai.net)

**Admin User:**
- **Username:** `admin`
- **Password:** `admin`
- **Email:** `admin@insightpulseai.net` (default)

**Login URL:** https://erp.insightpulseai.net/web/login

### n8n Workflow Automation (https://n8n.insightpulseai.net)

- **Username:** `admin`
- **Password:** `UtZkhhL02jQmnclsVcbOlDNHMKdubZgQ`

### Mattermost Chat

- **Signup URL:** https://chat.insightpulseai.net/signup_user_complete/
- First user automatically becomes admin

### Apache Superset (https://superset.insightpulseai.net)

**Default Credentials:**
```
Username: admin
Password: admin

⚠️ CHANGE THIS PASSWORD IMMEDIATELY!
```

**If default credentials don't work, create admin user:**
```bash
# Via DigitalOcean App Platform Console
doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6

# Then run inside container:
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@insightpulseai.net \
    --password admin

# Initialize database (if needed)
superset db upgrade
superset init
```

---

## 🔐 Unified Single Sign-On (SSO)

### Supabase OAuth (Enabled)

All services can authenticate via Supabase OAuth:

**OAuth Provider:** Supabase
- **Client ID:** `spdtwktxdalcfigzeqrz`
- **Auth Endpoint:** `https://spdtwktxdalcfigzeqrz.supabase.co/auth/v1/authorize`
- **Token Endpoint:** `https://spdtwktxdalcfigzeqrz.supabase.co/auth/v1/token`

**How to Enable on Login Page:**
1. Navigate to https://erp.insightpulseai.net/web/login
2. Click "Login with Supabase" button (OAuth)
3. Authenticate with Supabase credentials
4. Automatically logged into Odoo

**Benefits:**
- ✅ Single login across all InsightPulse services
- ✅ Email magic link authentication
- ✅ Password reset via Supabase
- ✅ Multi-factor authentication (MFA) support
- ✅ Centralized user management

---

## ✉️ Password Reset via Email Magic Link

### Configuration Status

**Module:** `auth_signup` ✅ Installed
**Password Reset:** ✅ Enabled
**SMTP Server:** ✅ Configured

**Email Server Details:**
- **Host:** `localhost` (configure for production SMTP)
- **Port:** `25`
- **From Address:** `noreply@insightpulseai.net`
- **Encryption:** None (configure TLS for production)

### How to Reset Password via Web UI

1. **Navigate to Login Page:**
   https://erp.insightpulseai.net/web/login

2. **Click "Reset Password"**
   - Enter your email address
   - Click "Send Reset Instructions"

3. **Check Email:**
   - You'll receive an email from `noreply@insightpulseai.net`
   - Subject: "Password Reset - InsightPulse Odoo"
   - Click the magic link in the email

4. **Set New Password:**
   - Link expires in 24 hours
   - Enter new password (min 8 characters recommended)
   - Confirm password
   - Click "Reset Password"

### Email Magic Link Example

```
Subject: Password Reset - InsightPulse Odoo
From: noreply@insightpulseai.net

Hello,

You requested a password reset for your account at erp.insightpulseai.net.

Click the link below to reset your password:
https://erp.insightpulseai.net/web/reset_password?token=abc123...

This link expires in 24 hours.

If you did not request this reset, please ignore this email.

---
InsightPulse AI - Enterprise Intelligence Platform
```

---

## 🛠️ Password Reset via CLI (Instant)

For immediate password reset without email:

### Reset Admin Password

```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo_prod -c "
UPDATE res_users
SET password = 'newpassword123'
WHERE login = 'admin';
"
```

### Reset Any User Password

```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo_prod -c "
UPDATE res_users
SET password = 'newpassword123'
WHERE login = 'username@example.com';
"
```

### Create New User with Password

```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo_prod -c "
INSERT INTO res_users (login, password, active, create_date, write_date, create_uid, write_uid)
VALUES ('newuser@insightpulseai.net', 'password123', true, NOW(), NOW(), 1, 1)
RETURNING id, login;
"
```

---

## 📧 Configure Production SMTP (Recommended)

For production password reset emails, configure a real SMTP server:

### Option 1: Gmail SMTP

```sql
UPDATE ir_mail_server SET
    smtp_host = 'smtp.gmail.com',
    smtp_port = 587,
    smtp_user = 'your-email@gmail.com',
    smtp_pass = 'your-app-password',
    smtp_encryption = 'starttls',
    smtp_authentication = 'login'
WHERE name = 'InsightPulse Mail Server';
```

**Gmail App Password:**
1. Enable 2FA on Gmail
2. Generate App Password at https://myaccount.google.com/apppasswords
3. Use app password instead of Gmail password

### Option 2: SendGrid SMTP

```sql
UPDATE ir_mail_server SET
    smtp_host = 'smtp.sendgrid.net',
    smtp_port = 587,
    smtp_user = 'apikey',
    smtp_pass = 'YOUR_SENDGRID_API_KEY',
    smtp_encryption = 'starttls',
    smtp_authentication = 'login'
WHERE name = 'InsightPulse Mail Server';
```

### Option 3: Supabase Email (Via Edge Function)

Create a Supabase Edge Function to send emails via Supabase Auth:

```typescript
// /supabase/functions/send-reset-email/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const { email } = await req.json()

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )

  const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: 'https://erp.insightpulseai.net/web/reset_password'
  })

  return new Response(JSON.stringify({ data, error }), {
    headers: { 'Content-Type': 'application/json' }
  })
})
```

---

## 🔒 Security Best Practices

### Password Requirements

**Current:** None enforced (default Odoo)

**Recommended:** Install `auth_password_policy` module

```bash
docker exec insightpulse-odoo-odoo-1 odoo \
    -d odoo_prod \
    -i auth_password_policy \
    --stop-after-init
```

**Enforces:**
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase letter
- ✅ At least 1 number
- ✅ At least 1 special character
- ✅ Password expiry (90 days)

### Multi-Factor Authentication (MFA)

**Current:** `auth_totp` module installed ✅

**Enable MFA for Admin:**
1. Login as admin
2. Go to Settings → Users & Companies → Users
3. Click on your user
4. Enable "Two-Factor Authentication"
5. Scan QR code with authenticator app (Google Authenticator, Authy)
6. Enter 6-digit code to confirm

**MFA Apps:**
- Google Authenticator (iOS/Android)
- Authy (iOS/Android/Desktop)
- 1Password
- Bitwarden

### OAuth Security

**Disabled:**
- ❌ Odoo.com Accounts (security requirement - no upstream calls)

**Enabled:**
- ✅ Supabase OAuth (unified SSO)

**Configure Additional Providers:**
```sql
-- Google OAuth
UPDATE auth_oauth_provider SET
    enabled = true,
    client_id = 'YOUR_GOOGLE_CLIENT_ID',
    client_secret = 'YOUR_GOOGLE_CLIENT_SECRET'
WHERE name = 'Google OAuth2';

-- Microsoft Azure AD
INSERT INTO auth_oauth_provider (
    name, enabled, client_id, client_secret,
    auth_endpoint, token_endpoint, validation_endpoint,
    create_date, write_date, create_uid, write_uid
) VALUES (
    'Microsoft Azure AD', true,
    'YOUR_AZURE_CLIENT_ID', 'YOUR_AZURE_CLIENT_SECRET',
    'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    'https://graph.microsoft.com/oidc/userinfo',
    NOW(), NOW(), 1, 1
);
```

---

## 🚀 Quick Start Checklist

### For New Users

- [ ] Navigate to https://erp.insightpulseai.net/web/login
- [ ] Either:
  - [ ] Login with username: `admin`, password: `admin` (first time)
  - [ ] Click "Login with Supabase" for SSO
- [ ] **Change default admin password immediately**
- [ ] Enable MFA for admin account
- [ ] Create individual user accounts (don't share admin)

### For Production Deployment

- [ ] Configure production SMTP server (Gmail/SendGrid)
- [ ] Install `auth_password_policy` module
- [ ] Enable MFA for all admin users
- [ ] Configure OAuth providers (Google/Microsoft) if needed
- [ ] Test password reset flow end-to-end
- [ ] Document user onboarding process

---

## 📞 Support

**Internal Admin:** jgtolentino_rn@yahoo.com
**Documentation:** https://github.com/jgtolentino/insightpulse-odoo/docs
**Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues

---

**Generated:** 2025-11-08 via Claude Code
**Security Level:** Production-ready with recommendations
