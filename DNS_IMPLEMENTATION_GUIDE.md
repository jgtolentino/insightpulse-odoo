# DNS Implementation Guide - InsightPulse Odoo

**Status**: Ready for execution
**Date**: 2025-11-11
**Purpose**: Step-by-step guide to configure all missing DNS records and SSL certificates

---

## Overview

This guide provides the complete workflow to configure DNS records, issue SSL certificates, and verify all endpoints for the InsightPulse Odoo infrastructure.

**Current Status**:
- ✅ DNS audit completed
- ✅ Automation scripts created
- ❌ DNS records not yet created (8 missing)
- ❌ SSL certificates not yet issued
- ❌ Endpoints not accessible

---

## Prerequisites

- DigitalOcean account with `doctl` authenticated
- Access to Nginx server (165.227.10.178)
- Root/sudo access for SSL certificate issuance
- Certbot installed on Nginx server

---

## Phase 1: Create DNS Records (15 minutes)

### 1.1 Test with Dry Run

```bash
cd /path/to/insightpulse-odoo
./scripts/setup-dns-records.sh --dry-run
```

**What this does**:
- Shows what DNS records will be created
- Does NOT make any changes
- Validates doctl authentication

**Expected output**:
```
🌐 Setting up DNS records for insightpulseai.net
🔍 DRY RUN MODE - No changes will be made

DNS Records to be created:
==========================

1. Root domain (A record)
[DRY RUN] Would create: A @.insightpulseai.net → 165.227.10.178 (TTL: 3600)

... (8 more records)

✅ Dry run complete
Review the records above and run without --dry-run to create them
```

### 1.2 Create DNS Records

```bash
./scripts/setup-dns-records.sh
```

**What this creates**:
1. Root domain: `insightpulseai.net` (A → 165.227.10.178)
2. WWW: `www.insightpulseai.net` (CNAME → insightpulseai.net)
3. Local services (A records → 165.227.10.178):
   - chat.insightpulseai.net (Mattermost)
   - n8n.insightpulseai.net (n8n Automation)
   - ocr.insightpulseai.net (OCR Backend)
   - gittodoc.insightpulseai.net (Git to Docs)
4. DigitalOcean App Platform (CNAME):
   - superset.insightpulseai.net → superset-nlavf.ondigitalocean.app
   - mcp.insightpulseai.net → pulse-hub-web-an645.ondigitalocean.app
5. DO Gradient AI Agent (CNAME):
   - agent.insightpulseai.net → wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

**Expected duration**: ~2 minutes

### 1.3 Verify DNS Records Created

```bash
doctl compute domain records list insightpulseai.net --format Type,Name,Data,TTL
```

**Expected output**: 8+ DNS records listed

---

## Phase 2: Wait for DNS Propagation (30-60 minutes)

DNS changes take time to propagate globally. **Do not proceed to Phase 3 until DNS has propagated.**

### 2.1 Check DNS Propagation

```bash
# Check specific subdomain
dig @8.8.8.8 superset.insightpulseai.net

# Check all subdomains
for subdomain in superset mcp agent chat n8n ocr gittodoc; do
  echo "Checking $subdomain.insightpulseai.net"
  dig +short @8.8.8.8 "$subdomain.insightpulseai.net"
  echo ""
done
```

**Ready when**: All subdomains return valid responses (A record IP or CNAME target)

---

## Phase 3: Issue SSL Certificates (10 minutes)

**Run on Nginx server (165.227.10.178)**

### 3.1 Test with Dry Run

```bash
# SSH to Nginx server
ssh root@165.227.10.178

# Navigate to repo
cd /path/to/insightpulse-odoo

# Test certificate issuance
sudo ./scripts/issue-ssl-certificates.sh --dry-run
```

**What this does**:
- Checks DNS propagation
- Tests Certbot configuration
- Does NOT issue real certificates
- Validates Nginx configs

**Expected output**:
```
🔐 Issuing SSL certificates for insightpulseai.net
🔍 Checking DNS propagation...
✅ DNS propagation verified

🔍 DRY RUN MODE - Testing certificate issuance
... (certbot dry run output)

✅ Dry run successful
Run without --dry-run to issue real certificates
```

### 3.2 Issue SSL Certificates

```bash
sudo ./scripts/issue-ssl-certificates.sh
```

**What this does**:
- Issues Let's Encrypt certificates for all 10 subdomains
- Configures Nginx for HTTPS
- Sets up auto-renewal
- Enables HTTP to HTTPS redirect

**Expected duration**: ~5 minutes

### 3.3 Verify SSL Certificates

```bash
# List certificates
sudo certbot certificates

# Check auto-renewal
sudo systemctl status certbot.timer
```

