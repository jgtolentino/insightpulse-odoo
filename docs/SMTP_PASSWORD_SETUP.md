# SMTP Password Setup - Zoho App Password Required

**Status:** ⚠️ Password set, but likely incorrect - Zoho app password needed

---

## Current Status

**SMTP Server:** ✅ Configured
- Host: smtp.zoho.com
- Port: 587
- Encryption: STARTTLS
- Username: business@insightpulseai.com
- Password: ⚠️ **SET** (but may be incorrect)

**Issue:** The password currently set (`Odoo_ipai_26`) appears to be the Odoo admin password, **not** a Zoho app password. SMTP will likely fail until a proper Zoho app password is configured.

---

## Required: Zoho App Password

### Why App Password?

Zoho Mail requires **application-specific passwords** for SMTP authentication when using third-party apps like Odoo. Your regular Zoho account password **will not work** for SMTP.

### How to Generate Zoho App Password

1. **Log in to Zoho Accounts:**
   - URL: https://accounts.zoho.com/

2. **Navigate to Security:**
   - Click your profile icon (top-right)
   - Select "My Account"
   - Go to "Security" tab

3. **Generate App Password:**
   - Scroll to "Application-Specific Passwords"
   - Click "Generate New Password"
   - **Application Name:** `Odoo ERP - InsightPulse AI`
   - Click "Generate"

4. **Copy Password:**
   - Zoho will show a 16-character password
   - **COPY IT IMMEDIATELY** (shown only once!)
   - Example format: `abcd efgh ijkl mnop` (with spaces)

5. **Save Password:**
   - Store in password manager
   - You'll need it for the next step

---

## Setting the App Password in Odoo

### Option 1: Via Odoo UI (Recommended)

1. **Navigate to SMTP Settings:**
   ```
   URL: https://erp.insightpulseai.net/web#menu_id=110&action=135
   Path: Settings → Technical → Email → Outgoing Mail Servers
   ```

2. **Open Configuration:**
   - Click "Zoho SMTP - InsightPulse AI"

3. **Update Password:**
   - Click "Edit"
   - Paste Zoho app password in "Password" field
   - **Remove spaces** from the password (if any)

4. **Test Connection:**
   - Click "Test Connection" button
   - Should show: **"Connection Test Succeeded! Everything seems properly set up!"**

5. **Save:**
   - Click "Save"

### Option 2: Via SSH (Advanced)

```bash
# Set SMTP password (replace YOUR_APP_PASSWORD with actual password)
ssh root@165.227.10.178 "docker exec odoo19_db psql -U odoo -d insightpulse -c \"UPDATE ir_mail_server SET smtp_pass = 'YOUR_APP_PASSWORD' WHERE smtp_host = 'smtp.zoho.com';\""

# Verify password is set
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -c "SELECT name, smtp_host, CASE WHEN smtp_pass IS NOT NULL THEN '\''[SET]'\'' ELSE '\''[NOT SET]'\'' END as password_status FROM ir_mail_server;"'
```

---

## Testing Email Sending

### Via Odoo UI

1. **Navigate to General Settings:**
   ```
   Settings → General Settings
   ```

2. **Scroll to Email Configuration:**
   - Look for "Outgoing Mail Server" section

3. **Send Test Email:**
   - Click "Test Email" or "Send Test Email"
   - Enter your email address
   - Click "Send"

4. **Check Inbox:**
   - Email should arrive within 1-2 minutes
   - **From:** InsightPulse AI <no-reply@insightpulseai.com>
   - Check spam folder if not in inbox

5. **Verify Authentication:**
   - View email headers
   - Should show:
     ```
     spf=pass
     dkim=pass
     dmarc=pass
     ```

### Via Python Script

