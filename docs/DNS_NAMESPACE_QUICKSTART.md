# DNS Namespace Alignment - Quick Start Guide

**Status**: Ready to Execute
**Estimated Time**: 3-4 hours (including DNS propagation wait)
**Strategy**: Option A+ (Minimal Changes + Strategic Aliases)

---

## Summary

This implementation adds missing DNS records and creates CNAME aliases to align your infrastructure with the PRD, while maintaining all existing production services without disruption.

### What Gets Created

**New DNS Records** (14 total):
- ✅ A records: `staging.*`, `metrics.*`, root domain, `chat.*`, `n8n.*`, `gittodoc.*`
- ✅ CNAME records: `www.*`, `superset.*`, `mcp.*`, `agent.*`, `bi.*` (alias), `api.*` (alias)

**New Services**:
- 🆕 Staging Odoo environment (port 8070)
- 🆕 Grafana metrics dashboard (port 3000)

**Updated Documentation**:
- ✅ PRD.md with correct domain references
- ✅ Key Links section added to PRD

---

## Quick Start (Copy-Paste Ready)

### Step 1: Create DNS Records (5 minutes)

```bash
# Navigate to repo
cd /home/user/insightpulse-odoo

# Test first (dry run)
./scripts/setup-dns-records.sh --dry-run

# Review output, then create records
./scripts/setup-dns-records.sh

# Verify records created
doctl compute domain records list insightpulseai.net
```

**Expected Output**: 14 DNS records created successfully

---

### Step 2: Wait for DNS Propagation (30-60 minutes)

```bash
# Check DNS propagation status
for subdomain in erp staging metrics bi api superset mcp agent chat n8n ocr gittodoc www; do
  echo "=== $subdomain.insightpulseai.net ==="
  dig +short @8.8.8.8 "$subdomain.insightpulseai.net"
  echo ""
done
```

**Ready when**: All subdomains return IP addresses or CNAME targets

---

### Step 3: Setup Staging Odoo (On Server: 165.227.10.178)

```bash
# SSH to server
ssh root@165.227.10.178

# Create staging directory
mkdir -p /root/odoo-staging
cd /root/odoo-staging

# Copy docker-compose files from repo
# (You'll need to git clone or scp the files from infra/docker/odoo-staging/)

# Create .env file
cp .env.example .env
nano .env  # Fill in passwords

# Start staging environment
docker-compose up -d

# Verify containers running
docker ps | grep staging

# Check logs
docker logs -f odoo-staging
```

**Expected Output**: Odoo staging accessible at http://localhost:8070

---

### Step 4: Setup Grafana Metrics (On Server: 165.227.10.178)

```bash
# Create Grafana directory
mkdir -p /root/grafana
cd /root/grafana

# Copy docker-compose files from repo
# (You'll need to git clone or scp the files from infra/docker/grafana/)

# Create .env file
cp .env.example .env
nano .env  # Fill in passwords

# Start Grafana
docker-compose up -d

# Verify container running
docker ps | grep grafana

# Check logs
docker logs -f grafana-metrics
```

**Expected Output**: Grafana accessible at http://localhost:3000

---

### Step 5: Configure Nginx (On Server: 165.227.10.178)

```bash
# Copy Nginx configs from repo
# (You'll need to git clone or scp the files from infra/nginx/)

# Copy staging config
cp infra/nginx/staging.insightpulseai.net.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/staging.insightpulseai.net.conf /etc/nginx/sites-enabled/

# Copy metrics config
cp infra/nginx/metrics.insightpulseai.net.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/metrics.insightpulseai.net.conf /etc/nginx/sites-enabled/

# Test Nginx config
nginx -t

# DO NOT reload yet - wait for SSL certificates
```

---

### Step 6: Issue SSL Certificates (On Server: 165.227.10.178)

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

**Expected Output**: SSL certificates issued successfully, Nginx reloaded

---

### Step 7: Verify All Endpoints

```bash
# Test all HTTPS endpoints
curl -I https://erp.insightpulseai.net
curl -I https://staging.insightpulseai.net
curl -I https://metrics.insightpulseai.net
curl -I https://superset.insightpulseai.net
curl -I https://bi.insightpulseai.net  # Should redirect to superset
curl -I https://api.insightpulseai.net  # Should redirect to erp
curl -I https://mcp.insightpulseai.net
curl -I https://agent.insightpulseai.net

# All should return HTTP 200 or 302
```

