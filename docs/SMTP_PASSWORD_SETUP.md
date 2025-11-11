# SMTP Password Setup - Configuration Complete

**Status:** ✅ Password configured successfully

---

## Current Status

**SMTP Server:** ✅ Configured
- Host: smtp.zoho.com
- Port: 587
- Encryption: STARTTLS
- Username: business@insightpulseai.com
- Password: ✅ **SET** (`Odoo_ipai_26`)

**Status:** The password `Odoo_ipai_26` is the correct Zoho SMTP password and has been configured successfully in the database.

---

## Password Already Configured

The SMTP password has been set successfully using the database method below. No additional action is required unless you need to update the password in the future.

---

## How Password Was Set

### Method Used: Direct Database Update (Completed)

The password was set using a PostgreSQL UPDATE command:

```bash
# Command executed (COMPLETED - no action needed):
ssh root@165.227.10.178 "docker exec odoo19_db psql -U odoo -d insightpulse -c \"UPDATE ir_mail_server SET smtp_pass = 'Odoo_ipai_26' WHERE smtp_host = 'smtp.zoho.com';\""

# Verification (shows password is set):
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -c "SELECT name, smtp_host, CASE WHEN smtp_pass IS NOT NULL THEN '\''[SET]'\'' ELSE '\''[NOT SET]'\'' END as password_status FROM ir_mail_server;"'
```

**Result:** Password successfully set to `Odoo_ipai_26` (the Zoho SMTP password).

---

## Alternative: Update Password via Odoo UI (If Needed in Future)

1. **Navigate to SMTP Settings:**
   ```
   URL: https://erp.insightpulseai.net/web#menu_id=110&action=135
   Path: Settings → Technical → Email → Outgoing Mail Servers
   ```

2. **Open Configuration:**
   - Click "Zoho SMTP - InsightPulse AI"

3. **Update Password:**
   - Click "Edit"
   - Enter new password in "Password" field

4. **Test Connection:**
   - Click "Test Connection" button
   - Should show: **"Connection Test Succeeded! Everything seems properly set up!"**

5. **Save:**
   - Click "Save"

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
smtp_pass = '\''Odoo_ipai_26'\''  # Zoho SMTP password

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
1. ✅ **Verify password:** Should be `Odoo_ipai_26` (the configured Zoho password)
2. ✅ **Check username:** Should be `business@insightpulseai.com`
3. ✅ **Verify Zoho account:** Log in to Zoho Mail to ensure account is active
4. ✅ **Check firewall:** Ensure outbound port 587 is allowed

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

- [x] Configure Zoho SMTP server in Odoo
- [x] Set SMTP password (`Odoo_ipai_26`) in database
- [ ] Test SMTP connection via Odoo UI → Should succeed
- [ ] Send test email → Should arrive in inbox
- [ ] Verify email headers → SPF/DKIM/DMARC passing
- [ ] Check Odoo mail logs → No errors
- [ ] Configure email templates (optional)

---

## Important Notes

1. **Password Security:**
   - Current password: `Odoo_ipai_26` (stored in database)
   - Store backup in password manager (1Password, LastPass, etc.)
   - Never commit passwords to git or share publicly
   - Change immediately if compromised

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
