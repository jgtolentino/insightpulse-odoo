# DNS Namespace Alignment Plan - InsightPulse Odoo

**Status**: Ready for Implementation
**Date**: 2025-11-11
**Strategy**: Option A+ (Minimal Changes + Strategic Aliases)
**Estimated Time**: 2-3 hours

---

## Executive Summary

### Problem Statement
The PRD references domains (`app.*`, `bi.*`) that conflict with existing production infrastructure (`erp.*`, `superset.*`). Missing DNS records for `staging.*` and `metrics.*` prevent PRD milestone completion.

### Recommended Solution: Option A+ (Enhanced Minimal Changes)

**Strategy**: Keep what works, add what's missing, create aliases for consistency.

**Benefits**:
- ✅ Zero disruption to production services
- ✅ Maintains existing SSL certificates
- ✅ Adds PRD-required domains (`staging.*`, `metrics.*`)
- ✅ Creates CNAME aliases for PRD compatibility
- ✅ Production-ready in 2-3 hours
- ✅ Defers complex multi-org routing until needed

**Cost**: $0 (uses existing infrastructure)

---

## Namespace Architecture

### Production Domains (Keep Existing ✅)

```
# Core ERP (Production)
erp.insightpulseai.net → 165.227.10.178:8069 (Odoo 18 CE)
  Status: ✅ Active in production
  SSL: ✅ Let's Encrypt via Nginx
  DNS: ✅ A record configured

# Analytics
superset.insightpulseai.net → App Platform
  Status: ✅ Active (needs DNS record)
  SSL: ✅ DigitalOcean managed
  DNS: ❌ Missing (create CNAME)

# Agent Coordination
mcp.insightpulseai.net → App Platform
  Status: ✅ Active (needs DNS record)
  SSL: ✅ DigitalOcean managed
  DNS: ❌ Missing (create CNAME)

# AI Agent
agent.insightpulseai.net → Gradient AI
  Status: ✅ Active (needs DNS record)
  SSL: ✅ DO Gradient managed
  DNS: ❌ Missing (create CNAME)
```

### New Domains (Add for PRD Alignment 🆕)

```
# Staging Environment
staging.insightpulseai.net → 165.227.10.178:8070 (Staging Odoo)
  Purpose: Pre-production testing
  SSL: 🆕 Issue Let's Encrypt cert
  DNS: 🆕 Create A record
  Service: 🆕 Docker container on port 8070

# Observability
metrics.insightpulseai.net → 165.227.10.178:3000 (Grafana)
  Purpose: System monitoring dashboards
  SSL: 🆕 Issue Let's Encrypt cert
  DNS: 🆕 Create A record
  Service: 🆕 Grafana container on port 3000
```

### CNAME Aliases (PRD Compatibility 🔗)

```
# BI Alias (for PRD consistency)
bi.insightpulseai.net → CNAME superset.insightpulseai.net
  Purpose: PRD references "bi.*" in documentation
  Benefit: Both URLs work, no service changes

# API Alias (for developer clarity)
api.insightpulseai.net → CNAME erp.insightpulseai.net
  Purpose: Explicit API endpoint reference
  Benefit: Clear separation of concerns
```

### Supporting Services (Existing, Need DNS 🔧)

```
# Communication
chat.insightpulseai.net → 165.227.10.178:8065 (Mattermost)
  DNS: ❌ Create A record
  SSL: ✅ Nginx managed

# Automation
n8n.insightpulseai.net → 165.227.10.178:5678 (n8n)
  DNS: ❌ Create A record
  SSL: ✅ Nginx managed

# OCR Service
ocr.insightpulseai.net → 188.166.237.231:5000 (PaddleOCR)
  DNS: ❌ Create A record
  SSL: ✅ Nginx managed

# Documentation
gittodoc.insightpulseai.net → 165.227.10.178:8099
  DNS: ❌ Create A record
  SSL: ✅ Nginx managed

# Root & WWW
insightpulseai.net → 165.227.10.178 (Landing page)
www.insightpulseai.net → CNAME insightpulseai.net
  DNS: ❌ Create A + CNAME records
  SSL: ✅ Nginx managed
```

---

## Complete DNS Record Table

