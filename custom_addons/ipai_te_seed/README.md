# IPAI Travel & Expense Seed Module

## Overview

The `ipai_te_seed` module provides essential seed data and configuration for Travel & Expense (T&E) management in InsightPulse AI's multi-agency environment.

## Features

### 1. Chart of Accounts
- Travel Expenses (Domestic & Foreign)
- Meals & Entertainment
- Accommodation
- Transportation & Fuel
- Cash Advance accounts (Receivable/Payable)

### 2. Journals
- Travel & Expense Journal (EXP)
- Cash Advances Journal (CADV)

### 3. Expense Products
Pre-configured expense products:
- Airfare
- Hotel/Accommodation
- Taxi/Ride Share
- Mileage Reimbursement
- Client Meals
- Per Diem - Meals

### 4. MIS Builder KPIs
Key performance indicators for T&E management:
- Total Travel Expenses
- Meals & Entertainment tracking
- Outstanding Cash Advances
- Average Expense Processing Time

### 5. Multi-Agency Company Structure
Demo data for InsightPulse AI agencies:
- **RIM** - Research & Innovation Management
- **CKVC** - Connectivity & Virtual Collaboration
- **BOM** - Business Operations Management
- **JPAL** - Joint Procurement & Logistics
- **JLI** - Joint Legal & IP
- **JAP** - Joint Audit & Process
- **LAS** - Learning & Skills
- **RMQB** - Risk Management & Quality Bench

### 6. Demo Data
Sample expense records for testing and training purposes.

## Dependencies

- `account` - Core accounting module
- `hr_expense` - HR Expense management
- `mis_builder` - OCA MIS Builder for KPIs

## Installation

```bash
# Via Odoo CLI
odoo -d odoo --init ipai_te_seed

# Via Docker (one-shot install)
docker run --rm --network <network_name> \
  -v /opt/odoo/custom_addons:/mnt/extra-addons:ro \
  -e INIT=1 \
  -e HOST=insightpulse-db \
  -e USER=odoo \
  -e PASSWORD=odoo \
  -e PGDATABASE=odoo \
  -e ODOO_INSTALL="account,hr_expense,mis_builder,ipai_te_seed" \
  ghcr.io/jgtolentino/odoo-18-ce:latest
```

## Configuration

After installation:

1. **Review Chart of Accounts**: Navigate to Accounting > Configuration > Chart of Accounts
2. **Configure Journals**: Check Accounting > Configuration > Journals
3. **Review Expense Products**: Go to Expenses > Configuration > Expense Products
4. **Setup MIS Reports**: Access MIS Reports > Configuration > MIS Report Templates

## Usage

### For Administrators
- Use demo companies to test multi-agency expense workflows
- Configure expense approval hierarchies per agency
- Set up expense policies and limits

### For Developers
- Extend with custom expense categories
- Add BIR compliance fields
- Integrate with OCR receipt processing
- Connect to Supabase for analytics

## BIR Compliance

This module provides the foundation for Philippine BIR compliance:
- Account codes follow Philippine Chart of Accounts
- Expense categories align with BIR allowable deductions
- Ready for 2307 (Withholding Tax) integration

## License

LGPL-3

## Author

InsightPulseAI
