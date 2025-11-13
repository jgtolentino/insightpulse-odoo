# SMTP Configuration Guide - Zoho Mail

**Last Updated:** 2025-11-12
**For:** InsightPulse Odoo 18 CE Production Deployment

---

## Overview

This guide walks through configuring Zoho Mail SMTP for outgoing emails in Odoo 18 CE. The SMTP server is already configured in the database with placeholder credentials - you just need to update the password with a Zoho App Password.

## Critical Domain Architecture

**IMPORTANT:** Email and app domains are separate for security and deliverability:

- **Email Domain:** `insightpulseai.com` (mail sending/receiving via Zoho)
- **App Domain:** `insightpulseai.net` (Odoo ERP, Keycloak, Superset, etc.)

**Why Separate?**
- Better email deliverability (dedicated mail domain)
- Cleaner DNS records (MX/SPF/DKIM on .com only)
- Security isolation (email reputation separate from apps)
- BIR compliance (professional @insightpulseai.com addresses)

**Email Flow:**
```
Odoo ERP (erp.insightpulseai.net)
    ↓ SMTP
Zoho Mail (smtp.zoho.com:587)
    ↓ Send as
no-reply@insightpulseai.com
```

## Prerequisites

- ✅ Odoo 18 CE installed and running
- ✅ Database `db_ckvc` initialized
- ✅ SMTP server record created (via production hardening script)
- ⚠️ **Need:** Zoho App Password (see Configuration Steps below)
- ⚠️ **Need:** DNS records configured on insightpulseai.com (see DNS Configuration below)

---

## DNS Configuration (insightpulseai.com)

**⚠️ CRITICAL:** Add these records to **insightpulseai.com** DNS zone (NOT .net):

### MX Records (Mail Routing)
```
Record Type    Host    Priority    Value
MX             @       10          mx.zoho.com
MX             @       20          mx2.zoho.com
MX             @       50          mx3.zoho.com
```

### SPF Record (Sender Authentication)
```
Record Type    Host    Value
TXT            @       v=spf1 include:zohomail.com ~all
```

### DKIM Record (Email Signing)
```
Record Type                          Host    Value
CNAME                                zselector._domainkey    zselector.domainkey.zoho.com
```
**Note:** Copy exact selector/value from Zoho Admin → Mail → Domains → DKIM

### DMARC Record (Email Policy)
```
Record Type    Host     Value
TXT            _dmarc   v=DMARC1; p=quarantine; rua=mailto:postmaster@insightpulseai.com; ruf=mailto:postmaster@insightpulseai.com; fo=1; pct=100; adkim=s; aspf=s
```
**Production:** Change `p=quarantine` to `p=reject` after confirming SPF/DKIM pass

### DNS Verification Commands
```bash
# MX Records
dig +short MX insightpulseai.com

# SPF Record
dig +short TXT insightpulseai.com | grep v=spf1

# DKIM Record (replace 'zselector' with your actual selector)
dig +short zselector._domainkey.insightpulseai.com CNAME

# DMARC Record
dig +short _dmarc.insightpulseai.com TXT
```

**Expected Output:**
```
# MX
10 mx.zoho.com.
20 mx2.zoho.com.
50 mx3.zoho.com.

# SPF
"v=spf1 include:zohomail.com ~all"

# DKIM
zselector.domainkey.zoho.com.

# DMARC
"v=DMARC1; p=quarantine; rua=mailto:postmaster@insightpulseai.com..."
```

---

## Configuration Steps

### Step 1: Generate Zoho App Password

**CRITICAL SECURITY NOTE:** Never use your main Zoho Mail password. Always use app-specific passwords.