| Record Type | Hostname | Target | TTL | Priority | Status |
|-------------|----------|--------|-----|----------|--------|
| **A** | @ | 165.227.10.178 | 3600 | High | 🆕 Create |
| **A** | erp | 165.227.10.178 | 3600 | High | ✅ Exists |
| **A** | staging | 165.227.10.178 | 3600 | High | 🆕 Create |
| **A** | metrics | 165.227.10.178 | 3600 | High | 🆕 Create |
| **A** | chat | 165.227.10.178 | 3600 | Medium | 🆕 Create |
| **A** | n8n | 165.227.10.178 | 3600 | Medium | 🆕 Create |
| **A** | gittodoc | 165.227.10.178 | 3600 | Low | 🆕 Create |
| **A** | ocr | 188.166.237.231 | 3600 | High | 🆕 Create |
| **CNAME** | www | insightpulseai.net | 3600 | High | 🆕 Create |
| **CNAME** | superset | superset-nlavf.ondigitalocean.app | 3600 | High | 🆕 Create |
| **CNAME** | mcp | pulse-hub-web-an645.ondigitalocean.app | 3600 | High | 🆕 Create |
| **CNAME** | agent | wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run | 3600 | High | 🆕 Create |
| **CNAME** | bi | superset.insightpulseai.net | 3600 | Medium | 🆕 Create |
| **CNAME** | api | erp.insightpulseai.net | 3600 | Medium | 🆕 Create |

**Total Records to Create**: 14
**Existing Records**: 1 (erp)
**Final Total**: 15 DNS records

---

## Port Allocation

| Service | Port | Container | Status |
|---------|------|-----------|--------|
| Odoo Production | 8069 | odoo-production | ✅ Active |
| Odoo Staging | 8070 | odoo-staging | 🆕 Create |
| Odoo Longpolling (Prod) | 8072 | odoo-production | ✅ Active |
| Odoo Longpolling (Stage) | 8073 | odoo-staging | 🆕 Create |
| Grafana | 3000 | grafana | 🆕 Create |
| PostgreSQL (Prod) | 5432 | postgres-prod | ✅ Active |
| PostgreSQL (Stage) | 5433 | postgres-stage | 🆕 Create |
| Mattermost | 8065 | mattermost | ✅ Active |
| n8n | 5678 | n8n | ✅ Active |
| GitToDoc | 8099 | gittodoc | ✅ Active |

---

## Implementation Phases

### Phase 1: Create Core DNS Records (30 minutes)

**Prerequisites**:
- `doctl` authenticated
- Access to DigitalOcean account

**Actions**:
```bash
# 1. Test with dry run
./scripts/setup-dns-records.sh --dry-run

# 2. Create all DNS records
./scripts/setup-dns-records.sh

# 3. Verify records created
doctl compute domain records list insightpulseai.net
```

**Expected Outcome**:
- 14 new DNS records created
- Total of 15 records (including existing erp)

**Verification**:
```bash
# Check DNS propagation (wait 5-10 minutes)
for subdomain in staging metrics bi api chat n8n ocr gittodoc superset mcp agent www; do
  echo "Checking $subdomain.insightpulseai.net"
  dig +short @8.8.8.8 "$subdomain.insightpulseai.net"
done
```

---

### Phase 2: Setup Staging Environment (45 minutes)

**Prerequisites**:
- SSH access to 165.227.10.178
- Docker and docker-compose installed

**Actions**:

#### 2.1 Create Staging Docker Compose Configuration

Create `/root/odoo-staging/docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres-stage:
    image: postgres:15
    container_name: odoo-staging-db
    environment:
      POSTGRES_DB: odoo_staging
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-stage-data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    restart: unless-stopped

  odoo-staging:
    image: odoo:18.0
    container_name: odoo-staging
    depends_on:
      - postgres-stage
    environment:
      HOST: postgres-stage
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - odoo-stage-data:/var/lib/odoo
      - /mnt/addons:/mnt/addons:ro
      - /mnt/oca:/mnt/oca:ro
      - ./odoo-staging.conf:/etc/odoo/odoo.conf:ro
    ports:
      - "8070:8069"
      - "8073:8072"
    restart: unless-stopped
    command: odoo --config=/etc/odoo/odoo.conf --db-filter=^odoo_staging$

volumes:
  postgres-stage-data:
  odoo-stage-data:
```

