# DNS Audit Report - InsightPulse Odoo Infrastructure

**Date**: 2025-11-11
**Audited By**: Claude Code
**Scope**: All DNS records, domain configurations, and SSL/TLS settings

---

## Executive Summary

### Domain Overview
- **Primary Domain**: insightpulseai.net
- **DNS Provider**: DigitalOcean
- **SSL/TLS**: Let's Encrypt (via DigitalOcean & Nginx)
- **Total Subdomains**: 8 configured
- **Status**: ⚠️ **Issues Identified** (see Critical Issues section)

### Critical Issues Found
1. ❌ **Missing DNS Records**: Only erp.insightpulseai.net has DNS records, other subdomains not configured
2. ⚠️ **Domain Mismatch**: DigitalOcean apps have domains configured but no corresponding DNS records
3. ⚠️ **Orphaned Nginx Configs**: Multiple Nginx configs for domains without DNS records

---

## DNS Configuration Audit

### DigitalOcean DNS Records

#### erp.insightpulseai.net (Configured ✅)

| Record Type | Name | Value | TTL |
|-------------|------|-------|-----|
| SOA | @ | ns1.digitalocean.com | 1800 |
| NS | @ | ns1.digitalocean.com | 1800 |
| NS | @ | ns2.digitalocean.com | 1800 |
| NS | @ | ns3.digitalocean.com | 1800 |
| A | @ | 165.227.10.178 | 3600 |

**Status**: ✅ Active
**IP Address**: 165.227.10.178
**Services**: Odoo ERP

#### Missing DNS Records ❌

The following subdomains have Nginx configurations or app specs but **no DNS records**:

1. **superset.insightpulseai.net** ❌
   - App ID: 73af11cb-dab2-4cb1-9770-291c536531e6
   - Default Ingress: https://superset-nlavf.ondigitalocean.app
   - Nginx Config: `infra/nginx/superset.insightpulseai.net.conf`
   - **Issue**: Domain configured in app spec but no DNS record

2. **mcp.insightpulseai.net** ❌
   - App ID: 844b0bb2-0208-4694-bf86-12e750b7f790
   - Default Ingress: https://pulse-hub-web-an645.ondigitalocean.app
   - Spec: `infra/do/mcp-coordinator.yaml`
   - **Issue**: Domain configured in app spec but no DNS record

3. **agent.insightpulseai.net** ❌
   - Proxy: https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run
   - Nginx Config: `infra/nginx/agent.insightpulseai.net.conf`
   - **Issue**: Nginx config exists but no DNS record

4. **chat.insightpulseai.net** ❌
   - Service: Mattermost (port 8065)
   - Nginx Configs: `chat.conf`, `chat.insightpulseai.net.conf`
   - **Issue**: Nginx config exists but no DNS record

5. **n8n.insightpulseai.net** ❌
   - Service: n8n Workflow Automation (port 5678)
   - Nginx Config: `infra/nginx/n8n.conf`
   - **Issue**: Nginx config exists but no DNS record

6. **ocr.insightpulseai.net** ❌
   - Service: OCR Backend (port 8080)
   - Nginx Config: `infra/nginx/ocr.insightpulseai.net.conf`
   - **Issue**: Nginx config exists but no DNS record

7. **gittodoc.insightpulseai.net** ❌
   - Service: Git to Docs (port 8099)
   - Nginx Config: `infra/nginx/gittodoc.insightpulseai.net.conf`
   - **Issue**: Nginx config exists but no DNS record

8. **www.insightpulseai.net** ❌
   - Nginx Config: `infra/nginx/insightpulseai.net.conf`
   - **Issue**: www subdomain configured but no DNS record

---

## DigitalOcean App Platform Configuration

### Active Apps

#### 1. odoo-saas-platform
- **App ID**: 04de4372-7a4f-472a-9c3f-5deb895b7ad2
- **Spec**: `infra/do/odoo-saas-platform.yaml`
- **Default Ingress**: None configured
- **Custom Domain**: ❓ Not specified in spec
- **Status**: ⚠️ No domain configuration

#### 2. superset-analytics
- **App ID**: 73af11cb-dab2-4cb1-9770-291c536531e6
- **Spec**: `infra/do/superset.yaml`
- **Default Ingress**: https://superset-nlavf.ondigitalocean.app
- **Custom Domain**: superset.insightpulseai.net (configured in spec)
- **DNS Status**: ❌ No DNS record
- **Issue**: Domain in spec but not in DNS

#### 3. mcp-coordinator
- **App ID**: 844b0bb2-0208-4694-bf86-12e750b7f790
- **Spec**: `infra/do/mcp-coordinator.yaml`
- **Default Ingress**: https://pulse-hub-web-an645.ondigitalocean.app
- **Custom Domain**: mcp.insightpulseai.net (configured in spec)
- **DNS Status**: ❌ No DNS record
- **Issue**: Domain in spec but not in DNS

