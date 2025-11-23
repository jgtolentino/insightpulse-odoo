# Canonical Tag + Label Vocabulary
## Finance Operations Taxonomy (TBWA)

**Version**: 1.0.0
**Last Updated**: 23 Nov 2025
**Scope**: Odoo, GitHub, Clarity PPM, n8n, Supabase

---

## 🎯 Purpose

Unified semantic markers across all finance systems to enable:
- ✅ End-to-end traceability (Odoo expense → GitHub issue → Clarity project → n8n workflow)
- ✅ Cross-platform filtering and dashboards
- ✅ Automated workflow routing
- ✅ Compliance audit trails
- ✅ SLA monitoring and escalation

---

## 📋 Taxonomy Structure

### Tag Hierarchy
```
{domain}/{category}/{identifier}

Examples:
- finance/closing/2025-11
- compliance/bir/1601-c
- integration/concur/expense-sync
- integration/cheqroom/asset-tracking
- operations/monthly-close/rim
```

### Label Categories
```
1. Workflow State Labels (controlled, workflow-specific)
2. Priority Labels (severity, urgency)
3. Ownership Labels (team, role)
4. Compliance Labels (regulatory, audit)
5. Integration Labels (system, status)
```

---

## 🏷️ TAGS: Semantic Markers

### 1. Finance Domain Tags

#### Monthly Closing
```yaml
closing-2025-11:          # November 2025 close cycle
closing-2025-12:          # December 2025 close cycle
closing-q4-2025:          # Q4 2025 quarterly close
closing-fy-2025:          # FY 2025 year-end close

month-end:                # General month-end activities
quarter-end:              # Quarterly close activities
year-end:                 # Annual close activities
```

**Usage**:
- Odoo: `hr.expense.sheet.tag_ids`, `ppm.monthly.close.tag_ids`
- GitHub: Issue/PR labels
- n8n: Workflow tags
- Clarity PPM: Project tags

#### Expense Categories
```yaml
expense/travel:           # Travel expenses
expense/meals:            # Meals & entertainment
expense/supplies:         # Office supplies
expense/utilities:        # Utilities
expense/professional:     # Professional services
expense/equipment:        # Equipment purchases
expense/software:         # Software subscriptions
expense/other:            # Miscellaneous
```

#### Cash Advance
```yaml
cash-advance/standard:    # Standard CA (≤₱50K)
cash-advance/high-value:  # High-value CA (>₱50K)
cash-advance/overdue:     # Overdue liquidation
cash-advance/emergency:   # Emergency CA
```

#### Payroll
```yaml
payroll/regular:          # Regular payroll
payroll/final-pay:        # Final pay separation
payroll/sl-conversion:    # Sick leave conversion
payroll/13th-month:       # 13th month pay
payroll/bonus:            # Performance bonus
```

#### Tax & Compliance
```yaml
bir/1601-c:              # Monthly withholding tax
bir/1702-rt:             # Annual income tax
bir/2550q:               # Quarterly VAT
bir/alphalist:           # Annual alphalist
vat/input:               # Input VAT
vat/output:              # Output VAT
compliance/audit:         # Compliance audit
compliance/external:      # External audit
```

---

### 2. Agency Tags

```yaml
agency/rim:              # RIM agency
agency/ckvc:             # CKVC agency
agency/bom:              # BOM agency
agency/jpal:             # JPAL agency
agency/jli:              # JLI agency
agency/jap:              # JAP agency
agency/las:              # LAS agency
agency/rmqb:             # RMQB agency
agency/multi:            # Multi-agency transaction
agency/consolidated:     # Consolidated reporting
```

---

### 3. Integration Tags

#### Concur Parity
```yaml
concur-parity/expense:        # Concur expense feature parity
concur-parity/approval:       # Concur approval workflow
concur-parity/receipt:        # Concur receipt OCR
concur-parity/policy:         # Concur policy validation
concur-parity/reporting:      # Concur reporting
concur-parity/mobile:         # Concur mobile app
```

#### Cheqroom Parity
```yaml
cheqroom-parity/asset:        # Cheqroom asset tracking
cheqroom-parity/checkout:     # Cheqroom check-in/out
cheqroom-parity/reservation:  # Cheqroom reservation
cheqroom-parity/maintenance:  # Cheqroom maintenance
cheqroom-parity/qr:          # Cheqroom QR codes
```

#### Spectra Integration
```yaml
spectra/export:          # Spectra export batch
spectra/mapping:         # GL code mapping
spectra/validation:      # Export validation
spectra/archive:         # Export archive
```

#### Supabase
```yaml
supabase/storage:        # Supabase file storage
supabase/rls:            # Row-level security
supabase/rpc:            # RPC functions
supabase/edge:           # Edge Functions
```

---

