# InsightPulse ERP – v1 Scope Tasks

**Reference**: See [MODULE_SERVICE_MATRIX.md](./MODULE_SERVICE_MATRIX.md) for complete platform architecture.

---

## A. SAP Concur-equivalent (Expenses & Travel) – v1 Checklist

### Odoo Modules Installation
- [x] Core CE modules installed:
  - [x] `hr` - Base HR model for employees
  - [x] `hr_expense` - Expense claims backbone
  - [x] `hr_holidays` - Time Off (optional travel integration)
  - [x] `account` - Posting, journals, tax
  - [x] `account_accountant` - Advanced accounting features
  - [x] `project` - Tag expenses to projects
  - [x] `calendar` - Approvals and travel dates

- [x] Custom InsightPulse modules installed:
  - [x] `ipai_ce_cleaner` - Remove Enterprise/odoo.com branding
  - [x] `ipai_ocr_expense` - OCR integration with statusbar
  - [ ] `ipai_expense` - PH travel/expense workflows (**IN PROGRESS**)

### OCR Infrastructure
- [x] OCR adapter live at `https://ocr.insightpulseai.net/api/expense/ocr`
- [x] PaddleOCR-VL + OpenAI engine deployed on `ocr-service-droplet`
- [x] Odoo OCR settings configured:
  - [x] OCR URL set in System Parameters
  - [x] API key configured (if applicable)
- [x] PH normalization active in OCR adapter:
  - [x] Date format: MM/DD/YYYY → YYYY-MM-DD
  - [x] Amount format: ₱1,234.56 → 1234.56
  - [x] Vendor name cleaning (remove "Inc.", "Corp.", etc.)

### Expense Workflows
- [ ] Travel request workflow active in `ipai_expense`:
  - [ ] Travel request model created
  - [ ] M-5, M-3 workflow fields implemented
  - [ ] Project tagging enabled
  - [ ] BIR tags configured
- [ ] Expense approval workflow:
  - [ ] Finance approver role configured
  - [ ] Email notifications enabled
  - [ ] Stage transitions validated

### Month-end Closing Integration
- [ ] Month-end closing project template created
- [ ] Tasks imported from CSV template:
  - [ ] Expense reconciliation tasks
  - [ ] Travel advance clearing tasks
  - [ ] BIR withholding tax filing tasks

### n8n Automation
- [ ] n8n workflows deployed (fin-workspace):
  - [ ] Daily "pending expenses" reminder
  - [ ] "Ready to Post" → mark tasks in closing project as synced
  - [ ] Email → expense creation (optional)
  - [ ] Receipt OCR → auto-create expense

### Testing & Validation
- [ ] End-to-end OCR test:
  - [ ] Upload receipt via Odoo UI
  - [ ] Verify OCR extraction accuracy ≥80%
  - [ ] Confirm expense fields auto-populated
- [ ] Approval workflow test:
  - [ ] Submit expense for approval
  - [ ] Verify reviewer receives notification
  - [ ] Approve and verify posting to accounting
- [ ] BIR compliance test:
  - [ ] Verify withholding tax calculation
  - [ ] Generate 1601-C report from expenses
  - [ ] Validate against BIR requirements

---

## B. Cheqroom-equivalent (Equipment Booking) – v1 Checklist

### Odoo Modules Installation
- [x] Core CE modules installed:
  - [x] `stock` - Equipment as stockable items
  - [x] `stock_account` - Asset valuations
  - [x] `maintenance` - Maintenance requests
  - [x] `project` - Booking contexts (shoots, events)
  - [x] `calendar` - Booking dates and conflicts

- [ ] Custom InsightPulse modules installed:
  - [x] `ipai_ce_cleaner` - UI cleanup
  - [ ] `ipai_equipment` - Equipment catalog and booking (**PENDING**)

### Equipment Catalog Setup
- [ ] Equipment categories created:
  - [ ] Cameras (Sony FX3, Canon C70, etc.)
  - [ ] Lenses (EF, RF, E-mount)
  - [ ] Audio (lavs, boom mics, recorders)
  - [ ] Lighting (LED panels, softboxes)
  - [ ] Grip (tripods, gimbals, sliders)
  - [ ] Locations (Manila, Makati, BGC studios)

- [ ] Equipment assets created:
  - [ ] Asset ID / serial number
  - [ ] Category and subcategory
  - [ ] Purchase date and value
  - [ ] Current location
  - [ ] Status (available, in-use, maintenance, retired)

### Booking System
- [ ] `ipai_equipment` module scaffolded:
  - [ ] `equipment.asset` model created
  - [ ] `equipment.booking` model created
  - [ ] `equipment.incident` model created

