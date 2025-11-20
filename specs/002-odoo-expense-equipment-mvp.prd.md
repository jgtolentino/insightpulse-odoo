# InsightPulse ERP – Expense & Equipment MVP (SAP Concur + Cheqroom Parity)

**Status:** Draft v0.1 (MVP Scope)
**Owner:** InsightPulseAI – ERP Platform Team
**Repo:** `insightpulse-odoo`
**Last Updated:** 2025-11-20

---

## 1. Purpose & Context

InsightPulse wants a **self-hosted Odoo CE/OCA stack** that delivers:

1. **SAP Concur–equivalent expense & travel management**
2. **Cheqroom–equivalent equipment management & bookings**

This stack **must not use any Odoo Enterprise or IAP features** and must **never upsell or deep-link to odoo.com**. All UX, help links, and call-to-actions must either:

* Point to `*.insightpulseai.net` (docs, support, billing)
* Or to **OCA / CE documentation** for the underlying modules

All visible menu items, app store tiles, and settings screens must reflect the **actual installed/activated state** of modules and services to avoid stale or misleading links.

This PRD defines the **MVP feature set** and constraints, GitHub Spec-Kit style, to drive initial implementation and CI/CD.

---

## 2. Goals & Non-Goals

### 2.1 Goals

1. **Unified Expense + Equipment Platform (MVP)**

   * Replace SAP Concur (PH use cases) for:

     * Expense capture & approval
     * Travel requests
     * Reimbursements & GL posting
   * Replace Cheqroom for:

     * Asset & equipment catalog
     * Reservations / check-in / check-out
     * Condition tracking & incidents

2. **Pure Odoo CE + OCA Implementation**

   * Run only **Community Edition 18** with **OCA addons**.
   * No Enterprise addons installed; no Enterprise code paths enabled.

3. **No Odoo.com / IAP Upsell**

   * Remove or override all:

     * "Upgrade to Enterprise" banners
     * IAP credits, SMS, mail, and other paid connectors
     * Links that open `*.odoo.com` or Enterprise docs
   * Replace with internal or OCA links.

4. **Accurate UI State**

   * App launcher, module list, and settings:

     * Only show apps that are **installed or explicitly installable from CE/OCA**.
     * Disable / hide non-functional tiles.
   * All help/documentation links must reflect **current installed version** (stateful, not generic marketing).

5. **InsightPulse-branded Routing**

   * All environments accessible via:

     * `https://erp.insightpulseai.net` (primary)
     * Additional sub-domains if needed: `https://docs.insightpulseai.net/erp`, etc.
   * No outbound links that confuse users into thinking odoo.com is the provider.

### 2.2 Non-Goals (MVP)

* Full HR/payroll suite (only basic employee references needed for approvals).
* Advanced fleet/maintenance workflows beyond simple equipment upkeep.
* Multi-company consolidations beyond a single PH entity (can be added later).
* Deep Spectra / external ERP integration (abstract in design; implement later).

---

## 3. Personas & Key Use Cases

### 3.1 Personas

1. **Employee / Talent**

   * Creates expense reports and travel requests.
   * Books equipment (camera, lights, laptops, etc.) for projects.

2. **Approver / Line Manager**

   * Reviews & approves expenses and travel.
   * Approves equipment bookings & incident reports.

3. **Finance Officer**

   * Validates expenses & GL postings.
   * Monitors reimbursements, vendor payments, and budgets.

4. **Equipment Manager / Studio Tech**

   * Manages asset catalog and serials.
   * Tracks check-in/out, damage, and maintenance.

5. **System Admin**

   * Manages Odoo CE/OCA modules, user roles, and branding.
   * Ensures there are **no Enterprise/IAP leaks**.

---

## 4. MVP Feature Scope

### 4.1 Expense & Travel (SAP Concur Equivalent – MVP)

**Core Modules (CE/OCA candidates)**
*(exact technical module list to be finalized in design, but must be CE/OCA only)*

* `hr_expense` (community) or OCA equivalent (`hr-expense` family).
* `account`, `account_payment`, `purchase` (CE).
* OCA enhancements (examples): `account-financial-tools`, `account-fiscal-rule`, `mis-builder` (optional later).

**MVP User Flows**

1. **Capture Expense**

   * Employee creates expense entry:

     * Type (meal, flight, hotel, ride, per diem, misc).
     * Amount, currency (PHP primary).
     * Date, attachment (receipt image or PDF).
     * Project / job code.
   * Expenses can be grouped into a **report**.

