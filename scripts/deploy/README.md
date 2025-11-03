# Odoo 19 Production Deployment Scripts

Automated deployment scripts for setting up Odoo 19 on DigitalOcean infrastructure.

## Overview

These scripts automate the complete deployment process from a fresh Ubuntu 24.04 droplet to a fully configured Odoo 19 production instance with SSL/TLS.

## Prerequisites

- Fresh DigitalOcean droplet (Ubuntu 24.04 LTS)
- Root SSH access
- Domain name configured in DNS
- Email address for Let's Encrypt

## Quick Start

### Option 1: Automated Deployment

Run the master deployment script that executes all steps:

```bash
# SSH into your droplet as root
ssh root@your-droplet-ip

# Clone the repository
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/scripts/deploy

# Make scripts executable
chmod +x *.sh

# Run master deployment (will prompt for inputs)
bash deploy-all.sh
```

### Option 2: Step-by-Step Deployment

Execute scripts individually for more control:

```bash
# 1. Initial server setup (as root)
bash 01-server-setup.sh

# 2. PostgreSQL configuration (as root)
bash 02-postgres-setup.sh

# 3. Odoo installation (as odoo user)
sudo su - odoo
bash /root/insightpulse-odoo/scripts/deploy/03-odoo-install.sh

# 4. Odoo configuration (as odoo user)
ODOO_DB_PASSWORD="$(sudo cat /root/odoo_db_password.txt)" \
bash /root/insightpulse-odoo/scripts/deploy/04-odoo-configure.sh

# 5. Systemd service (as root)
exit  # back to root
bash 05-systemd-setup.sh

# 6. Nginx and SSL (as root)
DOMAIN=erp.insightpulseai.net \
EMAIL=admin@insightpulseai.net \
bash 06-nginx-setup.sh

# 7. Install custom modules (as odoo user)
sudo su - odoo
bash /root/insightpulse-odoo/scripts/deploy/07-install-modules.sh

# 8. Install IPAI modules into database (as odoo user)
bash /root/insightpulse-odoo/scripts/deploy/08-install-ipai-modules.sh <database_name>
```

## Script Descriptions

### 01-server-setup.sh
- Creates odoo user with sudo access
- Configures UFW firewall
- Installs system dependencies
- Configures PostgreSQL service

**Run as:** root

### 02-postgres-setup.sh
- Creates PostgreSQL odoo user
- Sets random secure password
- Grants CREATEDB privileges
- Saves password to `/root/odoo_db_password.txt`

**Run as:** root

### 03-odoo-install.sh
- Creates Python 3 virtual environment
- Clones Odoo 19 from official repository
- Installs Python dependencies
- Creates directory structure

**Run as:** odoo user

### 04-odoo-configure.sh
- Creates production-ready configuration file
- Sets up database connection
- Configures workers and performance settings
- Generates master password

**Run as:** odoo user
**Environment:** `ODOO_DB_PASSWORD`

### 05-systemd-setup.sh
- Creates systemd service file
- Enables auto-start on boot
- Starts Odoo service
- Provides service management commands

**Run as:** root

### 06-nginx-setup.sh
- Configures Nginx as reverse proxy
- Sets up SSL/TLS with Let's Encrypt
- Configures HTTP to HTTPS redirect
- Adds security headers

**Run as:** root
**Environment:** `DOMAIN`, `EMAIL`

### 07-install-modules.sh
- Clones OCA dependencies (server-tools, server-env)
- Clones IPAI custom modules
- Updates Odoo addons path
- Restarts Odoo service

**Run as:** odoo user
**Environment:** `IPAI_REPO` (optional), `IPAI_BRANCH` (optional)

### 08-install-ipai-modules.sh
- Installs all IPAI modules into database
- Runs Odoo CLI in init mode
- Verifies installation success

**Run as:** odoo user
**Arguments:** `<database_name>`

### backup-odoo.sh
- Backs up PostgreSQL database
- Backs up filestore
- Uploads to S3 (optional)
- Cleans up old backups

**Run as:** root
**Arguments:** `<database_name> [s3_bucket]`
**Environment:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (if using S3)

## Configuration

### Environment Variables

Create a `.env` file for easier configuration:

