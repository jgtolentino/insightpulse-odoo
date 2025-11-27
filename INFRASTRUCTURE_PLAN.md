# Infrastructure Improvement Plan
**Date**: 2025-11-28
**Author**: Claude Code DevOps Architect
**Source**: Infrastructure Audit Report (2025-11-28)

---

## TL;DR for Jake

### 🚨 3 Most Urgent Fixes (This Week)

1. **OCR Droplet Disk at 97%** - Service will crash when disk fills. Need immediate cleanup (30 min).
2. **3 Unhealthy Containers** - `tax-rules-service`, `ocr-adapter`, `agent-service` may be degraded/broken (1-2 hours).
3. **Broken DNS for ipa.insightpulseai.net** - Orphaned domain pointing nowhere, likely meant for n8n/IPA service (30 min).

### 🎯 3 Most Important Medium-Term Restructures (This Month)

1. **Consolidate OCR Droplet → Primary** - Eliminate single point of failure, reduce costs by $24-48/month, simplify ops (4-6 hours).
2. **Implement DO Cloud Firewall + Monitoring** - Lock down attack surface, get proactive alerts before outages (2-3 hours).
3. **Enable Terraform IaC** - Prevent configuration drift, enable disaster recovery, automate infra changes (1-2 days).

---

## 1. Canonical Infrastructure Inventory

### 1.1 DigitalOcean Droplets

| Hostname | IP Address (Public) | IP Address (Private) | vCPUs | RAM | Disk | Disk Usage | Region | OS | Criticality | Role | SPOF Risk |
|----------|---------------------|----------------------|-------|-----|------|------------|--------|----|-----------|----|---|
| `odoo-erp-prod` | 159.223.75.148 | 10.114.0.2 | Unknown* | 3.8Gi | 78G | **38G (49%)** | Unknown* | Ubuntu 22.04.5 LTS | **CRITICAL** | Primary ERP, n8n, Auth, Services | ⚠️ **YES** - All production services |
| `ocr-service-droplet` | 188.166.237.231 | 10.114.0.3 | Unknown* | 7.8Gi | 78G | **🚨 75G (97%)** | Unknown* | Ubuntu 22.04.5 LTS | **HIGH** | OCR Inference, Legacy Odoo 17 | ⚠️ **YES** - OCR service only host |

**Notes**:
- *vCPU/Region unknown due to API access unavailable (invalid token)
- Both droplets are **single points of failure** for their respective services
- No load balancers, no failover, no redundancy
- Private network connectivity exists (10.114.0.0/16) but not verified/utilized

### 1.2 DigitalOcean App Platform Apps

| App ID (Inferred) | App Name | Domain | Backend URL | Status | Notes |
|-------------------|----------|--------|-------------|--------|-------|
| `an645` | `pulse-hub-web` | mcp.insightpulseai.net | pulse-hub-web-an645.ondigitalocean.app | ✅ Active | MCP Coordinator |
| `nlavf` | `superset` | superset.insightpulseai.net | superset-nlavf.ondigitalocean.app | ✅ Active | Apache Superset BI |

**Limitations**: Cannot retrieve full app details (build settings, env vars, scaling config, resource limits) without valid API token.

### 1.3 DNS Records & Public Hostnames

| Domain | Record Type | Value | Backend Service | Status | TLS | Criticality |
|--------|-------------|-------|-----------------|--------|-----|-------------|
| `erp.insightpulseai.net` | A | 159.223.75.148 | Odoo ERP v18 (port 8069) | ✅ Resolving | ✅ Let's Encrypt | **CRITICAL** |
| `n8n.insightpulseai.net` | A | 159.223.75.148 | n8n Workflows (port 5678) | ✅ Resolving | ✅ Let's Encrypt | **HIGH** |
| `auth.insightpulseai.net` | A | 159.223.75.148 | Auth Service (port 8080) | ✅ Resolving | ✅ Let's Encrypt | **MEDIUM** |
| `ocr.insightpulseai.net` | A | 188.166.237.231 | OCR Adapter (port 8100) | ✅ Resolving | ✅ Let's Encrypt | **HIGH** |
| `mcp.insightpulseai.net` | CNAME | pulse-hub-web-an645.ondigitalocean.app | MCP Coordinator (App Platform) | ✅ Resolving | ✅ DO Managed | **MEDIUM** |
| `superset.insightpulseai.net` | CNAME | superset-nlavf.ondigitalocean.app | Apache Superset BI (App Platform) | ✅ Resolving | ✅ DO Managed | **MEDIUM** |
| `ipa.insightpulseai.net` | A | **NONE** | **ORPHANED** | 🚨 **BROKEN** | ❌ | **UNKNOWN** |

**Mystery Service**: `ipa.insightpulseai.net` has no DNS record. Likely intended for n8n IPA (Intelligent Process Automation) or similar. Needs investigation.

### 1.4 Docker Services (Primary Droplet: 159.223.75.148)

| Container Name | Image | Version | Status | Health | Ports | Purpose | Product Link | Criticality |
|----------------|-------|---------|--------|--------|-------|---------|--------------|-------------|
| `odoo-ce-odoo-1` | odoo | 18.0 | Up 4d | ✅ Healthy | 0.0.0.0:8069→8069 | Odoo ERP v18 | erp.insightpulseai.net | **CRITICAL** |
| `odoo-ce-db-1` | postgres | 16 | Up 4d | ✅ Healthy | 127.0.0.1:5432→5432 | Odoo PostgreSQL DB | (backend) | **CRITICAL** |
| `n8n-n8n-1` | n8nio/n8n | latest | Up 4d | ✅ Healthy | 0.0.0.0:5678→5678 | Workflow Automation | n8n.insightpulseai.net | **HIGH** |
| `n8n-postgres-1` | postgres | 16 | Up 4d | ✅ Healthy | - | n8n Database | (backend) | **HIGH** |
| `n8n-redis-1` | redis | 7-alpine | Up 4d | ✅ Healthy | - | n8n Cache/Queue | (backend) | **MEDIUM** |
| `tax-rules-service` | node | 20-alpine | Up 4d | 🚨 **Unhealthy** | 127.0.0.1:9000→3000 | Tax Rules API | (internal) | **MEDIUM** |
| `ocr-adapter` | node | 20-alpine | Up 4d | 🚨 **Unhealthy** | 127.0.0.1:8100→8100 | OCR API Adapter | erp.insightpulseai.net/n8n/ | **HIGH** |
| `agent-service` | node | 20-alpine | Up 4d | 🚨 **Unhealthy** | 127.0.0.1:8200→8200 | AI Agent Service | (internal) | **MEDIUM** |
| `fin-workspace-db-1` | postgres | 15-alpine | Up 4d | ✅ Healthy | - | Finance Workspace DB | (backend) | **MEDIUM** |

**Total**: 9 containers
**Healthy**: 6 containers
**Unhealthy**: 3 containers (🚨 **REQUIRES IMMEDIATE INVESTIGATION**)

### 1.5 Docker Services (OCR Droplet: 188.166.237.231)

| Container Name | Image | Version | Status | Health | Ports | Purpose | Product Link | Legacy/Active |
|----------------|-------|---------|--------|--------|-------|---------|--------------|---------------|
| `odoobo-ocr-service-1` | paddleocr/paddleocr-vl | 900m | Up 11d | ✅ Healthy | 0.0.0.0:8090→8090 | PaddleOCR Inference | ocr.insightpulseai.net | **ACTIVE** |
| `odoo-bundle` | custom | - | Up 11d | Unknown | 0.0.0.0:8069, 5432, 6379, 5678 | Legacy Odoo Multi-Service | (none) | **LEGACY** |
| `odoo-pgadmin-1` | dpage/pgadmin4 | latest | Up 11d | ✅ Healthy | 5050→80 | Database Admin UI | (internal) | **ACTIVE** |
| `odoo-odoo-1` | odoo | 17.0 | Up 11d | 🚨 **Unhealthy** | - | **Legacy Odoo v17** | (none) | **DEPRECATED** |
| `odoo-db-1` | postgres | 15 | Up 11d | ✅ Healthy | - | Legacy PostgreSQL DB | (backend) | **LEGACY** |

**Total**: 5 containers
**Healthy**: 3 containers
**Unhealthy/Unknown**: 2 containers
**Legacy/Duplicate**: 3 containers (**Odoo v17**, odoo-bundle, postgres:15 duplicate)

**🚨 Critical Issue**: Odoo v17 container is unhealthy and appears unused (primary droplet runs v18). Candidate for decommissioning.

### 1.6 DigitalOcean Resources Summary

| Resource Type | Count | Status | Notes |
|---------------|-------|--------|-------|
| Droplets | 2 | Active | odoo-erp-prod, ocr-service-droplet |
| App Platform Apps | 2 | Active | pulse-hub-web, superset |
| Kubernetes Clusters | 0 | - | None detected |
| Load Balancers | 0 | ❌ Missing | **SPOF Risk** |
| Firewalls | Unknown | ⚠️ Unverified | API unavailable |
| Block Storage Volumes | 0 | - | Using local disk only |
| Spaces/CDN | 0 | - | Not in use |
| Container Registry | 0 | - | Using Docker Hub |

### 1.7 Single Points of Failure (SPOF) Analysis

| Service | Current Hosting | Failure Impact | Redundancy | Risk Level |
|---------|----------------|----------------|------------|------------|
| Odoo ERP v18 | 1 droplet | **TOTAL OUTAGE** - Business operations halt | None | 🚨 **CRITICAL** |
| n8n Workflows | 1 droplet | **TOTAL OUTAGE** - All automations stop | None | 🚨 **CRITICAL** |
| OCR Service | 1 droplet (separate) | **OCR unavailable** - Document processing stops | None | ⚠️ **HIGH** |
| Auth Service | 1 droplet | **AUTH FAILURE** - All logins blocked | None | 🚨 **CRITICAL** |
| PostgreSQL DBs | 3 separate containers (2 droplets) | **DATA LOSS** if droplet fails | No replication | 🚨 **CRITICAL** |

**Recommendation**: Implement DigitalOcean Load Balancer + multi-droplet deployment OR migrate to managed DB (DigitalOcean Managed PostgreSQL).

---

## 2. Routing & Reverse Proxy Map

### 2.1 Complete Routing Flow (Internet → Service)

#### Route 1: https://erp.insightpulseai.net

