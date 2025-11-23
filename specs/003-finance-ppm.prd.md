# PRD: IPAI Finance PPM (Project Portfolio Management)

**Version:** 1.0
**Status:** Draft
**Source:** User Blueprint (Notion/Excel Parity)

## 1. Overview
This module implements a "Notion-style" Project Portfolio Management (PPM) system for the Finance team. It replaces manual spreadsheets/Notion boards with structured Odoo models to track:
1.  **People & Roles** (Directory)
2.  **Recurring Monthly Tasks** (RACI + SLAs)
3.  **Regulatory Compliance** (BIR Filing Calendar)

## 2. Core Models

### 2.1. Finance Directory (`ipai.finance.person`)
*   **Purpose:** Single source of truth for Finance team members, codes, and roles.
*   **Fields:**
    *   `code` (Char, Required): Unique initial code (e.g., CKVC, RIM, LAS).
    *   `name` (Char, Required): Full name.
    *   `email` (Char): Email address.
    *   `role` (Selection): Supervisor, Manager, Director, Staff.
    *   `user_id` (Many2one `res.users`): Link to Odoo user (optional).

### 2.2. Monthly Task Template (`ipai.finance.task.template`)
*   **Purpose:** Defines the recurring work packages (RACI matrix).
*   **Fields:**
    *   `employee_code_id` (Many2one `ipai.finance.person`): The "Owner".
    *   `category` (Char/Selection): Task category (e.g., "Payables", "Reporting").
    *   `name` (Text): Detailed monthly task description (Rich Text).
    *   `reviewed_by_id` (Many2one `ipai.finance.person`): Reviewer.
    *   `approved_by_id` (Many2one `ipai.finance.person`): Approver.
    *   `prep_duration` (Float): SLA for preparation (days).
    *   `review_duration` (Float): SLA for review (days).
    *   `approval_duration` (Float): SLA for approval (days).

### 2.3. BIR Form Schedule (`ipai.bir.form.schedule`)
*   **Purpose:** Tracks regulatory filing deadlines and internal milestones.
*   **Fields:**
    *   `form_code` (Char): Form Name (e.g., "1601-C", "2550Q").
    *   `period` (Char): Period Covered (e.g., "Dec 2025").
    *   `bir_deadline` (Date): Actual hard deadline.
    *   `prep_date` (Date): Internal deadline for Prep.
    *   `review_date` (Date): Internal deadline for Review.
    *   `approval_date` (Date): Internal deadline for Payment Approval.
    *   `responsible_prep_id` (Many2one `ipai.finance.person`).
    *   `responsible_review_id` (Many2one `ipai.finance.person`).
    *   `responsible_approval_id` (Many2one `ipai.finance.person`).

### 2.4. BIR Process Step (`ipai.bir.process.step`)
*   **Purpose:** Detailed SOP steps for each filing.
*   **Fields:**
    *   `schedule_id` (Many2one `ipai.bir.form.schedule`): Parent schedule.
    *   `step_no` (Integer): Sequence (1, 2, 3...).
    *   `title` (Char): Step Name (e.g., "Report Approval").
    *   `detail` (Text): Narrative SOP.
    *   `target_offset` (Integer): Days before deadline.
    *   `role` (Char): Responsible Role.
    *   `person_id` (Many2one `ipai.finance.person`): Specific assignee.

## 3. Views & UX

### 3.1. Directory
*   **List View:** Code, Name, Email, Role.

### 3.2. Monthly Tasks (PPM Board)
*   **Kanban/List:** Grouped by `employee_code_id` or `category`.
*   **Visuals:** Display Reviewer/Approver as "Tags" or "Chips". Show SLA durations clearly.

### 3.3. BIR Calendar
*   **Calendar View:** Based on `bir_deadline`.
*   **Gantt (Optional):** Visualizing the Prep -> Review -> Approval timeline.

## 4. Workflows
*   **Generation:** A wizard or cron job to generate actual `project.task` or `mail.activity` records from these templates each month (Future Phase).
*   **For MVP:** This module acts as the **Master Data / Planning** layer.
