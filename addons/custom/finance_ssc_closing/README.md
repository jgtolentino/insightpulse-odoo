# Finance SSC Month-End Closing Module

**Notion Enterprise Alternative for Finance Shared Service Centers**

## Overview

This Odoo module provides comprehensive month-end closing workflow management for Finance Shared Service Centers (SSC) handling multiple agencies. It replaces Notion Enterprise's database and workflow features with native Odoo functionality enhanced with OCA modules.

## Features

### 1. Month-End Closing Management
- **Closing Periods**: Manage monthly closing cycles with state tracking
- **Task Management**: Create and track closing tasks across multiple agencies
- **BIR Compliance**: Track BIR form submissions and deadlines
- **Multi-Agency Support**: Handle RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB agencies

### 2. Workflow Automation
- **Task Templates**: Reusable templates for common closing tasks
- **Automatic Reminders**: Email and activity reminders for deadlines
- **Approval Workflows**: Multi-level review and approval process
- **Dependency Management**: Task dependencies to ensure proper sequence

### 3. Collaboration Features
- **@Mentions**: Notify team members via Odoo Chatter
- **Comments & Notes**: Discussion threads on tasks and periods
- **File Attachments**: Attach supporting documents to tasks
- **Activity Tracking**: Track all changes with audit log

### 4. Reporting & Analytics
- **Completion Dashboard**: Real-time progress tracking
- **BIR Compliance Report**: Track filing status across all agencies
- **Variance Analysis**: Compare actual vs estimated completion times
- **Custom Reports**: Excel and PDF export capabilities

## Installation

### Prerequisites

- Odoo 19.0 Community Edition
- PostgreSQL 16 with pgvector extension
- OCA modules (see dependencies below)

### Dependencies

**Odoo Core Modules:**
- `account` - Accounting
- `account_accountant` - Advanced accounting features
- `project` - Project management
- `mail` - Messaging and activities
- `hr` - Human resources (for departments)
- `web` - Web interface

**OCA Modules (Optional but Recommended):**
- `auditlog` - Complete audit trail
- `approval_request` - Multi-level approvals
- `report_xlsx` - Excel report generation
- `web_timeline` - Timeline/Gantt view

### Installation Steps

1. **Copy module to addons directory:**
   ```bash
   cp -r finance_ssc_closing /path/to/odoo/addons/custom/
   ```

2. **Update module list:**
   ```bash
   docker-compose exec odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoo19 --update-all --stop-after-init
   ```

3. **Install the module:**
   - Go to Apps menu
   - Search for "Finance SSC Month-End Closing"
   - Click Install

## Configuration

### 1. Setup Companies (Agencies)

1. Go to Settings > Companies
2. Create companies for each agency:
   - RIM - Razon Industries Management
   - CKVC - CK Venture Capital
   - BOM - Bill of Materials Corp
   - JPAL - JP Analytics Limited
   - JLI - JL Investments
   - JAP - JP Asia Pacific
   - LAS - Legal Advisory Services
   - RMQB - RM Quality Bank

### 2. Configure Task Templates

1. Go to Finance SSC > Configuration > Task Templates
2. Create templates for common tasks:
   - Bank Reconciliation
   - Journal Entries
   - Trial Balance Review
   - BIR Form Preparation
   - etc.

### 3. Setup User Access

1. Go to Settings > Users
2. Assign groups:
   - **Accountant**: Read/write access to tasks
   - **Accounting Manager**: Full access including deletion

### 4. Configure BIR Forms

The module comes pre-configured with common BIR forms:
- Form 1601-C (Monthly Withholding Tax)
- Form 1702-RT (Annual Income Tax)
- Form 2550-Q (Quarterly VAT)
- etc.

## Usage

### Creating a Closing Period

1. Go to Finance SSC > Closing Periods
2. Click "Create"
3. Fill in:
   - Period Name (e.g., "2025-01")
   - Start Date and End Date
   - Fiscal Year
   - Responsible Person
   - Reviewers
4. Click "Save"

### Generating Tasks

1. Open a Closing Period
2. Click "Generate Tasks" button
3. Select task templates to apply
4. Choose companies/agencies
5. Confirm to create tasks

### Working on Tasks

1. Go to Finance SSC > Closing Tasks
2. Filter by your assigned tasks
3. Click "Start" to begin working
4. Update progress as you work
5. Attach supporting documents
6. Click "Submit for Review" when complete

### BIR Compliance Tracking