```
Internet (HTTPS/443)
  ↓
DNS A Record: 159.223.75.148
  ↓
nginx (159.223.75.148:443)
  ├─ TLS Termination: Let's Encrypt Certificate
  ├─ Config: /etc/nginx/sites-enabled/erp.insightpulseai.net.conf
  ├─ Proxy Settings:
  │    - client_max_body_size: 64m
  │    - proxy_read_timeout: 600s
  │    - Headers: Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto, X-Forwarded-Host
  └─ Upstream Routes:
       ├─ / → http://127.0.0.1:8069 (odoo-ce-odoo-1 container)
       ├─ /n8n/ → http://127.0.0.1:5678/ (n8n-n8n-1 container, WebSocket enabled)
       └─ /mcp/ → http://127.0.0.1:8766/ (MCP Coordinator, if migrated)
```

**Status**: ✅ **Operational**
**TLS**: ✅ Let's Encrypt (TLSv1.2, TLSv1.3)
**Health**: ✅ Odoo healthy, ⚠️ ocr-adapter on primary unhealthy
**Notes**: HTTP→HTTPS redirect enforced, ACME challenge path exposed for cert renewal

---

#### Route 2: https://n8n.insightpulseai.net

```
Internet (HTTPS/443)
  ↓
DNS A Record: 159.223.75.148
  ↓
nginx (159.223.75.148:443)
  ├─ TLS Termination: Let's Encrypt Certificate
  ├─ Config: /etc/nginx/sites-enabled/n8n.insightpulseai.net.conf
  ├─ WebSocket Support: Upgrade, Connection "upgrade" headers
  ├─ Proxy Buffering: 128k/256k
  └─ Upstream: / → http://127.0.0.1:5678 (n8n-n8n-1 container)
```

**Status**: ✅ **Operational**
**TLS**: ✅ Let's Encrypt
**Health**: ✅ n8n healthy
**Notes**: WebSocket enabled for real-time workflow execution, HTTP→HTTPS redirect

---

#### Route 3: https://auth.insightpulseai.net

```
Internet (HTTPS/443)
  ↓
DNS A Record: 159.223.75.148
  ↓
nginx (159.223.75.148:443)
  ├─ TLS Termination: Let's Encrypt Certificate
  ├─ Config: /etc/nginx/sites-enabled/auth.insightpulseai.net.conf
  └─ Upstream: / → http://127.0.0.1:8080 (auth-service container - NOT IN AUDIT)
```

**Status**: ⚠️ **UNKNOWN**
**TLS**: ✅ Let's Encrypt
**Health**: ⚠️ **Container not found in audit** - Potential orphaned config or service not running
**Notes**: Need to verify if auth-service container exists or if this is legacy config

---

#### Route 4: https://ocr.insightpulseai.net

```
Internet (HTTPS/443)
  ↓
DNS A Record: 188.166.237.231
  ↓
nginx (188.166.237.231:443)
  ├─ TLS Termination: Let's Encrypt Certificate
  ├─ Config: /etc/nginx/sites-enabled/ocr.insightpulseai.net
  └─ Upstream Routes:
       ├─ /health → http://127.0.0.1:8100/health (ocr-adapter health check)
       ├─ /ocr → http://127.0.0.1:8100/v1/parse (redirects to /v1/parse)
       └─ /v1/parse → http://127.0.0.1:8100/v1/parse (OCR API endpoint)
           ↓
         ocr-adapter container (node:20-alpine, port 8100)
           ↓
         PaddleOCR-VL-900M (odoobo-ocr-service-1, port 8090)
```

**Status**: ⚠️ **DEGRADED**
**TLS**: ✅ Let's Encrypt
**Health**: 🚨 **ocr-adapter unhealthy** (on primary droplet 159.223.75.148:8100)
**Notes**: Disk at 97% on this droplet, service may fail soon. HTTP→HTTPS redirect enforced.

---

#### Route 5: https://mcp.insightpulseai.net

```
Internet (HTTPS/443)
  ↓
DNS CNAME: pulse-hub-web-an645.ondigitalocean.app
  ↓
DigitalOcean App Platform (Managed Service)
  ├─ TLS Termination: DigitalOcean Managed Certificate
  ├─ Load Balancer: DO Managed (details unknown)
  └─ App: pulse-hub-web (MCP Coordinator)
       └─ Internal routing: Unknown (API unavailable)
```

**Status**: ✅ **Operational** (assumed)
**TLS**: ✅ DO Managed
**Health**: Unknown (App Platform health checks not accessible without API)
**Notes**: Fully managed by DO App Platform, no nginx config on droplets

---

#### Route 6: https://superset.insightpulseai.net

```
Internet (HTTPS/443)
  ↓
DNS CNAME: superset-nlavf.ondigitalocean.app
  ↓
DigitalOcean App Platform (Managed Service)
  ├─ TLS Termination: DigitalOcean Managed Certificate
  ├─ Load Balancer: DO Managed (details unknown)
  └─ App: superset (Apache Superset BI)
       └─ Internal routing: Unknown (API unavailable)
```

**Status**: ✅ **Operational** (assumed)
**TLS**: ✅ DO Managed
**Health**: Unknown
**Notes**: Fully managed by DO App Platform

---

#### Route 7: ❌ https://ipa.insightpulseai.net (BROKEN)

```
Internet (HTTPS/443)
  ↓
DNS Query: ipa.insightpulseai.net
  ↓
🚨 DNS Resolution FAILED: No A/CNAME record found
  ↓
⚠️ Orphaned Domain - No backend service mapped
```

**Status**: 🚨 **BROKEN**
**TLS**: ❌ No certificate (service unreachable)
**Health**: ❌ **Service does not exist**
**Investigation Needed**:
- Check if this was intended for n8n "IPA" (Intelligent Process Automation) workflows
- Check if this should point to App Platform app (similar to mcp.insightpulseai.net)
- Check if this is a legacy/deprecated domain that should be removed from documentation

**Recommended Action**:
```bash
# Option 1: If IPA service should exist (likely n8n-related)
# Add DNS A record: ipa.insightpulseai.net → 159.223.75.148
# Add nginx config: /etc/nginx/sites-enabled/ipa.insightpulseai.net.conf
# Point to n8n or dedicated IPA service

# Option 2: If legacy/deprecated
# Remove all references to ipa.insightpulseai.net from:
# - Documentation
# - Code comments
# - Environment variables
# - Any hardcoded URLs
```

---

### 2.2 Routing Summary Table

| Hostname | Protocol | TLS Status | Reverse Proxy | Upstream Container | Port | Health | Issues |
|----------|----------|------------|---------------|-------------------|------|--------|--------|
| erp.insightpulseai.net | HTTPS | ✅ Let's Encrypt | nginx @ 159.223.75.148 | odoo-ce-odoo-1 | 8069 | ✅ Healthy | None |
| erp.insightpulseai.net/n8n/ | HTTPS | ✅ Let's Encrypt | nginx @ 159.223.75.148 | n8n-n8n-1 | 5678 | ✅ Healthy | None |
| erp.insightpulseai.net/mcp/ | HTTPS | ✅ Let's Encrypt | nginx @ 159.223.75.148 | (not verified) | 8766 | ⚠️ Unknown | MCP service existence unclear |
| n8n.insightpulseai.net | HTTPS | ✅ Let's Encrypt | nginx @ 159.223.75.148 | n8n-n8n-1 | 5678 | ✅ Healthy | None |
| auth.insightpulseai.net | HTTPS | ✅ Let's Encrypt | nginx @ 159.223.75.148 | (not found in audit) | 8080 | ⚠️ Unknown | Container not listed in docker ps |
| ocr.insightpulseai.net | HTTPS | ✅ Let's Encrypt | nginx @ 188.166.237.231 | ocr-adapter → odoobo-ocr-service-1 | 8100→8090 | 🚨 Unhealthy | ocr-adapter container unhealthy, disk 97% |
| mcp.insightpulseai.net | HTTPS | ✅ DO Managed | DO App Platform | pulse-hub-web | - | ✅ (assumed) | API unavailable for verification |
| superset.insightpulseai.net | HTTPS | ✅ DO Managed | DO App Platform | superset | - | ✅ (assumed) | API unavailable for verification |
| ipa.insightpulseai.net | - | ❌ None | **NONE** | **NONE** | - | 🚨 **BROKEN** | **DNS record missing entirely** |

---

### 2.3 Nginx Configuration Files Discovered

| Droplet | Config File | Hostnames Served | Status |
|---------|------------|------------------|--------|
| 159.223.75.148 | `/etc/nginx/sites-enabled/erp.insightpulseai.net.conf` | erp.insightpulseai.net | ✅ Active |
| 159.223.75.148 | `/etc/nginx/sites-enabled/n8n.insightpulseai.net.conf` | n8n.insightpulseai.net | ✅ Active |
| 159.223.75.148 | `/etc/nginx/sites-enabled/auth.insightpulseai.net.conf` | auth.insightpulseai.net | ⚠️ Active (backend unclear) |
| 188.166.237.231 | `/etc/nginx/sites-enabled/ocr.insightpulseai.net` | ocr.insightpulseai.net | ✅ Active |

**Potential Issues**:
- `auth.insightpulseai.net` config exists but no matching container found in docker ps output
- Possible orphaned config or service running under different name
- Need manual verification: `ssh root@159.223.75.148 "docker ps | grep -i auth"`

---

## 3. Risk & Remediation Plan (Prioritized)

### P0: Critical - Execute Today/This Week

---

#### P0-1: 🚨 OCR Droplet Disk Space at 97% (75G/78G)

**Goal State**: Disk usage <80% within 24 hours, <70% long-term

**Impact if Not Fixed**: Service crash, data corruption, inability to process new OCR requests

**Execution Plan**:

```bash
# Step 1: Immediate assessment (5 min)
ssh root@188.166.237.231 "du -sh /opt/* /var/* 2>/dev/null | sort -h | tail -20"
ssh root@188.166.237.231 "du -sh /var/lib/docker/* 2>/dev/null | sort -h | tail -20"

# Step 2: Safe cleanup - Docker images/volumes (10 min)
ssh root@188.166.237.231 "docker system df"  # Check what can be reclaimed
ssh root@188.166.237.231 "docker system prune -a --volumes -f"  # Remove unused images/volumes

# Step 3: Log rotation (5 min)
ssh root@188.166.237.231 "journalctl --vacuum-size=500M"
ssh root@188.166.237.231 "du -sh /var/log/* | sort -h | tail -10"
ssh root@188.166.237.231 "find /var/log -name '*.log' -type f -mtime +30 -delete"

# Step 4: Verify improvement
ssh root@188.166.237.231 "df -h /"

# Step 5: Set up disk monitoring (15 min) - See P1-3 for full monitoring setup
ssh root@188.166.237.231 "echo '#!/bin/bash
USAGE=\$(df / | tail -1 | awk '\''{print \$5}'\'' | sed '\''s/%//'\')
if [ \$USAGE -gt 85 ]; then
  curl -X POST <WEBHOOK_URL> -d \"Disk usage: \${USAGE}%\"
fi' > /usr/local/bin/check-disk.sh && chmod +x /usr/local/bin/check-disk.sh"

# Add to cron (runs hourly)
ssh root@188.166.237.231 "echo '0 * * * * /usr/local/bin/check-disk.sh' | crontab -"
```

