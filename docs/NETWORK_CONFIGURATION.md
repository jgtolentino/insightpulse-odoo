# Network Configuration Guide

## Overview

This document describes the network architecture and DNS configuration for the InsightPulse AI infrastructure.

## Infrastructure Components

### Production Environment

| Component | Domain | IP Address | Platform | Region |
|-----------|--------|------------|----------|--------|
| Odoo ERP | erp.insightpulseai.net | 165.227.10.178 | DigitalOcean Droplet | SFO2 |
| Superset BI | superset.insightpulseai.net | (App Platform) | DO App Platform | SFO3 |
| MCP Skill Hub | mcp.insightpulseai.net | (App Platform) | DO App Platform | SFO3 |

### Droplet Specifications

**Name**: ipai-odoo-erp

| Specification | Value |
|---------------|-------|
| RAM | 4GB |
| CPU | 2 vCPU |
| Storage | 120GB SSD |
| Region | SFO2 (San Francisco) |
| OS | Ubuntu 24.04 LTS |
| IPv4 | 165.227.10.178 |

## DNS Configuration

### DNS Provider

**Provider**: Squarespace Domains
**Domain**: insightpulseai.net

### Required DNS Records

Add these records in your Squarespace DNS settings:

```
# Odoo ERP
Type: A
Name: erp
Value: 165.227.10.178
TTL: 3600 (1 hour)

# Superset BI (if using custom domain on App Platform)
Type: CNAME
Name: superset
Value: <app-platform-url>
TTL: 3600

# MCP Skill Hub (if using custom domain on App Platform)
Type: CNAME
Name: mcp
Value: <app-platform-url>
TTL: 3600
```

### DNS Propagation

- Changes typically propagate within 1-4 hours
- Use `dig` or `nslookup` to verify:

```bash
# Check A record
dig erp.insightpulseai.net +short

# Check CNAME record
dig superset.insightpulseai.net +short

# Full DNS lookup
nslookup erp.insightpulseai.net
```

## Network Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Internet                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS (443)
                     │
┌────────────────────┴────────────────────────────────────┐
│              Squarespace DNS                             │
│         (insightpulseai.net)                            │
├─────────────────────────────────────────────────────────┤
│  erp.insightpulseai.net    → 165.227.10.178            │
│  superset.insightpulseai.net → App Platform            │
│  mcp.insightpulseai.net      → App Platform            │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │               │
      ▼              ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Odoo    │  │ Superset │  │   MCP    │
│  Droplet │  │   App    │  │   App    │
│  SFO2    │  │ Platform │  │ Platform │
└──────────┘  └──────────┘  └──────────┘
      │              │               │
      │              │               │
      └──────────────┴───────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   PostgreSQL    │
            │   (Local DB)    │
            └─────────────────┘
```

## Firewall Configuration

### UFW (Uncomplicated Firewall)

The droplet uses UFW for firewall management:

```bash
# View current rules
sudo ufw status verbose

# Default configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allowed ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

### Open Ports

| Port | Protocol | Service | Access |
|------|----------|---------|--------|
| 22 | TCP | SSH | Admin only |
| 80 | TCP | HTTP | Public (redirects to 443) |
| 443 | TCP | HTTPS | Public |
| 8069 | TCP | Odoo | Localhost only |
| 8072 | TCP | Longpolling | Localhost only |
| 5432 | TCP | PostgreSQL | Localhost only |

### DigitalOcean Cloud Firewall

For additional security, consider adding a DigitalOcean Cloud Firewall:

```yaml
Inbound Rules:
  - Type: SSH
    Protocol: TCP
    Port: 22
    Sources: Your IP / Trusted IPs

  - Type: HTTP
    Protocol: TCP
    Port: 80
    Sources: All IPv4, All IPv6

  - Type: HTTPS
    Protocol: TCP
    Port: 443
    Sources: All IPv4, All IPv6

Outbound Rules:
  - All TCP, UDP, ICMP
    Destinations: All IPv4, All IPv6
```

## SSL/TLS Configuration

### Let's Encrypt Certificate

- **Provider**: Let's Encrypt
- **Tool**: Certbot with Nginx plugin
- **Auto-renewal**: Enabled via systemd timer
- **Certificate Location**: `/etc/letsencrypt/live/<domain>/`

### Certificate Files

```
/etc/letsencrypt/live/erp.insightpulseai.net/
├── fullchain.pem  → Public certificate + intermediate
├── privkey.pem    → Private key
├── cert.pem       → Public certificate only
└── chain.pem      → Intermediate certificate
```

### Auto-Renewal

Certbot automatically renews certificates via systemd:

```bash
# Check renewal timer
systemctl status certbot.timer

# Test renewal process
certbot renew --dry-run

# Force renewal (if needed)
certbot renew --force-renewal
```

### SSL Configuration

Nginx is configured with strong SSL settings:

```nginx
# Modern SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;

# SSL Session
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;
```

## Load Balancing & High Availability

### Current Setup