2. **Submit & Approve Expense Report**

   * Workflow states: Draft → Submitted → Manager Approved → Finance Approved → Posted → Reimbursed.
   * At each step:

     * Role-based access & approvals.
     * Comments and change log.

3. **Travel Request**

   * Simple form:

     * Destination, dates, purpose, estimated budget, cost center.
   * Approval workflow:

     * Employee → Manager → Finance (optional).
   * Once approved:

     * Travel request can be linked to actual expenses.

4. **Reimbursement & Posting**

   * Approved reports generate accounting entries:

     * Debit expense account, credit employee payable.
   * Finance can mark as paid/reimbursed with reference to payment method.

5. **Reporting (MVP)**

   * Basic dashboards:

     * Expenses by category, by project, by employee, by month.
   * Export to CSV/Excel for TBWA finance workflows.

### 4.2 Equipment Management (Cheqroom Equivalent – MVP)

**Core Modules (CE/OCA candidates)**

* Base: `stock`, `product`, `maintenance`.
* OCA addons for asset/equipment if available (e.g. `stock-logistics-warehouse`, `maintenance` extras, or custom `ipai_equipment` module).

**MVP User Flows**

1. **Equipment Catalog**

   * Model: category → asset (e.g., "Camera" → "Sony A7S III – Body 001").
   * Attributes: serial number, condition, storage location, tags (studio, field, etc.).
   * Link to images and manuals (stored on InsightPulse).

2. **Reservation & Booking**

   * Employee or Equipment Manager creates a **booking**:

     * Equipment item(s)
     * Start/end datetime
     * Project / shoot / client reference
   * Checks for conflicts (no double bookings).

3. **Check-out / Check-in**

   * Status changes:

     * Available → Reserved → Checked-out → Returned → In maintenance.
   * Capture:

     * Borrower, timestamps, condition on return, notes.

4. **Incidents & Maintenance**

   * Report damage or issues linked to equipment & booking.
   * Optional maintenance ticket opened under `maintenance` module.

5. **Reporting (MVP)**

   * Utilization per asset and category.
   * Overdue equipment and upcoming bookings.
   * Incident rates (damage/loss).

---

## 5. Odoo CE/OCA Only – Hard Constraints

### 5.1 No Enterprise Modules

* **Must not install** Enterprise addons or load Enterprise code paths.
* CI guardrail:

  * Script that scans `addons/` and installed modules:

    * Fails build if module name matches Enterprise known list.
* Odoo config:

  * `server_wide_modules` and `addons_path` must point only to:

    * CE addons
    * OCA addons
    * InsightPulse custom addons (`ipai_*`).

### 5.2 No IAP / Upsell / odoo.com Touchpoints

**Requirements:**

1. **Disable or Remove IAP Modules**

   * Uninstall or never install `iap_*`, `mail_*_iap`, or related connectors.
   * If technical dependencies require IAP stubs, they must be **no-op and invisible** to end users.

2. **Suppress Upgrade Banners**

   * Override views to hide "Upgrade to Enterprise" sections in:

     * App list
     * Settings pages
     * Kanban views or systray menus.

3. **Block odoo.com Links**

   * Any `href` or redirect to `*.odoo.com` must be:

     * Removed, or
     * Repointed to `https://docs.insightpulseai.net/erp` or specific OCA docs.

4. **No IAP Price / Credit Screens**

   * Any UI related to credits (SMS/email/other IAP) must be removed or replaced with InsightPulse self-hosted service equivalents only if implemented.

### 5.3 Accurate State in Views

* App launcher, menu items, and settings must:

  * Show **installed modules** as active.
  * Hide or grey-out modules that are not available in CE/OCA.
* For each custom module (`ipai_expense`, `ipai_equipment`, etc.):

  * Provide **settings page** that shows:

    * Installed version
    * Last upgrade date
    * Required dependencies.

---

## 6. Routing & Branding Requirements

1. **Domains**

   * Production ERP: `https://erp.insightpulseai.net`
   * Optional:

     * Docs: `https://docs.insightpulseai.net/erp`
     * API: `https://api.insightpulseai.net/erp` (if exposed later).

2. **Branding**

   * InsightPulse logo & name in:

     * Main navbar
     * Login screen
     * About dialog.
   * No Odoo Enterprise logos or marketing text.

3. **Help & Docs Links**

   * Replace "Documentation" / "Support" menu items with:

     * `docs.insightpulseai.net/erp/expense`
     * `docs.insightpulseai.net/erp/equipment`
     * or direct OCA docs pages for modules in use.

---

## 7. Architecture Overview (MVP)

**High Level**

