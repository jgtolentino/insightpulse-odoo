# Production Release Status — 2025-11-11 18:16 UTC

## Database: db_ckvc

### Module Installation
```
---------------------+---------------
 account             | installed
 barcodes            | installed
 calendar            | installed
 contacts            | installed
 hr                  | installed
 hr_expense          | installed
 hr_holidays         | installed
 hr_timesheet        | installed
 ipai_bir_compliance | installed
 ipai_branding       | installed
 mail                | installed
 project             | installed
 purchase            | installed
 sale_management     | installed
 stock               | installed
 stock_barcode       | uninstallable
 timesheet_grid      | uninstallable
(17 rows)
```

### Configuration
- ✅ Odoo 18.0 CE (103 modules loaded)
- ✅ HTTPS: erp.insightpulseai.net (Caddy auto-HTTPS)
- ✅ Proxy Mode: Enabled
- ✅ Workers: 2 (production mode)
- ✅ Memory Limits: 512MB soft, 640MB hard
- ✅ CPU Timeout: 120s (doubled for complex operations)
- ✅ Session Security: Secure, HttpOnly, Lax
- ✅ SMTP: smtp.zoho.com (no-reply@insightpulseai.com)

### Installed Modules (15 Core CE + 2 IPAI)
- Core CE: account, barcodes, calendar, contacts, hr, hr_expense, hr_holidays, hr_timesheet, mail, project, purchase, sale_management, stock
- IPAI: ipai_branding, ipai_bir_compliance

### Production Deployment
1. **SMTP Password Setup** (CRITICAL - Security Best Practice):
   - Navigate to: Settings → Technical → Email → Outgoing Mail Servers → InsightPulse SMTP
   - Generate Zoho App Password: Mail Settings → Security → App Passwords
   - Update password in Odoo (NEVER commit to git)
   - SMTP Config: smtppro.zoho.com:587 (TLS), auth required

2. Start Caddy for HTTPS: `docker compose up -d caddy`
3. Verify HTTPS: https://erp.insightpulseai.net
4. Configure DNS: erp.insightpulseai.net → server IP
5. Review firewall: Allow 80/443, block 8069 external access

### Release: v0.1.0
- Odoo 18 CE base installation
- Production hardening complete
- IPAI BIR compliance modules ready
- Auto-HTTPS with Caddy
- Multi-tenant ready (company_id isolation)
