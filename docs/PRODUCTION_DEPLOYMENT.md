# Odoo 19 Production Deployment Guide

## Overview

This guide documents the production deployment of Odoo 19 on DigitalOcean infrastructure for InsightPulse AI.

## Infrastructure

* **Server**: ipai-odoo-erp
* **Size**: 4GB RAM / 2 vCPU / 120GB SSD
* **Region**: SFO2 (San Francisco)
* **Public IPv4**: 165.227.10.178
* **Domain**: erp.insightpulseai.net
* **Odoo Version**: 19.0 (Community Edition)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     InsightPulse Stack                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  erp.insightpulseai.net → Odoo 19 (Droplet: 165.227.10.178) │
│  superset.insightpulseai.net → Superset (DO App Platform)   │
│  mcp.insightpulseai.net → MCP Skill Hub (DO App Platform)   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- DigitalOcean droplet provisioned
- Root SSH access
- DNS access to insightpulseai.net (Squarespace)
- Email for Let's Encrypt: admin@insightpulseai.net

## Deployment Steps

### 0. Initial Server Setup

```bash
# SSH into the droplet
ssh root@165.227.10.178

# Create odoo user and grant sudo access
adduser odoo
usermod -aG sudo odoo

# Configure firewall
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable

# System updates and dependencies
apt-get update && apt-get -y upgrade
apt-get -y install nginx certbot python3-certbot-nginx postgresql-16 \
  python3-pip python3-venv libpq-dev build-essential \
  libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev \
  libldap2-dev libsasl2-dev libffi-dev
```

### 1. PostgreSQL Database Setup

```bash
# Create Odoo database role
sudo -u postgres psql -c "CREATE USER odoo WITH PASSWORD 'CHANGE_ME_DB';"
sudo -u postgres psql -c "ALTER ROLE odoo CREATEDB;"
```

**Security Note**: Replace `CHANGE_ME_DB` with a strong password. Store securely.

### 2. Odoo 19 Installation

```bash
# Switch to odoo user
su - odoo

# Create Python virtual environment
python3 -m venv ~/odoo19
source ~/odoo19/bin/activate

# Upgrade pip and essential packages
pip install --upgrade pip wheel setuptools

# Clone Odoo 19 from official repository
mkdir -p ~/src && cd ~/src
git clone --depth=1 --branch 19.0 https://github.com/odoo/odoo.git odoo

# Install Odoo dependencies
pip install -r odoo/requirements.txt

# Create Odoo directory structure
mkdir -p ~/etc ~/data ~/logs ~/addons
```

### 3. Odoo Configuration

Create the main configuration file:

```bash
cat > ~/etc/odoo.conf <<'EOF'
[options]
addons_path = /home/odoo/addons,/home/odoo/src/odoo/addons
data_dir = /home/odoo/data
admin_passwd = CHANGE_ME
db_host = 127.0.0.1
db_port = 5432
db_user = odoo
db_password = CHANGE_ME_DB
workers = 4
longpolling_port = 8072
proxy_mode = True
logfile = /home/odoo/logs/odoo.log
EOF
```

**Security Note**:
- Replace `CHANGE_ME` with a strong master password
- Replace `CHANGE_ME_DB` with the PostgreSQL password from step 1

### 4. Systemd Service Configuration

```bash
# Exit back to root
exit

# Create systemd service file
cat >/etc/systemd/system/odoo19.service <<'EOF'
[Unit]
Description=Odoo 19 InsightPulse
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/home/odoo/odoo19/bin/python /home/odoo/src/odoo/odoo-bin -c /home/odoo/etc/odoo.conf
Restart=always
RestartSec=10
SyslogIdentifier=odoo19

[Install]
WantedBy=multi-user.target
EOF

# Stop any existing Odoo services (from marketplace image)
systemctl stop odoo 2>/dev/null || true
systemctl disable odoo 2>/dev/null || true

# Enable and start Odoo 19
systemctl daemon-reload
systemctl enable --now odoo19

# Monitor service logs
journalctl -u odoo19 -f
```

