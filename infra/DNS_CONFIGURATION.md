# DNS Configuration - insightpulseai.net

Complete DNS configuration for DigitalOcean domain management.

## DNS Records (DigitalOcean → Domains → insightpulseai.net)

| Host         | Type      | Data                                      | TTL | Purpose                                       |
| ------------ | --------- | ----------------------------------------- | --- | --------------------------------------------- |
| **@**        | **A**     | `165.227.10.178`                          | 1h  | Apex → Odoo droplet (ipai-odoo-erp)           |
| **www**      | **CNAME** | `insightpulseai.net.`                     | 1h  | `www` follows apex                            |
| **erp**      | **A**     | `165.227.10.178`                          | 1h  | Odoo (already present)                        |
| **ocr**      | **A**     | `188.166.237.231`                         | 1h  | OCR droplet (already present)                 |
| **superset** | **CNAME** | `superset-nlavf.ondigitalocean.app.`      | 1h  | DO App (already present)                      |
| **mcp**      | **CNAME** | `pulse-hub-web-an645.ondigitalocean.app.` | 1h  | **Public Skill Hub broker** (already present) |
| **mcp-core** | **A**     | `165.227.10.178`                          | 1h  | **Private MCP Secure** on Odoo droplet        |
| **@**        | **CAA**   | `0 issue "letsencrypt.org"`               | 1h  | (already present)                             |

## Infrastructure Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Domain: insightpulseai.net                                      │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ @ (apex) ───────────────► 165.227.10.178 (Odoo droplet)
         │                             └─ Nginx → optional redirect to Superset
         │
         ├─ www ────────────────────► CNAME → insightpulseai.net
         │
         ├─ erp ────────────────────► 165.227.10.178 (Odoo 19.0)
         │                             └─ Nginx → Odoo :8069
         │
         ├─ mcp-core ───────────────► 165.227.10.178 (MCP Secure)
         │                             └─ Nginx → 127.0.0.1:8001
         │                             └─ TLS via Let's Encrypt
         │                             └─ BasicAuth + Bearer + IP allowlist
         │
         ├─ ocr ────────────────────► 188.166.237.231 (OCR droplet)
         │
         ├─ superset ───────────────► DO App Platform
         │                             └─ superset-nlavf.ondigitalocean.app
         │
         └─ mcp ────────────────────► DO App Platform
                                       └─ pulse-hub-web-an645.ondigitalocean.app
                                       └─ Public Skill Hub (port 8088)
```

## Nginx Configuration (Odoo Droplet: 165.227.10.178)

### 1. MCP Core (mcp-core.insightpulseai.net)

Private MCP Secure service with TLS + BasicAuth + Bearer + IP allowlist.

**Nginx site config:**

```bash
sudo tee /etc/nginx/sites-available/mcp-core <<'NG'
server {
  listen 80;
  server_name mcp-core.insightpulseai.net;

  location / {
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300;
  }
}
NG

sudo ln -sf /etc/nginx/sites-available/mcp-core /etc/nginx/sites-enabled/mcp-core
sudo nginx -t && sudo systemctl reload nginx
```

**TLS setup with Let's Encrypt:**

```bash
sudo snap install core && sudo snap refresh core
sudo snap install --classic certbot
sudo certbot --nginx -d mcp-core.insightpulseai.net --redirect
```

### 2. Apex Redirect (Optional)

Redirect apex and www to Superset landing page.

```bash
sudo tee /etc/nginx/sites-available/apex <<'NG'
server {
  listen 80;
  server_name insightpulseai.net www.insightpulseai.net;
  return 301 https://superset.insightpulseai.net$request_uri;
}
NG

sudo ln -sf /etc/nginx/sites-available/apex /etc/nginx/sites-enabled/apex
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d insightpulseai.net -d www.insightpulseai.net --redirect
```

## MCP Secure Service Configuration

**Environment variables (on Odoo droplet):**

```bash
export MCP_BEARER="supersecret-bearer"
export MCP_BASIC_USER="ipai"
export MCP_BASIC_PASS="choose-a-strong-pass"
export MCP_ALLOW_IPS="127.0.0.1,165.227.10.178"   # Add office IPs as needed
export CORS_ORIGINS="https://mcp.insightpulseai.net,https://erp.insightpulseai.net"
```

**Start service:**

```bash
cd /Users/tbwa/insightpulse-odoo
uvicorn services.mcp-secure.server:app --host 127.0.0.1 --port 8001
```

**Systemd service (persistent):**

```bash
sudo tee /etc/systemd/system/mcp-secure.service <<'UNIT'
[Unit]
Description=MCP Secure API
After=network.target

