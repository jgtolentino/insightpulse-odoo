# Odoo CE 18 M1 Deployment Guide

## Overview

This guide covers production deployment of InsightPulse Odoo CE 18 (M1 milestone) on DigitalOcean droplets using the automated deployment script.

## Prerequisites

### Infrastructure Requirements

- **Droplet**: Ubuntu 22.04 or 24.04 LTS
- **Resources**: Minimum 2 CPU, 4GB RAM, 80GB SSD
- **DNS**: A record pointing `erp.insightpulseai.net` to droplet IP
- **Network**: Ports 22, 80, 443 accessible

### Access Requirements

- Root SSH access to droplet
- GitHub account (for cloning repository)
- Email address for Let's Encrypt SSL certificate

## Quick Deployment

### Step 1: Prepare Droplet

```bash
# SSH into your droplet as root
ssh root@your-droplet-ip

# Verify OS version
cat /etc/os-release | grep VERSION=

# Expected output:
# VERSION="22.04.x LTS (Jammy Jellyfish)" or
# VERSION="24.04.x LTS (Noble Numbat)"
```

### Step 2: Verify DNS

```bash
# Check DNS resolution
host erp.insightpulseai.net

# Expected output:
# erp.insightpulseai.net has address YOUR_DROPLET_IP
```

If DNS not resolving, wait for propagation (can take up to 48 hours, typically 5-15 minutes).

### Step 3: Run Deployment Script

```bash
# Download deployment script
curl -fsSL https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/deploy_m1.sh.template -o deploy_m1.sh

# Make executable
chmod +x deploy_m1.sh

# Run deployment (as root)
sudo ./deploy_m1.sh
```

### Step 4: Monitor Deployment

The script will:

1. **Check Prerequisites** (5 seconds)
   - Verify running as root
   - Check OS version
   - Verify DNS resolution

2. **Install System Dependencies** (~2 minutes)
   - Docker Engine and Docker Compose plugin
   - Nginx web server
   - Certbot for SSL certificates
   - UFW firewall

3. **Configure Firewall** (10 seconds)
   - Allow SSH (port 22)
   - Allow HTTP (port 80)
   - Allow HTTPS (port 443)
   - Enable UFW

4. **Clone Repository** (~30 seconds)
   - Git clone from GitHub
   - Checkout main branch

5. **Generate Secrets** (1 second)
   - Auto-generate 256-bit database password
   - Auto-generate 256-bit admin password
   - No manual editing required

6. **Configure Odoo** (5 seconds)
   - Replace placeholders in config files
   - Create `.env` file with secrets
   - Set secure file permissions (600)

7. **Configure Nginx** (10 seconds)
   - Copy reverse proxy configuration
   - Enable site configuration
   - Test and reload Nginx

8. **Obtain SSL Certificate** (~30 seconds)
   - Request Let's Encrypt certificate
   - Configure auto-renewal
   - Enable HTTPS

9. **Start Odoo Stack** (~1 minute)
   - Pull Docker images (PostgreSQL 16, Odoo 18)
   - Start containers
   - Wait for health checks

10. **Setup Automated Backups** (5 seconds)
    - Copy backup script
    - Configure daily cron job (2 AM UTC)

**Total deployment time**: ~5-7 minutes

### Step 5: Access Odoo

After deployment completes, you'll see:

```
=========================================
✅ Deployment Complete!
=========================================

Odoo URL: https://erp.insightpulseai.net
Admin Email: admin
Master Password: AbC123XyZ...32chars...

Database Password: DeF456UvW...32chars...

Secrets saved to: /opt/odoo-ce/deploy/.env
Logs: /var/log/odoo_deploy.log
Backups: /opt/odoo-backups (daily at 2 AM)
=========================================
```

**Save the master password immediately!** You'll need it to create databases.

## Post-Deployment Configuration

### Create Database

1. Navigate to `https://erp.insightpulseai.net/web`
2. Click "Manage Databases"
3. Click "Create Database"
4. Fill in:
   - Master Password: (from deployment output)
   - Database Name: `insightpulse`
   - Email: `jgtolentino_rn@yahoo.com`
   - Password: (choose admin user password)
   - Language: English
   - Country: Philippines
   - Demo Data: Uncheck (production deployment)
5. Click "Create Database"

### Install Custom Modules

1. Navigate to Apps menu
2. Search for "IPAI"
3. Install modules:
   - **IPAI CE Cleaner** (install first to hide Enterprise banners)
   - **IPAI Expense & Travel (PH)** (expense management)
   - **IPAI Equipment Management** (equipment booking)

### Verify CE/OCA-Only Policy

After installation, verify no Enterprise/IAP references:

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Check for Enterprise modules
docker exec odoo-ce odoo shell -d insightpulse << EOF
import odoo
for module in odoo.modules.registry.Registry.new('insightpulse')['ir.module.module'].search([]):
    if 'enterprise' in module.name.lower():
        print(f"WARNING: {module.name}")
EOF
```

Should return no output.

## Existing Deployment Handling

If deployment script detects existing installation at `/opt/odoo-ce`, it will prompt:

```
Existing deployment found. What would you like to do?
1) Update configuration only (safe)
2) Redeploy from scratch (DANGEROUS - data loss)
3) Exit
Choose an option [1-3]:
```

### Option 1: Update Configuration (Safe)

- Pulls latest code from GitHub
- Regenerates configuration files
- Preserves database and filestore volumes
- **Use case**: Update Odoo config, add OCA modules, change settings

### Option 2: Redeploy from Scratch (DANGEROUS)

- **Deletes all data** (database + filestore)
- Removes all containers and volumes
- Runs fresh deployment
- **Use case**: Reset to clean state, major version upgrade
- **Requires confirmation**: Type `YES` to proceed

### Option 3: Exit

- Aborts deployment script
- No changes made

## Backup & Restore

### Automated Backups

Script configures daily backups at 2 AM UTC:

```bash
# Check cron job
crontab -l | grep backup_odoo