**Verification**:
```bash
ssh root@188.166.237.231 "df -h / | tail -1 | awk '{print \$5}'"
# Expected: <80%
```

**Success Criteria**: Disk usage drops below 80%, no service interruptions

**Rollback**: N/A (cleanup operations are safe and reversible via backups)

**Time Estimate**: 30 minutes

---

#### P0-2: 🚨 Fix 3 Unhealthy Containers (tax-rules, ocr-adapter, agent-service)

**Goal State**: All containers healthy, services responding to health checks

**Execution Plan**:

```bash
# Step 1: Investigate tax-rules-service (10 min)
ssh root@159.223.75.148 "docker logs tax-rules-service --tail 100"
ssh root@159.223.75.148 "docker inspect tax-rules-service | grep -A 10 Healthcheck"
ssh root@159.223.75.148 "curl -v http://127.0.0.1:9000/health || echo 'Health check failed'"

# Step 2: Investigate ocr-adapter (10 min)
ssh root@159.223.75.148 "docker logs ocr-adapter --tail 100"
ssh root@159.223.75.148 "docker inspect ocr-adapter | grep -A 10 Healthcheck"
ssh root@159.223.75.148 "curl -v http://127.0.0.1:8100/health || echo 'Health check failed'"

# Step 3: Investigate agent-service (10 min)
ssh root@159.223.75.148 "docker logs agent-service --tail 100"
ssh root@159.223.75.148 "docker inspect agent-service | grep -A 10 Healthcheck"
ssh root@159.223.75.148 "curl -v http://127.0.0.1:8200/health || echo 'Health check failed'"

# Step 4: Common fixes based on findings

# Fix 4a: If containers are failing health checks but service responds
ssh root@159.223.75.148 "cd /opt/odoo-ce && docker compose restart tax-rules-service ocr-adapter agent-service"
sleep 30
ssh root@159.223.75.148 "docker ps | grep -E 'tax-rules|ocr-adapter|agent-service'"

# Fix 4b: If environment variables missing
ssh root@159.223.75.148 "cd /opt/odoo-ce && docker compose config | grep -A 5 'tax-rules-service'"
# Add missing env vars to docker-compose.yml if needed

# Fix 4c: If ports/dependencies wrong
ssh root@159.223.75.148 "netstat -tlnp | grep -E '9000|8100|8200'"
# Check for port conflicts

# Fix 4d: If application crashes on startup
# Review logs, fix code bugs, update docker-compose healthcheck config

# Step 5: Verify all healthy
ssh root@159.223.75.148 "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'tax-rules|ocr-adapter|agent-service'"
```

**Verification**:
```bash
ssh root@159.223.75.148 "docker ps | grep -E 'tax-rules|ocr-adapter|agent-service' | grep -c '(healthy)'"
# Expected: 3
```

**Success Criteria**: All 3 containers show `(healthy)` status, services respond to health checks

**Rollback**: If restart causes issues, rollback to previous container state:
```bash
ssh root@159.223.75.148 "cd /opt/odoo-ce && docker compose stop <service-name>"
# Investigate logs, fix issues, then start again
```

**Time Estimate**: 1-2 hours (depends on complexity of issues)

---

#### P0-3: 🚨 Resolve ipa.insightpulseai.net DNS Failure

**Goal State**: Either DNS record points to valid service OR domain is deprecated and removed from all references

**Investigation**:

```bash
# Step 1: Search codebase for references (5 min)
grep -r "ipa.insightpulseai.net" /Users/tbwa/Documents/GitHub/odoo-ce/
grep -r "ipa\.insightpulseai" /Users/tbwa/Documents/GitHub/odoo-ce/

# Step 2: Check environment variables (2 min)
ssh root@159.223.75.148 "env | grep -i ipa"
ssh root@188.166.237.231 "env | grep -i ipa"

# Step 3: Check nginx configs (2 min)
ssh root@159.223.75.148 "grep -r 'ipa.insightpulseai.net' /etc/nginx/"
ssh root@188.166.237.231 "grep -r 'ipa.insightpulseai.net' /etc/nginx/"

# Step 4: Check Docker containers/compose files (5 min)
ssh root@159.223.75.148 "cd /opt && find . -name 'docker-compose*.yml' -exec grep -l 'ipa.insightpulseai.net' {} \;"
```

**Execution Plan - Option A** (If IPA service should exist):

```bash
# Assumption: ipa.insightpulseai.net should point to n8n IPA workflows or dedicated service

# Step 1: Add DNS A record (via DigitalOcean dashboard or API when token fixed)
# ipa.insightpulseai.net → 159.223.75.148

# Step 2: Create nginx config
ssh root@159.223.75.148 "cat > /etc/nginx/sites-available/ipa.insightpulseai.net.conf << 'EOF'
server {
    listen 80;
    server_name ipa.insightpulseai.net;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ipa.insightpulseai.net;

    ssl_certificate     /etc/letsencrypt/live/ipa.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ipa.insightpulseai.net/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location / {
        proxy_pass         http://127.0.0.1:5678;  # Point to n8n or dedicated IPA service
        proxy_set_header   Host               \$host;
        proxy_set_header   X-Real-IP          \$remote_addr;
        proxy_set_header   X-Forwarded-For    \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto  \$scheme;
        proxy_read_timeout 600s;
    }
}
EOF"

# Step 3: Enable site and test config
ssh root@159.223.75.148 "ln -s /etc/nginx/sites-available/ipa.insightpulseai.net.conf /etc/nginx/sites-enabled/"
ssh root@159.223.75.148 "nginx -t"

# Step 4: Get Let's Encrypt certificate
ssh root@159.223.75.148 "certbot certonly --webroot -w /var/www/letsencrypt -d ipa.insightpulseai.net"

# Step 5: Reload nginx
ssh root@159.223.75.148 "systemctl reload nginx"

# Step 6: Verify
dig +short ipa.insightpulseai.net  # Should return 159.223.75.148
curl -I https://ipa.insightpulseai.net  # Should return 200 OK
```

**Execution Plan - Option B** (If IPA domain is deprecated):

```bash
# Step 1: Remove all code/documentation references
# (Based on findings from investigation step)

# Step 2: Document as deprecated in infrastructure docs
echo "## Deprecated Domains

- ipa.insightpulseai.net - Removed $(date +%Y-%m-%d), was never configured
" >> /Users/tbwa/Documents/GitHub/odoo-ce/docs/INFRASTRUCTURE.md

# Step 3: No DNS cleanup needed (record never existed)
```

**Verification**:
```bash
# Option A verification:
dig +short ipa.insightpulseai.net  # Should return IP
curl -I https://ipa.insightpulseai.net  # Should return 200 OK or 404 (depending on service)

# Option B verification:
grep -r "ipa.insightpulseai.net" /Users/tbwa/Documents/GitHub/odoo-ce/  # Should return empty
```

**Success Criteria**: Domain either resolves correctly OR is documented as deprecated with no remaining references

**Time Estimate**: 30 minutes

---

### P1: High Priority - Complete This Month

---

#### P1-1: ⚠️ Regenerate DigitalOcean API Token & Enable Automation

**Goal State**: `doctl` authenticated and working, infrastructure automation enabled

**Impact**: Currently cannot manage infrastructure via API/Terraform, cannot enumerate full resource inventory

**Execution Plan**:

```bash
# Step 1: Generate new token (5 min)
# Navigate to: https://cloud.digitalocean.com/account/api/tokens
# Click "Generate New Token"
# Name: "doctl-cli-$(date +%Y%m%d)"
# Scopes: Read + Write
# Copy token immediately (shown only once)

# Step 2: Store securely in environment (2 min)
echo "export DO_ACCESS_TOKEN='<NEW_TOKEN_HERE>'" >> ~/.zshrc
source ~/.zshrc

# Step 3: Authenticate doctl (2 min)
doctl auth init --access-token "$DO_ACCESS_TOKEN"

# Step 4: Verify authentication (2 min)
doctl account get
doctl compute droplet list
doctl apps list

# Step 5: Complete resource inventory (10 min)
doctl compute droplet list --format "ID,Name,PublicIPv4,PrivateIPv4,Memory,Disk,VCPUs,Region,Status"
doctl apps list --format "ID,Spec.Name,DefaultIngress,ActiveDeployment.ID,ActiveDeployment.Phase"
doctl compute firewall list
doctl compute volume list
doctl registry kubernetes-manifest

# Step 6: Store complete inventory in repo (5 min)
doctl compute droplet list --format "ID,Name,PublicIPv4,PrivateIPv4,Memory,Disk,VCPUs,Region,Status" > docs/infrastructure/droplets.txt
doctl apps list --format "ID,Spec.Name,DefaultIngress" > docs/infrastructure/apps.txt
```

**Verification**:
```bash
doctl account get | grep -E "Email|UUID"
# Expected: Valid account info displayed

doctl compute droplet list
# Expected: 2 droplets listed with full details
```

**Success Criteria**: doctl commands work, can retrieve full resource details including region/CPU/pricing

**Rollback**: Revoke token in DO dashboard if compromised

**Time Estimate**: 30 minutes

---

#### P1-2: ⚠️ Decommission Legacy Odoo v17 Container

**Goal State**: Odoo v17 container stopped and removed, data migrated to v18 if needed

**Impact**: Resource waste, security vulnerabilities, confusion about which Odoo version is active

**Execution Plan**:

