# InsightPulse Odoo Documentation

Welcome to the InsightPulse Odoo documentation! This directory contains comprehensive guides for users, developers, and administrators.

## 📚 Documentation Index

### Quick Start
- **[Main README](../README.md)** - Project overview and quick start
- **[QUICKSTART.md](../QUICKSTART.md)** - 5-minute deployment guide
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines

### Architecture & Design
- **[architecture/README.md](architecture/)** - System architecture overview
- **[architecture/tech-stack.md](architecture/tech-stack.md)** - Complete technology stack
- **[architecture/decisions/](architecture/decisions/)** - Architecture Decision Records (ADRs)
- **[architecture/integrations/](architecture/integrations/)** - Third-party service guides

### SaaS Parity & Gap Analysis
- **[saas-parity/README.md](saas-parity/)** - SaaS feature equivalence overview
- **[saas-parity/notion-enterprise.md](saas-parity/notion-enterprise.md)** - Notion → Odoo Knowledge mapping (87% parity)
- **[saas-parity/sap-concur.md](saas-parity/sap-concur.md)** - Concur → ipai_expense mapping (85% parity)
- **[saas-parity/sap-ariba.md](saas-parity/sap-ariba.md)** - Ariba → ipai_procure mapping (90% parity)
- **[saas-parity/tableau.md](saas-parity/tableau.md)** - Tableau → Superset mapping (110% parity)
- **[saas-parity/gap-matrix.csv](saas-parity/gap-matrix.csv)** - Automated gap tracking

### Deployment
- **[deployment/local-development.md](deployment/local-development.md)** - Local dev environment setup
- **[deployment/digitalocean-production.md](deployment/digitalocean-production.md)** - Production deployment to DigitalOcean
- **[deployment/ssl-setup.md](deployment/ssl-setup.md)** - SSL/TLS configuration
- **[deployment/backup-restore.md](deployment/backup-restore.md)** - Backup and restore procedures

### User Guides
- **[user-guides/finance-team/](user-guides/finance-team/)** - Finance team workflows
  - Month-end closing
  - BIR compliance
  - Expense reports
- **[user-guides/admin/](user-guides/admin/)** - System administration
  - User management
  - Security setup
  - Backup monitoring
- **[user-guides/developer/](user-guides/developer/)** - Developer guides
  - Custom module development
  - OCA contribution
  - API integration

### Compliance & Security
- **[compliance/bir-requirements.md](compliance/bir-requirements.md)** - Philippines BIR compliance
- **[compliance/gdpr.md](compliance/gdpr.md)** - GDPR compliance checklist
- **[compliance/soc2.md](compliance/soc2.md)** - SOC 2 controls mapping
- **[../SECURITY_AUDIT_REPORT.md](../SECURITY_AUDIT_REPORT.md)** - Complete security audit

## 🗺️ Project Status

- **[ROADMAP.md](ROADMAP.md)** - Product roadmap and future plans
- **[STATUS.md](STATUS.md)** - Current implementation status
- **[../CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes

## 📦 Module Documentation

Each module has its own README with detailed documentation:

### Finance Modules
- [ipai_rate_policy](../addons/insightpulse/finance/ipai_rate_policy/README.md) - Rate policy automation
- [ipai_ppm](../addons/insightpulse/finance/ipai_ppm/README.md) - Program & project management
- [ipai_ppm_costsheet](../insightpulse_odoo/addons/insightpulse/finance/ipai_ppm_costsheet/README.md) - Cost sheet analysis
- [ipai_expense](../insightpulse_odoo/addons/insightpulse/finance/ipai_expense/README.md) - OCR expense automation
- [ipai_subscriptions](../insightpulse_odoo/addons/insightpulse/finance/ipai_subscriptions/README.md) - Subscription management
- [ipai_approvals](../insightpulse_odoo/addons/insightpulse/finance/ipai_approvals/README.md) - Multi-stage approvals

### Operations Modules
- [ipai_procure](../insightpulse_odoo/addons/insightpulse/ops/ipai_procure/README.md) - Procurement & supplier management
- [ipai_saas_ops](../addons/insightpulse/ops/ipai_saas_ops/README.md) - SaaS tenant management
- [superset_connector](../insightpulse_odoo/addons/insightpulse/ops/superset_connector/README.md) - Apache Superset integration

### AI & Knowledge Modules
- [ipai_knowledge_ai](../insightpulse_odoo/addons/insightpulse/knowledge/ipai_knowledge_ai/README.md) - AI knowledge workspace

## 🤝 Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/jgtolentino/insightpulse-odoo/discussions)
- **Email**: support@insightpulseai.net

## 📝 Contributing to Documentation

Found an error or want to improve the docs? See our [Contributing Guide](../CONTRIBUTING.md).

All documentation is written in Markdown and follows the [Google Developer Documentation Style Guide](https://developers.google.com/style).
