# DNS Configuration Guide

## Overview
This document provides the exact DNS records needed to configure custom domains for the InsightPulse deployment.

## DNS Records Required

### Domain: insightpulseai.net

Configure these records in your domain registrar (e.g., Namecheap, GoDaddy, Cloudflare):

| Type | Name | Value | TTL | Status | Notes |
|------|------|-------|-----|--------|-------|
| **CNAME** | `mcp` | `mcp-coordinator-<app-id>.ondigitalocean.app.` | 3600 | ⏳ Pending | Replace `<app-id>` after deployment |
| **CNAME** | `superset` | `superset-analytics-<app-id>.ondigitalocean.app.` | 3600 | ⏳ Pending | Replace `<app-id>` after deployment |
| **CNAME** | `odoo` | `odoo-saas-platform-<app-id>.ondigitalocean.app.` | 3600 | ⏳ Pending | Replace `<app-id>` after deployment |

## Step-by-Step Configuration

### Step 1: Deploy Applications
First, deploy all three applications to DigitalOcean App Platform:

```bash
# Deploy services and capture app IDs
doctl apps create --spec infra/do/odoo-saas-platform.yaml
doctl apps create --spec infra/superset/superset-app.yaml
doctl apps create --spec infra/do/mcp-coordinator.yaml

# List all apps to get their URLs
doctl apps list
```

### Step 2: Get App URLs
After deployment, retrieve the default DigitalOcean URLs:

```bash
# Get Odoo URL
doctl apps get <ODOO_APP_ID> --format URL

# Get Superset URL
doctl apps get <SUPERSET_APP_ID> --format URL

# Get MCP URL
doctl apps get <MCP_APP_ID> --format URL
```

Example output:
```
odoo-saas-platform-abc123.ondigitalocean.app
superset-analytics-def456.ondigitalocean.app
mcp-coordinator-ghi789.ondigitalocean.app
```

### Step 3: Configure DNS in Domain Registrar

#### Using Namecheap
1. Log in to Namecheap account
2. Go to Domain List → Manage → Advanced DNS
3. Add the following CNAME records:

```
Type: CNAME Record
Host: mcp
Value: mcp-coordinator-<app-id>.ondigitalocean.app.
TTL: Automatic (or 3600)

Type: CNAME Record
Host: superset
Value: superset-analytics-<app-id>.ondigitalocean.app.
TTL: Automatic (or 3600)

Type: CNAME Record
Host: odoo
Value: odoo-saas-platform-<app-id>.ondigitalocean.app.
TTL: Automatic (or 3600)
```

#### Using Cloudflare
1. Log in to Cloudflare dashboard
2. Select domain: insightpulseai.net
3. Go to DNS → Records
4. Add records:

```
Type: CNAME
Name: mcp
Target: mcp-coordinator-<app-id>.ondigitalocean.app
Proxy status: DNS only (grey cloud)
TTL: Auto

Type: CNAME
Name: superset
Target: superset-analytics-<app-id>.ondigitalocean.app
Proxy status: DNS only (grey cloud)
TTL: Auto

Type: CNAME
Name: odoo
Target: odoo-saas-platform-<app-id>.ondigitalocean.app
Proxy status: DNS only (grey cloud)
TTL: Auto
```

**Important**: Use "DNS only" mode initially. Enable Cloudflare proxy (orange cloud) only after SSL is working.

#### Using GoDaddy
1. Log in to GoDaddy account
2. Go to My Products → Domain → DNS
3. Add records:

```
Type: CNAME
Name: mcp
Value: mcp-coordinator-<app-id>.ondigitalocean.app
TTL: 1 Hour

Type: CNAME
Name: superset
Value: superset-analytics-<app-id>.ondigitalocean.app
TTL: 1 Hour

Type: CNAME
Name: odoo
Value: odoo-saas-platform-<app-id>.ondigitalocean.app
TTL: 1 Hour
```

### Step 4: Verify DNS Propagation

Wait 5-60 minutes for DNS propagation, then verify:

```bash
# Check MCP
dig mcp.insightpulseai.net
nslookup mcp.insightpulseai.net

# Check Superset
dig superset.insightpulseai.net
nslookup superset.insightpulseai.net

# Check Odoo
dig odoo.insightpulseai.net
nslookup odoo.insightpulseai.net
```

Expected output:
```
mcp.insightpulseai.net. 3600 IN CNAME mcp-coordinator-<app-id>.ondigitalocean.app.
```

### Step 5: Add Domains to DigitalOcean Apps

The domains are already configured in the YAML specs, but verify in DO dashboard:

1. Go to DigitalOcean App Platform
2. Open each app
3. Navigate to Settings → Domains
4. Verify custom domain is listed and SSL is "Active"

## SSL/TLS Certificate Status

DigitalOcean App Platform automatically provisions Let's Encrypt SSL certificates for custom domains.

### Certificate Provisioning Timeline
1. **0-5 minutes**: DNS verification
2. **5-15 minutes**: Certificate issuance
3. **15+ minutes**: Certificate active

