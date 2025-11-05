# 🚀 Quick Start: Notion → Odoo OCA Deployment

**5-Minute Setup Guide**

## Prerequisites

- DigitalOcean account
- Docker installed locally
- SSH key configured

## Step 1: Clone Repository (1 min)

```bash
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
git checkout claude/notion-to-odoo-mapping-011CUpkKA5LugAkD5mKLr66J
```

## Step 2: Install OCA Modules (2 min)

```bash
chmod +x scripts/install_oca_modules.sh
./scripts/install_oca_modules.sh
```

## Step 3: Configure Environment (1 min)

```bash
cp .env.example .env
nano .env  # Edit required variables
```

**Minimum required:**
```bash
POSTGRES_PASSWORD=<strong-password>
ODOO_ADMIN_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
SUPERSET_SECRET_KEY=<random-secret>
```

## Step 4: Deploy (1 min)

```bash
docker-compose -f docker-compose.oca.yml up -d --build
```

## Step 5: Access Odoo

1. Open browser: `http://localhost:8069`
2. Create database:
   - Master Password: `<ODOO_ADMIN_PASSWORD>`
   - Database Name: `odoo19`
   - Email: `admin`
   - Password: `<ODOO_ADMIN_PASSWORD>`
   - Language: English
   - Country: Philippines

3. Install Finance SSC Module:
   - Go to Apps
   - Search "Finance SSC"
   - Click Install

## Quick Commands

### View Logs
```bash
docker-compose -f docker-compose.oca.yml logs -f odoo
```

### Restart Services
```bash
docker-compose -f docker-compose.oca.yml restart odoo
```

### Install Module via CLI
```bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf -d odoo19 -i <module-name> --stop-after-init
```

### Backup Database
```bash
docker-compose -f docker-compose.oca.yml exec db \
  pg_dump -U odoo odoo19 > backup_$(date +%Y%m%d).sql
```

### Update OCA Modules
```bash
cd addons/oca
git pull origin 19.0
docker-compose -f docker-compose.oca.yml restart odoo
```

## Next Steps

1. **Read full documentation:**
   - [Notion to Odoo Mapping](./NOTION_TO_ODOO_MAPPING.md)
   - [Deployment Guide](./DEPLOYMENT_GUIDE_OCA.md)
   - [Finance SSC Module README](../addons/custom/finance_ssc_closing/README.md)

2. **Configure multi-company:**
   - Settings > Companies > Create companies for RIM, CKVC, BOM, etc.

3. **Setup security:**
   - Install auth_totp, password_security
   - Enable 2FA for admins

4. **Import data:**
   - Create closing periods
   - Setup task templates
   - Configure BIR forms

## Troubleshooting

**Service not starting?**
```bash
docker-compose -f docker-compose.oca.yml down
docker-compose -f docker-compose.oca.yml up -d
```

**Module not found?**
```bash
# Update module list
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf -d odoo19 --update-all --stop-after-init
```

**Database connection error?**
```bash
# Check PostgreSQL
docker-compose -f docker-compose.oca.yml exec db psql -U odoo -d odoo19 -c "\l"
```

## Production Deployment

For production deployment on DigitalOcean:

```bash
# 1. Create droplet
doctl compute droplet create insightpulse-odoo \
  --region sgp1 \
  --size s-8vcpu-16gb \
  --image ubuntu-22-04-x64

# 2. SSH to server
ssh root@<droplet-ip>

# 3. Follow Steps 1-4 above

# 4. Configure SSL
# See: docs/DEPLOYMENT_GUIDE_OCA.md#ssl-configuration
```

## Support

- **Documentation:** `/docs/`
- **GitHub Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues
- **OCA Community:** https://odoo-community.org/

---

**Last Updated:** 2025-11-05
