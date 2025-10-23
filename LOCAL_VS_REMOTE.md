# 📍 Local vs Remote Architecture - Odoo 19 Deployment

## Overview

Your Odoo 19 deployment has **two locations**: local development on your Mac and production running on DigitalOcean.

---

## 🖥️ LOCAL (Your Mac)

**Location**: `/Users/tbwa/insightpulse-odoo/`

**Purpose**: Development, documentation, and deployment source

### What's Local

```
/Users/tbwa/insightpulse-odoo/
├── bundle/                          ← Source bundle (uploaded to remote)
│   ├── addons/
│   │   ├── knowledge_notion_clone/  ← Custom Notion clone
│   │   └── oca/                     ← OCA modules (8 repos)
│   ├── caddy/
│   │   └── Caddyfile               ← Reverse proxy config
│   ├── docker-compose.yml          ← Service definitions
│   ├── odoo/
│   │   └── odoo.conf               ← Odoo configuration
│   ├── services/
│   │   └── ocr-service/            ← PaddleOCR-VL
│   └── .env                        ← Environment variables
│
├── Documentation:
│   ├── DEPLOYMENT_STATUS.md
│   ├── SECURITY_LOCKDOWN_COMPLETE.md
│   ├── APPS_INSTALLATION_GUIDE.md
│   ├── CONSOLIDATION_COMPLETE.md
│   └── [other docs]
│
└── odoo19-bundle.tar.gz            ← Compressed bundle (52MB)
```

### Local Actions
- ✅ Edit configuration files
- ✅ Update documentation
- ✅ Modify Notion clone code
- ✅ Test changes locally (optional)
- ✅ Create deployment bundles
- ❌ **NOT running services** (all services are on remote)

---

## 🌐 REMOTE (DigitalOcean Droplet)

**Location**: `root@188.166.237.231:/opt/bundle/`

**Purpose**: Production deployment running all services

### What's Remote

```
188.166.237.231:/opt/bundle/
├── addons/
│   ├── knowledge_notion_clone/     ← DEPLOYED (installed & running)
│   └── oca/                        ← 308+ modules available
│
├── caddy/
│   └── Caddyfile                   ← Active HTTPS proxy
│
├── docker-compose.yml              ← Running services
│
├── odoo/
│   └── odoo.conf                   ← Active config
│
├── services/
│   └── ocr-service/                ← PaddleOCR-VL running
│
├── .env                            ← Production environment
│
└── Scripts:
    ├── install-modules.sh          ← OCA installer
    └── install-all-oca.sh          ← Bulk installer
```

### Remote Services (Running)

**Docker Containers**:
```
bundle-odoo-1          ← Main Odoo (port 8069)
bundle-odoo-longpoll-1 ← Longpolling (port 8072)
bundle-postgres-1      ← PostgreSQL 14
bundle-redis-1         ← Redis cache
bundle-caddy-1         ← HTTPS proxy (80/443)
bundle-onlyoffice-1    ← Document editing
bundle-ocr-service-1   ← OCR API
```

**Domain**: https://insightpulseai.net → 188.166.237.231

### Remote System Paths

**Database Backups**:
```
/var/backups/odoo/
└── odoo_2025-10-23.sql.gz (447KB)
```

**Logs**:
```
docker logs bundle-odoo-1          ← Odoo application logs
docker logs bundle-postgres-1      ← Database logs
docker logs bundle-ocr-service-1   ← OCR service logs
/var/log/pg_backup.log            ← Backup logs
```

**Container Data**:
```
/opt/bundle/
└── (Docker manages volumes internally)
```

---

## 🔄 Workflow: Local → Remote

### Development Cycle

1. **Edit Locally** (Your Mac)
   ```bash
   cd /Users/tbwa/insightpulse-odoo/bundle
   # Edit files: odoo.conf, Caddyfile, module code, etc.
   ```

2. **Test Locally** (Optional)
   ```bash
   cd bundle
   docker compose up -d  # Run services on Mac
   ```