### 4. Project Tags

#### Development
```yaml
dev/feature:             # New feature development
dev/bugfix:              # Bug fix
dev/enhancement:         # Enhancement to existing feature
dev/refactor:            # Code refactoring
dev/performance:         # Performance optimization
dev/security:            # Security fix
```

#### Operations
```yaml
ops/deployment:          # Deployment activity
ops/migration:           # Data migration
ops/backup:              # Backup operations
ops/monitoring:          # System monitoring
ops/incident:            # Incident response
```

#### Documentation
```yaml
docs/user-guide:         # User documentation
docs/technical:          # Technical documentation
docs/sop:                # Standard operating procedure
docs/api:                # API documentation
```

---

### 5. Temporal Tags

```yaml
# Year-Month format
2025-11:                 # November 2025
2025-12:                 # December 2025
2025-q4:                 # Q4 2025
2025-fy:                 # FY 2025

# Week format
2025-w47:                # Week 47 of 2025
2025-w48:                # Week 48 of 2025
```

---

## 🔖 LABELS: Workflow States & Visual Markers

### 1. Workflow State Labels (Odoo)

#### Cash Advance States
```yaml
ca:draft:                # ⚪ Draft (editable)
ca:submitted:            # 🔵 Submitted for approval
ca:approved-l1:          # 🟡 Manager approved
ca:approved-l2:          # 🟢 Finance approved
ca:rejected:             # 🔴 Rejected
ca:paid:                 # 💵 Payment completed
ca:liquidating:          # 🔄 Liquidation in progress
ca:done:                 # ✅ Liquidated and closed
ca:overdue:              # ⚠️ Liquidation overdue
```

#### Expense Report States
```yaml
exp:draft:               # ⚪ Draft
exp:submitted:           # 🔵 Submitted
exp:for-review:          # 🟡 Awaiting reviewer
exp:for-approval:        # 🟠 Awaiting approver
exp:approved:            # 🟢 Approved
exp:for-posting:         # 📊 Ready for GL posting
exp:posted:              # ✅ Posted to GL
exp:rejected:            # 🔴 Rejected
```

#### Monthly Close States
```yaml
close:draft:             # ⚪ Draft schedule
close:scheduled:         # 📅 Tasks generated
close:in-progress:       # 🔄 Close in progress
close:for-review:        # 🟡 Awaiting review
close:done:              # ✅ Close completed
close:late:              # ⚠️ Behind schedule
```

#### Spectra Export States
```yaml
spectra:draft:           # ⚪ Draft export
spectra:validating:      # 🔍 Validating data
spectra:ready:           # 🟢 Ready for export
spectra:exported:        # 📤 Files generated
spectra:approved:        # ✅ Finance approved
spectra:failed:          # 🔴 Validation failed
```

---

### 2. Priority Labels

```yaml
priority:critical:       # 🔴 Critical (resolve immediately)
priority:high:           # 🟠 High (resolve within 24h)
priority:medium:         # 🟡 Medium (resolve within week)
priority:low:            # 🟢 Low (backlog)

sla:breach:              # ⚠️ SLA breached
sla:at-risk:             # 🟡 SLA at risk (80%)
sla:on-track:            # 🟢 SLA on track
```

---

### 3. Ownership Labels

```yaml
owner:finance:           # Finance team ownership
owner:accounting:        # Accounting team
owner:hr:                # HR team
owner:operations:        # Operations team
owner:it:                # IT team

role:approver:           # Approver role required
role:reviewer:           # Reviewer role required
role:preparer:           # Preparer/owner role
```

---

### 4. Compliance Labels

```yaml
audit:required:          # Audit trail required
audit:sensitive:         # Sensitive data (PII/Financial)
audit:retention-7y:      # 7-year retention policy

compliance:bir:          # BIR compliance requirement
compliance:sec:          # SEC compliance
compliance:internal:     # Internal policy compliance
```

---

### 5. Integration Status Labels

```yaml
integration:synced:      # ✅ Successfully synced
integration:pending:     # 🔄 Sync pending
integration:failed:      # 🔴 Sync failed
integration:conflict:    # ⚠️ Data conflict

export:ready:            # Ready for export
export:blocked:          # Export blocked
export:in-progress:      # Export in progress
```

---

## 🗺️ Cross-Platform Mapping

### Odoo Models → Tags/Labels

#### `hr.expense.sheet` (Expense Reports)
```python
# Tags (Many2many)
tag_ids = [
    'expense/travel',           # Expense category
    'agency/rim',               # Agency
    'closing-2025-11',          # Close period
    'concur-parity/expense',    # Feature parity
]

# Labels (Selection/Status fields)
state = 'exp:for-approval'      # Workflow state
priority = 'priority:high'       # Priority level
compliance_flag = 'audit:required'  # Compliance flag
```

