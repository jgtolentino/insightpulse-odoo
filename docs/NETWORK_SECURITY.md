# Network Security Configuration - InsightPulse AI

**Version**: 1.0
**Last Updated**: 2025-01-06
**Classification**: Internal

## 🛡️ Overview

This document outlines the network security architecture, configurations, and best practices for InsightPulse AI infrastructure.

## 🏗️ Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Internet (Public)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼─────┐
                    │  Cloudflare  │ (DDoS Protection)
                    │  CDN/WAF     │
                    └────┬─────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
     ┌────▼────┐                   ┌────▼────┐
     │  DO App │                   │ Droplets │
     │ Platform│                   │          │
     └────┬────┘                   └────┬────┘
          │                             │
          └──────────────┬──────────────┘
                         │
                    ┌────▼─────┐
                    │    VPC    │
                    │ 10.10.0.0/16│
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ Supabase  │
                    │ PostgreSQL│
                    └──────────┘
```

## 🔒 VPC Configuration

### Private Network
- **CIDR Block**: 10.10.0.0/16
- **Region**: Singapore (sgp1)
- **Purpose**: Secure internal communication

### Subnet Allocation
- **App Platform**: 10.10.1.0/24
- **Droplets**: 10.10.2.0/24
- **Reserved**: 10.10.3.0/24

### Terraform Configuration
```hcl
resource "digitalocean_vpc" "insightpulse_vpc" {
  name     = "insightpulse-vpc-sgp1"
  region   = "sgp1"
  ip_range = "10.10.0.0/16"

  description = "Private network for InsightPulse AI services"
}
```

## 🔥 Firewall Rules

### Web Application Firewall

#### Inbound Rules

**HTTP/HTTPS (Public)**
```hcl
inbound_rule {
  protocol         = "tcp"
  port_range       = "80"
  source_addresses = ["0.0.0.0/0", "::/0"]
}

inbound_rule {
  protocol         = "tcp"
  port_range       = "443"
  source_addresses = ["0.0.0.0/0", "::/0"]
}
```

**Application Ports**
```hcl
# Odoo
inbound_rule {
  protocol         = "tcp"
  port_range       = "8069"
  source_addresses = ["0.0.0.0/0", "::/0"]
}

# Superset
inbound_rule {
  protocol         = "tcp"
  port_range       = "8088"
  source_addresses = ["0.0.0.0/0", "::/0"]
}
```

**SSH (Restricted)**
```hcl
inbound_rule {
  protocol         = "tcp"
  port_range       = "22"
  source_addresses = var.admin_ip_whitelist  # Only specific IPs
}
```

#### Outbound Rules

```hcl
# Allow all outbound traffic
outbound_rule {
  protocol              = "tcp"
  port_range            = "1-65535"
  destination_addresses = ["0.0.0.0/0", "::/0"]
}

outbound_rule {
  protocol              = "udp"
  port_range            = "1-65535"
  destination_addresses = ["0.0.0.0/0", "::/0"]
}
```

### Monitoring Services Firewall

**Prometheus/Grafana**
```hcl
# Grafana (Public with auth)
inbound_rule {
  protocol         = "tcp"
  port_range       = "3000"
  source_addresses = ["0.0.0.0/0", "::/0"]
}

# Prometheus (Admin only)
inbound_rule {
  protocol         = "tcp"
  port_range       = "9090"
  source_addresses = var.admin_ip_whitelist
}

# Metrics collection from VPC
inbound_rule {
  protocol    = "tcp"
  port_range  = "9090"
  source_tags = ["insightpulse"]
}
```

## 🌐 DDoS Protection

### Cloudflare Integration

**Configuration**:
1. **DNS Management**: Route through Cloudflare
2. **Proxy Status**: Enabled (orange cloud)
3. **Security Level**: High
4. **Challenge Passage**: 1 hour

**Cloudflare Settings**:
```yaml
# cloudflare-config.yml
security_level: high
challenge_passage: 3600  # 1 hour

firewall_rules:
  - action: challenge
    expression: '(cf.threat_score > 10)'

  - action: block
    expression: '(ip.geoip.country in {"CN" "RU" "KP"})'  # Adjust as needed

  - action: block
    expression: '(http.user_agent contains "bot" and not cf.verified_bot)'

rate_limiting:
  - threshold: 100
    period: 60
    action: challenge
    match:
      url: '*/web/login*'
```

### DigitalOcean Cloud Firewalls

**Rate Limiting** (Application Level):
```nginx
# Nginx rate limiting
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

server {
    location /web/login {
        limit_req zone=login burst=2;
    }

    location /api/ {
        limit_req zone=api burst=10;
    }
}
```

## 🔐 SSL/TLS Configuration

### Certificate Management

**Provider**: Let's Encrypt via Caddy/Certbot
**Renewal**: Automatic (30 days before expiry)
**Protocols**: TLS 1.2, TLS 1.3 only

### Caddy Configuration
```
# Caddyfile
{
    # Global options
    email admin@insightpulseai.net
    acme_ca https://acme-v02.api.letsencrypt.org/directory
}