* **Frontend / Web**: Odoo CE 18 web client.
* **Backend**: Odoo CE server + OCA addons.
* **Database**: PostgreSQL (single instance for MVP).
* **Auth**: Odoo internal auth; SSO integration later.
* **Deployment**: Docker / docker-compose or k8s (per infra repo).

**Key Components**

* `ipai_expense` module:

  * Extends `hr_expense` + `account`.
  * Adds PH categories, project fields, travel requests, and Concur-style flow.

* `ipai_equipment` module:

  * Extends `stock` + `maintenance` to behave like Cheqroom.
  * Adds booking, calendar view, incident tracking.

* `ipai_ce_cleaner` (optional module):

  * Centralises **Enterprise/IAP removal overrides**:

    * XML view overrides.
    * Menu pruning.
    * URL rewriting.

---

## 8. Data Model (MVP Highlights)

### 8.1 Expense / Travel

* `hr.expense`

  * `employee_id`, `date`, `amount`, `currency_id`, `expense_type`, `project_id`, `attachment_ids`.
* `hr.expense.report`

  * `line_ids` (many2many to `hr.expense`), `state`, `approver_id`, `finance_approver_id`.
* `ipai.travel.request`

  * `employee_id`, `destination`, `start_date`, `end_date`, `purpose`, `budget_amount`, `state`.

### 8.2 Equipment

* `ipai.equipment.asset`

  * `name`, `category_id`, `serial_number`, `location_id`, `condition`, `image`, `status`.
* `ipai.equipment.booking`

  * `asset_id`, `borrower_id`, `project_id`, `start_datetime`, `end_datetime`, `state`.
* `ipai.equipment.incident`

  * `booking_id`, `asset_id`, `reported_by`, `severity`, `description`, `status`.

---

## 9. Security & Permissions

* **Employee**

  * Create/edit own expenses, travel requests, and bookings.
* **Manager**

  * Approve expenses, travel, bookings for their team.
* **Finance**

  * Approve & post expenses; access all finance reports.
* **Equipment Manager**

  * Full access to equipment catalog, bookings, and incidents.
* **Admin**

  * Install modules, manage users, manage branding & link targets.

All new models must define explicit access rules and record rules; no model should default to global read/write without review.

---

## 10. Telemetry, Observability & Quality

MVP minimum:

* Error logs accessible via `docker logs` / centralized logging.
* Basic metrics (if available):

  * Number of expense reports per month.
  * Number of active equipment bookings.

CI checks:

* Linting for Python and XML.
* OCA `pre-commit` hooks where possible.
* Enterprise/IAP detector script.

---

## 11. Milestones (MVP)

1. **M1 – CE/OCA Base Stack**

   * Odoo CE 18 running at `erp.insightpulseai.net`.
   * OCA repos mounted.
   * Enterprise/IAP guardrails in place.

2. **M2 – Expense MVP**

   * `ipai_expense` module installed.
   * Expense & travel flows working end-to-end.
   * Basic reports available.

3. **M3 – Equipment MVP**

   * `ipai_equipment` module installed.
   * Equipment catalog & booking flows working.
   * Basic utilization reports.

4. **M4 – Branding & Link Cleanup**

   * All odoo.com/IAP links removed or replaced.
   * All visible apps reflect actual state.

5. **M5 – UAT & Production Cutover**

   * Pilot users validate flows.
   * Go/no-go decision and production enablement.

---

## 12. Risks & Mitigations

* **Risk:** Hidden Enterprise dependencies in some OCA modules.
  **Mitigation:** Carefully audit module manifests and dependencies; CI script fails hard if Enterprise module named.

* **Risk:** Missed odoo.com links in nested views.
  **Mitigation:** Search across codebase for `odoo.com`, `iap_`, and Enterprise markers; maintain `ipai_ce_cleaner` overrides.

* **Risk:** Performance issues with equipment bookings at scale.
  **Mitigation:** Start with indexed models; stress-test with sample data and adjust.

---

## 13. Acceptance Criteria (MVP)

1. No Enterprise addon is installed or required for the system to run.
2. No screen displays "Upgrade to Enterprise" or any IAP pricing/credit text.
3. No link or redirect points to `*.odoo.com`.
4. Expense & travel workflows complete from creation → approval → posting.
5. Equipment booking workflows complete from reservation → checkout → check-in.
6. App launcher and settings show only real, functioning modules.
7. Everything is reachable via `erp.insightpulseai.net` and branded as InsightPulse.

---

You can now wire this into your Spec-Kit bundle (e.g. reference from `spec.md` and generate `plan.md`/`tasks.md` from the milestones and acceptance criteria above).