Press `Ctrl+C` to exit log monitoring once you verify Odoo is starting successfully.

### 5. DNS Configuration

In your Squarespace DNS settings, add:

| Type | Name | Value           | TTL |
|------|------|-----------------|-----|
| A    | erp  | 165.227.10.178  | 1h  |

### 6. Nginx Reverse Proxy Setup

```bash
# Create Nginx site configuration
cat >/etc/nginx/sites-available/odoo <<'EOF'
server {
  listen 80;
  server_name erp.insightpulseai.net;

  client_max_body_size 100M;

  location / {
    proxy_pass http://127.0.0.1:8069;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_redirect off;
  }

  location /longpolling/ {
    proxy_pass http://127.0.0.1:8072;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  location = /web/health {
    return 200 "OK\n";
    add_header Content-Type text/plain;
  }
}
EOF

# Enable site and test configuration
ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/odoo
nginx -t

# Reload Nginx if test passes
systemctl reload nginx
```

### 7. TLS Certificate (Let's Encrypt)

```bash
# Obtain and configure SSL certificate
certbot --nginx -d erp.insightpulseai.net --redirect -n \
  --agree-tos -m admin@insightpulseai.net

# Verify auto-renewal
certbot renew --dry-run
```

### 8. Install Custom Modules

```bash
# Switch to odoo user
su - odoo
cd ~/addons

# Clone OCA dependencies
git clone --depth=1 --branch 19.0 https://github.com/OCA/server-tools.git
git clone --depth=1 --branch 19.0 https://github.com/OCA/server-env.git

# Clone IPAI modules (adjust URL as needed)
git clone https://github.com/jgtolentino/insightpulse-odoo.git ipai_modules

# Update addons path in configuration
sed -i 's|addons_path = .*|addons_path = /home/odoo/addons,/home/odoo/addons/server-tools,/home/odoo/addons/server-env,/home/odoo/addons/ipai_modules,/home/odoo/src/odoo/addons|' ~/etc/odoo.conf

# Restart Odoo service
exit  # back to root
systemctl restart odoo19
```

### 9. Initialize Database and Modules

1. Visit `https://erp.insightpulseai.net` in your browser
2. Create a new database through the web interface
3. Note the database name (e.g., `insightpulse`)

Then install all IPAI modules:

```bash
su - odoo
source ~/odoo19/bin/activate

/home/odoo/odoo19/bin/python /home/odoo/src/odoo/odoo-bin \
  -c /home/odoo/etc/odoo.conf \
  -d <DBNAME> \
  -i ipai_core,ipai_approvals,ipai_ppm_costsheet,ipai_studio,ipai_rate_policy,ipai_ppm,ipai_subscriptions,ipai_knowledge_ai,superset_connector,ipai_saas_ops \
  --stop-after-init

exit  # back to root
systemctl restart odoo19
```

### 10. Configure Integrations

#### Superset Integration

- Superset dashboard: `https://superset.insightpulseai.net`
- In Odoo, configure `superset_connector` module with:
  - Superset URL
  - API credentials
  - Embed dashboard IDs

#### MCP Skill Hub Integration

- MCP endpoint: `https://mcp.insightpulseai.net`
- Configure AI skills and knowledge base connections

### 11. Backup Configuration