1. Log in to Zoho Mail admin console
2. Navigate to: **Mail Settings → Security → App Passwords**
3. Click **Generate New Password**
4. Name it: `Odoo_ipai_26` (or similar descriptive name)
5. Copy the generated password (you won't see it again)
6. Store securely in password manager

**Reference:** https://mail.zoho.com/zm/#settings/security

### Step 2: Update SMTP Password in Odoo

**Via Odoo Web UI (RECOMMENDED):**

1. Log in to Odoo: https://erp.insightpulseai.net
2. Navigate to: **Settings → Technical → Email → Outgoing Mail Servers**
3. Open: **InsightPulse SMTP**
4. Update fields:
   - **Password:** Paste Zoho App Password from Step 1
   - **SMTP Authentication:** login (already set)
   - **Connection Security:** STARTTLS (already set)
5. Click **Test Connection** to verify
6. Click **Save**

**Expected Success Message:**
```
Connection Test Succeeded!
Everything seems properly set up!
```

### Step 3: Configure Odoo System Parameters

**CRITICAL:** Set email domain parameters to ensure Odoo sends as @insightpulseai.com:

1. Navigate to: **Settings → Technical → Parameters → System Parameters**
2. Update/create these parameters:

| Parameter Key | Value | Purpose |
|---------------|-------|---------|
| `mail.catchall.domain` | `insightpulseai.com` | Default email domain |
| `mail.default.from` | `no-reply@insightpulseai.com` | Default FROM address |
| `mail.force.smtp` | `True` | Force SMTP for all outgoing mail |
| `web.base.url` | `https://erp.insightpulseai.net` | Already set (app domain) |
| `report.url` | `https://erp.insightpulseai.net` | PDF report links (optional) |

**Via Database (Alternative):**
```bash
docker compose exec -T postgres psql -U odoo -d db_ckvc << 'SQL'
DELETE FROM ir_config_parameter WHERE key IN ('mail.catchall.domain', 'mail.default.from', 'mail.force.smtp');
INSERT INTO ir_config_parameter (key, value) VALUES
  ('mail.catchall.domain', 'insightpulseai.com'),
  ('mail.default.from', 'no-reply@insightpulseai.com'),
  ('mail.force.smtp', 'True');
SQL
```

**Restart Odoo** to apply changes:
```bash
docker compose restart odoo
```

### Step 4: Verify Email Configuration

#### Test SMTP Connection
1. Settings → Technical → Email → Outgoing Mail Servers → InsightPulse SMTP
2. Click **Test Connection**
3. Expected: "Connection Test Succeeded!"

#### Send Test Email
1. Settings → Technical → Email → Send an Email
2. To: your-email@domain.com
3. Subject: "Odoo SMTP Test"
4. Click **Send**

#### Verify Email Headers
Check received email headers for authentication:
```
SPF: PASS (with IP ...)
DKIM: PASS (signature verified)
DMARC: PASS
From: no-reply@insightpulseai.com
Reply-To: no-reply@insightpulseai.com
Mailed-By: zoho.com
Signed-By: insightpulseai.com
```

**Gmail:** View Original → Check for "SPF=pass", "DKIM=pass", "DMARC=pass"

### Current SMTP Configuration

**Pre-configured values** (via SQL insert during production hardening):

```
Server Name:    InsightPulse SMTP
Host:           smtppro.zoho.com
Port:           587
Encryption:     STARTTLS (TLS)
Authentication: login
Username:       no-reply@insightpulseai.com
Password:       [PLACEHOLDER - UPDATE IN UI]
Priority:       10 (default)
Active:         Yes
```

### Zoho Mail Server Details

**Reference from Zoho Mail Settings:**

| Protocol | Server              | Port | Security | Auth Required |
|----------|---------------------|------|----------|---------------|
| SMTP     | smtppro.zoho.com    | 587  | TLS      | Yes           |
| SMTP SSL | smtppro.zoho.com    | 465  | SSL      | Yes           |
| IMAP     | imappro.zoho.com    | 993  | SSL      | Yes           |
| POP      | poppro.zoho.com     | 995  | SSL      | Yes           |

**We use:** Port 587 with STARTTLS (most compatible)

### Troubleshooting

#### Test Connection Fails

**Error:** `Authentication failed`

**Fix:**
- Verify you're using Zoho App Password (not main password)
- Check username is full email: `no-reply@insightpulseai.com`
- Verify domain MX records point to Zoho

**Error:** `Connection refused` or `Timeout`

**Fix:**
- Check firewall allows outbound port 587
- Verify Docker network can reach external SMTP
- Try port 465 with SSL instead of 587 with TLS

#### Emails Not Received

**Check:**
1. Spam/junk folder
2. Zoho Mail → Mail Logs for delivery status
3. Odoo → Settings → Technical → Email → Emails to verify send status

#### View SMTP Logs

**In Docker:**
```bash
docker compose logs odoo | grep -i smtp
docker compose logs odoo | grep -i mail
```

### Security Best Practices

✅ **DO:**
- Use Zoho App Passwords (never main password)
- Rotate App Passwords every 90 days
- Use different App Passwords per service
- Store passwords in password manager
- Use STARTTLS (port 587) for best compatibility

❌ **DON'T:**
- Commit passwords to git
- Use main Zoho password
- Share App Passwords across services
- Send passwords via email/chat
- Use plain SMTP (port 25) without encryption

### Domain Configuration (For Reference)

**MX Records** (already configured):
```
Record Type    Host    Priority    Value
MX             @       10          mx.zoho.com
MX             @       20          mx2.zoho.com
MX             @       50          mx3.zoho.com
```

**SPF Record** (for email validation):
```
Record Type    Host    Value
TXT            @       v=spf1 include:zohomail.com ~all
```

**DKIM/DMARC:** Configure in Zoho Mail → Domains → Email Configuration for better deliverability

---

## Quick Reference

**Odoo SMTP Record Location:**
```
Settings → Technical → Email → Outgoing Mail Servers → InsightPulse SMTP
```

**Zoho App Password Generation:**
```
Zoho Mail → Mail Settings → Security → App Passwords → Generate New Password
```

**Test Connection Command (Alternative - CLI):**
```bash
docker compose exec -T postgres psql -U odoo -d db_ckvc -c \
  "SELECT name, smtp_host, smtp_port, smtp_user, smtp_encryption, smtp_authentication
   FROM ir_mail_server WHERE name='InsightPulse SMTP';"
```

---

## Related Documentation

- [Production Release Status](MODULE_STATUS.md)
- [Odoo Email Documentation](https://www.odoo.com/documentation/18.0/applications/general/email_communication.html)
- [Zoho Mail SMTP Setup](https://www.zoho.com/mail/help/smtp-configuration.html)

---

**Maintained by:** InsightPulse AI DevOps Team
**Last Review:** 2025-11-12
**Next Review:** Before production deployment