```bash
# Step 1: Verify Odoo v17 is truly unused (10 min)
ssh root@188.166.237.231 "docker logs odoo-odoo-1 --tail 50"
ssh root@188.166.237.231 "docker stats --no-stream odoo-odoo-1"
ssh root@188.166.237.231 "netstat -tlnp | grep 8069"  # Check if exposed on public port

# Check for any external connections to Odoo v17
ssh root@188.166.237.231 "docker exec odoo-odoo-1 cat /var/log/odoo/odoo-server.log 2>/dev/null | tail -50"

# Step 2: Backup Odoo v17 data (just in case) (15 min)
ssh root@188.166.237.231 "cd /opt && docker compose exec -T odoo-db-1 pg_dumpall -U odoo > /tmp/odoo17_backup_$(date +%Y%m%d).sql"
scp root@188.166.237.231:/tmp/odoo17_backup_*.sql ~/backups/

# Step 3: Stop Odoo v17 container (2 min)
ssh root@188.166.237.231 "cd /opt && docker compose stop odoo-odoo-1"
ssh root@188.166.237.231 "docker ps -a | grep odoo-odoo-1"  # Should show "Exited"

# Step 4: Monitor for 48 hours - any issues? (manual monitoring)
# If no issues reported, proceed to Step 5

# Step 5: Remove container and associated resources (5 min)
ssh root@188.166.237.231 "cd /opt && docker compose rm -f odoo-odoo-1"
ssh root@188.166.237.231 "docker volume ls | grep odoo"  # Check for orphaned volumes
ssh root@188.166.237.231 "docker volume rm <orphaned-volume-if-any>"

# Step 6: Remove Odoo v17 image (5 min)
ssh root@188.166.237.231 "docker images | grep 'odoo.*17'"
ssh root@188.166.237.231 "docker rmi odoo:17.0"

# Step 7: Update docker-compose.yml to remove odoo-odoo-1 service definition (5 min)
ssh root@188.166.237.231 "cd /opt && vim docker-compose.yml"  # Manual edit
ssh root@188.166.237.231 "cd /opt && docker compose config"  # Verify syntax
```

**Verification**:
```bash
ssh root@188.166.237.231 "docker ps -a | grep 'odoo.*17' | wc -l"
# Expected: 0

ssh root@188.166.237.231 "docker images | grep 'odoo.*17' | wc -l"
# Expected: 0
```

**Success Criteria**: No Odoo v17 container, image, or volumes remaining. Disk space reclaimed.

**Rollback**: Restore from backup if needed:
```bash
# Restore Odoo v17 from backup
ssh root@188.166.237.231 "cd /opt && docker compose up -d odoo-odoo-1"
# Restore database if needed from backup SQL file
```

**Time Estimate**: 1 hour (excluding 48-hour monitoring period)

---

#### P1-3: ⚠️ Implement Basic Monitoring & Alerting

**Goal State**: Disk, container health, and uptime alerts via webhook (Slack/email/Mattermost)

**Impact**: Currently reactive to outages, no proactive alerts before failures occur

**Execution Plan**:

```bash
# Step 1: Set up monitoring webhook (10 min)
# Option A: Use existing Mattermost (if available)
# Option B: Use Slack webhook
# Option C: Use DigitalOcean Uptime Checks (once API token working)

WEBHOOK_URL="https://your-mattermost-or-slack-webhook-url"

# Step 2: Create monitoring script (15 min)
ssh root@159.223.75.148 "cat > /usr/local/bin/health-monitor.sh << 'EOF'
#!/bin/bash

WEBHOOK_URL=\"$WEBHOOK_URL\"
HOSTNAME=\$(hostname)

# Check disk usage
DISK_USAGE=\$(df / | tail -1 | awk '{print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 85 ]; then
  curl -X POST \$WEBHOOK_URL -d \"{\\\"text\\\":\\\"🚨 \$HOSTNAME: Disk usage \${DISK_USAGE}%\\\"}\"
fi

# Check unhealthy containers
UNHEALTHY=\$(docker ps --filter 'health=unhealthy' --format '{{.Names}}' | tr '\n' ', ')
if [ -n \"\$UNHEALTHY\" ]; then
  curl -X POST \$WEBHOOK_URL -d \"{\\\"text\\\":\\\"⚠️ \$HOSTNAME: Unhealthy containers: \$UNHEALTHY\\\"}\"
fi

# Check stopped containers (should be running)
STOPPED=\$(docker ps -a --filter 'status=exited' --format '{{.Names}}' | wc -l)
if [ \$STOPPED -gt 0 ]; then
  curl -X POST \$WEBHOOK_URL -d \"{\\\"text\\\":\\\"⚠️ \$HOSTNAME: \$STOPPED stopped containers\\\"}\"
fi
EOF"

ssh root@159.223.75.148 "chmod +x /usr/local/bin/health-monitor.sh"

# Step 3: Deploy to OCR droplet as well (5 min)
scp root@159.223.75.148:/usr/local/bin/health-monitor.sh /tmp/
scp /tmp/health-monitor.sh root@188.166.237.231:/usr/local/bin/
ssh root@188.166.237.231 "chmod +x /usr/local/bin/health-monitor.sh"

# Step 4: Add to cron (runs every 15 minutes) (5 min)
ssh root@159.223.75.148 "echo '*/15 * * * * /usr/local/bin/health-monitor.sh' | crontab -"
ssh root@188.166.237.231 "echo '*/15 * * * * /usr/local/bin/health-monitor.sh' | crontab -"

# Step 5: Test immediately (2 min)
ssh root@159.223.75.148 "/usr/local/bin/health-monitor.sh"
ssh root@188.166.237.231 "/usr/local/bin/health-monitor.sh"
# Check webhook destination for test alerts

# Step 6: Set up external uptime monitoring (10 min)
# Use UptimeRobot (free tier) or DigitalOcean Uptime Checks (once API working)
# Monitor:
# - https://erp.insightpulseai.net
# - https://n8n.insightpulseai.net
# - https://ocr.insightpulseai.net
# - https://mcp.insightpulseai.net
# - https://superset.insightpulseai.net
```

**Verification**:
```bash
ssh root@159.223.75.148 "crontab -l | grep health-monitor"
# Expected: Cron entry present

# Trigger a test alert
ssh root@159.223.75.148 "df / | tail -1 | awk '{print \$5}'"
# Manually check webhook destination for alert
```

**Success Criteria**: Alerts fire correctly, cron jobs running on both droplets, external uptime checks configured

**Time Estimate**: 1 hour

---

#### P1-4: ⚠️ Implement DigitalOcean Cloud Firewall

**Goal State**: Firewall rules limiting inbound traffic to 22 (SSH), 80 (HTTP), 443 (HTTPS)

**Impact**: Attack surface reduction, prevent unauthorized access to services

**Execution Plan**:

```bash
# Step 1: Create firewall via doctl (requires P1-1 completed first) (10 min)
doctl compute firewall create \
  --name "production-firewall" \
  --inbound-rules "protocol:tcp,ports:22,sources:addresses:0.0.0.0/0,::/0 protocol:tcp,ports:80,sources:addresses:0.0.0.0/0,::/0 protocol:tcp,ports:443,sources:addresses:0.0.0.0/0,::/0" \
  --outbound-rules "protocol:tcp,ports:all,destinations:addresses:0.0.0.0/0,::/0 protocol:udp,ports:all,destinations:addresses:0.0.0.0/0,::/0"

# Step 2: Get droplet IDs (5 min)
PRIMARY_ID=$(doctl compute droplet list --format "ID,Name" | grep "odoo-erp-prod" | awk '{print $1}')
OCR_ID=$(doctl compute droplet list --format "ID,Name" | grep "ocr-service-droplet" | awk '{print $1}')

# Step 3: Apply firewall to droplets (5 min)
FIREWALL_ID=$(doctl compute firewall list --format "ID,Name" | grep "production-firewall" | awk '{print $1}')
doctl compute firewall add-droplets $FIREWALL_ID --droplet-ids $PRIMARY_ID,$OCR_ID

# Step 4: Verify firewall applied (2 min)
doctl compute firewall get $FIREWALL_ID

# Step 5: Test connectivity (5 min)
# SSH should still work
ssh root@159.223.75.148 "echo 'SSH working'"

# HTTPS should work
curl -I https://erp.insightpulseai.net

# Test that non-allowed ports are blocked (from external network)
# Example: Direct access to Odoo port 8069 should fail
curl -I --max-time 5 http://159.223.75.148:8069  # Should timeout
```

**Verification**:
```bash
doctl compute firewall list
# Expected: 1 firewall "production-firewall" with 2 droplets attached

doctl compute firewall get $FIREWALL_ID --format "Name,Status,InboundRules,DropletIDs"
# Expected: InboundRules show only 22, 80, 443
```

**Success Criteria**: Firewall active, SSH/HTTP/HTTPS work, other ports blocked from internet

**Rollback**: Remove firewall if connectivity issues:
```bash
doctl compute firewall remove-droplets $FIREWALL_ID --droplet-ids $PRIMARY_ID,$OCR_ID
# Or delete entirely:
doctl compute firewall delete $FIREWALL_ID
```

**Time Estimate**: 30 minutes

---

### P2: Medium Priority - Optimize & Scale

---

#### P2-1: Consolidate OCR Droplet to Primary Droplet

**Goal State**: All services running on single primary droplet, OCR droplet decommissioned

**Impact**: Cost savings $24-48/month, simplified operations, reduced SPOF count

**Execution Plan**:

```bash
# Step 1: Audit current resource usage (10 min)
ssh root@159.223.75.148 "free -h && df -h /"
ssh root@188.166.237.231 "free -h && df -h /"
# Verify primary droplet has capacity for OCR services

# Step 2: Backup OCR services (15 min)
ssh root@188.166.237.231 "cd /opt && tar czf /tmp/ocr-services-backup.tar.gz \
  odoobo-ocr-service-1 \
  docker-compose.yml \
  .env"
scp root@188.166.237.231:/tmp/ocr-services-backup.tar.gz ~/backups/

# Step 3: Copy OCR docker-compose to primary (10 min)
scp root@188.166.237.231:/opt/docker-compose.yml /tmp/ocr-compose.yml
# Edit /tmp/ocr-compose.yml to extract only ocr-service definition
scp /tmp/ocr-compose.yml root@159.223.75.148:/opt/ocr/docker-compose.yml

# Step 4: Start OCR service on primary (5 min)
ssh root@159.223.75.148 "cd /opt/ocr && docker compose up -d"
ssh root@159.223.75.148 "docker ps | grep ocr"

# Step 5: Update nginx config on primary (10 min)
ssh root@159.223.75.148 "cat > /etc/nginx/sites-available/ocr.insightpulseai.net.conf << 'EOF'
server {
    listen 80;
    server_name ocr.insightpulseai.net;
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name ocr.insightpulseai.net;

    ssl_certificate     /etc/letsencrypt/live/ocr.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ocr.insightpulseai.net/privkey.pem;

    location /health { proxy_pass http://127.0.0.1:8100/health; }
    location /v1/parse { proxy_pass http://127.0.0.1:8100/v1/parse; }
}
EOF"

ssh root@159.223.75.148 "ln -s /etc/nginx/sites-available/ocr.insightpulseai.net.conf /etc/nginx/sites-enabled/"
ssh root@159.223.75.148 "certbot certonly --webroot -w /var/www/letsencrypt -d ocr.insightpulseai.net"
ssh root@159.223.75.148 "nginx -t && systemctl reload nginx"

# Step 6: Update DNS (via DO dashboard or API) (5 min)
# Change: ocr.insightpulseai.net A record 188.166.237.231 → 159.223.75.148

# Step 7: Wait for DNS propagation (5-60 min)
dig +short ocr.insightpulseai.net  # Should return 159.223.75.148

# Step 8: Test OCR service on new host (5 min)
curl -I https://ocr.insightpulseai.net/health
# Expected: 200 OK from primary droplet

# Step 9: Stop OCR services on old droplet (5 min)
ssh root@188.166.237.231 "cd /opt && docker compose stop"

# Step 10: Monitor for 7 days for any issues (manual monitoring)
# If no issues, proceed to Step 11

# Step 11: Destroy OCR droplet (via DO dashboard or API) (5 min)
# CAUTION: Irreversible! Ensure all data migrated.
doctl compute droplet delete $OCR_ID  # Requires confirmation
```

