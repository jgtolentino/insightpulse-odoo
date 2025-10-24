# InsightPulse Odoo 19 Enterprise Deployment

A production-grade, self-hosted Odoo 19 deployment with enterprise-equivalent features, built on open-source OCA modules and custom applications.

## 🚀 Purpose

This repository provides a complete Odoo 19 deployment with enterprise-level functionality including:

- **Notion-style knowledge workspace**
- **Expense capture with OCR integration**
- **Vendor rate card management**
- **Project budgeting and approval workflows**
- **Client portal with statement of account**
- **Mobile-responsive PWA interface**
- **AI-powered analytics and dashboards**

## 📋 Prerequisites

- Docker & Docker Compose
- Git
- Domain name (for SSL certificates)

## 🛠️ Quick Deployment

### 1. Clone and Setup
```bash
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
```

### 2. Configure Environment
```bash
cp env/.env.example env/.env
# Edit env/.env with your domain and credentials
```

### 3. Fetch OCA Modules
```bash
./scripts/fetch_oca.sh
```

### 4. Start Services
```bash
docker compose up -d --build
```

### 5. Install Modules
```bash
COMPOSE_DIR=$(pwd) ADMIN_PASSWD='STRONG_PASSWORD' ./scripts/install_modules.sh odoo
```

## 🔧 Post-Installation

1. **Access Odoo**: https://your-domain.com/odoo
2. **Configure System Parameters**:
   - Set `web.base.url` to your domain
   - Set `hr_expense_ocr_audit.ocr_api_url` to OCR endpoint
3. **Enable 2FA** for security
4. **Configure backup schedules**

## 📁 Repository Structure

```
insightpulse-odoo/
├─ docker-compose.yml          # Main deployment configuration
├─ odoo/odoo.conf             # Odoo server configuration
├─ caddy/Caddyfile            # Reverse proxy & SSL
├─ addons/                    # Custom and OCA modules
├─ scripts/                   # Deployment and maintenance scripts
├─ services/                  # Additional services (OCR API)
├─ env/                       # Environment configuration
├─ .github/workflows/         # CI/CD pipelines
└─ docs/                      # Documentation
```

## 🔒 Security Notes

- Change all default passwords in `env/.env`
- Enable 2FA authentication
- Regularly update Odoo and dependencies
- Configure proper backup strategies
- Monitor logs for suspicious activity

## 📊 Features

### Core Enterprise Modules
- **Security**: TOTP, password policies, session timeout
- **Accounting**: Financial reports, asset management, budget control
- **HR**: Contracts, expenses, holidays, payroll
- **CRM**: Marketing automation, mass mailing, events
- **Productivity**: Projects, helpdesk, timesheets, knowledge base
- **Reporting**: Excel/CSV exports, dashboards, SQL analytics

### Custom Applications
- **Knowledge Notion Clone**: Document/wiki with tags and search
- **BI Superset Agent**: AI-powered analytics integration
- **ExpenseFlow OCR**: Automated expense receipt processing

## 🛡️ Backup & Restore

### Backup Database
```bash
docker compose exec postgres pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
docker compose exec -T postgres psql -U odoo odoo < backup_file.sql
```

## 🔄 Upgrades

See `docs/UPGRADES.md` for detailed upgrade procedures.

## 📞 Support

- **Documentation**: Check `docs/` directory
- **Issues**: GitHub Issues
- **Security**: Report vulnerabilities via security advisory

## 📄 License

This project is licensed under the appropriate open-source licenses for Odoo and OCA modules.

---

**Production Ready**: This deployment follows enterprise standards with proper reverse proxy, SSL termination, service isolation, and CI/CD validation.
