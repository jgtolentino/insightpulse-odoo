# InsightPulse Odoo - Finance SSC Automation

Complete Finance Shared Services Center automation for 8 agencies in the Philippines.

## Overview

**Agencies:** RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

**Automation Coverage:**
- BIR Compliance (4 forms × 8 agencies)
- Month-End Closing (8 tasks × 8 agencies = 64 tasks/month)
- Field Documentation (auto-generated from Odoo models)
- SOPs (extracted from docstrings)

**Time Savings:** ~20 hours/month → 20 minutes/month (98.3% reduction)

## Quick Start

### BIR Compliance
```bash
python scripts/bir_calendar_generator.py --year 2025 --month 1 --output docs/bir_calendar_2025_01.json
python scripts/bir_notion_sync.py --calendar docs/bir_calendar_2025_01.json
```

### Month-End Tasks
```bash
python scripts/month_end_generator.py --year 2025 --month 1 --output docs/month_end_tasks_2025_01.json
python scripts/month_end_notion_sync.py --tasks docs/month_end_tasks_2025_01.json
```

### Field Documentation
```bash
python scripts/extract_odoo_fields.py --addons addons odoo_addons --output docs/fields
python scripts/notion_field_docs_sync.py --metadata docs/fields/metadata.json
```

### SOPs
```bash
python scripts/docstring_sop_parser.py --addons addons odoo_addons --output docs/sops
```

## Architecture

**Stack:**
- Odoo 19.0 Enterprise
- Supabase PostgreSQL
- DigitalOcean App Platform
- Apache Superset (BI)
- Notion (knowledge management)

**Deployment:**
- Main: `main` branch → production
- Feature: `ipai-bridges-v1` → preview

## Documentation

See navigation sidebar for complete documentation.