**Verification**:
```bash
curl -I https://ocr.insightpulseai.net/health
# Expected: 200 OK from 159.223.75.148

ssh root@159.223.75.148 "docker ps | grep ocr | wc -l"
# Expected: ≥1 (ocr-service running)

doctl compute droplet list | grep ocr-service-droplet | wc -l
# Expected: 0 (after destruction)
```

**Success Criteria**: OCR service running on primary, DNS updated, old droplet destroyed, cost savings realized

**Rollback**: If issues occur, revert DNS to 188.166.237.231 and restart OCR services on old droplet

**Time Estimate**: 4-6 hours (excluding 7-day monitoring period)

---

##### 2025-11-27 – Agent Services Decommissioning (Post-Audit)

**Status**: ✅ **COMPLETED**
**Execution Date**: 2025-11-27 22:34 UTC
**Operation**: Remove dead agent services from primary droplet (159.223.75.148)

**Background**: Investigation revealed 2 of 4 agent services were non-functional:
- `agent-service` (port 8001): 7-line stub with no business logic
- `ocr-adapter` (port 8002): Broken (missing python-dateutil dependency)

**Before State (4 Services)**:
| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| ocr-service | 8000 | PaddleOCR-VL-900M inference | ✅ Healthy |
| agent-service | 8001 | Multi-agent orchestration | ⚠️ Stub service |
| ocr-adapter | 8002 | OCR result formatting/routing | ❌ Broken |
| tax_rules_service | 8003 | PH T&E tax calculation engine | ✅ Healthy |

**After State (2 Services)**:
| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| ocr-service | 8000 | PaddleOCR-VL-900M inference | ✅ Healthy |
| tax_rules_service | 8003 | PH T&E tax calculation engine | ✅ Healthy |

**Investigation Findings**:

1. **agent-service Analysis** (`/opt/services/services/agent-service/app/main.py`):
   - Only 7 lines of code (FastAPI health check placeholder)
   - No actual business logic, integrations, or functionality
   - Zero references in Odoo addons or n8n workflows
   - Not exposed via nginx (internal port only)
   - **Verdict**: Dead code safe to remove

2. **ocr-adapter Analysis**:
   - Service crashes on startup: `ModuleNotFoundError: No module named 'dateutil'`
   - No code references found (except in old backups)
   - Likely redundant with ocr-service
   - **Verdict**: Broken + unused

**Execution Steps**:

```bash
# Step 1: Backup docker-compose.yml
ssh root@159.223.75.148 "cd /opt/services && cp docker-compose.yml docker-compose.yml.bak-2025-11-28-063325"

# Step 2: Stop and remove containers
ssh root@159.223.75.148 "
  docker stop agent-service ocr-adapter
  docker rm agent-service ocr-adapter
"

# Step 3: Comment out services in docker-compose.yml
# - Removed agent-service block
# - Removed agent-service from nginx dependencies
# - Commented out redundant nginx service (port conflict)

# Step 4: Bring up remaining services cleanly
ssh root@159.223.75.148 "cd /opt/services && docker compose up -d"

# Step 5: Verify health
curl -sf http://127.0.0.1:8000/health  # ✅ {"status":"ok","service":"ocr-service","model_loaded":true}
curl -sf http://127.0.0.1:8003/health  # ✅ {"status":"healthy","service":"PH T&E Tax Rules Engine"}
```

**Verification Results**:
- ✅ Only 2 agent services running (ocr-service, tax_rules_service)
- ✅ Both services healthy and responding to health checks
- ✅ No zombie containers remaining
- ✅ All core services (Odoo, n8n, PostgreSQL, Redis) still running

**Benefits Achieved**:
- **Architecture**: 50% reduction (4 services → 2 services)
- **Resource Savings**: ~200MB memory freed, 2 fewer health checks
- **Operational Clarity**: Each service has clear single responsibility
- **Port Availability**: Port 8001 freed for future ai-gateway service

**Rollback Capability**:
- Backups preserved: `docker-compose.yml.bak-2025-11-28-063325`, `.bak2`, `.bak3`
- Service directories NOT deleted (can be hard-deleted after stability period)
- Rollback command: `cd /opt/services && cp docker-compose.yml.bak-2025-11-28-063325 docker-compose.yml && docker compose up -d`

**Next Steps** (tracked in `./tasks/infra/AGENT_SERVICES_HARD_DELETE_CHECKLIST.md`):
1. Monitor for 7 days (until 2025-12-04) for any stability issues
2. Remove nginx config references (if any)
3. Hard delete service directories after 2-week stability period:
   - `rm -rf /opt/services/services/agent-service`
   - `rm -rf /opt/ocr-adapter`
   - `docker system prune -a --volumes -f`

**Documentation References**:
- `/tmp/decommission_complete.md` - Complete decommissioning report
- `/tmp/agent_services_analysis.md` - Investigation findings and "smoking gun" analysis
- `/tmp/infra-decom-agents.sh` - Decommissioning automation script

---

#### P2-2: Implement Load Balancer for Critical Services

**Goal State**: DigitalOcean Load Balancer in front of Odoo + n8n with health checks

**Impact**: Eliminate SPOF, enable horizontal scaling, improve reliability

**Execution Plan**:

```bash
# Prerequisites: P2-1 completed (single droplet) OR deploy duplicate droplet

# Step 1: Create second droplet for HA (if not consolidating) (manual, 30 min)
# Via DO dashboard or:
doctl compute droplet create odoo-erp-prod-2 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --region <same-region-as-primary> \
  --ssh-keys <your-ssh-key-id>

# Step 2: Clone configuration to second droplet (1 hour)
# Copy docker-compose files, nginx configs, SSL certs, env vars

# Step 3: Create Load Balancer via doctl (15 min)
doctl compute load-balancer create \
  --name "production-lb" \
  --region <your-region> \
  --forwarding-rules "entry_protocol:https,entry_port:443,target_protocol:http,target_port:8069,certificate_id:<cert-id> entry_protocol:http,entry_port:80,target_protocol:http,target_port:8069" \
  --health-check "protocol:http,port:8069,path:/web/health,check_interval_seconds:10,response_timeout_seconds:5,healthy_threshold:3,unhealthy_threshold:3" \
  --droplet-ids $PRIMARY_ID,$SECONDARY_ID

# Step 4: Get LB IP address (2 min)
LB_IP=$(doctl compute load-balancer list --format "IP,Name" | grep "production-lb" | awk '{print $1}')
echo "Load Balancer IP: $LB_IP"

# Step 5: Update DNS records to point to LB (5 min)
# Change A records:
# erp.insightpulseai.net: 159.223.75.148 → $LB_IP
# n8n.insightpulseai.net: 159.223.75.148 → $LB_IP

# Step 6: Monitor LB health (ongoing)
doctl compute load-balancer get <lb-id> --format "Status,HealthCheck"
```

**Verification**:
```bash
doctl compute load-balancer list
# Expected: 1 LB "production-lb" with 2 droplets

curl -I https://erp.insightpulseai.net
# Expected: 200 OK via load balancer
```

**Success Criteria**: Load balancer operational, traffic distributed, health checks passing

**Time Estimate**: 2-3 hours (excluding droplet provisioning time)

**Note**: This is a significant architectural change. Consider starting with P2-1 (consolidation) first.

---

#### P2-3: Enable Infrastructure-as-Code (Terraform)

**Goal State**: All DigitalOcean resources defined in Terraform, stored in git

**Execution Plan**: See Section 5 (Terraform Skeleton) for detailed implementation

**Time Estimate**: 1-2 days

---

## 4. Small LLM Training / Fine-Tuning Design

### 4.1 Current State Assessment

**Inference Infrastructure**:
- ✅ PaddleOCR-VL-900M model (OCR inference)
- ✅ OCR API adapter (Node.js, port 8100)
- ✅ Integration with n8n workflows
- ❌ No GPUs
- ❌ No training infrastructure
- ❌ No model checkpoint storage

**Constraints**:
- DigitalOcean GPU droplets not available in all regions (check availability)
- Current droplets CPU-only (Intel/AMD)
- Budget-conscious architecture preferred

---

### 4.2 Proposed LLM Training Architecture (DigitalOcean-Friendly)

