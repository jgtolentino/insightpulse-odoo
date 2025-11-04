# Cloudflare WAF Configuration Guide

## Overview

This guide explains how to configure Cloudflare as a Web Application Firewall (WAF) in front of DigitalOcean infrastructure while maintaining proper SSL/TLS certificate management.

**Contact**: jgtolentino_rn@yahoo.com | support@insightpulseai.com

## Architecture

```
User → Cloudflare (WAF) → Origin (DigitalOcean)
                           ├─ App Platform (MCP, Superset)
                           └─ Droplets (ERP, OCR, LLM)
```

## The Cloudflare + DigitalOcean Challenge

### Problem

When you enable Cloudflare's proxy (orange cloud ☁️) on a domain:

1. **Cloudflare terminates SSL/TLS** at their edge
2. **Cloudflare connects to your origin** using a new SSL/TLS connection
3. **Let's Encrypt HTTP-01 challenges fail** because:
   - HTTP-01 requires direct access to `/.well-known/acme-challenge/` on port 80
   - Cloudflare's proxy intercepts this traffic
   - Your origin never receives the validation request

### Solution

Use **DNS-01 challenges** instead of HTTP-01:

- **DNS-01** validates domain ownership via DNS TXT records
- **Works perfectly behind proxies** (no HTTP traffic needed)
- **Cloudflare provides an API** for automated DNS updates
- **Caddy supports DNS-01** with the Cloudflare DNS provider

## Configuration by Infrastructure Type

### 1. Droplets (ERP, OCR, LLM)

**Status**: ✅ Can be proxied (orange cloud)

#### DNS Configuration

```dns
Type: A
Name: erp
Content: 165.227.10.178
Proxy: Enabled (orange cloud ☁️)
TTL: Auto
```

```dns
Type: A
Name: ocr
Content: 188.166.237.231
Proxy: Enabled (orange cloud ☁️)
TTL: Auto
```

#### Origin Configuration (Caddy with DNS-01)

**File**: `infra/caddy/Caddyfile`

```caddy
{
  email jgtolentino_rn@yahoo.com
}

erp.insightpulseai.net {
  encode zstd gzip

  tls {
    dns cloudflare {env.CLOUDFLARE_DNS_API_TOKEN}
  }

  reverse_proxy odoo:8069
}

ocr.insightpulseai.net {
  encode zstd gzip

  tls {
    dns cloudflare {env.CLOUDFLARE_DNS_API_TOKEN}
  }

  reverse_proxy ocr:8000
}
```

**File**: `infra/caddy/docker-compose.yml`

```yaml
services:
  caddy:
    image: caddy:2-alpine
    environment:
      - CLOUDFLARE_DNS_API_TOKEN=${CLOUDFLARE_DNS_API_TOKEN}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
```

#### Environment Variables

Create `.env` file:

```bash
# Cloudflare DNS API token
# Permissions: Zone.DNS:Edit
CLOUDFLARE_DNS_API_TOKEN=your_token_here
```

#### Deployment Steps

1. **Generate Cloudflare API Token**
   - Go to https://dash.cloudflare.com/profile/api-tokens
   - Click "Create Token"
   - Use "Edit zone DNS" template
   - Select zone: `insightpulseai.net`
   - Permissions: `Zone.DNS:Edit`
   - Copy the token

2. **SSH into Droplet**
   ```bash
   ssh root@165.227.10.178
   ```

3. **Set Environment Variable**
   ```bash
   export CLOUDFLARE_DNS_API_TOKEN="your_token_here"

   # Or add to /etc/environment for persistence
   echo "CLOUDFLARE_DNS_API_TOKEN=your_token_here" >> /etc/environment
   ```

4. **Deploy Caddy**
   ```bash
   cd /opt/stack
   docker-compose -f infra/caddy/docker-compose.yml up -d
   ```