#### 2.2 Create Staging Odoo Configuration

Create `/root/odoo-staging/odoo-staging.conf`:

```ini
[options]
addons_path = /mnt/addons,/mnt/oca
admin_passwd = ${ADMIN_PASSWORD}
db_host = postgres-stage
db_port = 5432
db_user = odoo
db_password = ${POSTGRES_PASSWORD}
db_name = odoo_staging
db_filter = ^odoo_staging$

# Server config
http_port = 8069
longpolling_port = 8072
proxy_mode = True
workers = 2
max_cron_threads = 1

# Logging
logfile = /var/log/odoo/odoo-staging.log
log_level = info

# Performance
limit_time_cpu = 600
limit_time_real = 1200
```

#### 2.3 Start Staging Environment

```bash
cd /root/odoo-staging
docker-compose up -d

# Verify containers running
docker ps | grep staging

# Check logs
docker logs odoo-staging
```

**Verification**:
```bash
# Test staging Odoo
curl -I http://localhost:8070

# Should return HTTP 200
```

---

### Phase 3: Setup Grafana Metrics (30 minutes)

**Actions**:

#### 3.1 Create Grafana Docker Compose Configuration

Create `/root/grafana/docker-compose.yml`:

```yaml
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana-metrics
    environment:
      GF_SERVER_ROOT_URL: https://metrics.insightpulseai.net
      GF_SERVER_DOMAIN: metrics.insightpulseai.net
      GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana.ini:/etc/grafana/grafana.ini:ro
    ports:
      - "3000:3000"
    restart: unless-stopped

volumes:
  grafana-data:
```

#### 3.2 Start Grafana

```bash
cd /root/grafana
docker-compose up -d

# Verify container running
docker ps | grep grafana

# Check logs
docker logs grafana-metrics
```

**Verification**:
```bash
# Test Grafana
curl -I http://localhost:3000

# Should return HTTP 302 (redirect to login)
```

---

### Phase 4: Update Nginx Configurations (30 minutes)

**Prerequisites**:
- DNS propagation complete (30-60 minutes after Phase 1)
- Staging and Grafana services running

**Actions**:

#### 4.1 Create Staging Nginx Config

Create `/etc/nginx/sites-available/staging.insightpulseai.net.conf`:

```nginx
# HTTP (redirect to HTTPS)
server {
    listen 80;
    server_name staging.insightpulseai.net;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name staging.insightpulseai.net;

    # SSL certificates (will be created by certbot)
    ssl_certificate /etc/letsencrypt/live/staging.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/staging.insightpulseai.net/privkey.pem;

    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logs
    access_log /var/log/nginx/staging.insightpulseai.net.access.log;
    error_log /var/log/nginx/staging.insightpulseai.net.error.log;

    # Proxy to Odoo staging (port 8070)
    location / {
        proxy_pass http://localhost:8070;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
    }

    # Odoo longpolling (port 8073)
    location /longpolling {
        proxy_pass http://localhost:8073;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
    }
}
```

#### 4.2 Create Metrics Nginx Config

Create `/etc/nginx/sites-available/metrics.insightpulseai.net.conf`:

```nginx
# HTTP (redirect to HTTPS)
server {
    listen 80;
    server_name metrics.insightpulseai.net;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name metrics.insightpulseai.net;

    # SSL certificates (will be created by certbot)
    ssl_certificate /etc/letsencrypt/live/metrics.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/metrics.insightpulseai.net/privkey.pem;

    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logs
    access_log /var/log/nginx/metrics.insightpulseai.net.access.log;
    error_log /var/log/nginx/metrics.insightpulseai.net.error.log;

    # Proxy to Grafana (port 3000)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;

        # WebSocket support for Grafana
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:3000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

#### 4.3 Enable Nginx Configs

```bash
# Enable new configs
ln -s /etc/nginx/sites-available/staging.insightpulseai.net.conf /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/metrics.insightpulseai.net.conf /etc/nginx/sites-enabled/

# Test Nginx config
nginx -t

