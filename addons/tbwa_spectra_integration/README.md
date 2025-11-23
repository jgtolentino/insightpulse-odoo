# TBWA Spectra Integration Module

**Version**: 1.0.0
**Environment**: TBWA-PROD
**Odoo**: CE 18.0
**Author**: InsightPulse AI

Complete integration system for TBWA Finance Operations with Spectra GL, Okta SSO, and automated expense/cash advance workflows.

---

## 🎯 Features

### Core Capabilities
- ✅ **Spectra GL Export Automation** - Automated CSV/Excel export in Spectra-compliant format
- ✅ **Okta SSO Integration** - Centralized authentication with MFA enforcement
- ✅ **Cash Advance Workflow** - Dual approval with automatic liquidation tracking
- ✅ **Expense Liquidation** - Policy-validated expense reports with receipt management
- ✅ **n8n Automation** - Scheduled exports, approval reminders, compliance triggers
- ✅ **Audit Trail System** - Tamper-proof approval history for compliance
- ✅ **Role-Based Approval Matrix** - Configurable approval rules based on amount thresholds

### Spectra Mapping
| Finance Object | Odoo Source | Spectra Target |
|----------------|-------------|----------------|
| Cash Advance | hr.expense.advance | CASH_ADV_HO |
| Liquidation | hr.expense.sheet | EXPENSE_ENTRY |
| Vendor Payments | account.payment | AP_LEDGER |
| Journal Entries | account.move | GL_TRANSACTIONS |
| Approval Trail | Odoo chatter | AUDIT_LOG |

### Export Templates
- `TBWA_EXPENSES_MMYY.csv` - Monthly expense report export
- `TBWA_CA_MMYY.csv` - Cash advance register export
- `TBWA_JE_MMYY.csv` - Journal entry export
- `TBWA_AUDIT_MMYY.csv` - Approval audit trail export

---

## 📐 Architecture

### Systems Stack
```
┌─────────────────────────────────────────────────────────────┐
│                        Okta SSO                             │
│              (Identity Provider + MFA)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    Odoo CE 18.0                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ HR Expense  │  │ Cash Advance │  │ Spectra Mapping  │  │
│  │   Module    │  │    Module    │  │     Engine       │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                        n8n                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Monthly Export │  │   Approval   │  │ Liquidation  │   │
│  │   Automation   │  │   Reminders  │  │   Tracking   │   │
│  └────────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  Supabase Storage                           │
│        (Export Archive + Attachment Storage)                │
└─────────────────────────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    Spectra GL                               │
│              (Target Finance System)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites
```bash
# Required OCA modules
- auth_oauth
- base_export_manager

# Python dependencies
pip install okta pandas pytz
```

### Installation Steps

1. **Install Module**
```bash
# Navigate to Odoo addons
cd /opt/odoo-ce/addons

# Pull latest from Git
git pull origin feature/tbwa-spectra-integration

# Restart Odoo
systemctl restart odoo

# Check Odoo is running
systemctl status odoo
```

2. **Install via UI**
```
1. Open browser: https://erp.insightpulseai.net
2. Login as admin
3. Apps → Update Apps List
4. Search: "TBWA Spectra Integration"
5. Click Install
```

3. **Configure Okta SSO**
```
Settings → General Settings → OAuth Providers
→ Edit "Okta TBWA"
→ Set Client ID and Client Secret from Okta App
→ Save
```

4. **Verify Installation**
```
Navigate to: TBWA Finance (new menu in top menu bar)

You should see:
- Cash Advances
- Expense Reports
- Spectra Exports
- Approval Matrix
- Mapping Configuration
```

---

## ⚙️ Configuration

### 1. Okta SSO Setup

**Create Okta App**:
- Type: OIDC / OAuth 2.0
- Grant Type: Authorization Code + Refresh Token
- Redirect URI: `https://erp.insightpulseai.net/auth_oauth/signin`

**Security Policies**:
| Policy | Setting |
|--------|---------|
| MFA | Required (SMS / App / Okta Verify) |
| Session Timeout | 8 hours with forced re-auth every 24h |
| Device Trust | Only registered device + browser fingerprinting |
| Role Sync | Groups → Odoo User Roles |

