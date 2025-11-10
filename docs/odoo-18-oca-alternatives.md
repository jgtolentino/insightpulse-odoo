# Odoo 18.0 CE + OCA Alternatives Guide

**Last Updated**: 2025-11-10
**Odoo Version**: 18.0 CE (Production)
**Status**: ✅ Active Implementation

---

## Overview

This guide provides **practical, production-ready** OCA module alternatives for Odoo 18.0 Enterprise features, specifically for the InsightPulse AI Finance SSC implementation.

**Related Documentation**:
- Forward-looking guide: [`odoo-19-ce-vs-enterprise.md`](./odoo-19-ce-vs-enterprise.md)
- Module installation: [`scripts/admin/oca_module_manager.py`](../scripts/admin/oca_module_manager.py)

---

## 1. Current Stack (Production)

```yaml
deployment:
  environment: production
  url: https://erp.insightpulseai.net
  version: Odoo 18.0 CE
  database: insightpulse
  agencies: [RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB]

infrastructure:
  platform: DigitalOcean droplets + App Platform
  database: PostgreSQL 15 + Supabase (spdtwktxdalcfigzeqrz)
  analytics: Apache Superset 3.0
  ocr: PaddleOCR-VL + OpenAI gpt-4o-mini
```

---

## 2. Enterprise → OCA Mapping (18.0)

### 2.1 Accounting & Reporting

| Enterprise Module | OCA Alternative | Branch | Parity | Notes |
|-------------------|----------------|--------|--------|-------|
| `account_reports` | `account_financial_report` + `mis_builder` | 18.0 | 95% | Full financial reporting |
| `account_budget` | `mis_builder` | 18.0 | 90% | Budget vs actual |
| `account_consolidation` | `mis_builder` | 18.0 | 85% | Multi-company consolidation |
| `account_invoice_extract` | PaddleOCR-VL integration | N/A | 100% | Custom OCR implementation |

**Installation**:
```bash
# Financial reporting stack
python3 scripts/admin/oca_module_manager.py insightpulse install

# Or manual installation
odoo-bin -d insightpulse -i account_financial_report,mis_builder,report_xlsx --stop-after-init
```