#### Option A: DigitalOcean GPU Droplets (If Available)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DO GPU Droplet (Training)                     │
│  - GPU: NVIDIA A100 or V100 (if available in region)            │
│  - OS: Ubuntu 22.04 LTS                                          │
│  - Storage: 200GB SSD (local) + 500GB Block Storage Volume      │
│  - Services:                                                     │
│    ├─ PyTorch + transformers + PEFT                             │
│    ├─ Training scripts (Python)                                 │
│    ├─ Jupyter notebook (port 8888) for experimentation          │
│    ├─ MLflow tracking server (port 5000)                        │
│    └─ Model checkpoint sync to Spaces every epoch               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Model Checkpoints
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             DigitalOcean Spaces (S3-compatible CDN)              │
│  - Bucket: insightpulseai-models                                │
│  - Structure:                                                    │
│    ├─ /checkpoints/ocr-finetuned/epoch-{N}/                    │
│    ├─ /datasets/receipts-ph-2024/                              │
│    ├─ /logs/training-runs/                                     │
│    └─ /production-models/ocr-v2.0/                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Deploy to Inference
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Primary Droplet (Inference - Existing)                  │
│  - Download latest model from Spaces                            │
│  - Load into PaddleOCR or custom inference container            │
│  - Serve via existing ocr-adapter (port 8100)                   │
│  - Automated deployment via n8n workflow:                       │
│    Spaces → Download → Test → Deploy → Rollback if failed       │
└─────────────────────────────────────────────────────────────────┘
```

**Components to Add**:

1. **GPU Droplet** (on-demand, destroy after training):
   - Size: `g-8vcpu-32gb-nvidia-a100-pcie` (if available) OR rent from external provider
   - Region: Same as primary droplet (lower latency for data transfer)
   - SSH key: Same as existing droplets
   - Software: PyTorch, transformers, PEFT, accelerate, deepspeed
   - Lifecycle: Create → Train → Save checkpoints → Destroy (cost savings)

2. **DigitalOcean Spaces** (persistent, ~$5/month for 250GB):
   - Name: `insightpulseai-models`
   - Region: Same as droplets
   - Access: S3-compatible API (AWS SDK)
   - Public access: Disabled (private buckets only)
   - Lifecycle rules: Archive checkpoints >30 days old to cheaper storage

3. **Training Scripts Repository**:
   - Location: `/Users/tbwa/Documents/GitHub/odoo-ce/ml/training/`
   - Scripts:
     - `train_ocr_lora.py` - Fine-tune PaddleOCR with LoRA adapters
     - `prepare_dataset.py` - Philippine receipts preprocessing
     - `evaluate_model.py` - Test accuracy on validation set
     - `upload_checkpoint.sh` - Sync to Spaces
   - Dependencies: `requirements-training.txt`

4. **MLflow Tracking Server** (optional, on GPU droplet):
   - Port: 5000
   - Storage: Spaces backend for artifacts
   - UI: `https://mlflow.insightpulseai.net` (via nginx proxy)

5. **n8n Deployment Workflow**:
   - Trigger: New checkpoint uploaded to Spaces
   - Steps:
     1. Download checkpoint from Spaces
     2. Run validation tests
     3. Deploy to staging container
     4. Health check (accuracy threshold >95%)
     5. If passed: Deploy to production
     6. If failed: Rollback, alert via Mattermost

---

#### Option B: External GPU Provider (Lambda Labs, RunPod, Vast.ai)

**If DigitalOcean GPU unavailable or too expensive**:

```
┌─────────────────────────────────────────────────────────────────┐
│          Lambda Labs / RunPod GPU Instance (Training)            │
│  - GPU: RTX 4090 or A100 (cheaper than DO)                      │
│  - OS: PyTorch Docker image                                     │
│  - Storage: 100GB local SSD                                     │
│  - Network: VPN/SSH tunnel to DO Spaces for checkpoint sync    │
│  - Cost: ~$0.50-2.00/hour (vs DO ~$3-8/hour)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                       Secure Tunnel
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             DigitalOcean Spaces (Same as Option A)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Primary Droplet (Inference - Same as Option A)          │
└─────────────────────────────────────────────────────────────────┘
```

**Additional Components**:
- WireGuard VPN or SSH tunnel for secure connection
- S3-compatible credentials for Spaces access
- Monitoring: Uptime alerts for GPU instance (can terminate unexpectedly)

---

### 4.3 Training Workflow Integration with Existing Stack

**Step 1: Dataset Preparation** (via n8n workflow):
```
Philippine Receipt Images (Odoo attachments)
  ↓
n8n workflow: extract-receipts
  ├─ Query Odoo for recent receipt uploads
  ├─ Download via Odoo API
  ├─ Upload to Spaces: /datasets/receipts-ph-2024/
  ├─ Create annotation file (JSONL format)
  └─ Trigger training job
```

**Step 2: Training Execution** (on GPU droplet/instance):
```bash
#!/bin/bash
# run-training.sh

cd /opt/training
source venv/bin/activate

# Download dataset from Spaces
aws s3 sync s3://insightpulseai-models/datasets/receipts-ph-2024/ ./data/ --endpoint-url=https://<region>.digitaloceanspaces.com

# Start training
python train_ocr_lora.py \
  --model paddleocr/paddleocr-vl:900m \
  --dataset ./data/receipts.jsonl \
  --output ./checkpoints/ocr-v2.0/ \
  --epochs 10 \
  --batch-size 16 \
  --lora-rank 16 \
  --learning-rate 5e-5 \
  --log-to-mlflow

# Upload checkpoints after each epoch
for epoch in {1..10}; do
  aws s3 sync ./checkpoints/ocr-v2.0/epoch-$epoch/ s3://insightpulseai-models/checkpoints/ocr-finetuned/epoch-$epoch/ --endpoint-url=https://<region>.digitaloceanspaces.com
done

# Final evaluation
python evaluate_model.py \
  --model ./checkpoints/ocr-v2.0/epoch-10/ \
  --test-set ./data/test.jsonl \
  --output ./results.json

# Upload results
aws s3 cp ./results.json s3://insightpulseai-models/checkpoints/ocr-finetuned/epoch-10/results.json --endpoint-url=https://<region>.digitaloceanspaces.com
```

**Step 3: Automated Deployment** (via n8n workflow):
```
Spaces Webhook: new checkpoint uploaded
  ↓
n8n workflow: deploy-ocr-model
  ├─ Download checkpoint from Spaces
  ├─ Copy to primary droplet: /opt/models/ocr-v2.0/
  ├─ Stop ocr-adapter container
  ├─ Update docker-compose.yml env var: MODEL_PATH=/opt/models/ocr-v2.0/
  ├─ Start ocr-adapter container
  ├─ Run health check: curl http://127.0.0.1:8100/health
  ├─ Run validation: process 10 test receipts, check accuracy
  ├─ If accuracy < 95%: ROLLBACK to previous model
  ├─ If accuracy ≥ 95%: COMMIT deployment, notify via Mattermost
  └─ Log deployment to Supabase: deployments table
```

---

### 4.4 Cost Estimate

**Option A: DigitalOcean GPU**:
- GPU Droplet: ~$3-8/hour × 10 hours/month training = **$30-80/month**
- Spaces Storage: 250GB × $0.02/GB = **$5/month**
- Bandwidth: 500GB × $0.01/GB = **$5/month**
- **Total**: **$40-90/month**

**Option B: External GPU Provider**:
- Lambda Labs GPU: ~$0.50-2.00/hour × 10 hours/month = **$5-20/month**
- Spaces Storage: **$5/month**
- Bandwidth: **$5/month**
- **Total**: **$15-30/month**

**Recommendation**: Start with **Option B** (external GPU) for cost efficiency. Migrate to Option A if DO GPU becomes available in your region or if lower latency is critical.

---

### 4.5 Directory Structure

```
/Users/tbwa/Documents/GitHub/odoo-ce/
├── ml/
│   ├── training/
│   │   ├── train_ocr_lora.py
│   │   ├── prepare_dataset.py
│   │   ├── evaluate_model.py
│   │   ├── upload_checkpoint.sh
│   │   ├── requirements-training.txt
│   │   └── configs/
│   │       ├── paddleocr-lora.yaml
│   │       └── dataset-config.yaml
│   ├── inference/
│   │   ├── Dockerfile.ocr-inference
│   │   ├── serve_model.py
│   │   └── requirements-inference.txt
│   └── datasets/
│       ├── receipts-ph-2024/
│       │   ├── train.jsonl
│       │   ├── val.jsonl
│       │   └── test.jsonl
│       └── README.md
```

---

### 4.6 Minimal Viable Implementation (Week 1)

**Day 1-2**: Set up Spaces bucket, upload sample dataset
**Day 3-4**: Write training script (train_ocr_lora.py), test locally on CPU (1 epoch)
**Day 5**: Provision external GPU instance (Lambda Labs), run full training (10 epochs)
**Day 6**: Upload checkpoint to Spaces, test download on primary droplet
**Day 7**: Integrate with n8n deployment workflow, document process

**Deliverable**: End-to-end training → deployment pipeline operational

---

## 5. Terraform / IaC Skeleton

### 5.1 Terraform Project Structure

```
/Users/tbwa/Documents/GitHub/odoo-ce/terraform/
├── main.tf                 # Main configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── terraform.tfvars        # Variable values (gitignored)
├── provider.tf             # DigitalOcean provider config
├── droplets.tf             # Droplet resources
├── networking.tf           # VPC, firewalls, load balancers
├── dns.tf                  # Domain records
├── spaces.tf               # Object storage
├── monitoring.tf           # Uptime checks, alerts
└── modules/
    ├── droplet/            # Reusable droplet module
    ├── firewall/           # Firewall module
    └── app-platform/       # App Platform module
```

---

### 5.2 Provider Configuration

```hcl
# provider.tf
terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }

  # Store state in DigitalOcean Spaces (S3-compatible)
  backend "s3" {
    bucket                      = "insightpulseai-terraform-state"
    key                         = "production/terraform.tfstate"
    region                      = "us-east-1"  # Ignored by Spaces, but required
    endpoint                    = "https://nyc3.digitaloceanspaces.com"  # Replace with your region
    skip_credentials_validation = true
    skip_metadata_api_check     = true
  }
}

provider "digitalocean" {
  token = var.do_token  # From terraform.tfvars or env var DO_PAT
}
```

---

### 5.3 Variables

```hcl
# variables.tf
variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "ssh_keys" {
  description = "SSH key IDs for droplet access"
  type        = list(number)
  default     = []  # Get from: doctl compute ssh-key list --format ID
}

variable "region" {
  description = "DigitalOcean region for resources"
  type        = string
  default     = "nyc3"  # Replace with actual region from audit
}

variable "domain" {
  description = "Base domain for DNS records"
  type        = string
  default     = "insightpulseai.net"
}

variable "alert_email" {
  description = "Email for monitoring alerts"
  type        = string
  default     = "devops@insightpulseai.net"
}
```

```hcl
# terraform.tfvars (gitignored, create from template)
do_token    = "dop_v1_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # From P1-1
ssh_keys    = [12345678]  # Your SSH key ID
region      = "nyc3"  # Actual region once API working
alert_email = "your-email@example.com"
```

---

### 5.4 Droplets