1. Go to Finance SSC > BIR Compliance
2. View all BIR forms by period and agency
3. Track filing status:
   - Pending
   - Preparing
   - Ready to File
   - Filed
   - Paid
4. Upload BIR acknowledgments
5. Track payment confirmations

### Monitoring Progress

1. Go to Finance SSC > Dashboard
2. View real-time statistics:
   - Completion percentage by period
   - Overdue tasks
   - BIR filing status
   - Agency-wise breakdown

## Notion Feature Comparison

| Notion Feature | Odoo Equivalent | Module Feature |
|----------------|-----------------|----------------|
| Database | Model (finance.closing.task) | ✅ |
| Table View | Tree View | ✅ |
| Kanban Board | Kanban View | ✅ |
| Calendar | Calendar View | ✅ |
| Timeline | Timeline View (with OCA module) | ✅ |
| Form | Form View | ✅ |
| Filters | Search Filters | ✅ |
| Sorting | Order By | ✅ |
| Grouping | Group By | ✅ |
| Properties | Fields | ✅ |
| Relations | Many2one/One2many | ✅ |
| Formulas | Computed Fields | ✅ |
| Rollup | Aggregates | ✅ |
| @Mentions | Chatter Mentions | ✅ |
| Comments | Chatter Messages | ✅ |
| Files | Attachments | ✅ |
| Approvals | Approval Workflow | ✅ |
| Reminders | Activities | ✅ |
| Templates | Task Templates | ✅ |
| Dashboard | Pivot/Graph Views | ✅ |
| Export | Excel/PDF Reports | ✅ |
| Audit Log | Audit Trail (OCA) | ✅ |
| Version History | Document Versioning (OCA) | 🔄 |

✅ = Available | 🔄 = Requires OCA module

## Technical Details

### Models

#### finance.closing.period
Main model for managing closing periods.

**Key Fields:**
- `name` - Period identifier (e.g., "2025-01")
- `start_date` / `end_date` - Period dates
- `state` - Workflow state
- `task_ids` - Related tasks
- `bir_task_ids` - Related BIR compliance tasks

**States:**
1. Draft
2. Open
3. In Progress
4. Under Review
5. Approved
6. Closed

#### finance.closing.task
Individual closing tasks.

**Key Fields:**
- `name` - Task description
- `period_id` - Parent period
- `company_id` - Agency/company
- `task_type` - Type of task
- `assigned_to` - Assignee
- `state` - Task status
- `depends_on_ids` - Task dependencies

#### finance.bir.compliance.task
BIR form filing tracking.

**Key Fields:**
- `bir_form` - BIR form type
- `due_date` - Filing deadline
- `state` - Filing status
- `tax_amount` / `penalty_amount` - Tax details
- `reference_number` - BIR confirmation

### Security

The module implements row-level security:
- Users can only see tasks assigned to them or their company
- Accountants can create and edit tasks
- Managers have full access
- Multi-company rules prevent cross-agency data access

### API Integration

The module provides REST API endpoints (requires `base_rest` OCA module):

**Endpoints:**
- `GET /api/closing/periods` - List periods
- `GET /api/closing/tasks` - List tasks
- `POST /api/closing/tasks/<id>/start` - Start task
- `POST /api/closing/tasks/<id>/complete` - Complete task

## InsightPulse AI Integration

This module integrates with InsightPulse AI services:

### PaddleOCR Integration
Automatic document scanning for:
- BIR forms
- Bank statements
- Invoices
- Receipts

### AI Assistant
Natural language queries:
- "Show me overdue tasks for RIM"
- "What BIR forms are due next week?"
- "Generate closing summary report"

## Troubleshooting

### Common Issues

**Issue: Tasks not visible**
- Check user access rights
- Verify company assignment
- Check multi-company rules

**Issue: BIR forms not generating**
- Ensure tax configuration is complete
- Check account setup
- Verify company TIN is set

**Issue: Reminders not sending**
- Check email server configuration
- Verify cron jobs are running
- Check activity settings

## Support

For issues and questions:
- GitHub: https://github.com/jgtolentino/insightpulse-odoo
- Documentation: /docs/NOTION_TO_ODOO_MAPPING.md

## License

LGPL-3

## Credits

**Author:** InsightPulse AI Finance SSC Team
**Maintainer:** jgtolentino
**Contributors:**
- Claude Code (AI-assisted development)
- InsightPulse AI Community

---

**Version:** 19.0.1.0.0
**Last Updated:** 2025-11-05
