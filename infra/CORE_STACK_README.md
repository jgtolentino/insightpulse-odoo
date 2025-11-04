# InsightPulse Core Stack

Clean, production-ready infrastructure for InsightPulse Finance SSC platform.

## Architecture Overview

### 6-Endpoint Core Topology

| Purpose | Subdomain | Host | Port |
|---------|-----------|------|------|
| **Landing** | `insightpulseai.net` + `www` | **App Platform** (landing app) | 443 |
| **ERP** | `erp.insightpulseai.net` | **Droplet** @ 165.227.10.178 (SFO2) | 443→8069 |
| **Analytics** | `superset.insightpulseai.net` | **App Platform** (Superset) | 443 |
| **OCR** | `ocr.insightpulseai.net` | **Droplet** @ 188.166.237.231 (SGP1) | 443 |
| **AI Agent** | `agent.insightpulseai.net` | **Droplet** @ 165.227.10.178 (proxy) | 443→Agents |
| **Skill Hub** | `mcp.insightpulseai.net` | **App Platform** (optional) | 443 |

**Mobile App**: Uses ERP and Agent endpoints over HTTPS (no separate subdomain)

---

## DNS Configuration

### DigitalOcean DNS Records (insightpulseai.net)

```
Host: @
Type: CNAME
Value: [your-landing-app].ondigitalocean.app
TTL: 300

Host: www
Type: CNAME
Value: insightpulseai.net
TTL: 300

Host: erp
Type: A
Value: 165.227.10.178
TTL: 300

Host: ocr
Type: A
Value: 188.166.237.231
TTL: 300

Host: superset
Type: CNAME
Value: superset-[id].ondigitalocean.app
TTL: 300

Host: agent
Type: A
Value: 165.227.10.178
TTL: 300

Host: mcp (optional)
Type: CNAME
Value: pulse-hub-web-[id].ondigitalocean.app
TTL: 300

Host: @
Type: CAA
Value: 0 issue "letsencrypt.org"
TTL: 3600
```

**Validation:**
```bash
dig +short insightpulseai.net CNAME
dig +short erp.insightpulseai.net A
dig +short agent.insightpulseai.net A
dig +short ocr.insightpulseai.net A
dig +short superset.insightpulseai.net CNAME
```

---

## Infrastructure Details

### ERP Droplet (165.227.10.178)

**Services:**
- Odoo 19.0 Enterprise (ports 8069, 8072)
- Nginx reverse proxy (ports 80, 443)
- Agent reverse proxy (to DO Agents platform)

**Nginx Configuration:**
- `/etc/nginx/sites-available/erp.insightpulseai.net.conf`
- `/etc/nginx/sites-available/agent.insightpulseai.net.conf`

**TLS Certificates:**
- Let's Encrypt via certbot
- Auto-renewal via snap timer
- Domains: `erp.insightpulseai.net`, `agent.insightpulseai.net`

**Firewall (UFW):**
- Allow: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Deny: 8069, 8072 (Odoo direct access)

### OCR Droplet (188.166.237.231)

**Services:**
- PaddleOCR-VL service
- Nginx reverse proxy
- OpenAI API integration

**Region:** Singapore (SGP1) - closer to APAC users

### App Platform Services

**Superset (superset.insightpulseai.net):**
- Database: PostgreSQL (Supabase spdtwktxdalcfigzeqrz)
- Schema: `superset` (isolated via search_path)
- Connection: `postgresql://...?options=-csearch_path%3Dsuperset`

**Landing App (insightpulseai.net):**
- Static site or Next.js app
- Attached to apex domain
- Force HTTPS enabled

**Skill Hub (mcp.insightpulseai.net - optional):**
- Public MCP tool catalog
- OpenAPI broker for Custom GPT Actions
- CORS configured for ERP, Superset, mobile app

### AI Agent (agent.insightpulseai.net)

**Architecture:**
- DNS: `agent.insightpulseai.net` → ERP droplet (165.227.10.178)
- Nginx reverse proxy to: `https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run`
- TLS termination at Nginx
- CORS headers for ERP integration

