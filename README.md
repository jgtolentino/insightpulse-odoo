# InsightPulse Odoo CE – ERP Platform

[![odoo-ce-ci](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-ce.yml/badge.svg)](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-ce.yml)

**Self-hosted Odoo Community Edition + OCA stack for expense management and equipment booking.**

## Overview

This repository contains the **InsightPulse Odoo CE** implementation—a pure **Community Edition** deployment that replaces:

- **SAP Concur** for expense & travel management workflows (PH-focused)
- **Cheqroom** for equipment catalog, bookings, and incident tracking

### Key Constraints

✅ **CE + OCA only** – No Odoo Enterprise modules or IAP dependencies
✅ **No odoo.com upsells** – All branding and links point to InsightPulse or OCA
✅ **Self-hosted** – Full control via Docker/Kubernetes on DigitalOcean
✅ **Production URL** – `https://erp.insightpulseai.net`

## Repository Structure

```
odoo-ce/
├── addons/                    # Custom InsightPulse modules
│   ├── ipai_expense/          # PH expense & travel workflows
│   ├── ipai_equipment/        # Equipment booking system
│   └── ipai_ce_cleaner/       # Enterprise/IAP removal
├── oca/                       # OCA community addons (git submodules)
├── deploy/                    # Deployment configurations
│   ├── docker-compose.yml     # Docker Compose stack
│   ├── odoo.conf              # Odoo CE configuration
│   └── nginx/                 # Nginx reverse proxy configs
├── specs/                     # Product requirement documents
│   └── 002-odoo-expense-equipment-mvp.prd.md
├── .github/workflows/         # CI/CD pipelines
│   └── ci-odoo-ce.yml         # CE/OCA guardrails
├── spec.md                    # Project specification
├── plan.md                    # Implementation plan
└── tasks.md                   # Task checklist
```

## Quick Start

### M1 One-Shot Deployment (Recommended)

**For fresh DigitalOcean Ubuntu 22.04/24.04 droplets:**

1. **Prepare DNS**
   - Point `erp.insightpulseai.net` A record to your droplet IP
   - Wait for DNS propagation (check with `host erp.insightpulseai.net`)

2. **SSH into droplet as root**
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Download and run deployment script**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/deploy_m1.sh.template -o deploy_m1.sh
   chmod +x deploy_m1.sh
   sudo ./deploy_m1.sh
   ```

4. **What it does**
   - ✅ Installs Docker, Nginx, Certbot, UFW firewall
   - ✅ Auto-generates strong database and admin passwords
   - ✅ Clones repository and configures Odoo
   - ✅ Obtains Let's Encrypt SSL certificate
   - ✅ Starts Odoo stack with health checks
   - ✅ Configures automated daily backups (2 AM UTC)
   - ✅ Handles existing deployments safely (prompt: Update/Redeploy/Exit)

5. **Access Odoo**
   - Navigate to `https://erp.insightpulseai.net/web`
   - Use admin password from deployment output
   - Create database: `odoo` or `insightpulse`
   - Install modules: `IPAI Expense & Travel`, `IPAI Equipment Management`

6. **Credentials location**
   ```bash
   cat /opt/odoo-ce/deploy/.env  # Auto-generated secrets
   tail -f /var/log/odoo_deploy.log  # Deployment logs
   ```

### Manual Deployment (Advanced)

**Prerequisites:**
- Docker & Docker Compose
- Domain pointing to your server: `erp.insightpulseai.net`
- Nginx (for SSL termination and reverse proxy)

1. **Clone repository**
   ```bash
   git clone https://github.com/jgtolentino/odoo-ce.git
   cd odoo-ce
   ```

2. **Configure secrets**
   ```bash
   cd deploy
   # Generate strong passwords
   DB_PASSWORD=$(openssl rand -base64 32)
   ADMIN_PASSWORD=$(openssl rand -base64 32)

   # Replace placeholders
   sed -i "s/CHANGE_ME_STRONG_DB_PASSWORD/$DB_PASSWORD/g" odoo.conf docker-compose.yml
   sed -i "s/CHANGE_ME_SUPERMASTER_PASSWORD/$ADMIN_PASSWORD/g" odoo.conf
   ```

3. **Start stack**
   ```bash
   docker compose up -d
   ```

4. **Configure Nginx**
   ```bash
   sudo cp nginx/erp.insightpulseai.net.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/erp.insightpulseai.net.conf \
              /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

5. **Obtain SSL certificate**
   ```bash
   sudo certbot certonly --standalone \
     --email jgtolentino_rn@yahoo.com \
     -d erp.insightpulseai.net
   sudo systemctl reload nginx
   ```

6. **Access Odoo**
   - Navigate to `https://erp.insightpulseai.net/web`
   - Create database: `odoo` or `insightpulse`
   - Install modules: `IPAI Expense & Travel`, `IPAI Equipment Management`

## Custom Modules

### `ipai_expense`
PH-focused expense and travel management:
- Expense capture with receipt attachments
- Travel request workflows (Draft → Manager → Finance)
- GL posting integration with CE `account` module
- Project/job code tracking

### `ipai_equipment`
Cheqroom-style equipment management:
- Asset catalog with serial numbers and conditions
- Booking system with conflict detection
- Check-out/check-in workflows
- Incident reporting and maintenance tracking

### `ipai_ce_cleaner`
Enterprise/IAP removal:
- Hides "Upgrade to Enterprise" banners
- Removes IAP credit/SMS/email upsell menus
- Rewires help links to InsightPulse docs or OCA

## CI/CD Guardrails

GitHub Actions enforces CE/OCA-only policy:

✅ **Fails build if**:
- Enterprise module references detected in `addons/` or `oca/`
- `odoo.com` links found in user-facing code

See [`.github/workflows/ci-odoo-ce.yml`](.github/workflows/ci-odoo-ce.yml)

## Development

### Adding OCA Modules

```bash
# Add OCA repo as git submodule
git submodule add https://github.com/OCA/account-financial-tools.git oca/account-financial-tools

# Update odoo.conf addons_path if needed
# Restart Odoo container
docker compose restart odoo
```

### Local Testing

```bash
# Start stack locally
cd deploy
docker compose up

# Watch logs
docker compose logs -f odoo
```

## Documentation

- **Project Spec**: [`spec.md`](spec.md)
- **Implementation Plan**: [`plan.md`](plan.md)
- **Task Checklist**: [`tasks.md`](tasks.md)
- **PRD**: [`specs/002-odoo-expense-equipment-mvp.prd.md`](specs/002-odoo-expense-equipment-mvp.prd.md)

## License

Custom modules (`ipai_*`): **AGPL-3**
OCA modules: See respective module licenses in `oca/`

## Support

- **Issues**: [GitHub Issues](https://github.com/jgtolentino/odoo-ce/issues)
- **Documentation**: `https://docs.insightpulseai.net/erp`
- **Owner**: InsightPulseAI – ERP Platform Team

---

**Status**: Active development | MVP Phase 0-1 (CE/OCA Base Stack)