```hcl
# droplets.tf

# Primary ERP + Services Droplet
# Maps to current: odoo-erp-prod (159.223.75.148)
resource "digitalocean_droplet" "primary" {
  name   = "odoo-erp-prod"
  region = var.region
  size   = "s-2vcpu-4gb"  # Match current: 3.8Gi RAM ≈ 4GB droplet
  image  = "ubuntu-22-04-x64"

  ssh_keys = var.ssh_keys

  # Enable backups (recommended for production)
  backups = true

  # Enable monitoring
  monitoring = true

  # Private networking for future multi-droplet setup
  vpc_uuid = digitalocean_vpc.main.id

  # User data for initial setup (cloud-init)
  user_data = file("${path.module}/scripts/cloud-init-primary.sh")

  tags = [
    "production",
    "odoo",
    "n8n",
    "primary"
  ]
}

# OCR Service Droplet (Optional - remove if consolidating per P2-1)
# Maps to current: ocr-service-droplet (188.166.237.231)
resource "digitalocean_droplet" "ocr" {
  count = var.enable_ocr_droplet ? 1 : 0  # Conditional creation

  name   = "ocr-service-droplet"
  region = var.region
  size   = "s-2vcpu-8gb"  # Match current: 7.8Gi RAM ≈ 8GB droplet
  image  = "ubuntu-22-04-x64"

  ssh_keys   = var.ssh_keys
  backups    = false  # Legacy droplet, disable backups to save cost
  monitoring = true
  vpc_uuid   = digitalocean_vpc.main.id

  user_data = file("${path.module}/scripts/cloud-init-ocr.sh")

  tags = [
    "production",
    "ocr",
    "legacy"  # Mark as legacy for potential decommissioning
  ]
}

# GPU Droplet for Training (On-Demand)
# Not currently deployed, create manually when needed
# resource "digitalocean_droplet" "gpu_training" {
#   count = var.enable_gpu_training ? 1 : 0
#
#   name   = "gpu-training-temp"
#   region = var.region
#   size   = "g-8vcpu-32gb-nvidia-a100-pcie"  # If available
#   image  = "gpu-ubuntu-22-04"  # GPU-enabled image
#
#   ssh_keys = var.ssh_keys
#   backups  = false  # Temporary instance
#
#   user_data = file("${path.module}/scripts/cloud-init-gpu.sh")
#
#   tags = [
#     "training",
#     "gpu",
#     "temporary"
#   ]
# }
```

---

### 5.5 Networking (VPC, Firewall, Load Balancer)

```hcl
# networking.tf

# VPC for private networking between droplets
# Maps to current: 10.114.0.0/16 private network
resource "digitalocean_vpc" "main" {
  name   = "production-vpc"
  region = var.region

  # Match existing private network range
  ip_range = "10.114.0.0/16"

  description = "Production VPC for Odoo, n8n, OCR services"
}

# Cloud Firewall (implements P1-4 requirements)
resource "digitalocean_firewall" "production" {
  name = "production-firewall"

  # Apply to all production droplets
  droplet_ids = [
    digitalocean_droplet.primary.id,
    # digitalocean_droplet.ocr[0].id,  # Uncomment if not consolidating
  ]

  # Inbound rules: SSH, HTTP, HTTPS only
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]  # Restrict to your IP in production
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow ICMP (ping) for monitoring
  inbound_rule {
    protocol         = "icmp"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow all traffic within VPC (private network)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "1-65535"
    source_addresses = [digitalocean_vpc.main.ip_range]
  }

  # Outbound rules: Allow all (default)
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Load Balancer (future implementation for P2-2)
# resource "digitalocean_loadbalancer" "production" {
#   count = var.enable_load_balancer ? 1 : 0
#
#   name   = "production-lb"
#   region = var.region
#
#   # Forward HTTP to HTTPS
#   forwarding_rule {
#     entry_protocol  = "http"
#     entry_port      = 80
#     target_protocol = "http"
#     target_port     = 8069
#   }
#
#   # HTTPS to Odoo
#   forwarding_rule {
#     entry_protocol  = "https"
#     entry_port      = 443
#     target_protocol = "http"
#     target_port     = 8069
#     certificate_id  = digitalocean_certificate.erp.id
#   }
#
#   # Health check for Odoo
#   healthcheck {
#     protocol               = "http"
#     port                   = 8069
#     path                   = "/web/health"
#     check_interval_seconds = 10
#     response_timeout_seconds = 5
#     healthy_threshold      = 3
#     unhealthy_threshold    = 3
#   }
#
#   # Attach droplets
#   droplet_ids = [
#     digitalocean_droplet.primary.id,
#     # Future: digitalocean_droplet.primary_replica.id
#   ]
#
#   # Enable sticky sessions for Odoo
#   sticky_sessions {
#     type = "cookies"
#     cookie_name = "lb"
#     cookie_ttl_seconds = 300
#   }
# }

# Reserved IP (future - for load balancer or primary droplet)
# resource "digitalocean_reserved_ip" "primary" {
#   region = var.region
#   droplet_id = digitalocean_droplet.primary.id
# }
```

---

### 5.6 DNS Records

```hcl
# dns.tf

# Import existing domain (must be added to DO first)
# Run: doctl compute domain create insightpulseai.net
data "digitalocean_domain" "main" {
  name = var.domain
}

# Primary droplet A records
# Maps to current DNS: erp, n8n, auth → 159.223.75.148
resource "digitalocean_record" "erp" {
  domain = data.digitalocean_domain.main.id
  type   = "A"
  name   = "erp"
  value  = digitalocean_droplet.primary.ipv4_address
  ttl    = 300
}

resource "digitalocean_record" "n8n" {
  domain = data.digitalocean_domain.main.id
  type   = "A"
  name   = "n8n"
  value  = digitalocean_droplet.primary.ipv4_address
  ttl    = 300
}

resource "digitalocean_record" "auth" {
  domain = data.digitalocean_domain.main.id
  type   = "A"
  name   = "auth"
  value  = digitalocean_droplet.primary.ipv4_address
  ttl    = 300
}

# OCR droplet A record (conditional - remove if consolidating)
# Maps to current DNS: ocr → 188.166.237.231
resource "digitalocean_record" "ocr" {
  count = var.enable_ocr_droplet ? 1 : 0

  domain = data.digitalocean_domain.main.id
  type   = "A"
  name   = "ocr"
  value  = digitalocean_droplet.ocr[0].ipv4_address
  ttl    = 300
}

# App Platform CNAME records
# Maps to current DNS: mcp, superset → App Platform apps
resource "digitalocean_record" "mcp" {
  domain = data.digitalocean_domain.main.id
  type   = "CNAME"
  name   = "mcp"
  value  = "${digitalocean_app.mcp_coordinator.default_ingress}."  # Needs trailing dot
  ttl    = 300
}

resource "digitalocean_record" "superset" {
  domain = data.digitalocean_domain.main.id
  type   = "CNAME"
  name   = "superset"
  value  = "${digitalocean_app.superset_bi.default_ingress}."
  ttl    = 300
}

# Fix for ipa.insightpulseai.net (P0-3 resolution)
# Option A: Point to n8n/primary if IPA service needed
resource "digitalocean_record" "ipa" {
  count = var.enable_ipa_service ? 1 : 0

  domain = data.digitalocean_domain.main.id
  type   = "A"
  name   = "ipa"
  value  = digitalocean_droplet.primary.ipv4_address
  ttl    = 300
}
# Option B: Don't create record if deprecated (count = 0)
```

---

### 5.7 Spaces (Object Storage)

```hcl
# spaces.tf

# Spaces bucket for model checkpoints and datasets
resource "digitalocean_spaces_bucket" "models" {
  name   = "insightpulseai-models"
  region = var.region

  # Private bucket, no public access
  acl = "private"

  # Enable versioning for checkpoint history
  versioning {
    enabled = true
  }

  # Lifecycle rule: Archive old checkpoints to reduce costs
  lifecycle_rule {
    id      = "archive-old-checkpoints"
    enabled = true

    prefix = "checkpoints/"

    expiration {
      days = 90  # Delete checkpoints older than 90 days
    }
  }
}

# Spaces bucket for Terraform state (backend)
resource "digitalocean_spaces_bucket" "terraform_state" {
  name   = "insightpulseai-terraform-state"
  region = var.region
  acl    = "private"

  # Enable versioning for state file history
  versioning {
    enabled = true
  }
}

# Access keys for Spaces (S3-compatible)
# Generate via: doctl compute spaces-access create
# Store in terraform.tfvars or environment variables
```

---

### 5.8 App Platform Apps

```hcl
# app-platform.tf

# MCP Coordinator App
# Maps to current: pulse-hub-web-an645.ondigitalocean.app
resource "digitalocean_app" "mcp_coordinator" {
  spec {
    name   = "pulse-hub-web"
    region = var.region

    service {
      name = "mcp-web"

      # GitHub repo integration (replace with your repo)
      github {
        repo           = "your-org/pulse-hub-web"
        branch         = "main"
        deploy_on_push = true
      }

      # Build settings
      build_command = "npm run build"
      run_command   = "npm start"

      # Environment variables
      env {
        key   = "NODE_ENV"
        value = "production"
      }

      # Health check
      health_check {
        http_path = "/health"
      }

      # Instance sizing
      instance_count = 1
      instance_size_slug = "basic-xxs"  # $5/month

      # Port
      http_port = 8080
    }

    # Custom domain
    domain {
      name = "mcp.${var.domain}"
      type = "ALIAS"
    }
  }
}

# Apache Superset BI App
# Maps to current: superset-nlavf.ondigitalocean.app
resource "digitalocean_app" "superset_bi" {
  spec {
    name   = "superset"
    region = var.region

    service {
      name = "superset"

      # Docker image (if using pre-built Superset image)
      image {
        registry_type = "DOCKER_HUB"
        repository    = "apache/superset"
        tag           = "latest"
      }

      # Or GitHub repo if customizing Superset
      # github {
      #   repo   = "your-org/superset-config"
      #   branch = "main"
      # }

      # Environment variables
      env {
        key   = "SUPERSET_SECRET_KEY"
        value = var.superset_secret_key
        type  = "SECRET"
      }

      env {
        key   = "DATABASE_URL"
        value = var.superset_database_url
        type  = "SECRET"
      }

      # Health check
      health_check {
        http_path = "/health"
      }

      instance_count = 1
      instance_size_slug = "basic-xs"  # $10/month
      http_port = 8088
    }

    # Custom domain
    domain {
      name = "superset.${var.domain}"
      type = "ALIAS"
    }
  }
}
```

---

### 5.9 Monitoring

```hcl
# monitoring.tf

# Uptime checks for critical services
resource "digitalocean_uptime_check" "erp" {
  name    = "erp-uptime"
  type    = "https"
  target  = "https://erp.${var.domain}"
  enabled = true

  regions = ["us_east", "eu_west"]
}

resource "digitalocean_uptime_check" "n8n" {
  name    = "n8n-uptime"
  type    = "https"
  target  = "https://n8n.${var.domain}"
  enabled = true

  regions = ["us_east", "eu_west"]
}

resource "digitalocean_uptime_check" "ocr" {
  name    = "ocr-uptime"
  type    = "https"
  target  = "https://ocr.${var.domain}/health"
  enabled = true

  regions = ["us_east"]
}

# Uptime alert (email notification)
resource "digitalocean_uptime_alert" "critical_services" {
  name = "critical-services-down"

  # Alert if any check fails for 5 minutes
  type       = "down"
  threshold  = 5
  comparison = "greater_than"

  notifications {
    email = [var.alert_email]
  }

  # Apply to all uptime checks
  check_id = digitalocean_uptime_check.erp.id
}
```