**Why reverse proxy?**
- Custom domain (DO Agents doesn't support custom domains yet)
- TLS certificate control
- CORS and security header management
- Unified `insightpulseai.net` brand

---

## Deployment

### Prerequisites

```bash
# Install doctl (DigitalOcean CLI)
brew install doctl  # macOS
# OR
snap install doctl  # Linux

# Authenticate
doctl auth init
```

### One-Command Deployment

```bash
cd /path/to/insightpulse-odoo
./scripts/deploy-core-stack.sh
```

**This script:**
1. ✅ Deploys Nginx configurations to ERP droplet
2. ✅ Installs certbot (if not present)
3. ✅ Obtains TLS certificates for both domains
4. ✅ Configures UFW firewall
5. ✅ Enables unattended security updates
6. ✅ Validates deployment

### Manual Deployment

#### 1. Deploy Nginx Configs

```bash
scp infra/nginx/*.conf root@165.227.10.178:/etc/nginx/sites-available/
ssh root@165.227.10.178

# Enable sites
ln -s /etc/nginx/sites-available/erp.insightpulseai.net.conf /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/agent.insightpulseai.net.conf /etc/nginx/sites-enabled/

# Test and reload
nginx -t
systemctl reload nginx
```

#### 2. Obtain TLS Certificates

```bash
ssh root@165.227.10.178

# Install certbot
snap install core && snap refresh core
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

# Obtain certificates
certbot --nginx \
  -d erp.insightpulseai.net \
  -d agent.insightpulseai.net \
  --non-interactive \
  --agree-tos \
  --redirect \
  --email jgtolentino_rn@yahoo.com \
  --no-eff-email
```

#### 3. Configure Firewall

```bash
ssh root@165.227.10.178

# Reset UFW
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow public services
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Deny direct Odoo access
ufw deny 8069/tcp comment 'Odoo (use HTTPS)'
ufw deny 8072/tcp comment 'Odoo longpolling'

# Enable
ufw --force enable
ufw status verbose
```

#### 4. Enable Auto-Updates

```bash
ssh root@165.227.10.178
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## Validation

### Connectivity Tests

```bash
# HTTPS endpoints
curl -I https://erp.insightpulseai.net
curl -I https://agent.insightpulseai.net
curl -I https://superset.insightpulseai.net
curl -I https://ocr.insightpulseai.net

# Direct port access (should be blocked)
nc -zv erp.insightpulseai.net 8069  # Should fail
nc -zv erp.insightpulseai.net 8072  # Should fail
```

### TLS Certificate Check

```bash
ssh root@165.227.10.178 'certbot certificates'

# Expected output:
# Found the following certs:
#   Certificate Name: erp.insightpulseai.net
#     Domains: erp.insightpulseai.net agent.insightpulseai.net
#     Expiry Date: [90 days from now]
#     Certificate Path: /etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem
```

### Firewall Status

```bash
ssh root@165.227.10.178 'ufw status verbose'

# Expected output:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW IN    Anywhere
# 80/tcp                     ALLOW IN    Anywhere
# 443/tcp                    ALLOW IN    Anywhere
# 8069/tcp                   DENY IN     Anywhere
# 8072/tcp                   DENY IN     Anywhere
```

### Nginx Status

```bash
ssh root@165.227.10.178 'systemctl status nginx'

# Should show: active (running)
```

### Agent Proxy Test

```bash
curl -I https://agent.insightpulseai.net

# Should return:
# HTTP/2 200
# (or redirect to DO Agents auth page)
```

---

## GitHub Actions Integration

### Add OPENAI_API_KEY Secret

1. Go to: https://github.com/your-org/insightpulse-odoo/settings/secrets/actions
2. Click "New repository secret"
3. Name: `OPENAI_API_KEY`
4. Value: `sk-...` (your OpenAI API key)
5. Click "Add secret"

### Update Workflows

Workflows that use OpenAI:
- `.github/workflows/superset-postgres-guard.yml` (if using AI features)
- Any custom workflows for AI-powered tools

**Example usage:**
```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test
```

---

## Security Hardening

### Droplet Security

**✅ Implemented:**
- UFW firewall (ports 22, 80, 443 only)
- TLS via Let's Encrypt
- Unattended security updates
- Direct Odoo port access blocked
- HTTPS forced via Nginx redirect

**🔒 Additional Recommendations:**
- Enable DigitalOcean Cloud Firewall (team-wide rules)
- Add fail2ban for SSH brute-force protection
- Configure rate limiting in Nginx
- Enable Odoo security headers (CSP, HSTS)
- Set up daily backups with retention policy

### App Platform Security

**✅ Required:**
- Attach custom domains with TLS
- Enable "Force HTTPS" in DO dashboard
- Configure CORS allowed origins
- Store secrets in App Platform environment variables (not GitHub)

**Environment Variables (per app):**
- `OPENAI_API_KEY` (if using AI features)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` (if using Supabase)
- `DATABASE_URL` (connection string with search_path for Superset)

---

## Monitoring & Maintenance

### Health Checks

**Automated (GitHub Actions):**
- Superset PostgreSQL guard (daily)
- Visual parity tests (on PR)
- Database drift detection (daily)

**Manual:**
```bash
# Nginx logs
ssh root@165.227.10.178 'tail -f /var/log/nginx/erp.insightpulseai.net.access.log'
ssh root@165.227.10.178 'tail -f /var/log/nginx/agent.insightpulseai.net.error.log'

# Odoo logs
ssh root@165.227.10.178 'tail -f /var/log/odoo/odoo.log'

# System resources
ssh root@165.227.10.178 'htop'
```

### Certificate Renewal

**Automatic:**
- Certbot snap timer runs twice daily
- Check status: `ssh root@165.227.10.178 'systemctl list-timers | grep certbot'`

**Manual test:**
```bash
ssh root@165.227.10.178 'certbot renew --dry-run'
```

### Backup Strategy

**Droplets:**
- Enable daily backups in DO dashboard
- Retention: 4 snapshots (weekly rotation)

**Databases:**
- Supabase automatic backups (Pro plan: daily)
- Custom backup script to DigitalOcean Spaces (optional)

**Application State:**
- Odoo filestore: `/var/lib/odoo/filestore/`
- Odoo database: PostgreSQL dump via pg_dump

---

## Troubleshooting

### DNS Not Resolving

```bash
# Flush local DNS cache
sudo dscacheutil -flushcache  # macOS
sudo systemd-resolve --flush-caches  # Linux

# Check DO DNS
doctl compute domain records list insightpulseai.net
```

### TLS Certificate Issues

```bash
# Check certificate expiration
ssh root@165.227.10.178 'certbot certificates'

# Force renewal
ssh root@165.227.10.178 'certbot renew --force-renewal'

# Check Nginx SSL config
ssh root@165.227.10.178 'nginx -t'
```

### Agent Proxy Not Working

```bash
# Check Nginx logs
ssh root@165.227.10.178 'tail -100 /var/log/nginx/agent.insightpulseai.net.error.log'

# Test upstream connectivity
ssh root@165.227.10.178 'curl -I https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run'

# Verify DNS resolver
ssh root@165.227.10.178 'nginx -T | grep resolver'
```

### Odoo Not Accessible

```bash
# Check Odoo service
ssh root@165.227.10.178 'systemctl status odoo19'

# Check Nginx proxy
ssh root@165.227.10.178 'curl -I http://127.0.0.1:8069'

# Verify firewall NOT blocking internally
ssh root@165.227.10.178 'ufw status | grep 8069'
```

---

## Migration Notes

### From Azure to DigitalOcean

**Completed:**
- ✅ OCR service: Azure ACI → DO Droplet (SGP1)
- ✅ Superset: SQLite → PostgreSQL (Supabase)
- ✅ Cost: $100/month → <$20/month (87% reduction)

**Architecture Changes:**
- Removed: Azure ACR, ACI, Document Intelligence, Azure OpenAI, Key Vault
- Added: DigitalOcean App Platform, Droplets, Agents
- Database: Supabase PostgreSQL (free tier)
- OCR: PaddleOCR-VL + OpenAI API (direct, cheaper than Azure wrapper)

### Schema Separation

**Supabase schemas:**
- `superset` - Superset metadata (dashboards, charts, datasets)
- `ops` - Application tables (task_queue, visual_baseline, forum_posts)
- `scout_bronze` - Raw ingestion (expense_raw, ariba_cxml, crm_accounts, ppm_projects)
- `scout_silver` - Cleaned data
- `scout_gold` - Analytics-ready data

**Applied:** `supabase/migrations/002_schema_separation.sql`

---

## Cost Breakdown

| Service | Provider | Cost/Month |
|---------|----------|-----------|
| ERP Droplet (2GB) | DigitalOcean | $12 |
| OCR Droplet (1GB) | DigitalOcean | $6 |
| Superset App | DigitalOcean | $0 (starter tier) |
| Landing App | DigitalOcean | $0 (static) |
| Database | Supabase | $0 (free tier) |
| OpenAI API | OpenAI | ~$5 (usage-based) |
| **Total** | | **~$23/month** |

**Previous (Azure):** ~$100/month

---

## Future Enhancements

### Phase 2 (Optional)

- [ ] Add `api.insightpulseai.net` for mobile backend API
- [ ] Bootstrap mobile PWA on `app.insightpulseai.net`
- [ ] Add fail2ban for SSH protection
- [ ] Configure Nginx rate limiting
- [ ] Set up Prometheus + Grafana monitoring
- [ ] Add Redis for Superset caching
- [ ] Implement block storage volumes for Odoo data
- [ ] Add staging environment

### Phase 3 (Future)

- [ ] Multi-region deployment (US + APAC)
- [ ] Load balancer for high availability
- [ ] Kubernetes for container orchestration
- [ ] CI/CD pipeline for Odoo module deployment
- [ ] Automated integration tests
- [ ] Blue-green deployment strategy

---

## Support

**Primary Contact:** Jake Tolentino (jgtolentino_rn@yahoo.com)

**Resources:**
- DigitalOcean Dashboard: https://cloud.digitalocean.com/
- Supabase Dashboard: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
- GitHub Repository: https://github.com/jgtolentino/insightpulse-odoo

**Emergency Contacts:**
- ERP Down: Check Odoo service and Nginx on 165.227.10.178
- TLS Issues: Run certbot renew and reload Nginx
- Database Issues: Check Supabase dashboard and connection pooler
- Agent Issues: Check Nginx reverse proxy logs and upstream connectivity
