# InsightPulse AI - PRD Implementation Roadmap

**Document Version**: 1.0
**Date**: 2025-11-11
**Status**: 🟢 Ready for M0 Execution

---

## Executive Summary

This document maps the InsightPulse AI Enterprise SaaS Parity Platform PRD to the current codebase state and provides a detailed implementation roadmap for M0-M2 milestones (12 weeks).

### North Star Metrics
- **Cost Savings Target**: $25,000+ annual vs Enterprise licenses
- **BIR Compliance**: 98% validation pass rate
- **Finance SSC Hours Saved**: 20 hours/month
- **Deployment Frequency**: Daily (via CI/CD)

---

## Current State Assessment

### ✅ What Already Exists (Strong Foundation)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| Docker Compose | ✅ Complete | `/docker-compose.yml` | Odoo 18.0 + PostgreSQL + Redis + Celery |
| Dockerfile | ✅ Complete | `/Dockerfile.odoo` | 3-layer architecture (ipai > OCA > CE) |
| OCA Modules | ✅ Complete | `/bundle/addons/oca/` | 18 repositories vendored |
| Custom Modules | ✅ Complete | `/odoo_addons/` | 19 ipai_* modules |
| GitHub Actions | ✅ Complete | `/.github/workflows/` | 120+ CI/CD workflows |
| Deploy Scripts | ✅ Complete | `/scripts/deploy/` | Production DigitalOcean deployment |
| Configuration | ✅ Complete | `/config/odoo.conf` | Multi-company support configured |
| Environment | ✅ Complete | `/.env.example` | Comprehensive env vars |

### ⚠️ What Needs to Be Built (PRD Gaps)

#### M0 - Foundation (Weeks 1-4)
| Requirement | Status | Priority | Estimated Effort |
|-------------|--------|----------|------------------|
| BIR Compliance Module | ❌ Missing | P0 | 8 hours |
| Multi-Org Database Script | ❌ Missing | P0 | 4 hours |
| Seed Data Script (8 orgs) | ❌ Missing | P0 | 6 hours |
| Superset Docker Service | ❌ Missing | P1 | 4 hours |
| Update docker-compose.yml | ⚠️ Partial | P1 | 2 hours |

#### M1 - BIR Compliance Core (Weeks 5-8)
| Requirement | Status | Priority | Estimated Effort |
|-------------|--------|----------|------------------|
| BIR 1601-C Generator | ❌ Missing | P0 | 12 hours |
| BIR eBIRForms XML Exporter | ❌ Missing | P0 | 8 hours |
| BIR Validation Engine | ❌ Missing | P0 | 10 hours |
| BIR 2550Q Form | ❌ Missing | P1 | 6 hours |
| Unit Tests (>98% pass) | ❌ Missing | P0 | 8 hours |

#### M2 - Multi-Org + Superset (Weeks 9-12)
| Requirement | Status | Priority | Estimated Effort |
|-------------|--------|----------|------------------|
| Multi-Database Setup | ❌ Missing | P0 | 6 hours |
| Superset Dashboards (5) | ❌ Missing | P0 | 16 hours |
| Superset SSO Integration | ❌ Missing | P1 | 8 hours |
| Consolidated SQL Views | ❌ Missing | P0 | 10 hours |

---

## Architecture Alignment

### PRD Architecture vs Current Implementation

#### ✅ Aligned Components

**Frontend Layer**
- PRD: Odoo Web Client (OWL framework)
- Current: ✅ Odoo 18.0 with OWL framework
- Gap: None

**Backend Layer**
- PRD: Odoo Server (Python 3.10+) + OCA modules
- Current: ✅ Odoo 18.0 (Python 3.12) + 18 OCA repositories
- Gap: None

**Data Layer**
- PRD: PostgreSQL 15
- Current: ✅ PostgreSQL 15 configured
- Gap: Multi-database setup for 8 orgs (needs implementation)

**Auth**
- PRD: Odoo RBAC
- Current: ✅ Odoo built-in RBAC
- Gap: None

#### ⚠️ Missing Components

**Superset Integration**
- PRD: Apache Superset for BI dashboards
- Current: ❌ Not in docker-compose.yml
- Action: Add Superset service to docker-compose

**BIR Module**
- PRD: Custom bir_compliance module
- Current: ⚠️ Only calendar generator script exists
- Action: Create full Odoo module

**Multi-Org Setup**
- PRD: 8 separate databases (db_rim, db_ckvc, ...)
- Current: ❌ Single database setup
- Action: Create multi-org provisioning scripts

