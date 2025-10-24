# Installation Guide

## System Requirements

### Minimum Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB+ free space
- **OS**: Linux, macOS, or Windows with WSL2

### Software Requirements
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

## Step-by-Step Installation

### 1. Clone Repository
```bash
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
```

### 2. Environment Configuration
```bash
# Copy environment template
cp env/.env.example env/.env

# Edit with your settings
nano env/.env
```

**Required Environment Variables:**
```bash
DOMAIN=your-domain.com
EMAIL=your-email@domain.com
POSTGRES_DB=odoo
POSTGRES_USER=odoo
POSTGRES_PASSWORD=secure_password_here
OCR_PROVIDER=tesseract
```

### 3. Fetch OCA Modules
```bash
./scripts/fetch_oca.sh
```

This script clones the following OCA repositories:
- server-tools
- server-auth
- web
- queue
- account-financial-tools
- reporting-engine
- hr
- purchase-workflow

### 4. Start Services
```bash
# Start all services
docker compose up -d --build

# Check service status
docker compose ps

# View logs
docker compose logs -f odoo
```

### 5. Install Odoo Modules
```bash
# Install all available modules
COMPOSE_DIR=$(pwd) ADMIN_PASSWD='your_secure_password' ./scripts/install_modules.sh odoo
```

## Initial Setup

### 1. Access Odoo
- Open: `https://your-domain.com/odoo`
- Login with admin credentials

### 2. Configure System Parameters
Go to **Settings → Technical → Parameters → System Parameters** and set:

- `web.base.url`: `https://your-domain.com`
- `web.base.url.freeze`: `True`
- `hr_expense_ocr_audit.ocr_api_url`: `https://your-domain.com/ocr`

### 3. Security Configuration
- Enable 2FA in **Settings → Users & Companies → Users**
- Change default admin password
- Configure user access rights

### 4. Company Configuration
- Set company details in **Settings → Users & Companies → Companies**
- Configure fiscal year and chart of accounts
- Set up payment methods

## Module Installation Status

After running the installation script, verify these key modules are installed:

### Security & Access
- [ ] `auth_totp` - Two-factor authentication
- [ ] `auth_password_policy` - Password complexity
- [ ] `auth_session_timeout` - Session management
- [ ] `base_user_role` - Role-based access
- [ ] `auditlog` - Activity logging

### Performance & Server
- [ ] `queue_job` - Asynchronous job processing
- [ ] `server_environment` - Environment configuration
- [ ] `base_cron_exclusion` - Cron management

### Accounting & Finance
- [ ] `account_financial_report` - Financial statements
- [ ] `account_asset_management` - Fixed assets
- [ ] `account_payment_order` - Payment processing

### HR & Operations
- [ ] `hr` - Human resources
- [ ] `hr_contract` - Employee contracts
- [ ] `hr_holidays` - Leave management
- [ ] `hr_payroll_community` - Payroll

### CRM & Marketing
- [ ] `crm` - Customer relationship management
- [ ] `marketing_automation` - Campaign automation
- [ ] `mass_mailing` - Email marketing

### Productivity
- [ ] `project` - Project management
- [ ] `helpdesk` - Support ticketing
- [ ] `knowledge_notion_clone` - Notion-style workspace

## Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check if ports are in use
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Stop conflicting services or change ports in docker-compose.yml
```

**Database Connection Issues**
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Test database connection
docker compose exec postgres psql -U odoo -d odoo -c "SELECT version();"
```

**Module Installation Failures**
```bash
# Check Odoo logs for specific errors
docker compose logs odoo

# Try installing modules individually
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -i module_name --stop-after-init
```

**SSL Certificate Issues**
```bash
# Check Caddy logs
docker compose logs caddy

# Verify domain configuration in env/.env
```

### Performance Optimization

**Database Optimization**
```bash
# Regular vacuum and analyze
docker compose exec postgres psql -U odoo -d odoo -c "VACUUM ANALYZE;"
```

**Cache Configuration**
- Configure Redis for session caching
- Enable Odoo's built-in caching mechanisms

## Next Steps

After successful installation:

1. **Configure Users**: Set up user accounts and permissions
2. **Import Data**: Import existing customer, product, and accounting data
3. **Customize Workflows**: Adapt business processes to your needs
4. **Set Up Backups**: Configure automated backup procedures
5. **Monitor Performance**: Set up monitoring and alerting

## Support

- Check the `docs/OPERATIONS.md` for day-to-day operations
- Review `docs/UPGRADES.md` for upgrade procedures
- Create GitHub issues for bug reports and feature requests
