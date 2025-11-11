# Email Configuration - InsightPulse AI Odoo

**Last Updated:** 2025-11-12
**Status:** ✅ Configured (Password required via UI)

---

## Overview

InsightPulse AI uses **Zoho Mail** for all outgoing email with the domain **@insightpulseai.com**. The ERP runs at **erp.insightpulseai.net** but all mail uses the **.com** domain for DMARC/SPF/DKIM alignment.

---

## Current Configuration

### System Parameters (✅ Configured)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `web.base.url` | `https://erp.insightpulseai.net` | ERP base URL for links in emails |
| `mail.catchall.domain` | `insightpulseai.com` | Domain for catch-all aliases |
| `mail.catchall.alias` | `support` | Alias for incoming mail (support@insightpulseai.com) |
| `mail.default.from` | `"InsightPulse AI" <no-reply@insightpulseai.com>` | Default sender address |
| `mail.bounce.alias` | `bounce` | Bounce handling (bounce@insightpulseai.com) |

### SMTP Server (✅ Configured - Password Required)

| Setting | Value |
|---------|-------|
| **Name** | Zoho SMTP - InsightPulse AI |
| **Host** | smtp.zoho.com |
| **Port** | 587 |
| **Encryption** | STARTTLS (TLS) |
| **Username** | business@insightpulseai.com |
| **Password** | ⚠️ **Required via UI** |
| **Priority** | 1 (highest) |
| **Status** | ✅ Active |

---

## Complete Email Setup

### Step 1: Set Zoho SMTP Password

1. **Navigate to SMTP Settings:**
   - URL: https://erp.insightpulseai.net/web#menu_id=110&action=135
   - Or: Settings → Technical → Email → Outgoing Mail Servers

2. **Open Configuration:**
   - Click "Zoho SMTP - InsightPulse AI"

3. **Enter Zoho App Password:**
   - Get app password from Zoho Mail Admin
   - **NOT** your regular Zoho login password
   - Generate at: https://accounts.zoho.com/home#security/apppasswords

4. **Test Connection:**
   - Click "Test Connection" button
   - Should show: "Connection Test Succeeded!"

5. **Save:**
   - Click "Save" button

### Step 2: Verify DNS Records (Already Configured)

**Domain:** insightpulseai.com

**Required DNS Records:**

```dns
# SPF (TXT @ or root)
v=spf1 include:zoho.com ~all

# DKIM (TXT zohomail._domainkey)
[Value from Zoho Mail Admin → Domains → DKIM]

# DMARC (TXT _dmarc)
v=DMARC1; p=quarantine; adkim=s; aspf=s; rua=mailto:dmarc@insightpulseai.com
```

**Verification:**
```bash
# Check SPF
dig +short TXT insightpulseai.com | grep spf

# Check DKIM
dig +short TXT zohomail._domainkey.insightpulseai.com

# Check DMARC
dig +short TXT _dmarc.insightpulseai.com
```

### Step 3: Test Email Sending

1. **Navigate to General Settings:**
   - Settings → General Settings

2. **Scroll to "Email Servers"**

3. **Click "Test Email":**
   - Enter your email address
   - Click "Send Test Email"

4. **Verify Receipt:**
   - Check inbox (including spam folder)
   - Verify "From" shows: InsightPulse AI <no-reply@insightpulseai.com>
   - Check headers for: `spf=pass dkim=pass dmarc=pass`

---

## Email Addresses

### Active Mailboxes (Zoho)

| Address | Purpose | Type |
|---------|---------|------|
| business@insightpulseai.com | SMTP sender, business inquiries | Mailbox |
| ceo@insightpulseai.com | Executive communications | Mailbox |
| devops@insightpulseai.com | Technical operations, alerts | Mailbox |
| support@insightpulseai.com | Customer support, help desk | Mailbox/Alias |
| no-reply@insightpulseai.com | System notifications | Alias → business@ |
| bounce@insightpulseai.com | Bounce handling | Alias → devops@ |
| dmarc@insightpulseai.com | DMARC reports | Alias → devops@ |

### Recommended Aliases (To Configure)

| Alias | Forward To | Purpose |
|-------|-----------|---------|
| admin@insightpulseai.com | devops@ | System administration |
| noreply@insightpulseai.com | business@ | Alternative no-reply |
| help@insightpulseai.com | support@ | Alternative support |
| info@insightpulseai.com | business@ | General inquiries |

---

## Email Templates

### Default From Addresses

All Odoo email templates should use:

```python
# Default sender
From: "InsightPulse AI" <no-reply@insightpulseai.com>

# Reply-to (for actual replies)
Reply-To: support@insightpulseai.com

# Example template modification
{
    'email_from': '"InsightPulse AI" <no-reply@insightpulseai.com>',
    'reply_to': 'support@insightpulseai.com',
}
```

### Key Templates to Update