---

## Troubleshooting

### DNS Not Propagating

```bash
# Check DigitalOcean dashboard
doctl compute domain records list insightpulseai.net

# Check from different DNS servers
dig @1.1.1.1 staging.insightpulseai.net
dig @8.8.8.8 staging.insightpulseai.net

# Check global propagation: https://www.whatsmydns.net/
```

### SSL Certificate Fails

```bash
# Verify DNS resolves first
dig +short staging.insightpulseai.net

# Check ports 80/443 are accessible
nc -zv 165.227.10.178 80
nc -zv 165.227.10.178 443

# Check Nginx error logs
tail -f /var/log/nginx/error.log
```

### Docker Containers Not Starting

```bash
# Check logs
docker logs odoo-staging
docker logs grafana-metrics

# Check port conflicts
netstat -tlnp | grep :8070
netstat -tlnp | grep :3000

# Verify .env file has correct passwords
cat /root/odoo-staging/.env
cat /root/grafana/.env
```

---

## Success Checklist

After implementation, verify:

- [ ] DNS Records: All 14 records created and resolving
- [ ] Staging Odoo: Accessible at https://staging.insightpulseai.net
- [ ] Grafana: Accessible at https://metrics.insightpulseai.net
- [ ] CNAME Aliases: bi.* and api.* redirect correctly
- [ ] SSL Certificates: Valid and auto-renewing
- [ ] Production Services: Still working (erp, superset, mcp, agent)
- [ ] PRD Documentation: Updated with correct URLs

---

## Files Created/Modified

**New Files**:
- `docs/DNS_NAMESPACE_ALIGNMENT_PLAN.md` - Complete implementation plan
- `docs/DNS_NAMESPACE_QUICKSTART.md` - This file
- `infra/nginx/staging.insightpulseai.net.conf` - Staging Nginx config
- `infra/nginx/metrics.insightpulseai.net.conf` - Metrics Nginx config
- `infra/docker/odoo-staging/docker-compose.yml` - Staging Docker config
- `infra/docker/odoo-staging/odoo.conf` - Staging Odoo config
- `infra/docker/odoo-staging/.env.example` - Staging environment template
- `infra/docker/grafana/docker-compose.yml` - Grafana Docker config
- `infra/docker/grafana/.env.example` - Grafana environment template
- `infra/docker/grafana/provisioning/datasources/postgresql.yml` - Grafana datasources
- `infra/docker/grafana/provisioning/dashboards/default.yml` - Grafana dashboard config

**Modified Files**:
- `scripts/setup-dns-records.sh` - Enhanced with staging, metrics, and aliases
- `PRD.md` - Updated with correct domain references and Key Links section

---

## Next Steps After Implementation

1. **Configure Grafana Dashboards**
   - Connect to Odoo PostgreSQL datasources
   - Create business metrics dashboards
   - Setup alerting (optional)

2. **Setup Staging Data**
   - Copy production database to staging
   - Anonymize sensitive data
   - Configure staging-specific settings

3. **Update CI/CD**
   - Add staging deployment workflow
   - Configure automated testing against staging
   - Setup metrics collection in CI

4. **Documentation**
   - Update README.md with new URLs
   - Update INFRASTRUCTURE_ARCHITECTURE.md
   - Create runbooks for common operations

---

## Cost Impact

**$0** - All services run on existing infrastructure.

---

## Support Resources

- **DNS Implementation Guide**: `DNS_IMPLEMENTATION_GUIDE.md`
- **DNS Audit Report**: `docs/DNS_AUDIT_REPORT.md`
- **Full Alignment Plan**: `docs/DNS_NAMESPACE_ALIGNMENT_PLAN.md`
- **DigitalOcean Docs**: https://docs.digitalocean.com/products/networking/dns/
- **Let's Encrypt Docs**: https://letsencrypt.org/docs/
- **Nginx Docs**: https://nginx.org/en/docs/

---

**Status**: ✅ Ready to execute
**Next Action**: Run `./scripts/setup-dns-records.sh --dry-run`
