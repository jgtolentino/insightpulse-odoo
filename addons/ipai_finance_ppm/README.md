# IPAI Finance PPM

**TBWA Finance Logical Framework + BIR PPM on Odoo CE 18**

## Overview

Complete project portfolio management system for Finance SSC with:

- **Logical Framework** tracking (Goal → Outcome → IM1/IM2 → Outputs → Activities)
- **BIR Tax Filing Calendar** with auto-created tasks
- **ECharts Dashboard** (Clarity PPM-inspired)
- **Multi-Agency Support** (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)

## Features

### 1. Finance Logical Framework (`ipai.finance.logframe`)

Tracks strategic objectives with:
- Hierarchical levels (Goal, Outcome, IM1, IM2, Outputs, Activities)
- Indicators, Means of Verification, Assumptions
- Linked project tasks
- Integration with BIR schedule

**Levels**:
- **Goal**: 100% compliant and timely month-end closing and tax filing
- **Outcome**: Zero-penalty compliance with timely financial reporting
- **IM1**: Month-end closing processes completed accurately and on schedule
- **IM2**: Complete, on-time tax filing for payroll, VAT, and withholding taxes
- **Outputs**: Reconciliations, Journal Entries, BIR Forms
- **Activities**: Daily operations (Bank Recon, GL Recon, Tax Computation, etc.)

### 2. BIR Filing Calendar (`ipai.finance.bir_schedule`)

Comprehensive BIR tax form tracking:
- Filing deadlines from BIR calendar
- Internal deadlines: Preparation, Review, Approval
- Responsible persons: Supervisor, Reviewer, Approver
- Status tracking: Not Started → In Progress → Submitted → Filed
- Completion percentage
- Auto-created project tasks via cron

**Forms Tracked**:
- 1601-C (Monthly Withholding Tax on Compensation)
- 0619-E (Expanded Withholding Tax Monthly Remittance)
- 2550Q (Quarterly VAT Return)
- 1702-RT (Annual Income Tax Return)
- 1601-EQ (Expanded WHT Quarterly)
- 1601-FQ (Final WHT Quarterly)

### 3. ECharts Dashboard

Clarity PPM-inspired visualizations:
- BIR deadline timeline (bar chart with color-coded status)
- Completion percentage tracking
- Status distribution (pie chart)
- Logframe task distribution
- KPI cards: Total Forms, On-Time Rate, At Risk, Late Filings

**Access**: `/ipai/finance/ppm`

### 4. Automated Task Creation

Daily cron job (8AM) creates 3 tasks per BIR form:
1. **Preparation** (due: prep_deadline) → assigned to Finance Supervisor
2. **Review** (due: review_deadline) → assigned to Senior Finance Manager
3. **Approval** (due: approval_deadline) → assigned to Finance Director

All tasks linked to:
- Project: "TBWA Finance – Month-End & BIR"
- Logframe: IM2 "Tax Filing Compliance"
- BIR Schedule: Specific form

## Installation

1. Copy module to `addons/ipai_finance_ppm/`
2. Update Apps List in Odoo
3. Search "IPAI Finance PPM"
4. Click Install

## Configuration

### 1. Assign Responsible Users

Go to **Finance PPM → BIR Calendar** and edit each form to assign:
- Finance Supervisor
- Senior Finance Manager
- Finance Director

### 2. Verify Cron Job

Go to **Settings → Technical → Automation → Scheduled Actions** and verify:
- **Finance PPM: Sync BIR Tasks** is Active
- Next execution: 2025-11-24 08:00:00
- Runs daily

### 3. Check Project

Go to **Project** and verify:
- "TBWA Finance – Month-End & BIR" project exists
- Tasks are being created automatically

## Usage

### View Dashboard

1. Go to **Finance PPM → Dashboard**
2. View ECharts visualizations:
   - BIR filing timeline
   - Completion tracking
   - Status distribution
   - Logframe overview

### Manage Logframe

1. Go to **Finance PPM → Logframe**
2. View hierarchical objectives
3. Click entry to see:
   - Indicators
   - Means of Verification
   - Assumptions
   - Linked tasks

### Track BIR Filings

1. Go to **Finance PPM → BIR Calendar**
2. View upcoming filings
3. Update status: Not Started → In Progress → Submitted → Filed
4. Track completion percentage
5. View auto-created tasks

### Work with Tasks

1. Go to **Project → Tasks**
2. Filter by: "TBWA Finance – Month-End & BIR"
3. View tasks organized by BIR form
4. Update task status

## Data Model

```
ipai.finance.logframe (Logical Framework)
├── level: Selection (goal, outcome, im1, im2, output, activity_im1, activity_im2)
├── code: Char (e.g., "IM2", "OUT-1", "ACT-1.1")
├── name: Char (Objective description)
├── indicators: Text
├── means_of_verification: Text
├── assumptions: Text
├── task_ids: One2many (project.task)
└── bir_schedule_id: Many2one (ipai.finance.bir_schedule)

ipai.finance.bir_schedule (BIR Filing Calendar)
├── name: Char (e.g., "1601-C (Compensation) – Dec 2025")
├── period_covered: Char
├── filing_deadline: Date (BIR deadline)
├── prep_deadline: Date (Internal: BIR - 4 days)
├── review_deadline: Date (Internal: BIR - 2 days)
├── approval_deadline: Date (Internal: BIR - 1 day)
├── supervisor_id: Many2one (res.users)
├── reviewer_id: Many2one (res.users)
├── approver_id: Many2one (res.users)
├── status: Selection (not_started, in_progress, submitted, filed, late)
├── completion_pct: Float
├── task_ids: One2many (project.task)
└── logframe_id: Many2one (ipai.finance.logframe)

project.task (Extended)
├── finance_logframe_id: Many2one (ipai.finance.logframe)
├── bir_schedule_id: Many2one (ipai.finance.bir_schedule)
└── is_finance_ppm: Boolean (Computed)
```

## Seed Data

Module includes seed data for:
- 1 Project: "TBWA Finance – Month-End & BIR"
- 12 Logframe entries (Goal, Outcome, IM1, IM2, 3 Outputs, 4 Activities)
- 8 BIR schedule entries (Dec 2025 - Q1 2026 forms)

## API Endpoints

- `GET /ipai/finance/ppm` - Dashboard (HTML)
- `POST /ipai/finance/ppm/api/bir` - BIR data (JSON)
- `POST /ipai/finance/ppm/api/logframe` - Logframe data (JSON)

## ECharts Integration

Dashboard uses ECharts 5.5.1 for:
- Bar charts (deadlines, completion)
- Pie charts (status distribution)
- Color-coded visualizations (green=filed, orange=in_progress, red=late)
- Responsive design

## Dependencies

- `base` - Odoo base module
- `project` - Project management module
- `web` - Web framework

## License

LGPL-3

## Author

InsightPulse AI
https://insightpulseai.com

## Support

For issues or feature requests, contact Finance SSC team.

## Changelog

### 1.0.0 (2025-11-23)
- Initial release
- Logframe tracking
- BIR calendar with auto-tasks
- ECharts dashboard
- 8 BIR forms seeded