[Service]
Type=simple
User=odoo
WorkingDirectory=/opt/insightpulse-odoo
Environment="MCP_BEARER=supersecret-bearer"
Environment="MCP_BASIC_USER=ipai"
Environment="MCP_BASIC_PASS=choose-a-strong-pass"
Environment="MCP_ALLOW_IPS=127.0.0.1,165.227.10.178"
Environment="CORS_ORIGINS=https://mcp.insightpulseai.net,https://erp.insightpulseai.net"
ExecStart=/usr/bin/uvicorn services.mcp-secure.server:app --host 127.0.0.1 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable mcp-secure
sudo systemctl start mcp-secure
```

## App Platform Configuration

### Public Skill Hub (mcp.insightpulseai.net)

- **Domain:** mcp.insightpulseai.net (CNAME → pulse-hub-web-an645.ondigitalocean.app)
- **Port:** 8088
- **Purpose:** Public broker for OpenAPI/Custom GPT Actions
- **CORS:** Allow https://erp.insightpulseai.net, https://superset.insightpulseai.net

**Deployment:**
- Uses DigitalOcean App Platform
- No authentication required (public catalog)
- Proxies to mcp-core for tool execution

### Superset (superset.insightpulseai.net)

- **Domain:** superset.insightpulseai.net (CNAME → superset-nlavf.ondigitalocean.app)
- **Purpose:** Business Intelligence dashboards
- **Database:** PostgreSQL (Supabase: spdtwktxdalcfigzeqrz)
- **Schema:** `superset` (isolated with search_path)

## Validation Commands

### DNS Resolution

```bash
# Verify DNS records
dig +short insightpulseai.net A                    # Should return 165.227.10.178
dig +short www.insightpulseai.net CNAME            # Should return insightpulseai.net.
dig +short mcp-core.insightpulseai.net A           # Should return 165.227.10.178
dig +short superset.insightpulseai.net CNAME       # Should return superset-nlavf.ondigitalocean.app.
dig +short mcp.insightpulseai.net CNAME            # Should return pulse-hub-web-an645.ondigitalocean.app.
```

### TLS and Connectivity

```bash
# Test HTTPS endpoints
curl -I https://mcp-core.insightpulseai.net/health
curl -I https://superset.insightpulseai.net
curl -I https://mcp.insightpulseai.net/skills/catalog
```

### Authentication Tests

```bash
# BasicAuth
curl -I --user ipai:choose-a-strong-pass https://mcp-core.insightpulseai.net/mcp/catalog

# Bearer token
curl -s https://mcp-core.insightpulseai.net/mcp/catalog \
  -H "Authorization: Bearer supersecret-bearer" | jq .

# IP allowlist (should fail from unauthorized IP)
curl -s https://mcp-core.insightpulseai.net/mcp/catalog
```

## Security Features

### MCP Secure (mcp-core)

1. **CORS Protection:** Only allows configured origins
2. **IP Allowlist:** Restricts access to specific IPs
3. **Dual Authentication:**
   - Bearer token for API clients
   - BasicAuth for browser access (prompts credentials)
4. **TLS Encryption:** Let's Encrypt certificates
5. **Rate Limiting:** (Optional - can be added)

### Public Skill Hub (mcp)

1. **CORS Protection:** Configured for known frontends
2. **No Direct Tool Execution:** Proxies to mcp-core
3. **Public Catalog:** Read-only tool discovery
4. **TLS Encryption:** DigitalOcean App Platform default

## Deployment Checklist

- [ ] Add DNS records in DigitalOcean
- [ ] Configure Nginx on Odoo droplet (165.227.10.178)
- [ ] Obtain Let's Encrypt certificates for mcp-core
- [ ] Deploy updated mcp-secure with CORS + auth
- [ ] Configure environment variables
- [ ] Test DNS resolution
- [ ] Test TLS connectivity
- [ ] Test authentication (BasicAuth + Bearer)
- [ ] Test CORS from allowed origins
- [ ] Verify IP allowlist enforcement
- [ ] Monitor logs for unauthorized access attempts

## Monitoring

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log | grep mcp-core

# MCP Secure logs (if using systemd)
sudo journalctl -u mcp-secure -f

# Certificate expiration
sudo certbot certificates
```

## Troubleshooting

### DNS not resolving

```bash
# Check DigitalOcean DNS settings
doctl compute domain records list insightpulseai.net

# Force DNS refresh (macOS)
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

### TLS certificate issues

```bash
# Renew certificates
sudo certbot renew --dry-run
sudo certbot renew

# Check certificate validity
openssl s_client -connect mcp-core.insightpulseai.net:443 -servername mcp-core.insightpulseai.net
```

### Authentication failures

```bash
# Check environment variables
echo $MCP_BEARER
echo $MCP_BASIC_USER

# Verify credentials in guard function
# Check services/mcp-secure/server.py lines 42-58
```

## Future Enhancements

- [ ] Add rate limiting middleware (10 req/min per IP)
- [ ] Add /metrics endpoint for Prometheus
- [ ] Add request logging with structured JSON
- [ ] Add automated certificate renewal cron job
- [ ] Add health check monitoring (UptimeRobot/Pingdom)
- [ ] Add WAF rules for common attack patterns