---

## M0 - Foundation (Weeks 1-4) - Implementation Plan

### Week 1: BIR Compliance Module Skeleton

**Goal**: Create bir_compliance Odoo module structure

**Deliverables**:
```
odoo_addons/
└── ipai_bir_compliance/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── bir_form_1601c.py
    │   ├── bir_form_2550q.py
    │   └── bir_form_1702rt.py
    ├── views/
    │   ├── bir_form_1601c_views.xml
    │   ├── bir_form_2550q_views.xml
    │   └── bir_menu.xml
    ├── reports/
    │   ├── bir_1601c_pdf_template.xml
    │   └── bir_reports.xml
    ├── data/
    │   ├── bir_validation_rules.xml
    │   └── bir_tax_codes.xml
    ├── security/
    │   └── ir.model.access.csv
    ├── tests/
    │   ├── __init__.py
    │   └── test_bir_1601c.py
    └── README.md
```

**Acceptance Criteria**:
- [ ] Module appears in Odoo Apps menu
- [ ] Installable without errors
- [ ] Basic menu structure visible
- [ ] Unit test framework setup

**Estimated Time**: 8 hours

---

### Week 2: Multi-Org Database Scripts

**Goal**: Create scripts to provision 8 organization databases

**Deliverables**:
```bash
scripts/
├── multi-org/
│   ├── create-multi-org-dbs.sh
│   ├── seed-demo-data.py
│   ├── agencies.json
│   └── README.md
```

**Script: create-multi-org-dbs.sh**
```bash
#!/bin/bash
# Creates 8 databases for RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

AGENCIES=("rim" "ckvc" "bom" "jpal" "jli" "jap" "las" "rmqb")

for agency in "${AGENCIES[@]}"; do
    DB_NAME="db_${agency}"
    echo "Creating database: $DB_NAME"
    docker-compose exec -T postgres psql -U odoo -c "CREATE DATABASE $DB_NAME TEMPLATE template0 ENCODING 'UTF8';"

    # Initialize Odoo database
    docker-compose exec -T odoo odoo -d $DB_NAME -i base --stop-after-init

    echo "✓ Database $DB_NAME created"
done
```

**Acceptance Criteria**:
- [ ] Script creates 8 databases successfully
- [ ] Each database accessible in Odoo
- [ ] Base modules installed in each
- [ ] No errors during provisioning

**Estimated Time**: 4 hours

---

### Week 3: Seed Data Script

**Goal**: Populate 8 databases with realistic demo data

**Deliverables**:
```python
# scripts/multi-org/seed-demo-data.py
import odoorpc
import os
from faker import Faker

AGENCIES = {
    "rim": {"name": "Refugee International Mission", "tin": "123-456-789-000"},
    "ckvc": {"name": "CKVC Foundation", "tin": "234-567-890-000"},
    "bom": {"name": "BOM Organization", "tin": "345-678-901-000"},
    "jpal": {"name": "JPAL Philippines", "tin": "456-789-012-000"},
    "jli": {"name": "JLI Institute", "tin": "567-890-123-000"},
    "jap": {"name": "JAP Association", "tin": "678-901-234-000"},
    "las": {"name": "LAS Services", "tin": "789-012-345-000"},
    "rmqb": {"name": "RMQB Corp", "tin": "890-123-456-000"}
}

def seed_organization(agency_code, agency_data):
    """Seed data for one organization"""
    odoo = odoorpc.ODOO('localhost', port=8069)
    odoo.login(f'db_{agency_code}', 'admin', os.getenv('ODOO_ADMIN_PASSWORD'))

    # Create company
    Company = odoo.env['res.company']
    company_id = Company.create({
        'name': agency_data['name'],
        'vat': agency_data['tin'],
        'country_id': odoo.env.ref('base.ph').id,
        'currency_id': odoo.env.ref('base.PHP').id,
    })

    # Create 100 GL transactions
    Journal = odoo.env['account.journal']
    Move = odoo.env['account.move']

    for i in range(100):
        # Create invoice
        invoice = Move.create({
            'move_type': 'out_invoice',
            'partner_id': ...,  # Create sample customers
            'invoice_line_ids': [...]  # Create sample line items
        })
        invoice.action_post()

    print(f"✓ Seeded {agency_code} with 100 transactions")
```

**Acceptance Criteria**:
- [ ] Each org has 100+ GL transactions
- [ ] Sample customers/vendors created
- [ ] Chart of accounts configured
- [ ] BIR-compliant tax codes setup