```bash
# Install AWS CLI for S3 backups
apt-get -y install awscli

# Configure AWS credentials (if using S3)
aws configure

# Create backup script
cat >/usr/local/bin/pg_backup.sh <<'EOF'
#!/usr/bin/env bash
set -e

DB="<DBNAME>"
S3_BUCKET="s3://insightpulse-backups/odoo"
BACKUP_FILE="${DB}-$(date +%F-%H%M).dump"

# Create backup
pg_dump -Fc -U postgres "$DB" | aws s3 cp - "$S3_BUCKET/$BACKUP_FILE"

# Keep only last 30 days
aws s3 ls "$S3_BUCKET/" | while read -r line; do
  createDate=$(echo "$line" | awk {'print $1" "$2'})
  createDate=$(date -d "$createDate" +%s)
  olderThan=$(date -d "30 days ago" +%s)
  if [[ $createDate -lt $olderThan ]]; then
    fileName=$(echo "$line" | awk {'print $4'})
    if [[ $fileName != "" ]]; then
      aws s3 rm "$S3_BUCKET/$fileName"
    fi
  fi
done

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x /usr/local/bin/pg_backup.sh

# Add to crontab (daily at 2:15 AM)
(crontab -l 2>/dev/null; echo "15 2 * * * /usr/local/bin/pg_backup.sh >> /var/log/odoo_backup.log 2>&1") | crontab -
```

### 12. Health Monitoring

```bash
# Test health endpoint
curl -I https://erp.insightpulseai.net/web/health

# Should return: HTTP/2 200
```

Configure monitoring in your preferred tool (e.g., UptimeRobot, Datadog):
- Monitor: `https://erp.insightpulseai.net/web/health`
- Expected: 200 OK response

## Post-Deployment Checklist

- [ ] Odoo 19 service running (`systemctl status odoo19`)
- [ ] Database created and modules installed
- [ ] HTTPS working (`https://erp.insightpulseai.net`)
- [ ] Health endpoint responding (`/web/health`)
- [ ] Backups scheduled and tested
- [ ] Firewall configured (ports 22, 80, 443 only)
- [ ] Superset connector configured
- [ ] MCP integration tested
- [ ] Admin passwords rotated from defaults
- [ ] Monitoring alerts configured

## Troubleshooting

### Check Odoo Service Status

```bash
systemctl status odoo19
journalctl -u odoo19 -n 100 --no-pager
```

### Check Odoo Logs

```bash
tail -f /home/odoo/logs/odoo.log
```

### Check Nginx

```bash
nginx -t
systemctl status nginx
tail -f /var/log/nginx/error.log
```

### Check PostgreSQL

```bash
systemctl status postgresql
sudo -u postgres psql -c "\l"  # List databases
sudo -u postgres psql -c "\du" # List roles
```

### Restart All Services

```bash
systemctl restart postgresql
systemctl restart odoo19
systemctl restart nginx
```

## Maintenance

### Update Odoo

```bash
su - odoo
source ~/odoo19/bin/activate
cd ~/src/odoo
git pull origin 19.0
pip install -r requirements.txt --upgrade
exit

systemctl restart odoo19
```

### Update Custom Modules

```bash
su - odoo
cd ~/addons/ipai_modules
git pull origin main
exit

systemctl restart odoo19
```

### Database Backup (Manual)

```bash
/usr/local/bin/pg_backup.sh
```

### Database Restore

```bash
# Stop Odoo
systemctl stop odoo19

# Restore from backup
sudo -u postgres pg_restore -d <DBNAME> -c /path/to/backup.dump

# Start Odoo
systemctl start odoo19
```

## Security Recommendations

1. **Change Default Passwords**: Update all default passwords immediately
2. **SSH Key Authentication**: Disable password authentication for SSH
3. **Firewall**: Only allow necessary ports (22, 80, 443)
4. **Regular Updates**: Schedule weekly security updates
5. **Backup Encryption**: Encrypt backups at rest
6. **Access Logs**: Monitor access logs regularly
7. **Rate Limiting**: Configure Nginx rate limiting for API endpoints
8. **2FA**: Enable two-factor authentication for Odoo admin accounts

## Support

For issues or questions:
- GitHub: https://github.com/jgtolentino/insightpulse-odoo
- Documentation: /docs

---

**Last Updated**: 2025-11-03
**Odoo Version**: 19.0
**Infrastructure**: DigitalOcean SFO2