# Reload Nginx (do NOT reload yet - wait for SSL certs)
# systemctl reload nginx
```

---

### Phase 5: Issue SSL Certificates (15 minutes)

**Prerequisites**:
- DNS propagation complete (verify with `dig`)
- Nginx configs created
- Services running on backend ports

**Actions**:

```bash
# Issue certificates for staging and metrics
certbot certonly --nginx \
  -d staging.insightpulseai.net \
  -d metrics.insightpulseai.net \
  --non-interactive \
  --agree-tos \
  --email admin@insightpulseai.net

# Verify certificates issued
certbot certificates

# Now reload Nginx with SSL configs
nginx -t && systemctl reload nginx
```

**Verification**:
```bash
# Test HTTPS endpoints
curl -I https://staging.insightpulseai.net
curl -I https://metrics.insightpulseai.net

# Should return HTTP 200 or 302
```

---

### Phase 6: Update PRD Documentation (15 minutes)

**Actions**:

Update `PRD.md` "Key Links" section:

```markdown
**Key Links**:
- GitHub Repo: https://github.com/jgtolentino/insightpulse-odoo
- **Production ERP**: https://erp.insightpulseai.net (also: api.insightpulseai.net)
- **Staging ERP**: https://staging.insightpulseai.net (M1+)
- **Analytics**: https://superset.insightpulseai.net (also: bi.insightpulseai.net)
- **Metrics**: https://metrics.insightpulseai.net (Grafana - M1+)
- **MCP Coordinator**: https://mcp.insightpulseai.net
- **AI Agent**: https://agent.insightpulseai.net
- **OCR Service**: https://ocr.insightpulseai.net
- **Communication**: https://chat.insightpulseai.net (Mattermost)
- **Automation**: https://n8n.insightpulseai.net
```

Update all references from:
- `app.insightpulseai.net` → `erp.insightpulseai.net`
- `bi.insightpulseai.net` → `superset.insightpulseai.net` (bi.* is CNAME alias)

---

## Verification Checklist

### DNS Records Verification

```bash
# Run automated DNS tests
./scripts/test-dns-endpoints.sh

# Or manual verification
for subdomain in erp staging metrics bi api superset mcp agent chat n8n ocr gittodoc www; do
  echo "Testing $subdomain.insightpulseai.net"
  dig +short @8.8.8.8 "$subdomain.insightpulseai.net"
  curl -I "https://$subdomain.insightpulseai.net" 2>&1 | head -1
  echo ""
done
```

### SSL Certificates Verification

```bash
# Check all certificates
certbot certificates

# Verify expiry dates (should be ~90 days)
for domain in erp staging metrics; do
  echo "Checking $domain.insightpulseai.net"
  echo | openssl s_client -servername "$domain.insightpulseai.net" -connect "$domain.insightpulseai.net:443" 2>/dev/null | openssl x509 -noout -dates
  echo ""
done
```

### Service Health Verification

```bash
# Check Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check service responses
curl -I https://erp.insightpulseai.net          # Should return 200
curl -I https://staging.insightpulseai.net      # Should return 200
curl -I https://metrics.insightpulseai.net      # Should return 302 (login)
curl -I https://superset.insightpulseai.net     # Should return 200
curl -I https://mcp.insightpulseai.net          # Should return 200
curl -I https://agent.insightpulseai.net        # Should return 200
```

---

## Rollback Plan

If issues occur during implementation:

### DNS Rollback
```bash
# Delete newly created DNS records
doctl compute domain records list insightpulseai.net

# Delete specific record by ID
doctl compute domain records delete insightpulseai.net RECORD_ID
```

### Service Rollback
```bash
# Stop staging environment
cd /root/odoo-staging
docker-compose down

# Stop Grafana
cd /root/grafana
docker-compose down

# Remove Nginx configs
rm /etc/nginx/sites-enabled/staging.insightpulseai.net.conf
rm /etc/nginx/sites-enabled/metrics.insightpulseai.net.conf
nginx -t && systemctl reload nginx
```

### SSL Certificate Rollback
```bash
# Revoke certificates if needed
certbot revoke --cert-path /etc/letsencrypt/live/staging.insightpulseai.net/cert.pem
certbot revoke --cert-path /etc/letsencrypt/live/metrics.insightpulseai.net/cert.pem

