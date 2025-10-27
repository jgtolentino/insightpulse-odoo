# Enterprise Features to OCA Modules Mapping

## Complete Feature Replacement Guide

### Accounting & Finance

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Accounting Reports** | `account_financial_report`<br>`mis_builder` | `docker compose exec odoo odoo -d production -i account_financial_report,mis_builder --stop-after-init` |
| **Budget Management** | `budget_control`<br>`account_budget` | Repo: OCA/account-budgeting |
| **Assets Management** | `account_asset_management` | Repo: OCA/account-financial-tools |
| **Invoice OCR** | `account_invoice_extract` | Repo: OCA/account-invoicing |

### Studio & Customization

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Studio** | `web_studio_oca` | `docker compose exec odoo odoo -d production -i web_studio_oca --stop-after-init` |
| **Custom Reports** | `mis_builder`<br>`report_xlsx` | Repo: OCA/reporting-engine |

### CRM & Sales

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Advanced CRM** | `crm_*` modules | Repo: OCA/crm |
| **Sale Subscriptions** | `sale_subscription`<br>`contract` | Repo: OCA/contract |

### HR & Expenses

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **HR Expenses Advanced** | `hr_expense_advance_clearing`<br>`hr_expense_invoice` | `docker compose exec odoo odoo -d production -i hr_expense_advance_clearing,hr_expense_invoice --stop-after-init` |
| **Timesheets** | `hr_timesheet_sheet` | Repo: OCA/timesheet |
| **Appraisals** | `hr_appraisal` | Repo: OCA/hr |
| **Recruitment** | `hr_recruitment_*` | Repo: OCA/hr |

### Helpdesk & Support

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Helpdesk** | `helpdesk_mgmt`<br>`helpdesk_mgmt_ticket_type` | `docker compose exec odoo odoo -d production -i helpdesk_mgmt,helpdesk_mgmt_ticket_type --stop-after-init` |
| **Tickets** | `helpdesk_ticket_*` | Repo: OCA/helpdesk |

### Project Management

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Project** | `project_task_default_stage`<br>`project_timeline` | `docker compose exec odoo odoo -d production -i project_task_default_stage,project_timeline --stop-after-init` |
| **Gantt Charts** | `web_timeline` | Repo: OCA/web |

### Manufacturing

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **MRP Advanced** | `mrp_*` modules | Repo: OCA/manufacture |
| **Quality Control** | `quality_control_*` | Repo: OCA/manufacture |
| **PLM** | `product_*` | Repo: OCA/product-attribute |

### Maintenance

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Maintenance** | `maintenance_*`<br>`maintenance_plan` | `docker compose exec odoo odoo -d production -i maintenance_plan --stop-after-init` |

### Documents & Sign

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Sign** | `agreement`<br>`agreement_legal` | Repo: OCA/contract |
| **Documents** | `dms` (Document Management) | Repo: OCA/dms |

### Planning & Calendar

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Planning** | `resource_booking`<br>`calendar_*` | Repo: OCA/calendar |

### Dashboards & BI

| Enterprise Feature | OCA Modules | Installation |
|-------------------|-------------|--------------|
| **Dashboards** | `mis_builder`<br>`kpi_dashboard` | `docker compose exec odoo odoo -d production -i mis_builder,kpi_dashboard --stop-after-init` |

## Installation Commands by Use Case

### Basic Business (Small Company)
```bash
# Accounting + Studio + Helpdesk
docker compose exec odoo odoo -d production -i \
  account_financial_report,mis_builder,\
  web_studio_oca,\
  helpdesk_mgmt \
  --stop-after-init
```

### Service Company
```bash
# Project + Timesheets + Helpdesk
docker compose exec odoo odoo -d production -i \
  project_task_default_stage,project_timeline,\
  hr_timesheet_sheet,\
  helpdesk_mgmt,helpdesk_mgmt_ticket_type \
  --stop-after-init
```

### Manufacturing Company
```bash
# MRP + Quality + Maintenance
docker compose exec odoo odoo -d production -i \
  mrp_bom_structure,mrp_production_note,\
  quality_control,\
  maintenance_plan \
  --stop-after-init
```

### Your IPAI Use Case
```bash
# Document OCR + Expenses + BIR Compliance
docker compose exec odoo odoo -d production -i \
  account_financial_report,mis_builder,\
  hr_expense_advance_clearing,hr_expense_invoice,\
  ipai_document_ocr,\
  ipai_expense_management,\
  ipai_bir_compliance \
  --stop-after-init
```

## Cost Savings Calculator

### Per-User Annual Cost
```
Enterprise Feature: $432/user/year
OCA Alternative: $0/year
Savings: $432/user/year
```

### By Company Size

| Users | Enterprise Cost | OCA Cost | Annual Savings |
|-------|----------------|----------|----------------|
| 5 | $2,160/year | $0 | $2,160 (100%) |
| 10 | $4,320/year | $0 | $4,320 (100%) |
| 25 | $10,800/year | $0 | $10,800 (100%) |
| 50 | $21,600/year | $0 | $21,600 (100%) |
| 100 | $43,200/year | $0 | $43,200 (100%) |

*Plus hosting: Enterprise $720/year vs Self-hosted $288/year*

## OCA Repository List

Key repositories:
- `OCA/server-tools` - Server utilities
- `OCA/web` - Web interface enhancements
- `OCA/account-financial-reporting` - Financial reports
- `OCA/account-financial-tools` - Accounting tools
- `OCA/helpdesk` - Helpdesk system
- `OCA/project` - Project management
- `OCA/hr-expense` - Expense management
- `OCA/manufacture` - Manufacturing
- `OCA/reporting-engine` - Report builders
- `OCA/contract` - Contracts & agreements

Browse all: https://github.com/OCA

## Feature Comparison

### Studio vs web_studio_oca
✅ Visual view editor  
✅ Model creation  
✅ Field customization  
✅ Menu customization  
❌ Workflow automation (use server-tools instead)

### Accounting Reports vs account_financial_report + mis_builder
✅ Balance Sheet  
✅ Profit & Loss  
✅ Trial Balance  
✅ General Ledger  
✅ Custom KPI dashboards (mis_builder)  
✅ Budget vs Actual  

### Helpdesk vs helpdesk_mgmt
✅ Ticket management  
✅ SLA tracking  
✅ Team management  
✅ Email integration  
❌ Live chat (use website_livechat instead)

## Next Steps After Installation

1. **Configure modules**: Set up teams, categories, workflows
2. **Customize views**: Use web_studio_oca to adapt to your needs
3. **Train users**: OCA modules have similar UX to Enterprise
4. **Integrate systems**: Connect with external APIs as needed
5. **Monitor usage**: Track adoption and adjust configuration