**Estimated Time**: 6 hours

---

### Week 4: Superset Integration

**Goal**: Add Apache Superset to docker-compose

**Deliverables**:
```yaml
# Addition to docker-compose.yml

services:
  # ... existing services ...

  superset:
    image: apache/superset:3.0.0
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_DIALECT=postgresql
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_DB=superset
      - DATABASE_USER=odoo
      - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - SUPERSET_SECRET_KEY=${SUPERSET_SECRET_KEY}
    ports:
      - "8088:8088"
    volumes:
      - ./superset/config:/app/superset_home
      - ./superset/dashboards:/app/dashboards
    command: >
      bash -c "superset db upgrade &&
               superset fab create-admin --username admin --password ${SUPERSET_ADMIN_PASSWORD} --firstname Admin --lastname User --email admin@insightpulse.ai &&
               superset init &&
               superset run -h 0.0.0.0 -p 8088"
```

**Acceptance Criteria**:
- [ ] Superset accessible at http://localhost:8088
- [ ] Can connect to Odoo PostgreSQL databases
- [ ] Sample dashboard created
- [ ] SSO token passing works

**Estimated Time**: 4 hours

---

## M1 - BIR Compliance Core (Weeks 5-8)

### Week 5-6: BIR 1601-C Form Generator

**Goal**: Generate BIR 1601-C monthly withholding tax form

**Implementation**:
```python
# odoo_addons/ipai_bir_compliance/models/bir_form_1601c.py

from odoo import models, fields, api
from odoo.exceptions import UserError
import xml.etree.ElementTree as ET

class BIRForm1601C(models.Model):
    _name = 'bir.form.1601c'
    _description = 'BIR Form 1601-C - Monthly Withholding Tax'

    name = fields.Char(string='Form Name', compute='_compute_name')
    company_id = fields.Many2one('res.company', required=True)
    period_month = fields.Integer(required=True)
    period_year = fields.Integer(required=True)

    # Tax amounts
    tax_withheld = fields.Monetary(string='Tax Withheld', compute='_compute_totals')
    penalties = fields.Monetary(string='Penalties')
    total_amount = fields.Monetary(string='Total Amount Due', compute='_compute_totals')

    # Validation
    validation_status = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('filed', 'Filed'),
        ('rejected', 'Rejected')
    ], default='draft')

    # Generated files
    pdf_file = fields.Binary(string='PDF Form')
    xml_file = fields.Binary(string='eBIRForms XML')

    @api.depends('period_month', 'period_year')
    def _compute_name(self):
        for record in self:
            record.name = f"1601-C {record.period_year}-{record.period_month:02d}"

    @api.depends('tax_withheld', 'penalties')
    def _compute_totals(self):
        for record in self:
            # Query GL for withholding tax transactions
            domain = [
                ('company_id', '=', record.company_id.id),
                ('date', '>=', f'{record.period_year}-{record.period_month:02d}-01'),
                ('date', '<=', f'{record.period_year}-{record.period_month:02d}-{self._get_month_end(record.period_month)}'),
                ('account_id.code', 'like', '2151%')  # Withholding tax payable accounts
            ]

            moves = self.env['account.move.line'].search(domain)
            record.tax_withheld = sum(moves.mapped('credit')) - sum(moves.mapped('debit'))
            record.total_amount = record.tax_withheld + record.penalties

    def action_generate_pdf(self):
        """Generate BIR-compliant PDF"""
        self.ensure_one()

        # Use Odoo's QWeb reporting engine
        pdf_content = self.env.ref('ipai_bir_compliance.report_bir_1601c').render_qweb_pdf([self.id])[0]

        self.pdf_file = base64.b64encode(pdf_content)
        return True

    def action_generate_xml(self):
        """Generate eBIRForms XML"""
        self.ensure_one()

        # Build XML according to BIR schema v8.0
        root = ET.Element('eBIRForms')
        header = ET.SubElement(root, 'Header')
        ET.SubElement(header, 'FormType').text = '1601C'
        ET.SubElement(header, 'TIN').text = self.company_id.vat
        ET.SubElement(header, 'TaxableYear').text = str(self.period_year)
        ET.SubElement(header, 'TaxableMonth').text = str(self.period_month)

        body = ET.SubElement(root, 'Body')
        ET.SubElement(body, 'TaxWithheld').text = str(self.tax_withheld)
        ET.SubElement(body, 'Penalties').text = str(self.penalties)
        ET.SubElement(body, 'TotalAmountDue').text = str(self.total_amount)

        xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        self.xml_file = base64.b64encode(xml_string)

        # Validate against schema
        self.action_validate()

        return True

    def action_validate(self):
        """Validate form against BIR rules"""
        self.ensure_one()

        errors = []

        # Rule 1: TIN must be valid format
        if not self._validate_tin(self.company_id.vat):
            errors.append("Invalid TIN format")

        # Rule 2: Tax withheld must be positive
        if self.tax_withheld < 0:
            errors.append("Tax withheld cannot be negative")

        # Rule 3: Check XML schema compliance
        if self.xml_file:
            if not self._validate_xml_schema():
                errors.append("XML does not conform to BIR schema")

        if errors:
            self.validation_status = 'rejected'
            raise UserError("\n".join(errors))
        else:
            self.validation_status = 'validated'

        return True

    def _validate_tin(self, tin):
        """Validate TIN format: XXX-XXX-XXX-000"""
        import re
        return bool(re.match(r'^\d{3}-\d{3}-\d{3}-\d{3}$', tin or ''))

    def _validate_xml_schema(self):
        """Validate XML against official BIR XSD schema"""
        # TODO: Implement XSD validation
        # Download BIR schema from official website
        # Use lxml for validation
        return True
```