**OCA Repositories**:
- [account-financial-reporting](https://github.com/OCA/account-financial-reporting)
- [mis-builder](https://github.com/OCA/mis-builder)

### 2.2 Document Management

| Enterprise Module | OCA Alternative | Branch | Parity | Notes |
|-------------------|----------------|--------|--------|-------|
| `documents` | `dms` + `dms_field` | 18.0 | 85% | Full DMS with folder hierarchy |
| `documents_spreadsheet` | Apache Superset | N/A | 90% | External BI tool |
| `sign` | `agreement` | 18.0 | 70% | Contract management |

**Installation**:
```bash
# Document management stack
odoo-bin -d insightpulse -i dms,dms_field,attachment_preview --stop-after-init
```

**OCA Repositories**:
- [dms](https://github.com/OCA/dms)

### 2.3 Helpdesk & Support

| Enterprise Module | OCA Alternative | Branch | Parity | Notes |
|-------------------|----------------|--------|--------|-------|
| `helpdesk` | `helpdesk_mgmt` | 18.0 | 80% | Complete ticketing system |
| `helpdesk_timesheet` | `helpdesk_mgmt_timesheet` | 18.0 | 85% | Time tracking integration |

**Installation**:
```bash
# Helpdesk stack
odoo-bin -d insightpulse -i helpdesk_mgmt,helpdesk_mgmt_timesheet --stop-after-init
```

**OCA Repositories**:
- [helpdesk](https://github.com/OCA/helpdesk)

### 2.4 Approvals & Workflows

| Enterprise Module | OCA Alternative | Branch | Parity | Notes |
|-------------------|----------------|--------|--------|-------|
| `approvals` | `base_tier_validation` | 18.0 | 90% | Multi-tier approval system |
| `quality_control` | `quality_control` | 18.0 | 80% | QC and inspection |
| `planning` | `resource_booking` | 18.0 | 70% | Resource scheduling |

**Installation**:
```bash
# Approval workflow stack
odoo-bin -d insightpulse -i base_tier_validation,base_automation --stop-after-init
```

**OCA Repositories**:
- [server-tools](https://github.com/OCA/server-tools)
- [manufacture](https://github.com/OCA/manufacture)
- [calendar](https://github.com/OCA/calendar)

### 2.5 HR & Payroll

| Enterprise Module | OCA Alternative | Branch | Parity | Notes |
|-------------------|----------------|--------|--------|-------|
| `hr_payroll` | `hr_payroll_account` | 18.0 | 90% | Payroll accounting |
| `hr_expense_extract` | PaddleOCR-VL integration | N/A | 100% | Custom OCR for expenses |
| `hr_attendance` | `hr_attendance_overtime` | 18.0 | 85% | Overtime calculation |

**Installation**:
```bash
# HR & Payroll stack
odoo-bin -d insightpulse -i hr_payroll_account,hr_attendance_overtime --stop-after-init
```

**OCA Repositories**:
- [payroll](https://github.com/OCA/payroll)
- [hr-attendance](https://github.com/OCA/hr-attendance)

### 2.6 Procurement

| Enterprise Module | OCA Alternative | Branch | Parity | Notes |
|-------------------|----------------|--------|--------|-------|
| `purchase_requisition` | `purchase_request` | 18.0 | 85% | Purchase requests |
| `purchase_approval` | `purchase_order_approval` | 18.0 | 90% | Multi-tier approval |

**Installation**:
```bash
# Procurement stack
odoo-bin -d insightpulse -i purchase_order_approval,purchase_request --stop-after-init
```

**OCA Repositories**:
- [purchase-workflow](https://github.com/OCA/purchase-workflow)

---

## 3. InsightPulse Finance SSC Stack

### 3.1 Complete Module List

```python
# From scripts/admin/oca_module_manager.py
FINANCE_SSC_STACK = [
    # Core Accounting (CE)
    'account',
    'account_accountant',

    # OCA Accounting
    'account_financial_report',
    'mis_builder',
    'report_xlsx',

    # HR & Payroll
    'hr',
    'hr_expense',
    'hr_payroll_account',

    # Procurement
    'purchase',
    'purchase_order_approval',

    # Document Management
    'dms',
    'dms_field',

    # Approvals
    'base_tier_validation',

    # Custom Modules
    'insightpulse_travel_expense',
    'insightpulse_bir_compliance',
    'insightpulse_ppm',
]
```

### 3.2 Installation Sequence

**Step 1: Core CE Modules**
```bash
odoo-bin -d insightpulse -i account,account_accountant,hr,purchase --stop-after-init
```

**Step 2: OCA Accounting**
```bash
odoo-bin -d insightpulse -i account_financial_report,mis_builder,report_xlsx --stop-after-init
```

**Step 3: OCA Workflows**
```bash
odoo-bin -d insightpulse -i base_tier_validation,purchase_order_approval --stop-after-init
```

**Step 4: OCA Document Management**
```bash
odoo-bin -d insightpulse -i dms,dms_field --stop-after-init
```

**Step 5: Custom Modules**
```bash
odoo-bin -d insightpulse -i insightpulse_travel_expense,insightpulse_bir_compliance,insightpulse_ppm --stop-after-init
```

### 3.3 Automated Installation

```bash
# Complete Finance SSC stack installation
python3 scripts/admin/oca_module_manager.py insightpulse install
```

---

## 4. Financial Impact Analysis

### 4.1 Annual Cost Savings

| Component | Enterprise 18 | CE 18 + OCA | Annual Savings |
|-----------|---------------|-------------|----------------|
| Odoo Enterprise License (10 users) | $4,728 | $0 | $4,728 |
| Advanced Accounting | Included | $0 (OCA) | $0 |
| Document Management | Included | $0 (OCA) | $0 |
| Helpdesk | Included | $0 (OCA) | $0 |
| **Total** | **$4,728/year** | **$0/year** | **$4,728/year** |

### 4.2 Alternative Tool Savings

| SaaS Tool | Replacement | Annual Savings |
|-----------|-------------|----------------|
| SAP Concur | Odoo CE Expense + OCA | $15,000 |
| SAP Ariba | Odoo CE Purchase + OCA | $12,000 |
| Tableau | Apache Superset 3.0 | $8,400 |
| Slack Enterprise | Mattermost/Rocket.Chat | $12,600 |
| **Total SaaS Savings** | | **$48,000** |

**Combined Annual Savings**: $4,728 (Odoo) + $48,000 (SaaS) = **$52,728/year**

---

## 5. OCA Module Status Dashboard

### 5.1 Check Branch Availability

```bash
# Check all OCA repos for 18.0/19.0 branch status
python3 scripts/admin/oca_module_manager.py insightpulse status
```

**Sample Output**:
```json
{
  "repositories": [
    {
      "repo": "account-financial-reporting",
      "description": "Financial reporting and MIS Builder",
      "branch_18_available": true,
      "branch_18_last_commit": "2025-10-15T14:23:45Z",
      "branch_19_available": false,
      "branch_19_expected": "2026-03",
      "priority": 1,
      "modules": ["account_financial_report", "mis_builder", "report_xlsx"]
    }
  ],
  "summary": {
    "total_repos": 10,
    "branch_18_available": 10,
    "branch_19_available": 0,
    "odoo_version": "18.0"
  }
}
```

### 5.2 CI/CD Integration

**GitHub Actions Workflow**: `.github/workflows/oca-intel-sync.yml`

**Monitoring**:
- Daily OCA branch status checks (2 AM UTC)
- Automated issue creation for new 19.0 branches
- Documentation auto-updates

---

## 6. MCP Server Integration

### 6.1 OCA Intelligence MCP

**Location**: `mcp/oca-intel/`

**Features**:
- 8 tools: search, docs, branches, alternatives, install, dependencies, compatibility, deepwiki
- 7 resources: repositories, catalog, guides, compatibility
- 5 prompts: discovery, installation, migration

**Usage with Claude Code**:
```typescript
// Search for OCA modules
await server.callTool('search_oca_modules', {
  query: 'financial reporting',
  version: '18.0',
  limit: 10
});

// Get Enterprise alternatives
await server.callTool('find_enterprise_alternatives', {
  enterprise_module: 'account_reports',
  odoo_version: '18.0'
});
```

### 6.2 VSCode/Cursor Integration

**Configuration**: `.cursor/settings.json`

```json
{
  "mcpServers": {
    "oca-intel": {
      "command": "node",
      "args": ["${workspaceFolder}/mcp/oca-intel/dist/index.js"]
    }
  }
}
```

---

## 7. Testing & Validation

### 7.1 Module Installation Tests

```bash
# Run module installation tests
pytest odoo/tests/test_oca_installation.py -v
```

### 7.2 OCA Compatibility Tests

```bash
# Test OCA module compatibility
python3 scripts/admin/oca_module_manager.py insightpulse status | jq '.summary'
```

### 7.3 Visual Parity Tests

```bash
# Capture baseline screenshots
node scripts/snap.js --routes="/expenses,/accounting,/purchase" --base-url="https://erp.insightpulseai.net"

# Compare against Odoo 18.0 CE baseline
node scripts/ssim.js --routes="/expenses,/accounting,/purchase" --odoo-version="18.0"
```

---

## 8. Migration Path (Future: 18.0 → 19.0)

### 8.1 Prerequisites

**OpenUpgrade Availability**: ⏳ Expected Q1 2026
**OCA 19.0 Branches**: ⏳ Expected Q1-Q2 2026

### 8.2 Strategic Recommendation

```yaml
recommended_action:
  immediate: ⚠️ DO NOT upgrade to 19.0
  timing: Wait until Q2 2026

reasons:
  - OCA 19.0 branches unavailable (expected Q1 2026)
  - OpenUpgrade 19.0 not ready
  - Odoo 19.0 release: September 2025
  - Stabilization period: 6 months
  - OCA migration: Q1 2026
  - Production-ready: Q2 2026

current_action:
  continue: Odoo 18.0 CE + OCA
  monitor: OCA branch status via CI/CD
  prepare: Update custom modules for 19.0 compatibility
```

---

## 9. Resources

### 9.1 OCA Documentation
- [OCA Homepage](https://odoo-community.org/)
- [OCA GitHub Organization](https://github.com/OCA)
- [OCA Development Guidelines](https://odoo-community.org/how-to-guides)

### 9.2 InsightPulse Documentation
- [Odoo 19.0 Forward-Looking Guide](./odoo-19-ce-vs-enterprise.md)
- [MCP Server README](../mcp/oca-intel/README.md)
- [CI/CD Workflow](../.github/workflows/oca-intel-sync.yml)

### 9.3 External Tools
- [gitsearchai.com](https://gitsearchai.com) - Advanced GitHub search
- [gittodoc.com](https://gittodoc.com) - Automated documentation
- [DeepWiki](https://deepwiki.com) - Interactive documentation

---

## 10. Troubleshooting

### 10.1 Module Not Found

**Symptom**: Module shows as "uninstallable" or not found

**Solution**:
```bash
# Update module list
odoo-bin -d insightpulse --update-list --stop-after-init

# Check OCA branch status
python3 scripts/admin/oca_module_manager.py insightpulse status | jq '.repositories[] | select(.repo == "account-financial-reporting")'
```

### 10.2 Enterprise Dependency Conflict

**Symptom**: Module requires Enterprise-only dependencies

**Solution**:
```bash
# Find OCA alternative
python3 -c "
from scripts.admin.oca_module_manager import OCAModuleManager
manager = OCAModuleManager('insightpulse')
# Check ENTERPRISE_TO_OCA_MAP in alternatives.ts
"
```

### 10.3 Branch Not Available

**Symptom**: OCA repo doesn't have 18.0 branch

**Solution**:
```bash
# Check branch status via GitHub API
curl -s https://api.github.com/repos/OCA/[repo-name]/branches/18.0 | jq '.name'

# Monitor CI/CD for updates
gh run list --workflow=oca-intel-sync.yml
```

---

**Maintained by**: InsightPulse AI Team
**Contact**: jgtolentino_rn@yahoo.com
**Repository**: [jgtolentino/insightpulse-odoo](https://github.com/jgtolentino/insightpulse-odoo)
**Version**: odoo-18-oca@2025-11-10