```bash
# Test SMTP connection
ssh root@165.227.10.178 'docker exec odoo19 python3 -c "
import smtplib
from email.mime.text import MIMEText

# SMTP settings
smtp_server = '\''smtp.zoho.com'\''
smtp_port = 587
smtp_user = '\''business@insightpulseai.com'\''
smtp_pass = '\''YOUR_APP_PASSWORD'\''  # Replace with actual password

# Test connection
print('\''Testing SMTP connection...'\'')
smtp = smtplib.SMTP(smtp_server, smtp_port)
smtp.starttls()
smtp.login(smtp_user, smtp_pass)
print('\''✅ SMTP authentication successful!'\'')

# Send test email
msg = MIMEText('\''This is a test email from InsightPulse AI Odoo ERP.'\'')
msg['\''Subject'\''] = '\''Test Email from Odoo'\'']
msg['\''From'\''] = '\''InsightPulse AI <no-reply@insightpulseai.com>'\''
msg['\''To'\''] = '\''YOUR_EMAIL@example.com'\''  # Replace with your email

smtp.send_message(msg)
print('\''✅ Test email sent successfully!'\'')

smtp.quit()
"'
```

---

## Troubleshooting

### Error: "Connection Test Failed"

**Symptoms:**
```
Connection Test Failed! Here is what we got instead:
(535, b'Authentication failed')
```

**Solutions:**
1. ✅ **Verify app password:** Must be Zoho app password, not regular password
2. ✅ **Remove spaces:** Some password managers add spaces - remove them
3. ✅ **Check username:** Should be `business@insightpulseai.com`
4. ✅ **Verify Zoho account:** Log in to Zoho Mail to ensure account is active

### Error: "Connection refused"

**Symptoms:**
```
[Errno 111] Connection refused
```

**Solutions:**
1. Check firewall rules (port 587 outbound)
2. Verify network connectivity
3. Check if Zoho SMTP is available: `telnet smtp.zoho.com 587`

### Error: "TLS handshake failed"

**Symptoms:**
```
SSL/TLS error during connection
```

**Solutions:**
1. Verify encryption setting: Should be `STARTTLS`
2. Check port: Should be `587` (not 465 or 25)
3. Update SSL certificates: `apt-get update && apt-get install ca-certificates`

---

## Email Delivery Checklist

- [ ] Generate Zoho app password
- [ ] Set app password in Odoo (via UI or SSH)
- [ ] Test SMTP connection → Should succeed
- [ ] Send test email → Should arrive in inbox
- [ ] Verify email headers → SPF/DKIM/DMARC passing
- [ ] Check Odoo mail logs → No errors
- [ ] Configure email templates (optional)

---

## Important Notes

1. **App Password Security:**
   - Store in password manager (1Password, LastPass, etc.)
   - Never commit to git or share publicly
   - Regenerate if compromised

2. **Email Limits:**
   - Zoho Free: 5,000 emails/day
   - Zoho Mail Lite: 10,000 emails/day
   - Zoho Mail Premium: 50,000 emails/day

3. **DMARC Compliance:**
   - Sender must be @insightpulseai.com
   - DNS records already configured
   - Authentication should pass automatically

4. **Monitoring:**
   - Check Odoo mail logs regularly
   - Monitor Zoho Mail admin for delivery issues
   - Review DMARC reports (sent to dmarc@insightpulseai.com)

---

## Quick Commands

```bash
# Check SMTP configuration
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -c "SELECT name, smtp_host, smtp_port, smtp_user, active FROM ir_mail_server;"'

# Check recent email logs
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -c "SELECT subject, email_from, email_to, state, failure_reason, create_date FROM mail_mail ORDER BY create_date DESC LIMIT 10;"'

# Test SMTP connectivity (basic)
ssh root@165.227.10.178 'docker exec odoo19 telnet smtp.zoho.com 587'
```

---

## Resources

- **Zoho App Passwords:** https://accounts.zoho.com/home#security/apppasswords
- **Zoho SMTP Guide:** https://www.zoho.com/mail/help/zoho-smtp.html
- **Odoo Email Configuration:** https://www.odoo.com/documentation/19.0/applications/general/email_communication.html
- **Email Configuration Doc:** [EMAIL_CONFIGURATION.md](EMAIL_CONFIGURATION.md)

---

## Contact

For SMTP configuration help:
- **DevOps:** devops@insightpulseai.com
- **Technical:** support@insightpulseai.com