# View backup logs
tail -f /var/log/odoo_backup.log

# List backups
ls -lh /opt/odoo-backups/
```

### Manual Backup

```bash
# Run backup script manually
sudo /usr/local/bin/backup_odoo.sh
```

Backup includes:
- **Database**: PostgreSQL full dump (`odoo-db-YYYYMMDD_HHMMSS.sql.gz`)
- **Filestore**: All attachments and uploaded files (`odoo-filestore-YYYYMMDD_HHMMSS.tar.gz`)
- **Configuration**: Odoo config, Docker Compose, Nginx configs (`odoo-config-YYYYMMDD_HHMMSS.tar.gz`)

### Restore from Backup

```bash
# Stop Odoo stack
cd /opt/odoo-ce/deploy
docker compose down

# Restore database
gunzip < /opt/odoo-backups/odoo-db-20250115_020000.sql.gz | \
  docker exec -i odoo-db psql -U odoo

# Restore filestore
docker exec -i odoo-ce tar xzf - -C / < \
  /opt/odoo-backups/odoo-filestore-20250115_020000.tar.gz

# Start stack
docker compose up -d
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check container status
docker ps

# Check Odoo health endpoint
curl -sf https://erp.insightpulseai.net/web/health | jq

# Check PostgreSQL
docker exec odoo-db pg_isready -U odoo
```

### Logs

```bash
# Deployment logs
tail -f /var/log/odoo_deploy.log

# Odoo application logs
docker logs -f odoo-ce

# PostgreSQL logs
docker logs -f odoo-db

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

### Resource Usage

```bash
# Docker container stats
docker stats odoo-ce odoo-db

# Disk usage
df -h
du -sh /opt/odoo-ce
du -sh /opt/odoo-backups

# Memory usage
free -h
```

### SSL Certificate Renewal

Auto-renewal is configured via certbot.timer:

```bash
# Check renewal timer status
systemctl status certbot.timer

# Test renewal (dry run)
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

## Troubleshooting

### Deployment Failed

```bash
# Check deployment logs
tail -50 /var/log/odoo_deploy.log

# Common issues:
# 1. DNS not resolving → Wait for propagation
# 2. Port 443 blocked → Check UFW and cloud firewall
# 3. Docker installation failed → Check /var/log/apt/term.log
```

### Odoo Not Starting

```bash
# Check container logs
docker logs odoo-ce

# Common issues:
# 1. Database connection failed → Check db_password in odoo.conf
# 2. Addons path error → Check volume mounts in docker-compose.yml
# 3. Permission issues → Check file ownership: chown -R 101:101 /opt/odoo-ce/addons
```

### Health Check Failing

```bash
# Check Odoo health endpoint
curl -v http://127.0.0.1:8069/web/health

# If 404 error → Odoo not fully started, wait 60 seconds
# If connection refused → Container not running, check docker logs
```

### Cannot Access via HTTPS

```bash
# Check Nginx configuration
nginx -t

# Check SSL certificate
openssl s_client -connect erp.insightpulseai.net:443 -servername erp.insightpulseai.net

# Check UFW firewall
sudo ufw status
```

## Security Hardening Checklist

✅ **Applied by deployment script:**

- [x] UFW firewall enabled (ports 22, 80, 443 only)
- [x] Database passwords auto-generated (256-bit)
- [x] PostgreSQL SSL mode required
- [x] `list_db = False` (prevent database enumeration)
- [x] Nginx reverse proxy with SSL termination
- [x] Let's Encrypt SSL certificate with auto-renewal
- [x] Docker resource limits (CPU, memory)
- [x] Container health checks
- [x] Automated daily backups with 7-day retention

**Additional hardening (manual):**

- [ ] Setup SSH key authentication (disable password auth)
- [ ] Install fail2ban for brute-force protection
- [ ] Enable Docker log rotation
- [ ] Configure external monitoring (e.g., UptimeRobot, StatusCake)
- [ ] Setup offsite backup replication
- [ ] Enable Docker Content Trust (image signing)

## Rollback Procedure

If deployment fails, the script automatically rolls back:

1. Stops running containers
2. Preserves existing volumes
3. Logs error details to `/var/log/odoo_deploy.log`

Manual rollback:

```bash
# Stop containers
cd /opt/odoo-ce/deploy
docker compose down

# Restore from backup (see Restore section)

# Restart stack
docker compose up -d
```

## Production Checklist

Before going live:

- [ ] DNS A record configured and propagated
- [ ] SSL certificate obtained and auto-renewal working
- [ ] Database created with production data
- [ ] Custom modules installed and tested
- [ ] Admin password changed from default
- [ ] Automated backups verified (check `/opt/odoo-backups`)
- [ ] Health checks passing (`/web/health`)
- [ ] UFW firewall enabled and configured
- [ ] Nginx reverse proxy working
- [ ] Resource limits appropriate for load
- [ ] Monitoring setup (logs, health checks, uptime)
- [ ] Team access configured (SSH keys, user accounts)

## Support

- **Documentation**: [GitHub Repository](https://github.com/jgtolentino/odoo-ce)
- **Issues**: [GitHub Issues](https://github.com/jgtolentino/odoo-ce/issues)
- **Owner**: InsightPulseAI – ERP Platform Team

---

**Last updated**: January 2025
**Deployment script version**: M1 v1.0.0