3. **Deploy to Remote**
   ```bash
   # Package changes
   tar -czf changes.tar.gz bundle/

   # Upload to droplet
   scp changes.tar.gz root@188.166.237.231:/tmp/

   # Apply on remote
   ssh root@188.166.237.231
   cd /opt/bundle
   tar -xzf /tmp/changes.tar.gz --strip-components=1
   docker compose restart odoo
   ```

### Direct Remote Changes

**When to edit directly on remote**:
- Quick configuration tweaks
- Emergency fixes
- Testing before pulling back to local

**Commands**:
```bash
# SSH to droplet
ssh root@188.166.237.231

# Edit config
nano /opt/bundle/odoo/odoo.conf

# Restart service
cd /opt/bundle && docker compose restart odoo
```

---

## 📂 File Synchronization

### What Should Match

**Always Identical**:
- ✅ `odoo/odoo.conf` (configuration)
- ✅ `caddy/Caddyfile` (proxy config)
- ✅ `docker-compose.yml` (service definitions)
- ✅ `addons/knowledge_notion_clone/` (custom module)
- ✅ `.env` (environment - may differ slightly)

**Remote-Only**:
- ❌ `/var/backups/odoo/` (database backups)
- ❌ `/var/log/` (system logs)
- ❌ Container volumes (Docker managed data)

**Local-Only**:
- ❌ Documentation files (`*.md`)
- ❌ `odoo19-bundle.tar.gz` (deployment archive)

---

## 🔐 Access Methods

### Access Remote Services

**Web Interface**:
```
https://insightpulseai.net           ← Odoo UI
https://insightpulseai.net/odoo/apps ← Apps
https://insightpulseai.net/ocr/health ← OCR
```

**SSH**:
```bash
ssh root@188.166.237.231

# Check services
docker compose -f /opt/bundle/docker-compose.yml ps

# View logs
docker logs bundle-odoo-1 --tail=50

# Execute commands
docker compose exec odoo odoo shell -d odoo
```

**Database**:
```bash
# From remote
ssh root@188.166.237.231
docker exec -it bundle-postgres-1 psql -U odoo -d odoo

# From local (if PostgreSQL port exposed)
# NOT recommended for production
```

---

## 🎯 Current State

### Local (Mac)
- ✅ Source files and documentation
- ✅ Development environment (optional)
- ✅ Deployment bundles
- ❌ No running services

### Remote (Droplet)
- ✅ All services running
- ✅ Knowledge Notion Clone installed
- ✅ 308+ OCA modules available
- ✅ Production database with data
- ✅ Daily backups configured
- ✅ Security hardened

---

## 📋 Quick Commands

### Check Remote Status
```bash
# All services
ssh root@188.166.237.231 "docker compose -f /opt/bundle/docker-compose.yml ps"

# Website
curl -I https://insightpulseai.net

# OCR health
curl https://insightpulseai.net/ocr/health
```

### Sync Local Changes to Remote
```bash
# Upload specific file
scp bundle/odoo/odoo.conf root@188.166.237.231:/opt/bundle/odoo/

# Upload directory
scp -r bundle/addons/knowledge_notion_clone root@188.166.237.231:/opt/bundle/addons/

# Restart after changes
ssh root@188.166.237.231 "cd /opt/bundle && docker compose restart odoo"
```

### Pull Remote Backups to Local
```bash
# Download latest backup
scp root@188.166.237.231:/var/backups/odoo/odoo_2025-10-23.sql.gz ~/Downloads/

# Download all backups
scp root@188.166.237.231:/var/backups/odoo/*.sql.gz ~/Downloads/
```

---

## 💡 Best Practices

1. **Edit Locally First**
   - Make changes on Mac
   - Test if possible
   - Deploy to remote

2. **Document Remote Changes**
   - If you edit directly on remote, pull changes back to local
   - Keep local as source of truth

3. **Regular Backups**
   - Automated daily backups already configured
   - Manually backup before major changes

4. **Version Control**
   - Local directory is a git repo
   - Commit important changes
   - Tag releases/deployments

5. **Security**
   - Never commit secrets to git
   - Keep `.env` file secure
   - Use SSH keys for droplet access

---

**Summary**: Local = source code & docs. Remote = production services running 24/7.
