# InsightPulse AI - Infrastructure Architecture

**Last Updated:** 2025-11-09
**Environment:** Production (SFO2, SGP regions)
**Primary Domain:** insightpulseai.net

---

## Table of Contents

1. [Overview](#overview)
2. [Network Architecture](#network-architecture)
3. [Service Inventory](#service-inventory)
4. [Database Architecture](#database-architecture)
5. [Authentication Flow](#authentication-flow)
6. [Deployment Strategy](#deployment-strategy)
7. [Monitoring & Observability](#monitoring--observability)
8. [Disaster Recovery](#disaster-recovery)

---

## Overview

InsightPulse AI is a **multi-tenant Finance Shared Service Center (SSC)** platform built on:

- **Odoo 18 CE** (primary ERP)
- **Apache Superset** (BI/Analytics - Tableau replacement)
- **Supabase PostgreSQL** (database + auth backend)
- **DigitalOcean** (infrastructure hosting)
- **Google OAuth** (unified SSO across all services)

### Architecture Diagram

```mermaid
graph TB
    User[Users] -->|HTTPS| DNS[DNS: insightpulseai.net]

    DNS -->|erp.*| ERP[Odoo 18 CE<br/>165.227.10.178:8069]
    DNS -->|superset.*| Superset[Apache Superset<br/>superset-nlavf.ondigitalocean.app]
    DNS -->|mcp.*| MCP[MCP Coordinator<br/>pulse-hub-web-an645.ondigitalocean.app]
    DNS -->|ocr.*| OCR[OCR Service<br/>188.166.237.231:8080]
    DNS -->|agent.*| Agent[AI Agent Hub<br/>wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run]
    DNS -->|chat.*| Chat[Mattermost<br/>165.227.10.178:8065]
    DNS -->|n8n.*| N8N[n8n Automation<br/>165.227.10.178:5678]

    ERP -->|Connection Pooler<br/>Port 6543| Supabase[(Supabase PostgreSQL<br/>spdtwktxdalcfigzeqrz)]
    Superset -->|Direct Connection<br/>Port 5432| Supabase
    MCP -->|REST API| Supabase

    ERP -->|OAuth Flow| Google[Google OAuth 2.0]
    Superset -->|OAuth Flow| Google
    MCP -->|OAuth Flow| Google
    Chat -->|OAuth Flow| Google
    N8N -->|OAuth Flow| Google

    ERP -->|Session Cookie<br/>.insightpulseai.net| CookieStore[Shared Session]
    Superset --> CookieStore
    MCP --> CookieStore
    Chat --> CookieStore
    N8N --> CookieStore

    style ERP fill:#e1f5ff
    style Supabase fill:#ffe1f5
    style Google fill:#fff5e1
    style CookieStore fill:#e1ffe1
```

---

## Network Architecture

### DNS Record Mapping

All domains managed via **insightpulseai.net** registrar with the following CNAME/A records:

| Subdomain | Type | Target | Purpose |
|-----------|------|--------|---------|
| **erp**.insightpulseai.net | A | 165.227.10.178 | Odoo 18 CE (primary ERP) |
| **superset**.insightpulseai.net | CNAME | superset-nlavf.ondigitalocean.app | Apache Superset analytics |
| **mcp**.insightpulseai.net | CNAME | pulse-hub-web-an645.ondigitalocean.app | MCP Coordinator |
| **ocr**.insightpulseai.net | A | 188.166.237.231 | OCR service (PaddleOCR) |
| **agent**.insightpulseai.net | CNAME | wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run | AI Agent Hub |
| **chat**.insightpulseai.net | A | 165.227.10.178 | Mattermost (team chat) |
| **n8n**.insightpulseai.net | A | 165.227.10.178 | n8n (workflow automation) |

### Network Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Nginx as Nginx Reverse Proxy<br/>(165.227.10.178)
    participant Odoo as Odoo 18 CE<br/>(localhost:8069)
    participant Supabase as Supabase PostgreSQL<br/>(spdtwktxdalcfigzeqrz)
    participant Google as Google OAuth 2.0

    User->>Nginx: HTTPS Request<br/>erp.insightpulseai.net
    Nginx->>Nginx: Check SSL Certificate
    Nginx->>Nginx: Apply Security Headers

    alt OAuth Login
        Nginx->>Odoo: Proxy to /auth_oauth/signin
        Odoo->>Google: Redirect to OAuth consent
        Google->>User: Show consent screen
        User->>Google: Approve
        Google->>Odoo: Return authorization code
        Odoo->>Google: Exchange code for token
        Google->>Odoo: Return access token
        Odoo->>Supabase: Query user profile
        Supabase->>Odoo: Return user data
        Odoo->>Nginx: Set session cookie<br/>(Domain: .insightpulseai.net)
        Nginx->>User: Redirect to dashboard
    else Regular Request
        Nginx->>Odoo: Proxy with headers
        Odoo->>Supabase: Database query
        Supabase->>Odoo: Return data
        Odoo->>Nginx: Generate HTML response
        Nginx->>User: Return response
    end
```

### SSL/TLS Configuration

**Certificate Provider:** Let's Encrypt (auto-renewal via Certbot)

**Coverage:**
- Wildcard certificate: `*.insightpulseai.net`
- Root domain: `insightpulseai.net`
- Renewal: Automated via cron (daily check)

**TLS Settings:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

---

## Service Inventory

### DigitalOcean Apps (App Platform)

| App Name | App ID | Region | Status | Purpose |
|----------|--------|--------|--------|---------|
| **odoo-saas-platform** | 04de4372-7a4f-472a-9c3f-5deb895b7ad2 | SFO2 | ⚠️ Failing | Legacy Odoo deployment (not used) |
| **superset-analytics** | 73af11cb-dab2-4cb1-9770-291c536531e6 | SFO2 | ✅ Active | Apache Superset BI |
| **mcp-coordinator** | 844b0bb2-0208-4694-bf86-12e750b7f790 | SFO2 | ✅ Active | MCP Coordinator (Next.js) |

**Deployment Method:** DigitalOcean App Platform (container-based PaaS)

**Auto-Deploy:** GitHub Actions on push to `main` branch

### DigitalOcean Droplets (VMs)

| Droplet Name | IP Address | Region | Size | Purpose |
|--------------|------------|--------|------|---------|
| **ipai-odoo-erp** | 165.227.10.178 | SFO2 | 4GB RAM, 2 vCPUs | Primary Odoo 18 CE + Nginx + Mattermost + n8n |
| **ocr-service-droplet** | 188.166.237.231 | SGP1 | 8GB RAM, 4 vCPUs, GPU | PaddleOCR service (document processing) |

**OS:** Ubuntu 24.04 LTS

**Services on ipai-odoo-erp (165.227.10.178):**
- Nginx (reverse proxy, SSL termination)
- Odoo 18 CE (port 8069)
- Mattermost (port 8065)
- n8n (port 5678)
- PostgreSQL client (for Supabase connections)

**Services on ocr-service-droplet (188.166.237.231):**
- PaddleOCR-VL API (port 8080)
- RTX 4090 GPU for OCR inference
- Redis queue for job processing

### Database Architecture

**Provider:** Supabase (AWS us-east-1)

#### Primary Database: spdtwktxdalcfigzeqrz

**Connection Strings:**

```bash
# Direct connection (port 5432) - Use for migrations, admin tasks
DIRECT_URL="postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres?sslmode=require"

# Connection pooler (port 6543) - Use for high-concurrency applications
POOLER_URL="postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Public URL (for Supabase REST API)
SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
```

**When to use each:**
- **Direct (5432):** Migrations, `psql` commands, admin operations
- **Pooler (6543):** Odoo connections, high-traffic applications
- **REST API:** Frontend applications, serverless functions

**Database Size:**
- Current: ~500MB (within Supabase free tier)
- Limit: 500MB free tier (upgrade to Pro at 1GB)

**Key Tables:**
- `ir_*` - Odoo core tables (modules, config, sessions)
- `res_*` - Odoo resource tables (users, companies, partners)
- `account_*` - Odoo accounting tables (invoices, journals)
- `expense_*` - Custom expense management tables
- `scout_*` - Scout transaction data (ETL pipeline)

#### Secondary Database: xkxyvboeubffxxbebsll (SpendFlow - deprecated)

**Status:** ⚠️ Legacy (being migrated to spdtwktxdalcfigzeqrz)

**Connection:**
```bash
SPENDFLOW_URL="postgres://postgres.xkxyvboeubffxxbebsll:Postgres_26@db.xkxyvboeubffxxbebsll.supabase.co:5432/postgres"
```

**Migration Plan:**
1. Export Scout data from xkxyvboeubffxxbebsll
2. Import to spdtwktxdalcfigzeqrz (scout.* schema)
3. Deprecate xkxyvboeubffxxbebsll project

---

## Authentication Flow

### Google OAuth SSO Architecture

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Odoo as Odoo 18 CE<br/>(erp.insightpulseai.net)
    participant Google as Google OAuth 2.0
    participant Supabase as Supabase PostgreSQL

    User->>Browser: Navigate to erp.insightpulseai.net/web/login
    Browser->>Odoo: GET /web/login
    Odoo->>Browser: Render login page with OAuth buttons

    User->>Browser: Click "Sign in with Google"
    Browser->>Odoo: POST /auth_oauth/signin?provider=google

    Odoo->>Google: Redirect to OAuth consent<br/>(client_id, redirect_uri, scope)
    Google->>User: Show consent screen
    User->>Google: Approve access (email, profile)

    Google->>Odoo: Redirect with authorization code<br/>GET /auth_oauth/signin?code=XXX&state=YYY
    Odoo->>Google: Exchange code for access token<br/>POST /o/oauth2/token
    Google->>Odoo: Return access token + user info

    Odoo->>Supabase: Check if user exists<br/>SELECT * FROM res_users WHERE oauth_uid = ?

    alt User exists
        Supabase->>Odoo: Return user record
        Odoo->>Odoo: Create session
    else New user
        Odoo->>Supabase: INSERT INTO res_users<br/>(oauth_uid, email, name)
        Supabase->>Odoo: User created
        Odoo->>Odoo: Create session
    end

    Odoo->>Browser: Set session cookie<br/>Domain: .insightpulseai.net<br/>HttpOnly, Secure, SameSite=None
    Browser->>Browser: Store cookie
    Odoo->>Browser: Redirect to /web (dashboard)

    Browser->>User: Show Odoo dashboard

    Note over Browser,Odoo: Session cookie now valid for<br/>all *.insightpulseai.net subdomains

    Browser->>Browser: Navigate to superset.insightpulseai.net
    Browser->>Browser: Send session cookie (same domain)
    Note over Browser: Automatic SSO - No re-authentication needed
```

### Session Cookie Specification

**Cookie Name:** `session_id`

**Cookie Attributes:**
```
Domain: .insightpulseai.net
Path: /
Secure: true
HttpOnly: true
SameSite: None
Max-Age: 3600 (1 hour)
```

**Why SameSite=None?**
- Allows cookie to be sent in cross-site requests (e.g., Superset → Odoo API)
- Required for services on different subdomains to share authentication
- **Security:** Requires `Secure=true` (HTTPS only) when using `SameSite=None`

**Session Storage:**
- Database table: `ir_session`
- Fields: `sid`, `user_id`, `create_date`, `write_date`
- Cleanup: Expired sessions deleted by Odoo cron job (daily)

---

## Deployment Strategy

### CI/CD Pipeline

```mermaid
graph LR
    Dev[Developer] -->|git push| GitHub[GitHub Repository]
    GitHub -->|Trigger| GHA[GitHub Actions]

    GHA -->|Build Docker| Docker[Docker Build]
    Docker -->|Push Image| Registry[DO Container Registry]

    Registry -->|Deploy| DOApp[DigitalOcean App Platform]
    DOApp -->|Update| Superset[Superset App]
    DOApp -->|Update| MCP[MCP Coordinator]

    GHA -->|SSH Deploy| Droplet[Odoo Droplet<br/>165.227.10.178]
    Droplet -->|Restart Services| Nginx[Nginx + Odoo]

    GHA -->|Run Tests| Pytest[Pytest Suite]
    Pytest -->|Validation| Pass{Tests Pass?}

    Pass -->|Yes| Slack[Notify Slack: ✅ Success]
    Pass -->|No| Fail[Notify Slack: ❌ Failed]

    style GHA fill:#e1f5ff
    style Pass fill:#ffe1e1
```

### Deployment Environments

| Environment | Branch | Auto-Deploy | Approval Required |
|-------------|--------|-------------|-------------------|
| **Production** | `main` | ✅ Yes | ❌ No (direct deploy) |
| **Staging** | `develop` | ✅ Yes | ❌ No |
| **Feature** | `feature/*` | ❌ Manual | ✅ PR review required |

### Rollback Strategy

**Option 1: Git Revert (Recommended)**

```bash
# Identify failing commit
git log --oneline -n 10

# Revert commit (creates new commit)
git revert <commit-hash>

# Push to trigger auto-deploy
git push origin main
```

**Option 2: DigitalOcean App Rollback**

```bash
# List recent deployments
doctl apps list-deployments <app-id>

# Rollback to previous deployment
doctl apps rollback <app-id> --deployment-id <previous-deployment-id>
```

**Option 3: Manual Droplet Rollback**

```bash
# SSH to droplet
ssh root@165.227.10.178

# Pull previous version
cd /opt/odoo
git log --oneline -n 10
git checkout <previous-commit>

# Restart Odoo
systemctl restart odoo
```

**Recovery Time Objective (RTO):** <5 minutes

**Recovery Point Objective (RPO):** Last commit (no data loss)

---

## Monitoring & Observability

### Metrics Collection

**Nginx Access Logs:**
```bash
# Location
/var/log/nginx/odoo_access.log
/var/log/nginx/odoo_error.log

# Real-time monitoring
tail -f /var/log/nginx/odoo_access.log | grep -E "POST|GET"

# Error analysis
tail -n 100 /var/log/nginx/odoo_error.log | grep -i "error"
```

**Odoo Logs:**
```bash
# Systemd journal
journalctl -u odoo -f

# Filter by level
journalctl -u odoo -p err -since "1 hour ago"

# OAuth-specific logs
journalctl -u odoo -f | grep -i oauth
```

**Database Monitoring:**

```sql
-- Active connections
SELECT
  datname,
  count(*) AS connections
FROM pg_stat_activity
GROUP BY datname
ORDER BY connections DESC;

-- Slow queries
SELECT
  query,
  calls,
  total_time,
  mean_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 10;

-- Table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
```

### Health Checks

**Service Health Endpoints:**

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| Odoo | https://erp.insightpulseai.net/web/health | HTTP 200, JSON `{"status": "pass"}` |
| Superset | https://superset.insightpulseai.net/health | HTTP 200, JSON `{"ok": true}` |
| MCP | https://mcp.insightpulseai.net/api/health | HTTP 200, JSON `{"status": "healthy"}` |
| OCR | https://ocr.insightpulseai.net/health | HTTP 200, JSON `{"ok": true}` |

**Automated Health Monitoring:**

```bash
#!/bin/bash
# scripts/health_check.sh

SERVICES=(
  "https://erp.insightpulseai.net/web/health"
  "https://superset.insightpulseai.net/health"
  "https://mcp.insightpulseai.net/api/health"
  "https://ocr.insightpulseai.net/health"
)

for url in "${SERVICES[@]}"; do
  status=$(curl -sf -o /dev/null -w "%{http_code}" "$url")
  if [ "$status" -ne 200 ]; then
    echo "❌ $url is unhealthy (HTTP $status)"
    # Send alert to Slack
  else
    echo "✅ $url is healthy"
  fi
done
```

**Run Health Check:**
```bash
# Manual run
./scripts/health_check.sh

# Cron (every 5 minutes)
*/5 * * * * /opt/insightpulse-odoo/scripts/health_check.sh >> /var/log/health_check.log 2>&1
```

### Alert Channels

**Slack Integration:**
- Channel: `#insightpulse-alerts`
- Webhook URL: (stored in environment variables)
- Alert types: Deployment failures, health check failures, error spikes

**Email Alerts:**
- Recipient: `jgtolentino_rn@yahoo.com`
- Triggers: Critical errors, database connection failures

---

## Disaster Recovery

### Backup Strategy

**Database Backups (Supabase):**

```bash
# Manual backup
pg_dump "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres" \
  | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Automated backup (daily via cron)
0 2 * * * /opt/insightpulse-odoo/scripts/backup_database.sh
```

**Backup Retention:**
- Daily backups: Keep for 7 days
- Weekly backups: Keep for 4 weeks
- Monthly backups: Keep for 12 months

**Storage Location:**
- DigitalOcean Spaces: `insightpulse-backups` (encrypted at rest)
- Geographic redundancy: us-east-1 (primary), sfo2 (secondary)

### Recovery Procedures

**Scenario 1: Database Corruption**

```bash
# 1. Stop all applications
ssh root@165.227.10.178
systemctl stop odoo nginx mattermost n8n

# 2. Restore from backup
gunzip -c backup_YYYYMMDD_HHMMSS.sql.gz | psql "$POSTGRES_URL"

# 3. Verify restoration
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM res_users;"

# 4. Restart applications
systemctl start odoo nginx mattermost n8n
```

**Recovery Time:** ~15 minutes

**Scenario 2: Droplet Failure**

```bash
# 1. Create new droplet from snapshot
doctl compute droplet create odoo-recovery \
  --image <snapshot-id> \
  --region sfo2 \
  --size s-2vcpu-4gb

# 2. Update DNS to point to new IP
# (Manual in domain registrar or via API)

# 3. Verify services
curl -sf https://erp.insightpulseai.net/web/health
```

**Recovery Time:** ~30 minutes (DNS propagation delay)

**Scenario 3: Complete Infrastructure Loss**

```bash
# 1. Restore from infrastructure-as-code
git clone https://github.com/jgtolentino/insightpulse-odoo
cd infra/terraform
terraform apply

# 2. Restore database from backup
# (Same as Scenario 1)

# 3. Deploy applications
git push origin main  # Triggers CI/CD
```

**Recovery Time:** ~2 hours (full infrastructure rebuild)

---

## Performance Optimization

### Caching Strategy

**Nginx Cache:**
```nginx
# Static assets
location ~* /web/static/ {
    proxy_cache static_cache;
    proxy_cache_valid 200 24h;
    expires 7d;
}
```

**Odoo QWeb Template Cache:**
```python
# System parameter
ir.config_parameter: qweb.view.cache = True
```

**Database Query Optimization:**

```sql
-- Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_res_users_oauth_uid ON res_users(oauth_uid);
CREATE INDEX IF NOT EXISTS idx_ir_session_sid ON ir_session(sid);
CREATE INDEX IF NOT EXISTS idx_account_move_company_id ON account_move(company_id);
```

### Performance Metrics

**Target SLAs:**
- Page load time (p95): <2 seconds
- API response time (p95): <200ms
- Database query time (p95): <100ms
- Uptime: >99.9%

**Monitoring Tools:**
- Nginx access logs (response times)
- Odoo profiler (code execution times)
- pg_stat_statements (query performance)
- Apache Superset (analytics on metrics)

---

## Security Architecture

### Firewall Rules (UFW on Droplets)

```bash
# Default deny
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (restricted to specific IPs if possible)
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow Odoo (localhost only)
# (Access via Nginx reverse proxy only)

# Enable firewall
ufw enable
```

### SSL Certificate Management

**Renewal Process:**

```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal

# Auto-renewal cron (runs daily)
0 0 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

**Certificate Locations:**
```
/etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem
/etc/letsencrypt/live/erp.insightpulseai.net/privkey.pem
```

### Security Headers

**Enforced via Nginx:**

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

**Verification:**

```bash
curl -I https://erp.insightpulseai.net | grep -E "X-Frame-Options|X-Content-Type|HSTS"
```

---

## Cost Optimization

### Current Monthly Costs

| Service | Plan | Cost |
|---------|------|------|
| **DigitalOcean Droplet (ipai-odoo-erp)** | 4GB RAM, 2 vCPUs | $24/month |
| **DigitalOcean Droplet (ocr-service)** | 8GB RAM, 4 vCPUs, GPU | $48/month |
| **DigitalOcean App Platform (Superset)** | Basic | $5/month |
| **DigitalOcean App Platform (MCP)** | Basic | $5/month |
| **Supabase PostgreSQL** | Free tier | $0/month |
| **Google OAuth** | Free | $0/month |
| **Let's Encrypt SSL** | Free | $0/month |
| **GitHub Actions** | Free tier | $0/month |
| **Total** | | **$82/month** |

### Cost Savings vs SaaS

| SaaS Alternative | Annual Cost | Self-Hosted | Savings |
|------------------|-------------|-------------|---------|
| SAP Concur | $15,000 | Odoo Expense | $15,000 |
| Tableau | $8,400 | Superset | $8,400 |
| Mattermost Enterprise | $12,600 | Self-hosted | $12,600 |
| n8n Cloud | $6,000 | Self-hosted | $6,000 |
| **Total Savings** | | | **$42,000/year** |

**Break-even:** 2 months of self-hosted operation

**ROI:** 512% annually

---

## Appendix

### Reference Links

- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [Supabase Documentation](https://supabase.com/docs)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Let's Encrypt](https://letsencrypt.org/docs/)

### Contact Information

- **Maintainer:** InsightPulse AI Team
- **Support Email:** jgtolentino_rn@yahoo.com
- **GitHub Repository:** https://github.com/jgtolentino/insightpulse-odoo
- **Slack:** #insightpulse-support

---

**Last Updated:** 2025-11-09
**Document Version:** 2.0
**Next Review:** 2025-12-09