5. **Enable Orange Cloud in Cloudflare**
   - Go to Cloudflare DNS settings
   - Click the cloud icon next to `erp` A record
   - Should turn orange ☁️

6. **Verify Certificate**
   ```bash
   # Check certificate issuer
   echo | openssl s_client -servername erp.insightpulseai.net \
     -connect erp.insightpulseai.net:443 2>/dev/null | \
     openssl x509 -noout -issuer

   # Expected: issuer=C = US, O = Let's Encrypt, CN = R11
   ```

### 2. App Platform (MCP, Superset)

**Status**: ⚠️ Keep DNS-only (grey cloud) until certificates are issued

#### DNS Configuration (Initial)

```dns
Type: CNAME
Name: mcp
Content: pulse-hub-web-an645.ondigitalocean.app
Proxy: Disabled (grey cloud ☁)
TTL: Auto
```

```dns
Type: CNAME
Name: superset
Content: superset-nlavf.ondigitalocean.app
Proxy: Disabled (grey cloud ☁)
TTL: Auto
```

#### Why DNS-Only Initially?

1. **DigitalOcean issues certificates** for custom domains using HTTP-01
2. **HTTP-01 requires direct access** (can't be proxied)
3. **Once certificate is issued**, you can optionally enable proxy

#### Steps

1. **Add Custom Domain in DigitalOcean**
   - Go to App Platform → Settings → Domains
   - Add domain: `mcp.insightpulseai.net`
   - DigitalOcean will show DNS configuration

2. **Keep Cloudflare DNS-Only**
   - Add CNAME record in Cloudflare
   - **Keep grey cloud** (proxy disabled)
   - TTL: Auto

3. **Wait for Certificate Issuance**
   - DigitalOcean will issue Let's Encrypt certificate
   - Can take 5-15 minutes
   - Check in App Platform → Settings → Domains

4. **Enable Force HTTPS**
   - In App Platform domain settings
   - Enable "Force HTTPS"

5. **Optional: Enable Cloudflare Proxy**
   - After certificate is issued
   - Click grey cloud to turn orange
   - **Note**: If you see 525 errors, switch back to grey

#### Recommendation

For App Platform apps, **keep DNS-only (grey cloud)**:

- ✅ DigitalOcean's TLS is already strong
- ✅ DigitalOcean provides DDoS protection
- ✅ Fewer SSL/TLS handshake issues
- ✅ Simpler certificate management
- ⚠️ Orange cloud adds another proxy layer (may cause issues)

## Health Checks with WAF

### The 403 Problem

When Cloudflare's WAF is enabled, automated health checks may return **HTTP 403** ("Access denied") because:

- Cloudflare's Bot Fight Mode blocks automated requests
- WAF rules may block certain user agents
- Rate limiting may trigger on repeated requests

### Solution: Origin Health Checks

Check health **directly at origin IP**, bypassing Cloudflare:

```bash
# Check ERP origin (bypass Cloudflare)
curl -k -H "Host: erp.insightpulseai.net" \
  https://165.227.10.178/web/health

# Expected: HTTP 200 (not 403)
```

### Health Check Strategy

#### 1. Public Health Checks (via WAF)

**Accept 403 as valid** (indicates WAF is working):

```bash
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  https://erp.insightpulseai.net/web/health)

# Accept 200-3xx and 403
if [[ "$HTTP_CODE" =~ ^(200|301|302|307|308|403)$ ]]; then
  echo "✓ Healthy (via WAF)"
fi
```

#### 2. Origin Health Checks (bypass WAF)

**Check origin directly** to verify app is truly healthy:

```bash
HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" \
  -H "Host: erp.insightpulseai.net" \
  https://165.227.10.178/web/health)

# Expect 200-3xx (not 403)
if [[ "$HTTP_CODE" =~ ^(200|301|302|307|308)$ ]]; then
  echo "✓ Healthy (origin)"
else
  echo "✗ Unhealthy (HTTP $HTTP_CODE)"
fi
```

### Smoke Test Script

**File**: `scripts/smoke_test_production.sh`

```bash
#!/bin/bash

# Public health (via WAF) - accepts 403
check_health "ERP (WAF)" "https://erp.insightpulseai.net/web/health"

# Origin health (bypass WAF) - expects 200
check_origin "ERP (Origin)" "165.227.10.178" "/web/health" \
  "erp.insightpulseai.net"
```

### GitHub Actions Workflow

**File**: `.github/workflows/health-monitor.yml`

```yaml
- name: Check ERP Origin
  run: |
    HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" \
      -H "Host: erp.insightpulseai.net" \
      "https://165.227.10.178/web/health")

    if [[ "$HTTP_CODE" =~ ^(200|301|302|307|308)$ ]]; then
      echo "✓ ERP origin healthy"
    else
      echo "✗ ERP origin unhealthy: HTTP $HTTP_CODE"
      exit 1
    fi
```

## Cloudflare Settings

### SSL/TLS Configuration

Go to Cloudflare → SSL/TLS:

| Setting | Value | Reason |
|---------|-------|--------|
| **SSL/TLS encryption mode** | Full (strict) | Validates origin certificate |
| **Always Use HTTPS** | On | Force HTTPS redirects |
| **Minimum TLS Version** | TLS 1.2 | Security best practice |
| **Opportunistic Encryption** | On | Performance optimization |
| **TLS 1.3** | On | Latest TLS version |
| **Automatic HTTPS Rewrites** | On | Prevents mixed content |

### Security Settings

Go to Cloudflare → Security:

| Setting | Value | Notes |
|---------|-------|-------|
| **Security Level** | Medium | Balance security & usability |
| **Bot Fight Mode** | On | Blocks automated attacks |
| **Challenge Passage** | 30 minutes | User experience |
| **Browser Integrity Check** | On | Blocks known bad bots |

### Firewall Rules (Optional)

#### Rate Limiting for OCR

```
Expression: (http.host eq "ocr.insightpulseai.net")
Action: Rate Limit
Requests: 100 per minute
Duration: 1 hour
```

#### Allow GitHub Actions

```
Expression:
  (http.host eq "erp.insightpulseai.net") and
  (ip.geoip.asnum eq 36459)  # GitHub's ASN
Action: Allow
```

## Monitoring & Troubleshooting

### Check Certificate Details

```bash
# Via Cloudflare (edge)
echo | openssl s_client -servername erp.insightpulseai.net \
  -connect erp.insightpulseai.net:443 2>/dev/null | \
  openssl x509 -noout -text

# Direct to origin (bypass Cloudflare)
echo | openssl s_client -servername erp.insightpulseai.net \
  -connect 165.227.10.178:443 2>/dev/null | \
  openssl x509 -noout -text
```

### Cloudflare Security Events

1. Go to Cloudflare → Security → Events
2. Filter by domain (e.g., `erp.insightpulseai.net`)
3. Review blocked requests
4. Adjust rules if legitimate traffic is blocked

### Common Issues

#### Issue: 525 SSL Handshake Failed

**Cause**: Origin certificate invalid or expired

**Solution**:
```bash
# Check origin certificate
ssh root@165.227.10.178
docker logs caddy

# Verify Cloudflare token
echo $CLOUDFLARE_DNS_API_TOKEN

# Restart Caddy
docker restart caddy
```

#### Issue: 403 on All Requests

**Cause**: WAF blocking all traffic

**Solution**:
1. Check Cloudflare Security Events
2. Temporarily disable Bot Fight Mode
3. Add firewall rule to allow your IP
4. Check rate limiting rules

#### Issue: Certificate Not Renewing

**Cause**: DNS-01 challenge failing

**Solution**:
```bash
# Check Cloudflare API token permissions
# Must have Zone.DNS:Edit

# Check Caddy logs
docker logs caddy | grep -i "acme\|certificate\|dns"

# Manually trigger renewal
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## Best Practices

### ✅ Do

- Use DNS-01 for droplets behind orange cloud
- Keep App Platform DNS-only until certs issued
- Check origin health directly (bypass WAF)
- Accept 403 as valid for public endpoints
- Monitor Cloudflare Security Events
- Set up alerts for origin health failures

### ❌ Don't

- Use HTTP-01 with orange cloud (will fail)
- Proxy App Platform until certs are issued
- Block all 403 responses (may hide WAF protection)
- Expose origin IPs publicly (security risk)
- Disable SSL/TLS strict mode (man-in-the-middle risk)

## Cost Optimization

### Cloudflare

- **Free Plan**: ✅ Sufficient for most use cases
  - Unlimited DDoS protection
  - Shared SSL certificate
  - Basic WAF rules
  - Cache (saves bandwidth)

- **Pro Plan** ($20/month): Consider if you need:
  - Advanced WAF rules
  - Image optimization
  - Priority support
  - 20 Page Rules (vs 3 on Free)

### DigitalOcean

**Current Setup**:
- ERP Droplet: $24/month (4GB, 2 vCPUs)
- OCR Droplet: $24/month (4GB, 2 vCPUs)
- MCP App Platform: ~$12/month
- Superset App Platform: ~$12/month
- **Total**: ~$72/month

**With Cloudflare CDN**:
- Reduced bandwidth costs (Cloudflare caches static assets)
- Estimate: Save $5-10/month on bandwidth

## Deployment Checklist

### Initial Setup

- [ ] Generate Cloudflare DNS API token (Zone.DNS:Edit)
- [ ] Add token to GitHub Secrets: `CLOUDFLARE_DNS_API_TOKEN`
- [ ] Add token to droplet `/etc/environment`
- [ ] Deploy Caddy with DNS-01 configuration
- [ ] Verify certificate issuance (check Caddy logs)

### Droplet Configuration

- [ ] ERP: Caddy running with DNS-01
- [ ] ERP: Health endpoint `/web/health` responding
- [ ] ERP: Cloudflare proxied (orange cloud)
- [ ] OCR: Caddy running with DNS-01
- [ ] OCR: Health endpoint `/health` responding
- [ ] OCR: Cloudflare proxied (orange cloud)

### App Platform Configuration

- [ ] MCP: Custom domain added in DO
- [ ] MCP: Cloudflare DNS-only (grey cloud)
- [ ] MCP: Certificate issued (check DO dashboard)
- [ ] MCP: Force HTTPS enabled
- [ ] Superset: Custom domain added in DO
- [ ] Superset: Cloudflare DNS-only (grey cloud)
- [ ] Superset: Certificate issued
- [ ] Superset: Force HTTPS enabled

### Cloudflare Settings

- [ ] SSL/TLS mode: Full (strict)
- [ ] Always Use HTTPS: Enabled
- [ ] TLS 1.3: Enabled
- [ ] Bot Fight Mode: Enabled
- [ ] Security Level: Medium

### Monitoring

- [ ] Health monitor workflow runs every 5 minutes
- [ ] Origin health checks passing (200-3xx)
- [ ] Public health checks passing (200-3xx or 403)
- [ ] Smoke test script runs successfully
- [ ] Alerts configured for failures

## References

- [Cloudflare SSL/TLS Overview](https://developers.cloudflare.com/ssl/get-started/)
- [Caddy DNS-01 Challenge](https://caddyserver.com/docs/automatic-https#dns-challenge)
- [DigitalOcean Custom Domains](https://docs.digitalocean.com/products/app-platform/how-to/manage-domains/)
- [Let's Encrypt Challenge Types](https://letsencrypt.org/docs/challenge-types/)

## Support

- **Email**: jgtolentino_rn@yahoo.com | support@insightpulseai.com
- **GitHub Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Runbook**: `/docs/runbooks/cloudflare-waf-incident.md`