---

## Nginx Reverse Proxy Configuration

### Configured Subdomains

| Subdomain | Backend | Port | SSL | Status |
|-----------|---------|------|-----|--------|
| erp.insightpulseai.net | Odoo | 8069 | ✅ | ✅ Active |
| superset.insightpulseai.net | DO App | N/A | ✅ | ❌ No DNS |
| agent.insightpulseai.net | DO Agent | N/A | ✅ | ❌ No DNS |
| chat.insightpulseai.net | Mattermost | 8065 | ✅ | ❌ No DNS |
| n8n.insightpulseai.net | n8n | 5678 | ✅ | ❌ No DNS |
| ocr.insightpulseai.net | OCR Backend | 8080 | ✅ | ❌ No DNS |
| gittodoc.insightpulseai.net | GitToDoc | 8099 | ✅ | ❌ No DNS |
| insightpulseai.net | Root | N/A | ✅ | ❓ Unknown |

### Proxy Backends

```
erp.insightpulseai.net → http://127.0.0.1:8069 (Odoo)
superset.insightpulseai.net → https://superset-nlavf.ondigitalocean.app
agent.insightpulseai.net → https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run
chat.insightpulseai.net → http://127.0.0.1:8065 (Mattermost)
n8n.insightpulseai.net → http://localhost:5678 (n8n)
ocr.insightpulseai.net → http://127.0.0.1:8080 (OCR)
gittodoc.insightpulseai.net → http://127.0.0.1:8099 (GitToDoc)
```

---

## SSL/TLS Certificate Status

### Let's Encrypt Configuration

All Nginx configurations include SSL/TLS with:
- Listen on port 443 with `ssl http2`
- Automatic HTTP to HTTPS redirect (port 80 → 443)
- SSL certificate paths configured

