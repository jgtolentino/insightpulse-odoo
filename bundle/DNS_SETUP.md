# DNS Configuration for insightpulseai.net

## Required DNS Records

Configure these DNS records with your domain registrar or DNS provider:

### Primary Records

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | `YOUR_DROPLET_IP` | 300 |
| A | www | `YOUR_DROPLET_IP` | 300 |
| AAAA | @ | `YOUR_DROPLET_IPv6` | 300 (optional) |

### Example Configuration

**DigitalOcean DNS:**
```
A     @             159.89.xxx.xxx    300
A     www           159.89.xxx.xxx    300
AAAA  @             2400:6180::xxxx   300
```

**Cloudflare:**
```
A     @             159.89.xxx.xxx    Auto
A     www           159.89.xxx.xxx    Auto
AAAA  @             2400:6180::xxxx   Auto
```

**Note:** If using Cloudflare, set "Proxy status" to "DNS only" (gray cloud) for initial setup.

## Verification

After DNS propagation (usually 5-30 minutes):

```bash
# Check DNS resolution
dig +short insightpulseai.net
nslookup insightpulseai.net

# Check HTTPS certificate
curl -I https://insightpulseai.net

# Expected output:
HTTP/2 200
server: Caddy
```

## TLS Certificate Process

Caddy will automatically:
1. Request TLS certificate from Let's Encrypt
2. Verify domain ownership via HTTP-01 challenge
3. Install and configure certificate
4. Auto-renew every 60 days

**First request may take 30-60 seconds** while Caddy obtains the certificate.

## Troubleshooting

### Certificate Request Failed

```bash
# Check Caddy logs
docker compose logs caddy

# Common issues:
# - DNS not propagated yet (wait 30 minutes)
# - Port 80/443 blocked by firewall
# - Email address invalid
```

### Firewall Configuration

```bash
# DigitalOcean/Ubuntu UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Check status
sudo ufw status
```

### Force Certificate Renewal

```bash
cd /Users/tbwa/insightpulse-odoo/bundle
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## Security Recommendations

1. **Update firewall rules:**
   - Allow only ports 80, 443, and 22 (SSH)
   - Block all other incoming traffic

2. **Enable fail2ban:**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

3. **Configure SSH key-only access:**
   - Disable password authentication
   - Use SSH keys for server access

4. **Regular updates:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker compose pull
   docker compose up -d
   ```