```bash
# Database
ODOO_DB_PASSWORD=your-secure-password

# Master Password
ODOO_MASTER_PASSWORD=your-master-password

# Domain Configuration
DOMAIN=erp.insightpulseai.net
EMAIL=admin@insightpulseai.net

# Module Repository
IPAI_REPO=https://github.com/jgtolentino/insightpulse-odoo.git
IPAI_BRANCH=main

# Backup Configuration
S3_BUCKET=s3://insightpulse-backups/odoo
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-west-2
```

### DNS Configuration

Before running `06-nginx-setup.sh`, ensure DNS is configured:

| Type | Name | Value              | TTL  |
|---------|------|--------------------|------|
| A       | erp  | your-droplet-ip    | 3600 |

## Post-Deployment

### Verify Installation

```bash
# Check Odoo service
systemctl status odoo19

# Check Nginx
systemctl status nginx

# Test health endpoint
curl https://erp.insightpulseai.net/web/health

# View logs
journalctl -u odoo19 -f
tail -f /home/odoo/logs/odoo.log
```

### Create Database

1. Visit `https://your-domain` in browser
2. Click "Create Database"
3. Fill in database details
4. Save the master password securely

### Install Modules

```bash
sudo su - odoo
bash /path/to/08-install-ipai-modules.sh your-database-name
```

### Setup Backups

Add to crontab for daily backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2:15 AM
15 2 * * * /root/insightpulse-odoo/scripts/deploy/backup-odoo.sh your-database-name s3://your-bucket/odoo >> /var/log/odoo_backup.log 2>&1
```

## Maintenance

### Update Odoo

```bash
sudo su - odoo
source ~/odoo19/bin/activate
cd ~/src/odoo
git pull origin 19.0
pip install -r requirements.txt --upgrade
exit

sudo systemctl restart odoo19
```

### Update Custom Modules

```bash
sudo su - odoo
cd ~/addons/ipai_modules
git pull origin main
exit

sudo systemctl restart odoo19
```

### Manual Backup

```bash
bash backup-odoo.sh your-database-name s3://your-bucket/odoo
```

### Restore from Backup

```bash
# Stop Odoo
systemctl stop odoo19

# Restore database
sudo -u postgres pg_restore -d your-database-name -c /path/to/backup.dump

# Restore filestore
tar -xzf /path/to/filestore-backup.tar.gz -C /home/odoo/data/filestore/

# Start Odoo
systemctl start odoo19
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
systemctl status odoo19

# Check logs
journalctl -u odoo19 -n 100 --no-pager
tail -f /home/odoo/logs/odoo.log

# Verify configuration
cat /home/odoo/etc/odoo.conf

# Test Odoo manually
sudo su - odoo
source ~/odoo19/bin/activate
~/odoo19/bin/python ~/src/odoo/odoo-bin -c ~/etc/odoo.conf
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
sudo -u postgres psql -c "\l"
sudo -u postgres psql -c "\du"

# Test as odoo user
PGPASSWORD='your-password' psql -h 127.0.0.1 -U odoo -d postgres -c "SELECT 1"
```

### Nginx Issues

```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/error.log

# Restart services
systemctl restart nginx
systemctl restart odoo19
```

### SSL Certificate Issues

```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal

# Check certificate
certbot certificates
```

## Security Recommendations

1. **Change Default Passwords**: Update all generated passwords
2. **SSH Keys Only**: Disable password authentication
3. **Firewall Rules**: Only allow necessary ports
4. **Regular Updates**: Schedule weekly security updates
5. **Backup Encryption**: Encrypt backups at rest
6. **Monitor Logs**: Set up log monitoring and alerts
7. **Rate Limiting**: Configure Nginx rate limiting
8. **2FA**: Enable two-factor authentication

## Support

- Documentation: `/docs/PRODUCTION_DEPLOYMENT.md`
- Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- Repository: https://github.com/jgtolentino/insightpulse-odoo

## Infrastructure Details

- **Server**: ipai-odoo-erp
- **Size**: 4GB RAM / 2 vCPU / 120GB SSD
- **Region**: DigitalOcean SFO2
- **OS**: Ubuntu 24.04 LTS
- **Odoo**: 19.0 Community Edition
- **Python**: 3.12
- **PostgreSQL**: 16
- **Web Server**: Nginx 1.24
- **SSL**: Let's Encrypt (auto-renewal)

---

**Last Updated**: 2025-11-03
**Version**: 1.0.0