**Certificate Paths** (standard Let's Encrypt):
```
ssl_certificate /etc/letsencrypt/live/insightpulseai.net/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/insightpulseai.net/privkey.pem;
```

**Status**: ✅ Configured for all subdomains in Nginx

**Issue**: ⚠️ Certificates can only be issued after DNS records are created

---

## Critical Issues & Recommendations

### 🔴 Critical Issues

#### 1. Missing DNS Records for Active Services

**Impact**: Services are inaccessible via custom domains

**Affected Domains**:
- superset.insightpulseai.net
- mcp.insightpulseai.net
- agent.insightpulseai.net
- chat.insightpulseai.net
- n8n.insightpulseai.net
- ocr.insightpulseai.net
- gittodoc.insightpulseai.net

**Recommended Actions**:

1. **Create DNS Records in DigitalOcean**:
```bash
# For DigitalOcean App Platform services (CNAME)
doctl compute domain records create insightpulseai.net \
  --record-type CNAME \
  --record-name superset \
  --record-data superset-nlavf.ondigitalocean.app \
  --record-ttl 3600

doctl compute domain records create insightpulseai.net \
  --record-type CNAME \
  --record-name mcp \
  --record-data pulse-hub-web-an645.ondigitalocean.app \
  --record-ttl 3600

# For local services (A record pointing to server IP)
doctl compute domain records create insightpulseai.net \
  --record-type A \
  --record-name chat \
  --record-data 165.227.10.178 \
  --record-ttl 3600

doctl compute domain records create insightpulseai.net \
  --record-type A \
  --record-name n8n \
  --record-data 165.227.10.178 \
  --record-ttl 3600

doctl compute domain records create insightpulseai.net \
  --record-type A \
  --record-name ocr \
  --record-data 165.227.10.178 \
  --record-ttl 3600

doctl compute domain records create insightpulseai.net \
  --record-type A \
  --record-name gittodoc \
  --record-data 165.227.10.178 \
  --record-ttl 3600
```

2. **For DO Agent (CNAME to external service)**:
```bash
doctl compute domain records create insightpulseai.net \
  --record-type CNAME \
  --record-name agent \
  --record-data wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run \
  --record-ttl 3600
```

#### 2. Root Domain Configuration

**Issue**: No DNS records for bare domain (insightpulseai.net) or www subdomain

**Recommended Actions**:
```bash
# Create A record for bare domain
doctl compute domain records create insightpulseai.net \
  --record-type A \
  --record-name @ \
  --record-data 165.227.10.178 \
  --record-ttl 3600

# Create CNAME for www subdomain
doctl compute domain records create insightpulseai.net \
  --record-type CNAME \
  --record-name www \
  --record-data insightpulseai.net \
  --record-ttl 3600
```

#### 3. SSL Certificate Issuance

**Issue**: Certificates cannot be issued until DNS records are created

**Recommended Actions** (after DNS records are created):
```bash
# On Nginx server, issue certificates for all subdomains
sudo certbot --nginx -d insightpulseai.net \
  -d www.insightpulseai.net \
  -d erp.insightpulseai.net \
  -d superset.insightpulseai.net \
  -d mcp.insightpulseai.net \
  -d agent.insightpulseai.net \
  -d chat.insightpulseai.net \
  -d n8n.insightpulseai.net \
  -d ocr.insightpulseai.net \
  -d gittodoc.insightpulseai.net
```

### 🟡 Medium Priority Issues

#### 1. Inconsistent Domain Configuration

**Issue**: Domain configured in DigitalOcean App Platform but not in DigitalOcean DNS

**Affected Apps**:
- superset-analytics (superset.insightpulseai.net)
- mcp-coordinator (mcp.insightpulseai.net)

**Recommended Action**: Create DNS records first, then update app specs

#### 2. Multiple Nginx Configuration Files

**Issue**: Some services have multiple config files (e.g., chat.conf and chat.insightpulseai.net.conf)

**Recommended Action**: Consolidate to single config per service

### 🟢 Low Priority Issues

#### 1. TTL Optimization

**Current**: Mixed TTLs (1800s for NS, 3600s for A)

**Recommended**: Standardize to 3600s (1 hour) for all records

#### 2. DNS Monitoring

**Recommended**: Implement DNS monitoring for all subdomains

---

## Recommended DNS Architecture

### Production DNS Setup

```
insightpulseai.net
├── @ (A)           → 165.227.10.178 (Nginx server)
├── www (CNAME)     → insightpulseai.net
├── erp (A)         → 165.227.10.178 ✅ Configured
├── chat (A)        → 165.227.10.178 ❌ Missing
├── n8n (A)         → 165.227.10.178 ❌ Missing
├── ocr (A)         → 165.227.10.178 ❌ Missing
├── gittodoc (A)    → 165.227.10.178 ❌ Missing
├── superset (CNAME) → superset-nlavf.ondigitalocean.app ❌ Missing
├── mcp (CNAME)      → pulse-hub-web-an645.ondigitalocean.app ❌ Missing
└── agent (CNAME)    → wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run ❌ Missing
```

---

## Implementation Plan

### Phase 1: Create Missing DNS Records (Immediate)

```bash
# Script: scripts/setup-dns-records.sh
./scripts/setup-dns-records.sh
```

Expected time: 15 minutes
Propagation time: 30-60 minutes

### Phase 2: Issue SSL Certificates (After DNS propagation)

```bash
# Script: scripts/issue-ssl-certificates.sh
./scripts/issue-ssl-certificates.sh
```

Expected time: 10 minutes

### Phase 3: Verify and Test (After SSL issuance)

```bash
# Test all subdomains
./scripts/test-dns-endpoints.sh
```

Expected time: 15 minutes

### Phase 4: Update Documentation (Ongoing)

- Update README.md with correct URLs
- Update deployment guides
- Add DNS monitoring

---

## DNS Monitoring Recommendations

### Health Checks

Implement DNS health checks for:
- DNS resolution (all subdomains)
- SSL certificate validity
- HTTP/HTTPS accessibility
- Proxy backend health

### Monitoring Tools

- **UptimeRobot**: Free monitoring for up to 50 endpoints
- **DigitalOcean Monitoring**: App Platform health checks
- **Certbot**: Automatic SSL renewal (already configured)

### Alert Thresholds

- DNS resolution failure: Immediate alert
- SSL expiration: 7 days before expiry
- HTTP 5xx errors: After 3 consecutive failures
- Response time: >5 seconds for 3 consecutive checks

---

## Appendix

### A. DNS Record Templates

#### CNAME Record Template
```bash
doctl compute domain records create insightpulseai.net \
  --record-type CNAME \
  --record-name <subdomain> \
  --record-data <target> \
  --record-ttl 3600
```

#### A Record Template
```bash
doctl compute domain records create insightpulseai.net \
  --record-type A \
  --record-name <subdomain> \
  --record-data 165.227.10.178 \
  --record-ttl 3600
```

### B. Nginx Virtual Host Template

See: `infra/nginx/template.conf`

### C. Let's Encrypt Certbot Command

```bash
sudo certbot --nginx \
  -d <domain> \
  --non-interactive \
  --agree-tos \
  --email admin@insightpulseai.net
```

### D. DNS Verification Commands

```bash
# Check DNS resolution
dig <subdomain>.insightpulseai.net

# Check DNS propagation
nslookup <subdomain>.insightpulseai.net 8.8.8.8

# Check SSL certificate
openssl s_client -connect <subdomain>.insightpulseai.net:443 -servername <subdomain>.insightpulseai.net
```

---

**Report Generated**: 2025-11-11
**Next Review**: 2025-12-11 (Monthly)
**Status**: ⚠️ **Action Required**