#### `hr.expense.advance` (Cash Advances)
```python
# Tags
tag_ids = [
    'cash-advance/standard',    # CA type
    'agency/ckvc',              # Agency
    'closing-2025-11',          # Close period
]

# Labels
state = 'ca:approved-l2'        # Workflow state
sla_status = 'sla:on-track'     # SLA tracking
liquidation_status = 'ca:overdue'  # Liquidation status
```

#### `ppm.monthly.close` (Monthly Close)
```python
# Tags
tag_ids = [
    'closing-2025-11',          # Close period
    'month-end',                # Activity type
    'agency/consolidated',      # Scope
]

# Labels
state = 'close:in-progress'     # Close state
schedule_status = 'close:late'  # Schedule tracking
```

#### `tbwa.spectra.export` (Spectra Exports)
```python
# Tags
tag_ids = [
    'spectra/export',           # Export type
    'closing-2025-11',          # Period
    '2025-11',                  # Temporal tag
]

# Labels
state = 'spectra:validated'     # Export state
validation_status = 'export:ready'  # Readiness
approval_status = 'spectra:approved'  # Approval
```

---

### GitHub Issues/PRs → Tags/Labels

#### Issue Example: "Concur Expense OCR Parity"
```yaml
# Labels (GitHub native)
- concur-parity/receipt      # Integration tag
- dev/feature               # Project tag
- priority:high             # Priority
- owner:finance             # Team

# Milestones
- v1.0-concur-parity       # Release milestone

# Project Board
- Column: In Progress      # Workflow state
```

#### PR Example: "Add Spectra GL Mapping"
```yaml
# Labels
- spectra/mapping          # Integration tag
- dev/feature              # Type
- closing-2025-11          # Period
- priority:critical        # Priority

# Checks
- ✅ Lint passed
- ✅ Tests passed
- 🔄 Awaiting review
```

---

### Clarity PPM → Tags/Labels

#### Project: "November 2025 Month-End Close"
```yaml
# Custom Attributes (Tags)
Tags:
  - closing-2025-11
  - month-end
  - agency/consolidated
  - bir/1601-c

# Status (Label)
Status: In Progress         # Workflow state

# Investment Category
Category: Finance Operations

# Financial Properties
Budget: ₱500,000
Actual: ₱350,000

# Resources
Owner: jgtolentino
Team: Finance

# Custom Fields
SLA_Status: On Track
Compliance: BIR Required
Export_Status: Pending Spectra
```

---

### n8n Workflows → Tags

#### Workflow: "Spectra Monthly Export Automation"
```yaml
# Workflow Tags
tags:
  - spectra/export
  - closing-automation
  - finance/monthly
  - 2025-11

# Trigger Tags
trigger_tags:
  - cron-monthly
  - first-business-day

# Integration Tags
integration_tags:
  - odoo-api
  - supabase-storage
  - mattermost-notify
```

---

## 🔄 Tag/Label Governance

### 1. Creation Rules

**Tags** (Flexible, user-created):
- ✅ Anyone can create new tags
- ✅ Follow domain/category/identifier format
- ✅ Use lowercase with hyphens
- ✅ Document in this vocabulary file

**Labels** (Controlled, admin-defined):
- ❌ Only admins create new workflow state labels
- ✅ Must map to actual workflow states in code
- ✅ Must have color/emoji assigned
- ✅ Must be documented with usage rules

### 2. Naming Conventions

**Tags**:
```yaml
Format: {domain}/{category}/{identifier}

Rules:
- Use lowercase
- Use hyphens for spaces
- Use slashes for hierarchy
- Max 50 characters
- No special characters except /-

Good: closing-2025-11, agency/rim, concur-parity/expense
Bad: Closing 2025 Nov, AGENCY_RIM, concur.parity.expense
```

**Labels**:
```yaml
Format: {model-prefix}:{state-name}

Rules:
- Use model prefix (ca:, exp:, close:, spectra:)
- Use lowercase with hyphens
- Match actual state in model
- Assign color/emoji
- Max 30 characters

Good: ca:approved-l2, exp:for-posting, close:in-progress
Bad: approved_level_2, for posting, InProgress
```

### 3. Deprecation Process

**Tag Deprecation**:
```yaml
1. Mark as deprecated in vocabulary
2. Create migration tag mapping
3. Run bulk update script
4. Remove after 1 quarter

Example:
  Deprecated: month-end-2025-11
  Migrate to: closing-2025-11
  Removal: Q1 2026
```

**Label Deprecation**:
```yaml
1. Create new label in Odoo/GitHub
2. Update workflow code
3. Migrate existing records
4. Archive old label (don't delete for audit)

Example:
  Deprecated: ca:waiting-approval
  Migrate to: ca:approved-l1
  Code Update: models/hr_expense_advance.py
```