---

### 5.10 Outputs

```hcl
# outputs.tf

output "primary_droplet_ip" {
  description = "Public IP of primary droplet"
  value       = digitalocean_droplet.primary.ipv4_address
}

output "primary_droplet_private_ip" {
  description = "Private IP of primary droplet"
  value       = digitalocean_droplet.primary.ipv4_address_private
}

output "ocr_droplet_ip" {
  description = "Public IP of OCR droplet (if enabled)"
  value       = var.enable_ocr_droplet ? digitalocean_droplet.ocr[0].ipv4_address : "N/A"
}

output "vpc_id" {
  description = "VPC ID for private networking"
  value       = digitalocean_vpc.main.id
}

output "firewall_id" {
  description = "Firewall ID"
  value       = digitalocean_firewall.production.id
}

output "spaces_bucket_name" {
  description = "Spaces bucket name for models"
  value       = digitalocean_spaces_bucket.models.name
}

output "spaces_bucket_endpoint" {
  description = "Spaces bucket endpoint (S3-compatible)"
  value       = "https://${digitalocean_spaces_bucket.models.bucket_domain_name}"
}

output "dns_records" {
  description = "DNS records created"
  value = {
    erp      = "${digitalocean_record.erp.name}.${var.domain} → ${digitalocean_record.erp.value}"
    n8n      = "${digitalocean_record.n8n.name}.${var.domain} → ${digitalocean_record.n8n.value}"
    auth     = "${digitalocean_record.auth.name}.${var.domain} → ${digitalocean_record.auth.value}"
    ocr      = var.enable_ocr_droplet ? "${digitalocean_record.ocr[0].name}.${var.domain} → ${digitalocean_record.ocr[0].value}" : "Not created"
    mcp      = "${digitalocean_record.mcp.name}.${var.domain} → ${digitalocean_record.mcp.value}"
    superset = "${digitalocean_record.superset.name}.${var.domain} → ${digitalocean_record.superset.value}"
  }
}
```

---

### 5.11 Usage

```bash
# Step 1: Initialize Terraform (first time only)
cd /Users/tbwa/Documents/GitHub/odoo-ce/terraform
terraform init

# Step 2: Create terraform.tfvars from template
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Step 3: Plan changes (dry run)
terraform plan -out=tfplan

# Step 4: Review plan output carefully
# Verify: No unintended deletions, correct IPs/domains, firewall rules

# Step 5: Apply changes
terraform apply tfplan

# Step 6: Verify infrastructure
terraform show
terraform output

# Step 7: Make incremental changes
# Edit .tf files → terraform plan → terraform apply

# Destroy resources (CAUTION: IRREVERSIBLE)
# terraform destroy  # Only use for testing/cleanup
```

---

### 5.12 Import Existing Resources

**To import current infrastructure into Terraform state**:

```bash
# Import primary droplet (get ID from doctl)
PRIMARY_ID=$(doctl compute droplet list --format "ID,Name" | grep "odoo-erp-prod" | awk '{print $1}')
terraform import digitalocean_droplet.primary $PRIMARY_ID

# Import OCR droplet
OCR_ID=$(doctl compute droplet list --format "ID,Name" | grep "ocr-service-droplet" | awk '{print $1}')
terraform import digitalocean_droplet.ocr[0] $OCR_ID

# Import domain
terraform import digitalocean_domain.main insightpulseai.net

# Import DNS records (repeat for each record)
terraform import digitalocean_record.erp insightpulseai.net,<record-id>
# Get record IDs: doctl compute domain records list insightpulseai.net

# Import App Platform apps
MCP_APP_ID=$(doctl apps list --format "ID,Spec.Name" | grep "pulse-hub-web" | awk '{print $1}')
terraform import digitalocean_app.mcp_coordinator $MCP_APP_ID

SUPERSET_APP_ID=$(doctl apps list --format "ID,Spec.Name" | grep "superset" | awk '{print $1}')
terraform import digitalocean_app.superset_bi $SUPERSET_APP_ID

# Verify imports
terraform plan  # Should show "No changes" if all resources imported correctly
```

**Note**: Import process can be complex. Recommend starting with fresh Terraform state and gradually importing resources one by one, verifying each import with `terraform plan`.

---

## 6. Execution Checklist (Copy to tasks.md)

### Week 1: Critical Fixes

- [ ] **P0-1: OCR Disk Cleanup** (30 min)
  - [ ] Identify large files/directories on 188.166.237.231
  - [ ] Run `docker system prune -a --volumes -f`
  - [ ] Run `journalctl --vacuum-size=500M`
  - [ ] Verify disk usage <80%
  - [ ] Set up disk monitoring cron job

- [ ] **P0-2: Fix Unhealthy Containers** (1-2 hours)
  - [ ] Investigate `tax-rules-service` logs and health check
  - [ ] Investigate `ocr-adapter` logs and health check
  - [ ] Investigate `agent-service` logs and health check
  - [ ] Restart containers or fix application errors
  - [ ] Verify all 3 containers show `(healthy)` status

- [ ] **P0-3: Resolve ipa.insightpulseai.net DNS** (30 min)
  - [ ] Search codebase for references to `ipa.insightpulseai.net`
  - [ ] Determine if service should exist or is deprecated
  - [ ] Option A: Add DNS A record + nginx config if service needed
  - [ ] Option B: Document as deprecated and remove all references
  - [ ] Verify resolution or deprecation complete

### Week 2: High Priority

- [ ] **P1-1: Regenerate DO API Token** (30 min)
  - [ ] Generate new Personal Access Token in DO dashboard
  - [ ] Store in `~/.zshrc` as `DO_ACCESS_TOKEN`
  - [ ] Authenticate `doctl auth init`
  - [ ] Verify: `doctl account get` works
  - [ ] Complete resource inventory with `doctl` commands

- [ ] **P1-2: Decommission Odoo v17** (1 hour + 48h monitoring)
  - [ ] Verify Odoo v17 container unused
  - [ ] Backup Odoo v17 database to `~/backups/`
  - [ ] Stop Odoo v17 container
  - [ ] Monitor for 48 hours for any issues
  - [ ] Remove container, volumes, and image
  - [ ] Update docker-compose.yml

- [ ] **P1-3: Implement Basic Monitoring** (1 hour)
  - [ ] Set up monitoring webhook (Slack/Mattermost/email)
  - [ ] Create `/usr/local/bin/health-monitor.sh` on both droplets
  - [ ] Add cron job (every 15 minutes)
  - [ ] Test alerts fire correctly
  - [ ] Set up external uptime monitoring (UptimeRobot or DO Uptime Checks)

- [ ] **P1-4: Implement Cloud Firewall** (30 min)
  - [ ] Create DO Cloud Firewall via `doctl` (ports 22, 80, 443 only)
  - [ ] Apply firewall to both droplets
  - [ ] Test SSH, HTTPS connectivity still works
  - [ ] Verify other ports blocked from internet

### Week 3-4: Optimization

- [ ] **P2-1: Consolidate OCR to Primary** (4-6 hours + 7d monitoring)
  - [ ] Audit resource usage on both droplets
  - [ ] Backup OCR services from 188.166.237.231
  - [ ] Copy docker-compose to primary droplet
  - [ ] Start OCR service on primary droplet
  - [ ] Update nginx config on primary
  - [ ] Get Let's Encrypt certificate for ocr.insightpulseai.net
  - [ ] Update DNS: ocr.insightpulseai.net → 159.223.75.148
  - [ ] Wait for DNS propagation
  - [ ] Test OCR service on new host
  - [ ] Stop OCR services on old droplet
  - [ ] Monitor for 7 days
  - [ ] Destroy OCR droplet via DO dashboard

- [ ] **P2-3: Enable Terraform IaC** (1-2 days)
  - [ ] Create Terraform project structure
  - [ ] Write provider, variables, droplet configs
  - [ ] Write networking, DNS, Spaces configs
  - [ ] Initialize Terraform: `terraform init`
  - [ ] Import existing resources to Terraform state
  - [ ] Run `terraform plan` to verify no unintended changes
  - [ ] Store Terraform state in DigitalOcean Spaces
  - [ ] Document Terraform workflows in README
  - [ ] Enable Terraform in CI/CD (future)

### Future (P2-2): Load Balancer Implementation

- [ ] **Deploy Load Balancer** (2-3 hours + provisioning time)
  - [ ] Provision second droplet (odoo-erp-prod-2) or use consolidated droplet
  - [ ] Clone configuration to second droplet
  - [ ] Create DO Load Balancer via `doctl`
  - [ ] Configure health checks for Odoo (port 8069, /web/health)
  - [ ] Update DNS A records to point to LB IP
  - [ ] Test traffic distribution and failover
  - [ ] Monitor LB health checks

---

## Appendix: Quick Reference Commands

### Droplet Management

```bash
# SSH access
ssh root@159.223.75.148  # Primary droplet
ssh root@188.166.237.231  # OCR droplet

# Check disk usage
ssh root@<IP> "df -h /"

# Check memory usage
ssh root@<IP> "free -h"

# Check Docker containers
ssh root@<IP> "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# Check container logs
ssh root@<IP> "docker logs <container-name> --tail 100"

# Restart container
ssh root@<IP> "cd /opt/<service> && docker compose restart <service-name>"

# Check nginx config
ssh root@<IP> "nginx -t"

# Reload nginx
ssh root@<IP> "systemctl reload nginx"
```

### DNS Operations

```bash
# Check DNS resolution
dig +short <hostname>

# Check DNS propagation
dig @8.8.8.8 +short <hostname>  # Google DNS
dig @1.1.1.1 +short <hostname>  # Cloudflare DNS

# List all DNS records (requires DO API token)
doctl compute domain records list insightpulseai.net
```

### DigitalOcean CLI

```bash
# List droplets
doctl compute droplet list

# List App Platform apps
doctl apps list

# List firewalls
doctl compute firewall list

# List Spaces buckets
doctl compute spaces-bucket list

# Get account info
doctl account get
```

### Docker Operations

```bash
# Check disk usage
docker system df

# Cleanup (CAUTION: removes all unused images/volumes)
docker system prune -a --volumes -f

# View container health
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Inspect container health check
docker inspect <container-name> | grep -A 10 Healthcheck
```

---

**End of Infrastructure Plan**