### Check SSL Status

```bash
# Via DigitalOcean CLI
doctl apps get <APP_ID> --format Domains

# Via web browser
curl -I https://mcp.insightpulseai.net
curl -I https://superset.insightpulseai.net
curl -I https://odoo.insightpulseai.net
```

### Troubleshooting SSL Issues

**Problem**: SSL certificate not provisioning
```bash
# Check DNS is correctly pointed
dig mcp.insightpulseai.net

# Verify in DO dashboard
doctl apps get <APP_ID>

# Check domain configuration
doctl apps get <APP_ID> --format Domains
```

**Solution**:
1. Ensure CNAME points to correct DO URL (with trailing dot)
2. Wait 24-48 hours for DNS propagation
3. Contact DigitalOcean support if issue persists

## Final URLs

After DNS configuration and SSL provisioning:

| Service | URL | SSL | Status |
|---------|-----|-----|--------|
| **MCP Coordinator** | https://mcp.insightpulseai.net | ✅ Auto | ⏳ Pending DNS |
| **Superset Analytics** | https://superset.insightpulseai.net | ✅ Auto | ⏳ Pending DNS |
| **Odoo SaaS Platform** | https://odoo.insightpulseai.net | ✅ Auto | ⏳ Pending DNS |

## Testing

After DNS propagation and SSL activation:

```bash
# Test MCP health
curl -f https://mcp.insightpulseai.net/health
# Expected: {"status":"ok"}

# Test Superset health
curl -f https://superset.insightpulseai.net/health
# Expected: HTTP 200 OK

# Test Odoo health
curl -f https://odoo.insightpulseai.net/web/health
# Expected: HTTP 200 OK

# Test SSL certificates
openssl s_client -connect mcp.insightpulseai.net:443 -servername mcp.insightpulseai.net < /dev/null
openssl s_client -connect superset.insightpulseai.net:443 -servername superset.insightpulseai.net < /dev/null
openssl s_client -connect odoo.insightpulseai.net:443 -servername odoo.insightpulseai.net < /dev/null
```

## Alternative: Using A Records

If your DNS provider doesn't support CNAME for apex domain or subdomains, use A records:

1. Get the IP address of the DO app:
```bash
dig odoo-saas-platform-<app-id>.ondigitalocean.app A
```

2. Create A records instead of CNAME:
```
Type: A
Name: mcp
Value: <IP_ADDRESS>
TTL: 3600
```

**Warning**: A records are less flexible than CNAME. If DigitalOcean changes the IP, you'll need to update DNS manually.

## DNS Propagation Checker

Use online tools to verify DNS propagation globally:
- https://dnschecker.org
- https://www.whatsmydns.net

Enter:
- `mcp.insightpulseai.net` (CNAME)
- `superset.insightpulseai.net` (CNAME)
- `odoo.insightpulseai.net` (CNAME)

## Support

If you encounter issues:
1. **DigitalOcean Support**: https://cloud.digitalocean.com/support
2. **DNS Registrar Support**: Contact your domain provider
3. **Community Forums**: https://www.digitalocean.com/community

## Checklist

- [ ] Deploy all applications to DO App Platform
- [ ] Retrieve app URLs from `doctl apps list`
- [ ] Configure CNAME records in domain registrar
- [ ] Wait for DNS propagation (5-60 minutes)
- [ ] Verify DNS with `dig` or `nslookup`
- [ ] Check SSL certificate status in DO dashboard
- [ ] Test health endpoints via HTTPS
- [ ] Update internal service URLs if needed

## Security Notes

### HTTPS Only
All services are configured to use HTTPS only. HTTP requests are automatically redirected to HTTPS.

### HSTS (HTTP Strict Transport Security)
DigitalOcean App Platform automatically enables HSTS for custom domains.

### CAA Records (Optional)
Add CAA records to restrict which Certificate Authorities can issue certificates:

```
Type: CAA
Name: @
Value: 0 issue "letsencrypt.org"
```

This ensures only Let's Encrypt can issue SSL certificates for your domain.

## Maintenance

### Renewing SSL Certificates
- **Automatic**: DigitalOcean handles renewal (Let's Encrypt certificates valid 90 days)
- **No action required**: Auto-renewed 30 days before expiration

### Updating DNS Records
If you need to migrate to a different app:
1. Update CNAME to point to new app URL
2. Wait for DNS propagation
3. Verify new app is responding

### Monitoring DNS
Set up monitoring for DNS resolution:
```bash
# Create a simple monitoring script
#!/bin/bash
for domain in mcp.insightpulseai.net superset.insightpulseai.net odoo.insightpulseai.net; do
  if dig +short $domain | grep -q "ondigitalocean.app"; then
    echo "✅ $domain - OK"
  else
    echo "❌ $domain - FAILED"
  fi
done
```

Run this script periodically (e.g., via cron) to ensure DNS is always configured correctly.
