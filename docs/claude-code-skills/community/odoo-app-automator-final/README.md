# Odoo App Automator Skill

AI-powered automation for creating, deploying, and managing Odoo modules and custom applications.

## Quick Start

This skill enables AI agents to:

✅ **Generate complete Odoo modules** - Models, views, security, data  
✅ **Configure Odoo Studio** - Programmatic customizations  
✅ **Deploy to Odoo.sh** - Container setup and deployment  
✅ **Integrate third-party services** - APIs, payment providers, AI services  
✅ **Manage upgrades** - Version migrations and module updates

## Usage

Simply ask the AI agent to:

- "Create an Odoo module for BIR tax filing"
- "Build a travel expense management app"
- "Deploy this module to Odoo.sh staging"
- "Integrate Superset dashboards with Odoo"
- "Upgrade this module from Odoo 18 to 19"

## Contents

### SKILL.md
Main skill documentation with:
- Module scaffolding patterns
- Odoo Studio integration
- Container deployment
- Third-party integrations
- Upgrade management

### examples/
Practical implementations:
- **bir_tax_filing_module.md** - Philippine BIR compliance (Forms 1601-C, 2550Q, 1702-RT)
- **travel_expense_module.md** - SAP Concur alternative with OCR

### reference/
Technical documentation:
- **odoo_sh_deployment.md** - Container setup and deployment
- **odoo_studio_automation.md** - Studio configuration guide

## Real-World Use Cases

### Finance Shared Service Center

**Modules built using this skill:**
- BIR tax filing automation
- Multi-agency month-end closing
- Travel & expense management (replaces SAP Concur)
- Connection manager for infrastructure

**Agencies Supported:**
RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

**Cost Savings:**
- $14,400/year vs SAP Concur
- $4,728/year vs Tableau/Power BI (with Superset integration)
- Total: $19,128/year

### Key Features

1. **Production-Ready Code**: Following OCA guidelines
2. **Security Built-In**: Proper access control and record rules
3. **Performance Optimized**: Indexed fields, efficient queries
4. **Well-Documented**: Complete README and inline documentation
5. **Test Coverage**: Unit tests included

## Integration Points

Works seamlessly with:
- **Apache Superset** - BI dashboards
- **Supabase** - PostgreSQL database
- **PaddleOCR** - Document processing
- **Notion** - Task management
- **Google Drive** - File storage
- **MCP Servers** - AI agent integration

## Best Practices

The skill follows:
- Odoo 19 conventions
- OCA community guidelines
- PEP 8 Python style
- Semantic versioning
- Git workflow standards

## Requirements

- Odoo 19.0+
- Python 3.10+
- PostgreSQL 14+
- Git for version control

## License

LGPL-3.0 (consistent with Odoo)

## Support

Built for InsightPulse AI Finance SSC operations.

---

**Upload this skill to Claude.ai to enable automated Odoo module creation!**
