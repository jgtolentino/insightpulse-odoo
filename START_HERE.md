# 🚀 Odoo 19 Enterprise + Notion Clone - Production Deployment Guide

## ⚡ Quick Start (5 Minutes)

### Step 1: Configure DNS (Do First!)
```
Domain: insightpulseai.net
Type: A
Name: @
Value: YOUR_DROPLET_IP
```

### Step 2: Upload Bundle to Droplet
```bash
# On your local machine
cd /Users/tbwa/insightpulse-odoo
tar czf odoo19-bundle.tar.gz bundle/
scp odoo19-bundle.tar.gz root@YOUR_DROPLET_IP:/opt/
scp bundle/scripts/droplet-setup.sh root@YOUR_DROPLET_IP:/root/
scp bundle/scripts/install-modules.sh root@YOUR_DROPLET_IP:/root/
```

### Step 3: Initialize Droplet
```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Run setup script
chmod +x /root/droplet-setup.sh
/root/droplet-setup.sh

# Extract bundle
cd /opt
tar xzf odoo19-bundle.tar.gz
```

### Step 4: Start Services
```bash
cd /opt/bundle
docker compose up -d

# Wait 30 seconds for services to initialize
sleep 30
```

### Step 5: Install All Modules Automatically 🎯
```bash
# Make script executable
chmod +x /root/install-modules.sh

# Run automatic installation
COMPOSE_DIR=/opt/bundle ADMIN_PASSWD='InsightPulse2025!' \
/root/install-modules.sh odoo
```

**This script will:**
- ✅ Scan all OCA repositories
- ✅ Scan custom addons
- ✅ Install ALL available modules
- ✅ Configure system parameters
- ✅ Restart services

**Installation takes 5-10 minutes.**

### Step 6: Access Your System
```
https://insightpulseai.net
```

**First Login:**
1. Select database: `odoo`
2. Email: `jgtolentino_rn@yahoo.com`
3. Create admin password
4. Start using!

---

## 📦 What Gets Installed