**Odoo Mapping**:
| Okta Attribute | Odoo Field |
|----------------|------------|
| email | login |
| given_name | first_name |
| family_name | last_name |
| group.name | role/permission template |

### 2. Approval Matrix Configuration

**Default Rules** (Pre-configured):
```
Cash Advance - Standard (₱0 - ₱50,000):
  L1: Immediate Manager
  L2: Finance Head

Cash Advance - High Value (₱50,000+):
  L1: Finance Head
  L2: CFO
```

**Customization**:
```
TBWA Finance → Approval Matrix → Create

Fields:
- Amount Range (Min/Max)
- Level 1 Approver (Manager/Dept Head/Finance Head)
- Level 2 Approver (Dept Head/Finance Head/CFO/CEO)
- SLA Hours (L1: 24h, L2: 48h)
```

### 3. Spectra GL Mapping

**Pre-configured Expense Categories**:
```xml
Travel → GL 6210-001 (VAT 12%)
Meals & Entertainment → GL 6220-002 (VAT 12%)
Office Supplies → GL 6230-003 (VAT 12%)
Professional Services → GL 6240-004 (VAT 12%, W/H 2%)
```

**Add Custom Mappings**:
```
TBWA Finance → Spectra Mapping → Create

Fields:
- Mapping Type (GL Account / Cost Center / Employee / Category)
- Odoo Source Field
- Spectra Target Field
- Format (Text / Number / Date / Currency)
- Validation Rules
```

---

## 💼 User Workflows

### Cash Advance Workflow

**Employee**:
```
1. Navigate to: TBWA Finance → Cash Advances → Create
2. Fill in:
   - Amount (auto-calculates approvers based on matrix)
   - Purpose (detailed description required)
   - Project/Cost Center (optional)
3. Click "Submit for Approval"
4. Wait for approval notifications
5. After payment: Submit liquidation within 15 days
```

**Manager (Level 1)**:
```
1. Receive notification: "Cash Advance Approval Required"
2. Open cash advance from activity dashboard
3. Review amount and purpose
4. Click "Approve (L1)" or "Reject"
```

**Finance (Level 2)**:
```
1. Receive notification after L1 approval
2. Review cash advance details
3. Click "Approve (L2)" or "Reject"
4. After approval: Process payment
5. Click "Mark as Paid" and enter payment details
```

### Expense Liquidation Workflow

**Employee**:
```
1. From paid cash advance: Click "Create Liquidation"
2. OR: Navigate to TBWA Finance → Expense Reports → Create
3. Add expense lines:
   - Date, Category, Amount
   - Attach receipts (required for most categories)
   - Select Project/Cost Center
4. Link to cash advance (if applicable)
5. Submit for approval
```

**Approval Flow**:
```
Employee Submit → Manager Review → Finance Approval → Accounting Post
                        ↓ Reject
                  Returns to Employee
```

### Monthly Spectra Export Workflow

**Automatic (Cron)**:
```
Trigger: 1st business day of month at 06:30 AM
Process:
1. Query all approved, non-exported expense sheets from last month
2. Apply Spectra mapping transformations
3. Generate CSV files (Expenses, Cash Advances, Audit Trail)
4. Store in Supabase archive
5. Send notification to Finance team
```

**Manual Export**:
```
1. Navigate to: TBWA Finance → Spectra Exports → Create
2. Select:
   - Export Type (Expense / Cash Advance / Journal Entry)
   - Month and Year
   - Records to include
3. Click "Validate Export"
4. Review validation errors (if any)
5. Click "Generate Export Files"
6. Download CSV files
7. Finance approves export
8. Records marked as "Exported to Spectra"
```

---

## 📊 Data Model

### Cash Advance (`hr.expense.advance`)
```python
Fields:
- name: Reference (CA/202511/001)
- employee_id: Employee requesting advance
- amount: Cash advance amount
- description: Purpose
- analytic_account_id: Project/Cost Center
- state: draft → submitted → approved_l1 → approved_l2 → paid → liquidating → done
- approver_l1_id: Level 1 approver (auto-computed)
- approver_l2_id: Level 2 approver (auto-computed)
- liquidation_deadline: Payment date + 15 days
- expense_sheet_id: Linked liquidation report
- exported_to_spectra: Export tracking flag
```