**Acceptance Criteria**:
- [ ] Generate 1601-C from GL transactions
- [ ] PDF output matches BIR format
- [ ] XML validates against BIR schema v8.0
- [ ] 98% validation pass rate on 100 historical months
- [ ] Unit tests passing

**Estimated Time**: 12 hours

---

### Week 7: BIR Validation Engine + 2550Q

**Goal**: Validation engine and quarterly VAT form

**Implementation**: Similar pattern to 1601-C

**Acceptance Criteria**:
- [ ] 2550Q form generator functional
- [ ] Validation rules from BIR documented
- [ ] Error messages user-friendly

**Estimated Time**: 16 hours (combined)

---

### Week 8: Testing & Documentation

**Goal**: Comprehensive testing

**Deliverables**:
- Unit tests (pytest)
- Integration tests
- Red-team prompts for OCR safety
- User documentation

**Estimated Time**: 8 hours

---

## M2 - Multi-Org + Superset (Weeks 9-12)

### Week 9-10: Multi-Database Architecture

**Goal**: Configure 8 separate databases with consolidation

**Implementation**:
```python
# scripts/multi-org/consolidate-financials.py

def consolidate_financials(org_codes, date_from, date_to):
    """Query multiple databases and consolidate"""

    consolidated = {
        'balance_sheet': {},
        'income_statement': {},
        'cash_flow': {}
    }

    for org in org_codes:
        db_name = f'db_{org}'
        odoo = odoorpc.ODOO('localhost', port=8069)
        odoo.login(db_name, 'admin', os.getenv('ODOO_ADMIN_PASSWORD'))

        # Query trial balance
        TrialBalance = odoo.env['account.trial.balance']
        tb = TrialBalance.create({
            'date_from': date_from,
            'date_to': date_to
        })

        # Merge into consolidated
        for line in tb.line_ids:
            account_code = line.account_id.code
            if account_code not in consolidated['balance_sheet']:
                consolidated['balance_sheet'][account_code] = 0
            consolidated['balance_sheet'][account_code] += line.balance

    return consolidated
```

**Acceptance Criteria**:
- [ ] Query 8 databases in <5 seconds
- [ ] Consolidated P&L accurate
- [ ] Drill-down to entity level works

**Estimated Time**: 10 hours

---

### Week 11-12: Superset Dashboards

**Goal**: 5 pre-built dashboards

**Dashboards**:
1. **Finance SSC Overview** - Cost savings, BIR compliance, hours saved
2. **BIR Compliance Dashboard** - Form submission status, deadlines, penalties
3. **Multi-Org Consolidation** - Consolidated financials with drill-down
4. **Vendor Performance** - On-time delivery, quality scores
5. **Budget Tracking** - Actual vs budget by project

**Implementation**:
```sql
-- SQL view for BIR compliance dashboard
CREATE VIEW superset.bir_compliance_status AS
SELECT
    f.company_id,
    c.name as company_name,
    f.period_year,
    f.period_month,
    f.validation_status,
    f.total_amount,
    f.create_date,
    CASE
        WHEN f.validation_status = 'filed' THEN 'On-time'
        WHEN CURRENT_DATE > (DATE(f.period_year || '-' || f.period_month || '-10')) THEN 'Late'
        ELSE 'Pending'
    END as deadline_status
FROM bir_form_1601c f
JOIN res_company c ON f.company_id = c.id
```

