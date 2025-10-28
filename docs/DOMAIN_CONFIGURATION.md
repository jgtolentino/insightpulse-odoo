# Domain Configuration Guide

This guide covers the domain and DNS configuration for InsightPulse Odoo deployment.

## Overview

InsightPulse Odoo can be deployed with multiple access patterns:
- **Direct Access**: Direct connection to Odoo and Superset on their respective ports
- **Reverse Proxy**: Single domain with path-based routing via Caddy
- **Multi-Subdomain**: Separate subdomains for each service

## Recommended Setup: Reverse Proxy with Caddy

The recommended configuration uses Caddy as a reverse proxy to route traffic to Odoo and Superset on a single domain.

### Architecture

```
example.com/odoo     → Odoo (port 8069)
example.com/superset → Superset (port 8088)
```

### Prerequisites

- Domain name (e.g., example.com)
- DNS A record pointing to your server IP
- Ports 80 and 443 open for HTTP/HTTPS traffic

### DNS Configuration

1. **A Record Setup**
   ```
   Type: A
   Name: @ (or subdomain)
   Value: YOUR_SERVER_IP
   TTL: 3600
   ```

2. **CNAME for Subdomains (Optional)**
   ```
   Type: CNAME
   Name: odoo
   Value: example.com
   TTL: 3600
   ```

### Caddy Configuration

The `caddy/Caddyfile` is pre-configured for path-based routing:

```caddyfile
example.com {
    # Odoo service
    handle_path /odoo* {
        reverse_proxy odoo:8069 {
            header_up X-Forwarded-Prefix /odoo
        }
    }

    # Superset service
    handle_path /superset* {
        reverse_proxy superset:8088 {
            header_up X-Forwarded-Prefix /superset
        }
    }

    # Automatic HTTPS
    tls {
        # Caddy will automatically obtain Let's Encrypt certificate
    }
}
```

### Environment Configuration

Update `deploy/.env` with your domain:

```bash
# Domain Configuration
DOMAIN=example.com
ODOO_BASE_URL=https://example.com/odoo
SUPERSET_BASE_URL=https://example.com/superset

# SSL Configuration (Caddy handles this automatically)
USE_HTTPS=true
```

## Alternative Configurations

### Option 1: Direct Port Access

Simplest setup for development or internal use:

```
http://example.com:8069  → Odoo
http://example.com:8088  → Superset
```

**Firewall rules required:**
```bash
# Allow Odoo
sudo ufw allow 8069/tcp

# Allow Superset
sudo ufw allow 8088/tcp
```

### Option 2: Subdomain Configuration

Use separate subdomains for each service:

```
https://odoo.example.com     → Odoo
https://superset.example.com → Superset
```

**DNS Configuration:**
```
Type: CNAME
Name: odoo
Value: example.com

Type: CNAME
Name: superset
Value: example.com
```

**Caddyfile:**
```caddyfile
odoo.example.com {
    reverse_proxy odoo:8069
}

superset.example.com {
    reverse_proxy superset:8088
}
```

## Testing Domain Configuration

Use the provided test script:

```bash
./scripts/test-domain-access.sh
```

This script verifies:
- DNS resolution
- HTTP/HTTPS connectivity
- Service availability
- SSL certificate validity

## Troubleshooting

### DNS Issues

**Problem**: Domain not resolving
```bash
# Check DNS propagation
dig example.com
nslookup example.com

# Test with specific DNS server
dig @8.8.8.8 example.com
```

**Solution**: Wait for DNS propagation (up to 48 hours, typically much faster)

### SSL Certificate Issues

**Problem**: Caddy cannot obtain SSL certificate

**Common causes:**
- Port 80/443 not accessible from internet
- DNS not pointing to correct IP
- Firewall blocking ACME challenge

**Solution**:
```bash
# Check Caddy logs
docker logs caddy

# Verify ports are open
sudo netstat -tlnp | grep -E ':(80|443)'

# Test ACME challenge endpoint
curl -v http://example.com/.well-known/acme-challenge/test
```

### Routing Issues

**Problem**: 404 errors when accessing /odoo or /superset

**Solution**: Verify service configuration
```bash
# Check if services are running
docker ps

# Check if services are accessible internally
docker exec caddy curl -I http://odoo:8069
docker exec caddy curl -I http://superset:8088

# Check Caddy configuration
docker exec caddy caddy validate --config /etc/caddy/Caddyfile
```

## Security Considerations

1. **Always use HTTPS in production**
   - Caddy provides automatic HTTPS with Let's Encrypt
   - No manual certificate management required

2. **Restrict direct port access**
   ```bash
   # Only allow Caddy reverse proxy, block direct access
   sudo ufw deny 8069/tcp
   sudo ufw deny 8088/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **Enable firewall**
   ```bash
   sudo ufw enable
   sudo ufw status
   ```

4. **Use strong authentication**
   - Configure Odoo with strong admin password
   - Enable 2FA for critical accounts
   - Use Superset's authentication features

## Production Checklist

- [ ] DNS A record configured and propagated
- [ ] Firewall configured (ports 80, 443 open)
- [ ] Caddy reverse proxy configured
- [ ] SSL certificates obtained (automatic via Caddy)
- [ ] Services accessible via domain
- [ ] Direct port access blocked (if using reverse proxy)
- [ ] Monitoring configured for domain health
- [ ] Backup of domain configuration stored securely

## References

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Odoo Deployment Guide](./DEPLOYMENT.md)
- [Superset Deployment Guide](./SUPERSET_DEPLOY.md)