### 4. Audit & Cleanup

**Quarterly Review**:
```yaml
Tasks:
  - Review tag usage analytics
  - Merge duplicate tags
  - Archive unused tags (no usage in 6 months)
  - Update this vocabulary document
  - Communicate changes to team

Schedule:
  - Q1: January 15
  - Q2: April 15
  - Q3: July 15
  - Q4: October 15
```

---

## 📊 Usage Analytics

### Tag Distribution Targets

```yaml
Expense Reports:
  Tags per record: 3-5
  Most common:
    - expense/{category}
    - agency/{code}
    - closing-{YYYY-MM}

Cash Advances:
  Tags per record: 2-4
  Most common:
    - cash-advance/{type}
    - agency/{code}
    - closing-{YYYY-MM}

Monthly Close:
  Tags per record: 4-6
  Most common:
    - closing-{YYYY-MM}
    - month-end/quarter-end/year-end
    - agency/consolidated
    - bir/{form}

GitHub Issues:
  Labels per issue: 3-5
  Most common:
    - {integration}-parity/{feature}
    - dev/{type}
    - priority:{level}
    - owner:{team}
```

---

## 🔍 Search & Filter Examples

### Odoo Advanced Search

**Find all RIM expenses for November 2025 close**:
```python
domain = [
    ('tag_ids.name', 'in', ['agency/rim', 'closing-2025-11']),
    ('state', '=', 'exp:approved'),
]
```

**Find overdue cash advance liquidations**:
```python
domain = [
    ('state', '=', 'ca:paid'),
    ('liquidation_deadline', '<', today),
    ('tag_ids.name', 'ilike', 'cash-advance'),
]
```

### GitHub Search

**Find all Concur parity issues**:
```
is:issue label:concur-parity/* is:open
```

**Find high-priority finance features**:
```
is:issue label:priority:high label:owner:finance is:open
```

### Clarity PPM Filter

**November 2025 close activities**:
```sql
WHERE Tags CONTAINS 'closing-2025-11'
  AND Status IN ('In Progress', 'For Review')
```

---

## 🚀 Implementation Checklist

### Phase 1: Odoo Tag/Label Setup
- [ ] Create tag model (`tbwa.tag.vocabulary`)
- [ ] Add tag fields to all finance models
- [ ] Populate initial tag vocabulary
- [ ] Create label selection fields
- [ ] Add tag/label filters to views

### Phase 2: GitHub Integration
- [ ] Create GitHub label templates
- [ ] Import labels to repository
- [ ] Add label automation (PR templates)
- [ ] Create label usage guidelines

### Phase 3: Clarity PPM Sync
- [ ] Map Clarity custom attributes to tags
- [ ] Create tag sync automation (n8n)
- [ ] Setup bidirectional sync
- [ ] Test tag filtering

### Phase 4: n8n Automation
- [ ] Tag-based workflow routing
- [ ] Tag analytics collection
- [ ] Tag cleanup automation
- [ ] Tag suggestion engine

### Phase 5: Governance
- [ ] Document tag/label governance
- [ ] Train team on usage
- [ ] Setup quarterly review process
- [ ] Create tag analytics dashboard

---

## 📖 Quick Reference Card

### Common Tag Patterns

```yaml
# Expense Report
['expense/travel', 'agency/rim', 'closing-2025-11', 'concur-parity/expense']

# Cash Advance
['cash-advance/standard', 'agency/ckvc', 'closing-2025-11']

# Monthly Close
['closing-2025-11', 'month-end', 'agency/consolidated', 'bir/1601-c']

# Spectra Export
['spectra/export', 'closing-2025-11', '2025-11']

# GitHub Issue
['concur-parity/receipt', 'dev/feature', 'priority:high', 'owner:finance']

# n8n Workflow
['spectra/export', 'closing-automation', 'finance/monthly']
```

### Label Quick Reference

```yaml
# Workflow States
ca:draft → ca:submitted → ca:approved-l1 → ca:approved-l2 → ca:paid → ca:done
exp:draft → exp:submitted → exp:for-review → exp:for-approval → exp:posted
close:draft → close:scheduled → close:in-progress → close:done
spectra:draft → spectra:validating → spectra:ready → spectra:exported → spectra:approved

# Priority
priority:critical, priority:high, priority:medium, priority:low

# SLA
sla:breach, sla:at-risk, sla:on-track

# Ownership
owner:finance, owner:accounting, owner:hr, owner:operations

# Compliance
audit:required, compliance:bir, compliance:sec
```

---

**Version**: 1.0.0
**Next Review**: Q1 2026 (January 15, 2026)
**Owner**: Finance Operations Team
**Maintainer**: jgtolentino_rn@yahoo.com