**Acceptance Criteria**:
- [ ] All 5 dashboards functional
- [ ] Data refreshes in real-time
- [ ] Embedded in Odoo via iframe
- [ ] SSO authentication works

**Estimated Time**: 16 hours

---

## Implementation Timeline (Gantt)

```
Week  1 | BIR Module Skeleton ████████
Week  2 | Multi-Org DB Scripts ████████
Week  3 | Seed Data Script     ████████
Week  4 | Superset Integration ████████
      --|----------------------------------
Week  5 | BIR 1601-C Gen (1/2) ████████
Week  6 | BIR 1601-C Gen (2/2) ████████
Week  7 | BIR 2550Q + Valid    ████████
Week  8 | Testing & Docs       ████████
      --|----------------------------------
Week  9 | Multi-DB Arch (1/2)  ████████
Week 10 | Multi-DB Arch (2/2)  ████████
Week 11 | Superset Dash (1/2)  ████████
Week 12 | Superset Dash (2/2)  ████████
```

---

## Testing Strategy

### Unit Tests
- Framework: pytest + Odoo test suite
- Coverage: >80% for custom modules
- Run: On every commit (GitHub Actions)

### Integration Tests
- E2E: Create GL → Generate 1601-C → Validate → Download
- Framework: Selenium + pytest
- Run: Nightly on staging

### Red-Team Prompts (OCR Safety)
- Upload receipt with SQL injection in merchant name
- Upload oversized image (>10MB)
- Upload non-receipt image
- Expected: Graceful error, no data corruption

### Acceptance Testing
- [ ] All 12 user stories from PRD testable
- [ ] BIR forms pass 98% validation on 100 historical months
- [ ] Multi-org consolidation <5s
- [ ] CI/CD deploys to staging <10min

---

## Risk Mitigation

### Top 5 Risks

**1. OCA Module Compatibility**
- Mitigation: Vendor at specific commits, test in staging
- Owner: DevOps Lead
- Status: 🟢 Low Risk (already vendored)

**2. BIR Schema Changes**
- Mitigation: Monthly monitoring, regression tests
- Owner: Finance Director
- Status: 🟡 Medium Risk

**3. DigitalOcean Downtime**
- Mitigation: Daily backups to S3, read-only fallback
- Owner: DevOps Lead
- Status: 🟢 Low Risk

**4. OCR Budget Overrun**
- Mitigation: Self-hosted PaddleOCR, batch processing
- Owner: AI Lead
- Status: 🟢 Low Risk

**5. Custom Module Tech Debt**
- Mitigation: 100% test coverage, quarterly cleanup
- Owner: Backend Dev
- Status: 🟡 Medium Risk

---

## Success Criteria (MVP Completion)

### M0 Success
- [ ] Docker compose up → Odoo + PostgreSQL + Superset running
- [ ] 8 org databases created
- [ ] Demo data loaded
- [ ] BIR module installable

### M1 Success
- [ ] Generate 1601-C from GL transactions
- [ ] PDF + XML output BIR-compliant
- [ ] 98% validation pass rate
- [ ] Unit tests passing

### M2 Success
- [ ] Multi-org consolidation <5s
- [ ] 5 Superset dashboards functional
- [ ] Embedded dashboards in Odoo
- [ ] Production deployment successful

---

## Next Actions (This Week)

**Priority 1 - Critical Path**
1. ✅ Create this roadmap document
2. ⏳ Create BIR compliance module skeleton (8h)
3. ⏳ Create multi-org database scripts (4h)
4. ⏳ Update docker-compose.yml for Superset (4h)

**Priority 2 - Foundation**
5. ⏳ Create seed data script (6h)
6. ⏳ Write unit test framework (2h)
7. ⏳ Update README with PRD alignment (1h)

**Total Estimated Effort**: 25 hours (Week 1)

---

## References

- **PRD Location**: Root directory (provided by user)
- **GitHub Repo**: https://github.com/jgtolentino/insightpulse-odoo
- **Current Branch**: `claude/insightpulse-odoo-prd-setup-011CV1Y2YZrhQsyRy53V62y3`
- **Deployment Docs**: `/scripts/deploy/README.md`
- **Architecture Docs**: `/ARCHITECTURE.md`

---

**Prepared By**: Claude (AI Assistant)
**Reviewed By**: Pending
**Status**: 🟢 Ready for Implementation
**Last Updated**: 2025-11-11