### Spectra Export (`tbwa.spectra.export`)
```python
Fields:
- name: Export reference (SPECTRA_EXP_20251130_063000)
- export_month: Month (01-12)
- export_year: Year (2025)
- export_type: expense / cash_advance / journal_entry / audit_trail
- state: draft → validating → ready → exported → approved
- expense_sheet_ids: M2M to expense reports
- cash_advance_ids: M2M to cash advances
- record_count: Total records (computed)
- total_amount: Total amount (computed)
- export_file_expense: Binary CSV file
- export_file_je: Binary CSV file
- export_file_audit: Binary CSV file
- approved_by_finance: Finance approval flag
- validation_errors: Error messages (if any)
```

### Spectra Mapping (`tbwa.spectra.mapping`)
```python
Fields:
- name: Mapping name
- mapping_type: gl_account / cost_center / employee / category / vendor / tax
- odoo_field: Source field (e.g., account_id.code)
- odoo_value: Specific value to match
- spectra_field: Target column name
- spectra_value: Transformed value
- spectra_format: text / number / date / datetime / currency
- is_required: Required field flag
- validation_rule: Python expression for validation
```

---

## 🔧 n8n Automation Workflows

### 1. Monthly Export Automation

**Workflow**: `spectra_monthly_export_automation.json`

```json
{
  "name": "TBWA Spectra Monthly Export",
  "nodes": [
    {
      "name": "Monthly Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "30 6 1 * *"}]
        }
      }
    },
    {
      "name": "Call Odoo Export Cron",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://erp.insightpulseai.net/jsonrpc",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "bodyParameters": {
          "jsonrpc": "2.0",
          "method": "call",
          "params": {
            "service": "object",
            "method": "execute",
            "args": ["tbwa.spectra.export", "cron_auto_export", []]
          }
        }
      }
    },
    {
      "name": "Get Export Batch",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "return [$input.item.json.result];"
      }
    },
    {
      "name": "Notify Finance Team",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "{{$env.MATTERMOST_WEBHOOK_URL}}",
        "bodyParameters": {
          "channel": "#finance",
          "username": "Spectra Bot",
          "text": "📊 **Monthly Spectra Export Ready**\\n\\nExport Batch: {{$json.name}}\\nRecords: {{$json.record_count}}\\nTotal: ₱{{$json.total_amount}}\\n\\nPlease review and approve: https://erp.insightpulseai.net/web#model=tbwa.spectra.export&id={{$json.id}}"
        }
      }
    }
  ],
  "connections": {
    "Monthly Trigger": {"main": [[{"node": "Call Odoo Export Cron"}]]},
    "Call Odoo Export Cron": {"main": [[{"node": "Get Export Batch"}]]},
    "Get Export Batch": {"main": [[{"node": "Notify Finance Team"}]]}
  }
}
```

### 2. Liquidation Reminder Workflow

**Workflow**: `cash_advance_liquidation_reminders.json`

```json
{
  "name": "Cash Advance Liquidation Reminders",
  "nodes": [
    {
      "name": "Daily 9 AM Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
        }
      }
    },
    {
      "name": "Call Odoo Liquidation Cron",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://erp.insightpulseai.net/jsonrpc",
        "bodyParameters": {
          "params": {
            "args": ["hr.expense.advance", "cron_send_liquidation_reminders", []]
          }
        }
      }
    }
  ]
}
```

### 3. Approval SLA Monitoring

**Workflow**: `approval_sla_monitor.json`

```json
{
  "name": "Approval SLA Monitor",
  "nodes": [
    {
      "name": "Hourly Check",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {"interval": [{"field": "hours", "hours": 1}]}
      }
    },
    {
      "name": "Query Overdue Approvals",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://erp.insightpulseai.net/jsonrpc",
        "bodyParameters": {
          "params": {
            "domain": [
              ["state", "in", ["submitted", "approved_l1"]],
              ["create_date", "<", "{{ $now.minus({hours: 24}) }}"]
            ]
          }
        }
      }
    },
    {
      "name": "Escalate to Managers",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "subject": "⚠️ Overdue Cash Advance Approvals",
        "text": "The following cash advances have exceeded SLA..."
      }
    }
  ]
}
```