# Delete certificates
certbot delete --cert-name staging.insightpulseai.net
certbot delete --cert-name metrics.insightpulseai.net
```

---

## Cost Analysis

### Infrastructure Costs

| Resource | Current | After Implementation | Change |
|----------|---------|---------------------|--------|
| **DigitalOcean Droplet** (ipai-odoo-erp) | $48/mo | $48/mo | $0 |
| **DNS Records** | Free | Free | $0 |
| **SSL Certificates** | Free (Let's Encrypt) | Free (Let's Encrypt) | $0 |
| **Docker Containers** | Included | Included | $0 |
| **Bandwidth** | Included (1TB) | Included (1TB) | $0 |
| **Total** | **$48/mo** | **$48/mo** | **$0** |

**Note**: Staging and Metrics services run on existing droplet, no additional cost.

---

## Future Considerations (Not Implemented Now)

### Option B: Multi-Org Routing (Defer to Wave 5+)

When you actually need white-label multi-tenant routing:

```
# Multi-org subdomains (db_filter based routing)
rim.insightpulseai.net → 165.227.10.178:8069 (db_filter=^db_rim$)
ckvc.insightpulseai.net → 165.227.10.178:8069 (db_filter=^db_ckvc$)
bom.insightpulseai.net → 165.227.10.178:8069 (db_filter=^db_bom$)
# ... (8 agencies total)
```

**Implementation trigger**: When you need separate login URLs per agency.

**Estimated effort**: 2-3 hours (Nginx regex routing + Odoo db_filter config)

### Themed Branding (Adobo, Suka & Soy, etc.)

The themed naming schemes you provided are great for:
- White-label SaaS offerings
- Marketing/branding
- Future product lines

**Recommendation**: Defer branding decisions until you validate the core platform with real users.

**Next steps when ready**:
1. Choose brand name (e.g., "Adobo Systems")
2. Register new domain (e.g., `adobo.run`)
3. Create org slugs for GitHub, DB, S3 (e.g., `adobo-systems`, `adobo_db`, `adobo-raw`)
4. Update DNS, SSL, and Odoo configs

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: DNS Records | 30 min | doctl access |
| DNS Propagation Wait | 30-60 min | ⏳ Automatic |
| Phase 2: Staging Setup | 45 min | SSH access, Docker |
| Phase 3: Grafana Setup | 30 min | Docker |
| Phase 4: Nginx Configs | 30 min | DNS propagated |
| Phase 5: SSL Certificates | 15 min | DNS propagated, services running |
| Phase 6: PRD Updates | 15 min | Documentation access |
| **Total Active Time** | **~3 hours** | (excluding DNS wait) |
| **Total Elapsed Time** | **3-4 hours** | (including DNS wait) |

---

## Success Criteria

Implementation is successful when:

✅ **DNS Records**:
- [ ] 14 new DNS records created
- [ ] All subdomains resolve correctly
- [ ] CNAME aliases work (bi.* → superset.*, api.* → erp.*)

✅ **Services**:
- [ ] Staging Odoo accessible at https://staging.insightpulseai.net
- [ ] Grafana accessible at https://metrics.insightpulseai.net
- [ ] All existing services still functional

✅ **SSL/TLS**:
- [ ] SSL certificates issued for staging.* and metrics.*
- [ ] HTTPS redirect working (HTTP → HTTPS)
- [ ] Auto-renewal configured

✅ **Documentation**:
- [ ] PRD updated with correct URLs
- [ ] README updated
- [ ] INFRASTRUCTURE_ARCHITECTURE.md updated

✅ **Testing**:
- [ ] All DNS endpoints pass tests
- [ ] SSL certificate validation passes
- [ ] Service health checks pass

---

## Next Actions

1. **Review this plan** - Confirm Option A+ is acceptable
2. **Schedule implementation** - Block 3-4 hours
3. **Execute Phase 1** - Create DNS records
4. **Wait for DNS propagation** - 30-60 minutes
5. **Execute Phases 2-6** - Setup services, Nginx, SSL, docs

**Ready to proceed?** Start with:
```bash
./scripts/setup-dns-records.sh --dry-run
```

---

**Status**: ✅ Plan approved, ready for implementation
**Next Milestone**: M1 completion (Staging + Metrics operational)
**Estimated Completion**: 2025-11-11 (same day)
