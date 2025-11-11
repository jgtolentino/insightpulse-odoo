# DNS Configuration Checklist - insightpulseai.com

**Domain:** insightpulseai.com (NOT .net)
**DNS Provider:** [Your DNS provider - e.g., Cloudflare, DigitalOcean, Route53]

---

## Required DNS Records

### 1. MX Records (Mail Routing)
```
Type    Host    Priority    Value               TTL
MX      @       10          mx.zoho.com         3600
MX      @       20          mx2.zoho.com        3600
MX      @       50          mx3.zoho.com        3600
```

### 2. SPF Record (Sender Authentication)
```
Type    Host    Value                                TTL
TXT     @       v=spf1 include:zohomail.com ~all    3600
```

### 3. DKIM Record (Email Signing)
```
Type     Host                      Value                              TTL
CNAME    zselector._domainkey      zselector.domainkey.zoho.com      3600
```
**Note:** Get exact selector from Zoho Admin → Mail → Domains → DKIM

### 4. DMARC Record (Email Policy)
```
Type    Host      Value                                                                           TTL
TXT     _dmarc    v=DMARC1; p=quarantine; rua=mailto:postmaster@insightpulseai.com; ruf=mailto:postmaster@insightpulseai.com; fo=1; pct=100; adkim=s; aspf=s    3600
```

### 5. App Domain A Record (for erp.insightpulseai.net)
```
Type    Host    Value               TTL
A       erp     165.227.10.178      3600
```
**Note:** This goes on insightpulseai.net zone (already configured per screenshot)

---

## Verification Commands

### Check MX Records
```bash
dig +short MX insightpulseai.com
# Expected:
# 10 mx.zoho.com.
# 20 mx2.zoho.com.
# 50 mx3.zoho.com.
```

### Check SPF Record
```bash
dig +short TXT insightpulseai.com | grep v=spf1
# Expected:
# "v=spf1 include:zohomail.com ~all"
```

### Check DKIM Record
```bash
dig +short zselector._domainkey.insightpulseai.com CNAME
# Expected:
# zselector.domainkey.zoho.com.
```

### Check DMARC Record
```bash
dig +short _dmarc.insightpulseai.com TXT
# Expected:
# "v=DMARC1; p=quarantine; rua=mailto:postmaster@insightpulseai.com..."
```

### Check App Domain (erp.insightpulseai.net)
```bash
dig +short erp.insightpulseai.net A
# Expected:
# 165.227.10.178
```

---

## DNS Propagation

After adding records:
- **Local DNS:** 5-30 minutes
- **Global DNS:** Up to 48 hours (typically 1-4 hours)

Check propagation status:
```bash
# Multiple DNS servers
dig @8.8.8.8 MX insightpulseai.com +short
dig @1.1.1.1 MX insightpulseai.com +short
dig @ns1.digitalocean.com MX insightpulseai.com +short
```

Or use: https://dnschecker.org

---

## Zoho Mail Domain Verification

1. Log in to Zoho Mail Admin: https://mailadmin.zoho.com
2. Navigate to: **Domains → insightpulseai.com**
3. Click **Verify Domain**
4. Zoho will check:
   - ✅ MX records point to Zoho
   - ✅ SPF record includes zoho.com
   - ✅ DKIM CNAME configured
5. Status should show: **Domain Verified**

---

## Post-DNS Checklist

- [ ] Add all DNS records to insightpulseai.com zone
- [ ] Wait 30 minutes for propagation
- [ ] Verify records with dig commands
- [ ] Verify domain in Zoho Mail Admin
- [ ] Restart Odoo: `docker compose restart odoo`
- [ ] Test SMTP connection in Odoo UI
- [ ] Send test email
- [ ] Check email headers (SPF/DKIM/DMARC = PASS)
- [ ] Update DMARC policy from `p=quarantine` to `p=reject` (after 1 week)

---

**Status:** ⚠️ PENDING DNS CONFIGURATION
**Next:** Add records → Wait for propagation → Test SMTP → Verify headers