---

## 🔐 Security & Compliance

### Okta SSO Security
- ✅ Multi-Factor Authentication (MFA) required
- ✅ Session timeout: 8 hours
- ✅ Forced re-auth: Every 24 hours
- ✅ Device trust validation
- ✅ Browser fingerprinting

### Approval Controls
- ✅ Dual approval enforcement (L1 + L2)
- ✅ Role-based approval matrix
- ✅ SLA monitoring and escalation
- ✅ Approval history in chatter
- ✅ Tamper-proof audit trail

### Compliance Features
- ✅ Receipt requirement validation
- ✅ GL code mapping enforcement
- ✅ VAT calculation and validation
- ✅ Withholding tax computation
- ✅ Cost center/project code tracking
- ✅ Export approval workflow
- ✅ Supabase archive for 7 years retention

---

## 📈 Reports & Analytics

### Available Reports
1. **Cash Advance Register** - All cash advances by status, employee, period
2. **Liquidation Status Report** - Pending liquidations with deadlines
3. **Expense Analysis by Category** - Monthly expense breakdown
4. **Approval Performance** - SLA compliance metrics
5. **Spectra Export History** - All export batches with validation errors

### Export Formats
- PDF (Printable reports)
- Excel (Data analysis)
- CSV (Spectra import)

---

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Okta SSO not redirecting properly
```
Solution:
1. Verify redirect URI in Okta App matches Odoo URL
2. Check OAuth provider settings in Odoo
3. Ensure HTTPS is enforced
4. Clear browser cache and cookies
```

**Issue**: Spectra export validation errors
```
Solution:
1. Check validation errors in export batch
2. Verify GL code mappings exist for all categories
3. Ensure all employees have employee codes
4. Validate cost center codes in analytic accounts
```

**Issue**: Cash advance approvers not assigned
```
Solution:
1. Check approval matrix configuration
2. Verify amount thresholds are correct
3. Ensure employee hierarchy is set (parent_id)
4. Check user roles for approvers
```

**Issue**: n8n workflow not triggering
```
Solution:
1. Verify n8n workflow is active
2. Check cron expression syntax
3. Test manual execution
4. Check n8n logs for errors
5. Verify API credentials
```

---

## 🔄 Maintenance

### Regular Tasks

**Daily**:
- Monitor approval SLA compliance
- Check liquidation reminders sent
- Review failed export validations

**Weekly**:
- Audit approval matrix effectiveness
- Review GL mapping accuracy
- Check Supabase storage usage

**Monthly**:
- Verify Spectra export completion
- Finance approval of export batches
- Archive old export files
- Review compliance metrics

### Cron Schedule

| Cron Job | Schedule | Purpose |
|----------|----------|---------|
| Spectra Monthly Export | 1st day of month, 06:30 AM | Auto-generate export batch |
| Liquidation Reminders | Daily, 9:00 AM | Send liquidation due reminders |
| Approval SLA Monitor | Hourly | Check and escalate overdue approvals |

---

## 📚 Resources

**Documentation**:
- [Odoo CE HR Expense Module](https://github.com/odoo/odoo/tree/18.0/addons/hr_expense) - Official CE source
- [Okta OAuth 2.0](https://developer.okta.com/docs/guides/implement-grant-type/authcode/main/)
- [n8n Workflows](https://docs.n8n.io/)
- [Spectra GL Documentation](https://internal-spectra-docs)

**Support**:
- Email: jgtolentino_rn@yahoo.com
- Internal Wiki: https://tbwa.atlassian.net/wiki/finance
- GitHub Issues: https://github.com/jgtolentino/odoo-ce/issues

---

**Last Updated**: 23 Nov 2025
**Module Version**: 1.0.0
**Environment**: TBWA-PROD
**Tested On**: Odoo CE 18.0