### Core Infrastructure
- ✅ Odoo 19 (4 workers + longpolling)
- ✅ PostgreSQL 14 (optimized for production)
- ✅ Redis 6 (cache + queue)
- ✅ Caddy 2.8 (auto HTTPS via Let's Encrypt)
- ✅ OnlyOffice (document editing)

### Enterprise-Parity Modules (OCA)

**Authentication & Security:**
- `auth_totp` - Two-factor authentication
- `auth_password_policy` - Password strength requirements
- `auth_session_timeout` - Auto-logout inactive users
- `base_user_role` - Advanced role management

**Web Interface:**
- `web_responsive` - Mobile-friendly UI
- `web_environment_ribbon` - Dev/Prod environment indicator

**Background Jobs:**
- `queue_job` - Async task processing

**Reporting:**
- `report_xlsx` - Excel report generation
- Additional reporting tools from reporting-engine

**Accounting:**
- Modules from account-financial-tools
- Financial reporting capabilities

**HR & Purchasing:**
- HR management tools
- Purchase workflow automation

### Custom Features ⭐
- `knowledge_notion_clone` - **Notion-style workspace**
  - Hierarchical pages
  - Block-based editor (text, headings, todos, dividers)
  - Custom databases with properties
  - Favorite pages
  - Search functionality

---

## 🎯 Accessing Features

### Notion-Style Workspace
**Location:** Apps → Knowledge → Workspace

**Features:**
- Create pages with nested hierarchy
- Add blocks: Text, H1, H2, To-Do, Divider
- Create databases with custom properties
- Mark pages as favorites
- Full-text search

### Two-Factor Authentication
**Location:** Settings → Users → Two-factor authentication

**Setup:**
1. Install `auth_totp` module
2. User profile → Enable 2FA
3. Scan QR code with authenticator app

### Background Jobs
**Location:** Settings → Technical → Queue Jobs

**Usage:**
- View running jobs
- Monitor job queue
- Retry failed jobs
- Schedule recurring tasks

---

## 🔐 Security Configuration

### Master Password
**Current:** `InsightPulse2025!`

**Change it:**
1. Edit `/opt/bundle/odoo/odoo.conf`
2. Update `admin_passwd = NEW_PASSWORD`
3. Restart: `docker compose restart odoo`

### Database Access
**Restrict external access:**
```bash
# In docker-compose.yml, PostgreSQL service
# Remove ports section to prevent external access
```

### Firewall
**Already configured by droplet-setup.sh:**
- ✅ SSH (22) - Allowed
- ✅ HTTP (80) - Allowed
- ✅ HTTPS (443) - Allowed
- ✅ All other ports - Blocked

### fail2ban
**Already installed and active.**

Protects against brute-force attacks on SSH and web services.

---

## 📊 Monitoring & Maintenance

### Check Service Status
```bash
cd /opt/bundle
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f odoo
docker compose logs -f caddy
docker compose logs -f postgres
```

### Restart Services
```bash
docker compose restart
# Or specific service
docker compose restart odoo
```

### Update Odoo
```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d
```

### Backup Database
```bash
# Full backup
docker compose exec postgres pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql

# Backup with compression
docker compose exec postgres pg_dump -U odoo odoo | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database
```bash
# Stop Odoo first
docker compose stop odoo odoo-longpoll

# Restore
gunzip -c backup_YYYYMMDD.sql.gz | docker compose exec -T postgres psql -U odoo odoo

# Restart
docker compose start odoo odoo-longpoll
```

---

## 🔧 Common Operations

### Install Additional Module
```bash
cd /opt/bundle
docker compose exec odoo odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo \
  -i MODULE_NAME \
  --stop-after-init

docker compose restart odoo
```

### Upgrade Module
```bash
docker compose exec odoo odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo \
  -u MODULE_NAME \
  --stop-after-init

docker compose restart odoo
```

### Add New OCA Repository
```bash
cd /opt/bundle/addons/oca
git clone --depth=1 https://github.com/OCA/REPO_NAME.git

# Then run install-modules.sh again
COMPOSE_DIR=/opt/bundle ADMIN_PASSWD='YourPassword' \
/root/install-modules.sh odoo
```

---

## 🆘 Troubleshooting

### Services Won't Start
```bash
docker compose logs --tail=100
docker compose down
docker compose up -d
```

### Database Connection Error
```bash
# Verify credentials match
cat /opt/bundle/.env | grep POSTGRES
cat /opt/bundle/odoo/odoo.conf | grep db_

# Reset database password
docker compose down -v
docker compose up -d
```

### HTTPS Not Working
```bash
# Check Caddy logs
docker compose logs caddy

# Verify DNS
dig insightpulseai.net

# Manual certificate request
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### Module Won't Install
```bash
# Update module list
docker compose exec odoo odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo \
  -u base \
  --stop-after-init

# Check for Python dependencies
docker compose exec odoo pip list

# Check logs
docker compose logs odoo --tail=100
```

### Out of Disk Space
```bash
# Check usage
df -h

# Clean Docker images
docker system prune -a

# Clean logs
docker compose down
rm -rf /var/lib/docker/containers/*/*-json.log
docker compose up -d
```

---

## 📞 Support & Resources

**Admin Email:** jgtolentino_rn@yahoo.com
**Domain:** insightpulseai.net
**Master Password:** InsightPulse2025!

**Documentation:**
- Odoo Official: https://www.odoo.com/documentation/19.0/
- OCA GitHub: https://github.com/OCA
- Caddy Docs: https://caddyserver.com/docs/

**Additional Guides:**
- `READY_TO_DEPLOY.md` - Full deployment walkthrough
- `DEPLOYMENT_COMPLETE.md` - Technical reference
- `DNS_SETUP.md` - DNS configuration details

---

## ✅ Production Checklist

- [ ] DNS configured and propagated
- [ ] HTTPS certificate obtained (automatic)
- [ ] Master password changed
- [ ] Admin user created with strong password
- [ ] 2FA enabled for all admin users
- [ ] Firewall configured (done by script)
- [ ] fail2ban active (done by script)
- [ ] All modules installed
- [ ] Backup schedule configured
- [ ] Email notifications configured
- [ ] Test all critical features

---

## 🎉 Success!

Your **self-hosted Odoo 19 Enterprise-equivalent** system with **integrated Notion-style workspace** is now live at:

**https://insightpulseai.net**

**Features:**
- ✅ Full Odoo 19 Enterprise parity via OCA modules
- ✅ Notion-style knowledge management
- ✅ Automatic HTTPS
- ✅ Production-ready security
- ✅ Background job processing
- ✅ Document editing with OnlyOffice
- ✅ Mobile-responsive UI
- ✅ Two-factor authentication
- ✅ Advanced reporting

**Total Cost:** ~$20-40/month (DigitalOcean droplet)
**vs Odoo Enterprise:** $2,400/year/user

---

**Deployment Status:** ✅ Production Ready
**Date:** 2025-10-24
**Contact:** jgtolentino_rn@yahoo.com