**Expected output**: Certificate for insightpulseai.net covering all subdomains

---

## Phase 4: Test All Endpoints (5 minutes)

### 4.1 Run Endpoint Tests

```bash
# Can run from any machine
./scripts/test-dns-endpoints.sh
```

**What this tests**:
1. DNS resolution (all subdomains)
2. HTTP/HTTPS endpoint accessibility
3. SSL certificate validity
4. Service-specific content checks

**Expected output**:
```
🧪 Testing DNS endpoints for insightpulseai.net

═════════════════════════════════════
DNS Resolution Tests
═════════════════════════════════════

DNS Check: insightpulseai.net (A)
  ✅ Resolved: 165.227.10.178

... (more DNS tests)

═════════════════════════════════════
HTTP/HTTPS Endpoint Tests
═════════════════════════════════════

Testing: Root Domain
  URL: https://insightpulseai.net
  ✅ HTTP 200
  ✅ SSL valid

... (more endpoint tests)

═════════════════════════════════════
Test Summary
═════════════════════════════════════

Total Tests: 20
✅ Passed: 20
⚠️  Warnings: 0
❌ Failed: 0

🎉 All tests passed!
```

---

## Troubleshooting

### DNS Records Not Propagating

**Symptom**: `dig` returns no results after 30 minutes

**Solutions**:
1. Check DigitalOcean dashboard: https://cloud.digitalocean.com/networking/domains/insightpulseai.net
2. Verify records created: `doctl compute domain records list insightpulseai.net`
3. Check DNS from multiple locations: https://www.whatsmydns.net/

### SSL Certificate Issuance Failed

**Symptom**: Certbot fails with "Challenge failed"

**Solutions**:
1. Verify DNS propagation: `dig @8.8.8.8 [subdomain]`
2. Check Nginx config: `sudo nginx -t`
3. Check port 80/443 accessible: `nc -zv 165.227.10.178 80 443`
4. Review Nginx logs: `sudo tail -f /var/log/nginx/error.log`

### Endpoint Tests Failing

**Symptom**: HTTP 502 or 503 errors

**Solutions**:
1. Check service health:
   ```bash
   # Odoo
   curl https://erp.insightpulseai.net

   # Superset
   curl https://superset.insightpulseai.net

   # OCR
   curl https://ocr.insightpulseai.net/health
   ```

2. Check Nginx upstream configs:
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

3. Check backend services:
   ```bash
   # DigitalOcean apps
   doctl apps list

   # Local services
   docker ps
   systemctl status mattermost
   systemctl status n8n
   ```

---

## Post-Implementation

### 1. Update Documentation

Update the following files with new URLs:
- README.md (access URLs)
- docs/INFRASTRUCTURE_ARCHITECTURE.md (endpoint list)
- .github/workflows/*.yml (base URLs for testing)

### 2. Setup Monitoring

Configure uptime monitoring for:
- https://erp.insightpulseai.net
- https://superset.insightpulseai.net
- https://mcp.insightpulseai.net
- https://agent.insightpulseai.net

**Recommended tools**:
- UptimeRobot (free for 50 monitors)
- DigitalOcean Monitoring (built-in)

### 3. SSL Certificate Monitoring

Monitor certificate expiry:
```bash
# Check expiry dates
sudo certbot certificates

# Test auto-renewal
sudo certbot renew --dry-run
```

Let's Encrypt certificates auto-renew via `certbot.timer` systemd service.

---

## Next Steps

After successful implementation:

1. ✅ All services accessible via custom domains
2. ✅ SSL/TLS enabled for all endpoints
3. ✅ HTTP to HTTPS redirect working
4. ✅ Auto-renewal configured

**Future enhancements**:
- Setup CDN (Cloudflare or DigitalOcean CDN)
- Configure WAF (Web Application Firewall)
- Implement rate limiting
- Add DDoS protection

---

## Quick Reference

**Scripts**:
- `scripts/setup-dns-records.sh` - Create DNS records
- `scripts/issue-ssl-certificates.sh` - Issue SSL certificates
- `scripts/test-dns-endpoints.sh` - Test all endpoints

**Documentation**:
- `docs/DNS_AUDIT_REPORT.md` - Complete DNS audit findings
- `DNS_IMPLEMENTATION_GUIDE.md` - This file

**Support**:
- DigitalOcean Support: https://cloud.digitalocean.com/support
- Let's Encrypt Docs: https://letsencrypt.org/docs/
- Nginx Docs: https://nginx.org/en/docs/

---

**Status**: Ready for Phase 1 execution
**Next Action**: Run `./scripts/setup-dns-records.sh --dry-run`
