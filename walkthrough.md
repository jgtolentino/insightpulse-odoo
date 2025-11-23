# Walkthrough - Notion Parity Modules

## Overview
This walkthrough covers the installation and usage of the new `ipai_docs` and `ipai_docs_project` modules, designed to provide internal documentation capabilities and link them to projects/tasks in Odoo CE.

## 1. Installation
1.  **Update App List**: Go to **Apps** and click **Update App List**.
2.  **Install `ipai_docs`**: Search for "IPAI Docs" and click **Activate**.
3.  **Install `ipai_docs_project`**: Search for "IPAI Docs – Project & Task Integration" and click **Activate**.

## 2. Usage Guide

### Creating Documents
1.  Navigate to **Knowledge > Documents**.
2.  Click **New**.
3.  Enter a **Title** (e.g., "Deployment SOP").
4.  Select a **Type** (e.g., "SOP / Playbook").
5.  Add content in the **Content** tab.
6.  (Optional) Add **Tags** and **Collaborators**.

### Linking to Projects
1.  Navigate to **Project > Projects**.
2.  Open a project.
3.  Go to the **Documents** tab.
4.  Click **Add a line** to link existing docs or create new ones.
5.  Observe the **Documents** smart button at the top updating its count.

### Linking to Tasks
1.  Navigate to **Project > Tasks**.
2.  Open a task.
3.  Go to the **Documents** tab.
4.  Link documents similarly to projects.

## 3. Verification Checklist
- [ ] Module `ipai_docs` installs without error.
- [ ] Module `ipai_docs_project` installs without error.
- [ ] "Knowledge" menu appears.
- [ ] Can create, edit, and save a Document.
- [ ] "Documents" smart button appears on Project form.
- [ ] "Documents" smart button appears on Task form.
- [ ] Linking a doc to a project reflects in the smart button count.

## 4. Cash Advance Module
1.  **Install**: Search for "IPAI Cash Advance" and click **Activate**.
2.  **Create Request**:
    - Go to **Cash Advance > Requests**.
    - Click **New**.
    - Enter Amount Requested and Purpose.
    - Submit -> Approve -> Disburse.
3.  **Liquidation**:
    - Click **Start Liquidation**.
    - Add lines in the "Liquidation Details" tab (Meals, Transpo, etc.).
    - Verify "Amount Due" calculation.
    - Click **Submit Liquidation** -> **Close**.

## 5. Notion-style Workspace
1.  **Workspace Projects**:
    - Go to **Project**. You will see 5 new Workspace Projects (e.g., "WS – Finance & Tax").
    - These act as your "Spaces".
2.  **Root Docs**:
    - Go to **Knowledge > Documents**.
    - You will see 5 "Home" pages (e.g., "Finance – Home").
    - These are linked to their respective projects.
3.  **Using Templates**:
    - Go to **Project**.
    - Find **TEMPLATE – Month-End Closing**.
    - Click the "Actions" gear icon -> **Duplicate**.
    - Rename it (e.g., "Month-End Closing – Nov 2025").
    - **Result**: A new project is created with all tasks ("Prepare Trial Balance", etc.) pre-loaded and visible on mobile.

## 6. OCR Expense Module
1.  **Install**: Search for "IPAI OCR for Expenses" and click **Activate**.
2.  **Usage**:
    - Go to **Expenses > My Expenses > Create**.
    - You will see a "Send to OCR" button (if in Draft).
    - Clicking it sets the status to "Pending OCR".
    - (Integration Note: This is currently a skeleton waiting for the n8n webhook connection).