1. **Password Reset:**
   - Module: `auth_signup`
   - Template: `reset_password`
   - Current: Should use system default
   - Update: Ensure "From" is no-reply@insightpulseai.com

2. **User Invitation:**
   - Module: `mail`
   - Template: `mail_notification_paynow`
   - Update: Set Reply-To: support@insightpulseai.com

3. **Invoice Emails:**
   - Module: `account`
   - Template: `email_template_edi_invoice`
   - Update: Reply-To: business@insightpulseai.com

---

## Troubleshooting

### Issue: Test Connection Fails

**Error:** "Connection Test Failed! Here is what we got instead: [Errno 111] Connection refused"

**Solutions:**
1. Check SMTP credentials (especially app password)
2. Verify network connectivity from server
3. Check firewall rules (port 587 outbound)
4. Verify Zoho service status

**Debug Commands:**
```bash
# Test SMTP connectivity
ssh root@165.227.10.178 'docker exec odoo19 python3 -c "
import smtplib
smtp = smtplib.SMTP('\''smtp.zoho.com'\'', 587)
smtp.starttls()
print('\''Connection successful!'\'')
smtp.quit()
"'

# Check DNS resolution
ssh root@165.227.10.178 'docker exec odoo19 nslookup smtp.zoho.com'
```

### Issue: DMARC Failures

**Error:** Emails marked as spam or rejected

**Solutions:**
1. Verify SPF record: `v=spf1 include:zoho.com ~all`
2. Verify DKIM configured in Zoho Admin
3. Check DMARC policy: `p=quarantine` or `p=none` for testing
4. Use mail-tester.com to check email authentication

**Verification:**
```bash
# Send test email to check-auth@verifier.port25.com
# Or use: https://www.mail-tester.com/
```

### Issue: Wrong "From" Address

**Problem:** Emails showing wrong sender

**Solution:**
1. Check `mail.default.from` parameter
2. Update email templates
3. Clear Odoo cache: Restart Odoo container
4. Check company settings: Settings → Users & Companies → Companies

---

## Monitoring

### Email Delivery Logs

**Odoo UI:**
- Settings → Technical → Email → Mail Logs
- Filter by state: sent, exception, bounced

**Database Query:**
```sql
-- Recent emails
SELECT
    id,
    subject,
    email_from,
    email_to,
    state,
    failure_reason,
    create_date
FROM mail_mail
ORDER BY create_date DESC
LIMIT 50;

-- Failed emails
SELECT
    subject,
    email_to,
    failure_reason,
    create_date
FROM mail_mail
WHERE state = 'exception'
ORDER BY create_date DESC;
```

### DMARC Reports

**Configure in Zoho:**
1. Add email alias: dmarc@insightpulseai.com → devops@insightpulseai.com
2. Receive aggregate reports (daily)
3. Review for authentication failures

**Report Location:**
- Forwarded to: devops@insightpulseai.com
- Subject: "Report Domain: insightpulseai.com"

---

## Production Checklist

- [x] System parameters configured (mail.catchall.domain, mail.default.from, etc.)
- [x] Zoho SMTP server created and configured
- [ ] **CRITICAL:** SMTP password set via Odoo UI
- [ ] Test connection successful
- [ ] Test email sent and received
- [ ] DNS records verified (SPF, DKIM, DMARC)
- [ ] Email headers show authentication passing
- [ ] DMARC reports configured and monitored
- [ ] Email templates updated with correct From/Reply-To
- [ ] Alias forwarding configured in Zoho

---

## Quick Commands

```bash
# Check email configuration
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -c "SELECT key, value FROM ir_config_parameter WHERE key LIKE '\''mail%'\'' ORDER BY key;"'

# Check SMTP server configuration
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -c "SELECT name, smtp_host, smtp_port, smtp_encryption, smtp_user, active FROM ir_mail_server ORDER BY sequence;"'

# Check recent email logs
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -c "SELECT subject, email_from, email_to, state, create_date FROM mail_mail ORDER BY create_date DESC LIMIT 10;"'

# Test SMTP connectivity
ssh root@165.227.10.178 'docker exec odoo19 python3 -c "import smtplib; smtp = smtplib.SMTP('\''smtp.zoho.com'\'', 587); smtp.starttls(); print('\''OK'\''); smtp.quit()"'
```

---

## Resources

- **Zoho Mail Admin:** https://mailadmin.zoho.com/
- **App Password Generator:** https://accounts.zoho.com/home#security/apppasswords
- **Odoo Email Documentation:** https://www.odoo.com/documentation/19.0/applications/general/email_communication.html
- **SPF/DKIM/DMARC Guide:** https://www.zoho.com/mail/help/adminconsole/domain-authentication.html
- **Mail Tester:** https://www.mail-tester.com/

---

## Contact

For email configuration issues:
- **Technical:** devops@insightpulseai.com
- **Business:** business@insightpulseai.com
- **Support:** support@insightpulseai.com