- [ ] Booking workflow implemented:
  - [ ] Booking form with start/end datetime
  - [ ] Project/shoot linkage
  - [ ] Responsible person (employee)
  - [ ] Location selection
  - [ ] Conflict detection (double-booking prevention)

- [ ] Check-in/out workflow:
  - [ ] Check-out button on booking
  - [ ] Status update: available → in-use
  - [ ] Check-in button on booking
  - [ ] Status update: in-use → available
  - [ ] Condition notes field

### Incident Logging
- [ ] Incident model linked to booking and asset:
  - [ ] Incident type (damage, loss, malfunction)
  - [ ] Description and photos
  - [ ] Responsible person
  - [ ] Repair cost and status
  - [ ] Link to maintenance request

### n8n Automation (Optional)
- [ ] n8n workflows deployed:
  - [ ] Booking confirmation email
  - [ ] Pre-shoot reminder (24h before)
  - [ ] Overdue return alert
  - [ ] Sync bookings → Google Calendar per asset

### Testing & Validation
- [ ] End-to-end booking test:
  - [ ] Create booking for camera + lens kit
  - [ ] Verify conflict detection with overlapping dates
  - [ ] Check-out equipment
  - [ ] Check-in equipment with notes
- [ ] Incident test:
  - [ ] Log damage incident during booking
  - [ ] Link to maintenance request
  - [ ] Track repair cost and status

---

## C. Notion-equivalent (Finance Workspace & BIR) – v1 Checklist

### Odoo Modules Installation
- [x] Core CE modules installed:
  - [x] `project` - Main "databases" for tasks
  - [x] `knowledge` - Wiki pages for SOPs
  - [x] `mail` - Activities for review/approval
  - [x] `calendar` - Due dates and reminders
  - [x] `account` - Financial data for closing tasks

- [ ] Custom InsightPulse modules installed:
  - [x] `ipai_ce_cleaner` - UI cleanup
  - [ ] `ipai_finance_monthly_closing` - Finance closing tasks (**PENDING**)

### Project Template Setup
- [ ] Project template created: **"Month-end Closing – Template"**
  - [ ] Stages configured: To Do, In Progress, Review, Approved, Done
  - [ ] Custom fields added to project.task:
    - [ ] `cluster` (A/B/C/D)
    - [ ] `relative_due` (M-5, M-3, M+2, etc.)
    - [ ] `due_date` (computed from relative_due + month)
    - [ ] `owner_code` (RIM, CKVC, BOM, etc.)
    - [ ] `reviewer_id` (employee)
    - [ ] `approver_id` (employee)
    - [ ] `erp_ref` (reference to source record)
    - [ ] `auto_sync` (boolean for automation)
  - [ ] BIR-specific fields:
    - [ ] `bir_form` (1601-C, 1602, 2550Q, etc.)
    - [ ] `bir_period_label` (e.g., "Jan 2025")
    - [ ] `bir_deadline` (date)
    - [ ] `bir_agency` (multi-select: RIM, CKVC, etc.)

### Active Project Setup
- [ ] Active project created: **"Month-end Closing – Nov 2025"** (example)
  - [ ] Tasks imported from CSV template
  - [ ] Due dates calculated from relative_due
  - [ ] Owners assigned per cluster
  - [ ] Reviewers/approvers assigned

### CSV Import Template
- [ ] CSV template created with columns:
  ```
  name, cluster, relative_due, owner_code, reviewer, approver,
  bir_form, bir_agency, description, checklist
  ```
- [ ] Import script tested:
  - [ ] Parse CSV
  - [ ] Calculate due_date from relative_due + current month
  - [ ] Link reviewer/approver by employee name
  - [ ] Create tasks in active project

### Knowledge Pages (SOP Wiki)
- [ ] Knowledge workspace created: **"Finance SSC Documentation"**
- [ ] SOP pages created:
  - [ ] "Closing SOP – Cluster A (General Ledger)"
  - [ ] "Closing SOP – Cluster B (Accounts Payable)"
  - [ ] "Closing SOP – Cluster C (Accounts Receivable)"
  - [ ] "Closing SOP – Cluster D (Payroll & HR)"
- [ ] BIR reference pages:
  - [ ] "BIR Calendar – 2025"
  - [ ] "BIR Form 1601-C Filing Guide"
  - [ ] "BIR Form 1602 Filing Guide"
  - [ ] "BIR Form 2550Q Filing Guide"

### n8n Automation
- [ ] n8n workflows deployed (fin-workspace):
  - [ ] Daily digest of overdue tasks by cluster & owner
  - [ ] Due-in-3-days reminder
  - [ ] BIR deadline alert (7 days before)
  - [ ] Weekly rollup email to finance director
  - [ ] Auto-stage progression for auto_sync tasks

