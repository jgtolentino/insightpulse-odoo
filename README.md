# InsightPulse Odoo - Enterprise AI-Powered ERP Platform

## Architecture Overview

InsightPulse Odoo is a comprehensive enterprise resource planning platform enhanced with AI capabilities, built on Odoo 19.0 with custom modules for procurement, expense management, subscriptions, and business intelligence integration.

### Core Components

- **Odoo ERP Core**: Base Odoo 19.0 with custom modules
- **AI Integration**: Superset, Tableau, and custom BI connectors
- **Microservices**: Health monitoring and external service integration
- **Security**: Hardened security modules and access controls
- **Automation**: Pre-commit hooks, CI/CD, and documentation generation

### Module Categories

#### IPAI Core Modules
- `ipai_procure`: Procurement workflow with approvals and vendor management
- `ipai_expense`: Expense management with OCR audit capabilities
- `ipai_subscriptions`: Recurring subscription and usage tracking

#### Integration Modules
- `superset_connector`: Apache Superset BI integration
- `tableau_connector`: Tableau analytics integration
- `microservices_connector`: External service health monitoring

#### System Modules
- `apps_admin_enhancements`: Module management and refresh automation
- `security_hardening`: Security best practices and access controls

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Git

### Installation Order

1. **Clone and Setup**
   ```bash
   git clone https://github.com/jgtolentino/insightpulse-odoo.git
   cd insightpulse-odoo
   cp env.example .env
   # Edit .env with your configuration
   ```

2. **Start Core Services**
   ```bash
   docker-compose up -d postgres redis
   ```

3. **Initialize Odoo**
   ```bash
   docker-compose up -d odoo
   ```

4. **Install Modules**
   - Access Odoo at `http://localhost:8069`
   - Install base modules first: `apps_admin_enhancements`
   - Then install IPAI modules: `ipai_procure`, `ipai_expense`, `ipai_subscriptions`
   - Finally install integration modules

### Development Setup

1. **Install Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Run Tests**
   ```bash
   pre-commit run --all-files
   ```

3. **Generate Documentation**
   ```bash
   pre-commit run oca-gen-addon-readme --all-files
   ```

## Continuous Integration

The project uses GitHub Actions for automated testing and validation:

- **Code Quality**: Pylint, Flake8, Odoo module checks
- **Documentation**: Auto-generated README.rst files
- **Testing**: Odoo test suite execution
- **Security**: Pre-commit hooks and module validation

### CI Pipeline

```yaml
name: Odoo CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install pre-commit
      - name: Run pre-commit
        run: pre-commit run --all-files
      - name: Run Odoo tests
        run: docker-compose run odoo odoo --test-enable --stop-after-init
```

## Contributing

Please read our contributing guidelines in `CONTRIBUTING.md` and follow the OCA standards for module development.

## License

AGPL-3.0 - See LICENSE file for details.

## Support

- **Issues**: Use GitHub Issues with appropriate labels
- **Documentation**: Check `docs/` directory for detailed guides
- **Community**: Follow OCA standards and best practices
