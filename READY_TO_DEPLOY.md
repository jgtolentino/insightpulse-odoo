# ✅ Odoo 19 Enterprise + Notion Clone - Ready to Deploy

## 🎯 Configuration Summary

**Domain:** `insightpulseai.net`
**Admin Email:** `jgtolentino_rn@yahoo.com`
**Master Password:** `InsightPulse2025!`
**Database:** `odoo` / User: `odoo` / Pass: `odoo`

## 📦 What's Installed

### Core Services
- ✅ Odoo 19 (latest)
- ✅ PostgreSQL 14
- ✅ Redis 6
- ✅ Caddy 2.8 (automatic HTTPS)
- ✅ OnlyOffice Document Server

### OCA Modules Ready
Located in `bundle/addons/oca/`:
- `server-tools` - Core utilities
- `server-auth` - Authentication enhancements
- `web` - Web UI improvements
- `queue` - Background job processing
- `account-financial-tools` - Accounting features
- `reporting-engine` - Report generation
- `hr` - Human resources
- `purchase-workflow` - Purchase management

### Custom Addons
- `knowledge_notion_clone` - Notion-style workspace with pages & databases

## 🚀 Deployment Steps

### 1. DNS Configuration (Do This First!)

Point your domain to your server:

```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 300

Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 300
```

**Wait 5-10 minutes** for DNS propagation before proceeding.

### 2. Server Deployment

Upload the bundle to your DigitalOcean droplet:

```bash
# From your local machine
cd /Users/tbwa/insightpulse-odoo
tar czf odoo19-bundle.tar.gz bundle/
scp odoo19-bundle.tar.gz root@YOUR_DROPLET_IP:/opt/

# On the droplet
ssh root@YOUR_DROPLET_IP
cd /opt
tar xzf odoo19-bundle.tar.gz
cd bundle

# Start services
docker compose up -d
```

### 3. Initial Database Setup

Access via browser:
```
http://YOUR_DROPLET_IP
```

1. Create database `odoo`
2. Set admin password and email
3. Click "Create database"
4. Wait 2-3 minutes for initialization

### 4. Install Modules

From Apps menu, search and install:

**Essential Security:**
- Two-Factor Authentication (auth_totp)
- Password Security (auth_password_policy)
- Session Timeout (auth_session_timeout)
- User Roles (base_user_role)

**UI Improvements:**
- Responsive Design (web_responsive)
- Environment Ribbon (web_environment_ribbon)

**Background Processing:**
- Queue Jobs (queue_job)

**Knowledge Management:**
- Notion Clone (knowledge_notion_clone) ⭐

**Reporting:**
- XLSX Reports (report_xlsx)

### 5. Configure HTTPS

Once DNS is propagated, Caddy will automatically:
- Request TLS certificate from Let's Encrypt
- Configure HTTPS
- Set up auto-renewal

Check HTTPS status:
```bash
curl -I https://insightpulseai.net
```

## 📋 Post-Installation

### Access Points
- **Main URL:** https://insightpulseai.net
- **Database Manager:** https://insightpulseai.net/web/database/manager
- **Master Password:** `InsightPulse2025!`

### Recommended Settings

1. **System Parameters** (Settings → Technical → Parameters):
   - `web.base.url` = `https://insightpulseai.net`
   - `expenseflow.ocr_url` = `http://ocr-api:8000/parse`

2. **Email Configuration** (Settings → Technical → Outgoing Mail):
   - Configure SMTP for notifications
   - Test with `jgtolentino_rn@yahoo.com`

3. **Users** (Settings → Users):
   - Create additional admin/user accounts
   - Set up 2FA for all users

### Knowledge/Notion Clone Usage

Access from: **Apps → Knowledge → Workspace**

Features:
- Create hierarchical pages
- Add blocks: text, headings, todos, dividers
- Create databases with custom properties
- Favorite important pages
- Search and navigate pages

## 🔒 Security Checklist

- [ ] DNS configured and propagated
- [ ] HTTPS certificate obtained
- [ ] Master password changed from default
- [ ] Admin user created with strong password
- [ ] 2FA enabled for all admin users
- [ ] Firewall rules configured (ports 80, 443, 22 only)
- [ ] fail2ban installed and configured
- [ ] Regular backup schedule established

## 📚 Additional Resources

- **Odoo Documentation:** https://www.odoo.com/documentation/19.0/
- **OCA GitHub:** https://github.com/OCA
- **Support:** jgtolentino_rn@yahoo.com

## 🆘 Troubleshooting

### Services not starting
```bash
docker compose logs --tail=100
docker compose restart
```

### Database connection errors
```bash
docker compose logs postgres
# Check credentials in .env match odoo.conf
```

### HTTPS not working
```bash
docker compose logs caddy
# Ensure DNS is propagated: dig insightpulseai.net
# Ensure ports 80/443 are open
```

### Module installation fails
```bash
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u MODULE_NAME --stop-after-init
```

---

**Status:** ✅ Ready for deployment to insightpulseai.net
**Created:** 2025-10-24
**Contact:** jgtolentino_rn@yahoo.com