erp.insightpulseai.net {
    reverse_proxy localhost:8069

    tls {
        protocols tls1.2 tls1.3
        ciphers TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    }

    header {
        # Security headers
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
    }
}
```

### SSL Best Practices

1. **Force HTTPS**:
   ```
   http://erp.insightpulseai.net {
       redir https://erp.insightpulseai.net{uri} permanent
   }
   ```

2. **HSTS Header**:
   - Max-age: 1 year
   - Include subdomains: Yes
   - Preload: Yes

3. **Certificate Monitoring**:
   ```bash
   # Check expiry
   echo | openssl s_client -servername erp.insightpulseai.net -connect erp.insightpulseai.net:443 2>/dev/null | openssl x509 -noout -dates
   ```

## 🔑 Access Control

### SSH Access

**Key-based Authentication Only**:
```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

**Allowed Keys**:
```bash
# ~/.ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC... admin@insightpulseai.net
```

**Fail2Ban Configuration**:
```ini
# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
```

### Database Access

**Connection Restrictions**:
- Require SSL: Yes
- Allowed IPs: VPC only + Admin IPs
- Connection pooling: Enabled (Supabase Pooler)

**PostgreSQL pg_hba.conf**:
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
hostssl all             all             10.10.0.0/16            scram-sha-256
hostssl all             all             203.0.113.0/24          scram-sha-256  # Admin IP
```

### API Authentication

**Odoo**:
- Session-based authentication
- API token for external integrations
- Rate limiting per API key

**Superset**:
- JWT tokens
- OAuth integration (optional)
- RBAC enabled

**MCP Server**:
- GitHub App authentication
- Webhook signature verification

## 🛡️ Web Application Firewall (WAF) Rules

### ModSecurity Configuration

```nginx
# Basic WAF rules
SecRuleEngine On

# SQL Injection protection
SecRule ARGS "@detectSQLi" \
    "id:1001,phase:2,deny,status:403,msg:'SQL Injection Detected'"

# XSS protection
SecRule ARGS "@detectXSS" \
    "id:1002,phase:2,deny,status:403,msg:'XSS Attack Detected'"

# Directory traversal
SecRule REQUEST_URI "@contains ../" \
    "id:1003,phase:1,deny,status:403,msg:'Directory Traversal Attempt'"

# File upload restrictions
SecRule FILES "@rx (?i)\.(php|exe|sh|bat)$" \
    "id:1004,phase:2,deny,status:403,msg:'Dangerous File Extension'"
```

### OWASP ModSecurity Core Rule Set (CRS)

```bash
# Install CRS
git clone https://github.com/coreruleset/coreruleset /etc/modsecurity/crs
cp /etc/modsecurity/crs/crs-setup.conf.example /etc/modsecurity/crs/crs-setup.conf

# Enable in Nginx
Include /etc/modsecurity/crs/crs-setup.conf
Include /etc/modsecurity/crs/rules/*.conf
```

## 📊 Network Monitoring

### Traffic Analysis

**NetFlow Configuration**:
```bash
# Monitor network traffic
apt-get install nfdump nfsen

# Configure flow collection
nfcapd -w -D -p 9995 -l /var/cache/nfdump
```

**Wireshark Filters** (for troubleshooting):
```
# HTTP traffic
http

# Database connections
tcp.port == 5432

# SSH attempts
tcp.port == 22

# High traffic volume
tcp.len > 1400
```

### Intrusion Detection

**Suricata IDS**:
```yaml
# /etc/suricata/suricata.yaml
vars:
  address-groups:
    HOME_NET: "[10.10.0.0/16]"
    EXTERNAL_NET: "!$HOME_NET"

outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      types:
        - alert
        - http
        - dns
        - tls
```

## 🔒 Security Hardening Checklist

### System Level
- [ ] OS security patches applied
- [ ] Unnecessary services disabled
- [ ] Fail2Ban installed and configured
- [ ] Automatic security updates enabled
- [ ] Audit logging enabled (auditd)

### Network Level
- [ ] Firewall rules configured
- [ ] VPC isolation implemented
- [ ] DDoS protection enabled
- [ ] SSL/TLS properly configured
- [ ] Security headers implemented

### Application Level
- [ ] Strong authentication enabled
- [ ] RBAC implemented
- [ ] API rate limiting configured
- [ ] Input validation enabled
- [ ] Security headers set

### Monitoring
- [ ] Intrusion detection active
- [ ] Log aggregation configured
- [ ] Security alerts enabled
- [ ] Regular security scans scheduled

## 📝 Incident Response

### Security Incident Types

1. **DDoS Attack**
   - Activate Cloudflare "Under Attack" mode
   - Analyze traffic patterns
   - Block offending IPs/countries

2. **Unauthorized Access Attempt**
   - Review SSH/application logs
   - Check for privilege escalation
   - Rotate compromised credentials
   - Force password resets if needed

3. **Data Breach**
   - Isolate affected systems
   - Preserve evidence
   - Notify stakeholders
   - Conduct forensic analysis

### Security Contacts
- **Security Lead**: [Email]
- **Incident Response Team**: [Email]
- **Legal/Compliance**: [Email]

## 🔗 Related Documentation

- [Disaster Recovery Plan](./DISASTER_RECOVERY.md)
- [Operational Runbooks](./OPERATIONAL_RUNBOOKS.md)
- [Monitoring Guide](../monitoring/README.md)
- [Terraform Firewall Config](../terraform/main.tf)

## 📄 Compliance

### Standards
- OWASP Top 10
- CIS Benchmarks
- GDPR requirements
- PCI DSS (if applicable)

### Regular Audits
- Security audit: Quarterly
- Penetration testing: Annually
- Compliance review: Semi-annually