Single droplet configuration (suitable for MVP/staging).

### Future Considerations

For production scale:

1. **Load Balancer**:
   - DigitalOcean Load Balancer
   - Distribute traffic across multiple Odoo instances
   - Health checks on `/web/health`

2. **Database**:
   - Managed PostgreSQL (DigitalOcean)
   - Read replicas for reporting
   - Automated backups

3. **Caching**:
   - Redis for session storage
   - Varnish for HTTP caching
   - CDN for static assets

4. **Auto-scaling**:
   - Horizontal pod autoscaling
   - Based on CPU/memory metrics

## Monitoring & Health Checks

### Health Endpoints

```bash
# Odoo health check
curl https://erp.insightpulseai.net/web/health

# Nginx status (if enabled)
curl http://localhost/nginx_status

# Service status
systemctl status odoo19
systemctl status nginx
systemctl status postgresql
```

### Monitoring Tools

Recommended monitoring solutions:

1. **UptimeRobot** (Free tier):
   - Monitor: `https://erp.insightpulseai.net/web/health`
   - Interval: 5 minutes
   - Alerts: Email/SMS

2. **DigitalOcean Monitoring** (Free):
   - CPU usage
   - Memory usage
   - Disk usage
   - Network bandwidth

3. **Datadog/New Relic** (Production):
   - Application performance monitoring
   - Log aggregation
   - Custom metrics

## Backup & Disaster Recovery

### Backup Strategy

1. **Database Backups**:
   - Frequency: Daily at 2:15 AM
   - Retention: 30 days
   - Location: S3-compatible storage

2. **Filestore Backups**:
   - Frequency: Daily with database
   - Retention: 30 days
   - Location: S3-compatible storage

3. **Server Snapshots**:
   - Frequency: Weekly
   - Retention: 4 weeks
   - Location: DigitalOcean Snapshots

### Recovery Time Objective (RTO)

- Database restore: < 1 hour
- Full server rebuild: < 2 hours
- Droplet snapshot restore: < 30 minutes

### Recovery Point Objective (RPO)

- Database: < 24 hours (daily backups)
- Filestore: < 24 hours (daily backups)

## Network Performance

### Expected Latency

| Route | Latency |
|-------|---------|
| US West Coast → SFO2 | 10-30ms |
| US East Coast → SFO2 | 70-90ms |
| Europe → SFO2 | 150-200ms |
| Asia → SFO2 | 120-180ms |

### Bandwidth

- Droplet: 4TB transfer/month
- Expected usage: ~500GB/month (est.)
- Overage: $0.01/GB

## Security Best Practices

### Network Security

1. **SSH Hardening**:
   - Disable password authentication
   - Use SSH keys only
   - Change default port (optional)
   - Install fail2ban

2. **Rate Limiting**:
   - Configure Nginx rate limiting
   - Limit: 10 req/sec per IP for API
   - Limit: 50 req/sec per IP for static files

3. **IP Whitelisting**:
   - Consider restricting admin access
   - Use VPN for administrative access

4. **DDoS Protection**:
   - Enable DigitalOcean Cloud Firewall
   - Consider Cloudflare for DNS/CDN

### Application Security

1. **Database**:
   - Strong passwords (25+ characters)
   - No remote access (localhost only)
   - Encrypted connections

2. **Odoo**:
   - Strong master password
   - Disable database manager in production
   - Regular security updates

3. **SSL/TLS**:
   - Strong cipher suites
   - HSTS enabled
   - Certificate pinning (optional)

## Troubleshooting

### DNS Issues

```bash
# Check DNS propagation
dig erp.insightpulseai.net +short

# Flush local DNS cache (macOS)
sudo dscacheutil -flushcache

# Flush local DNS cache (Linux)
sudo systemd-resolve --flush-caches

# Check from different DNS servers
dig @8.8.8.8 erp.insightpulseai.net
dig @1.1.1.1 erp.insightpulseai.net
```

### Connection Issues

```bash
# Test connectivity
ping erp.insightpulseai.net

# Test specific port
telnet erp.insightpulseai.net 443
nc -zv erp.insightpulseai.net 443

# Check SSL certificate
openssl s_client -connect erp.insightpulseai.net:443 -servername erp.insightpulseai.net

# Trace route
traceroute erp.insightpulseai.net
mtr erp.insightpulseai.net
```

### Firewall Issues

```bash
# Check UFW status
sudo ufw status verbose

# Check if port is listening
sudo netstat -tulpn | grep :443
sudo ss -tulpn | grep :443

# Check iptables rules
sudo iptables -L -n -v
```

## Support & Documentation

- DigitalOcean Docs: https://docs.digitalocean.com/
- Nginx Docs: https://nginx.org/en/docs/
- Let's Encrypt Docs: https://letsencrypt.org/docs/
- Odoo Docs: https://www.odoo.com/documentation/19.0/

---

**Last Updated**: 2025-11-03
**Maintained By**: InsightPulse AI Infrastructure Team