### Views & Filters
- [ ] Kanban view by stage (default)
- [ ] List view with custom fields visible
- [ ] Filters created:
  - [ ] "BIR Tasks" (where bir_form is not null)
  - [ ] "Closing Tasks by Cluster" (group by cluster)
  - [ ] "Overdue for this month" (due_date < today AND stage != Done)
  - [ ] "My Tasks" (owner_code = current user's code)
  - [ ] "Pending Review" (stage = Review)

### Testing & Validation
- [ ] End-to-end closing workflow test:
  - [ ] Create new monthly project from template
  - [ ] Import tasks from CSV
  - [ ] Verify due dates calculated correctly
  - [ ] Move task through stages: To Do → In Progress → Review → Approved → Done
  - [ ] Verify reviewer receives activity notification
  - [ ] Verify approver receives activity notification after review
- [ ] BIR workflow test:
  - [ ] Filter for BIR tasks
  - [ ] Verify BIR deadline field calculated correctly
  - [ ] Verify multi-agency tagging works
  - [ ] Generate 1601-C report from linked expense data
  - [ ] Mark task as Done after filing

---

## D. Cross-Product Integration Tests

### Expense → Closing Task Sync
- [ ] Create expense in `hr_expense`
- [ ] Mark as "Ready to Post"
- [ ] Verify closing task stage updated in project (via n8n or RPC)
- [ ] Verify `erp_ref` field links to expense record

### Equipment Booking → Project Task
- [ ] Create equipment booking linked to project
- [ ] Verify project task shows linked booking
- [ ] Complete booking (check-in)
- [ ] Verify task status updated

### BIR Filing → Multiple Agencies
- [ ] Create BIR task tagged with 3 agencies (RIM, CKVC, BOM)
- [ ] Generate consolidated report across agencies
- [ ] File single form with BIR
- [ ] Mark task as Done
- [ ] Verify all 3 agencies reflected in filing record

---

## E. Quality Gates (v1 Release Criteria)

### Functional Requirements
- [ ] All v1 checklists above completed at ≥80%
- [ ] Core workflows tested end-to-end
- [ ] No critical bugs blocking primary use cases

### Performance Requirements
- [ ] OCR processing time: P95 < 30s per receipt
- [ ] Odoo response time: P95 < 2s for list views
- [ ] Database size: < 5GB for v1 dataset

### Security Requirements
- [ ] CE-only validation: 0 Enterprise modules installed
- [ ] 0 odoo.com links in database and UI
- [ ] RLS policies active on Supabase (if used)
- [ ] API keys stored in environment variables (not DB)

### Documentation Requirements
- [ ] MODULE_SERVICE_MATRIX.md complete and reviewed
- [ ] Installation sequence documented
- [ ] User guides created:
  - [ ] Expense submission guide (Concur-equivalent)
  - [ ] Equipment booking guide (Cheqroom-equivalent)
  - [ ] Month-end closing guide (Notion-equivalent)
- [ ] Admin guides created:
  - [ ] Module installation and upgrade guide
  - [ ] n8n workflow deployment guide
  - [ ] OCR adapter configuration guide

### Deployment Requirements
- [ ] Production deploy tested on staging first
- [ ] Rollback plan documented
- [ ] Database backup taken before upgrade
- [ ] Downtime window communicated to users

---

## F. Post-v1 Enhancements (Future Phases)

### OCA Addon Integration
- [ ] `account_invoice_import` - AP invoice ingestion
- [ ] `hr_expense_advance_clearing` - Travel advance reconciliation
- [ ] `mail_activity_board` - Enhanced activity boards
- [ ] `maintenance_equipment_hierarchy` - Parent/child equipment
- [ ] `stock_request` - Internal equipment requests
- [ ] `project_task_material` - Task material consumption

### Analytics & BI
- [ ] Superset dashboards deployed:
  - [ ] Expense analytics (spend by category, employee, project)
  - [ ] Equipment utilization (booking rate, downtime, incidents)
  - [ ] Closing SLA (on-time %, overdue by cluster)
- [ ] Supabase mirror configured for long-term analytics
- [ ] AI agents integrated (Mattermost + Claude)

### Advanced Features
- [ ] Mobile app for expense submission (PWA or native)
- [ ] QR code check-in/out for equipment
- [ ] Automated BIR form generation from Odoo data
- [ ] Real-time collaboration on closing tasks (live updates)
- [ ] Predictive analytics for expense trends and equipment maintenance

---

**Last Updated**: 2025-11-21
**Baseline Version**: v0.2.1-quality
**Target v1 Release**: TBD
