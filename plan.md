# Implementation Plan – InsightPulse Odoo CE

Status: Draft v0.1
Aligned PRD: specs/002-odoo-expense-equipment-mvp.prd.md

---

## Phase 0 – Repo & CI Skeleton

**Goal:** Make `odoo-ce` safe to extend: clean structure + basic guardrails.

- Create base folder layout:
  - `addons/ipai_expense/`
  - `addons/ipai_equipment/`
  - `addons/ipai_ce_cleaner/`
  - `oca/` (OCA addons via submodules or git sparse checkout)
  - `deploy/` (docker-compose, k8s manifests, nginx configs)
  - `.github/workflows/` (CI pipelines)
- Add CI guardrails:
  - Fail build on Enterprise modules.
  - Fail build on `odoo.com` links in user-facing code.
- Add coding standards + pre-commit baseline.

**Exit criteria:**

- CI runs on every push/PR.
- Any Enterprise/IAP/odoo.com artifact causes a red build.

---

## Phase 1 – CE/OCA Base Stack (M1 in PRD)

**Goal:** Odoo CE 18 running with OCA base repos wired; no Enterprise modules.

- Provision target runtime:
  - Docker Compose or K8s (DigitalOcean/DOKS acceptable).
- Add `deploy/docker-compose.yml`:
  - Odoo CE 18 container.
  - PostgreSQL container.
  - Volume mounts for `addons/` and `oca/`.
- Add `deploy/odoo.conf`:
  - `addons_path` including `addons/` and `oca/`.
  - `dbfilter` for the intended DB(s).
  - Logging config.
- Configure Nginx reverse proxy:
  - `erp.insightpulseai.net` → Odoo container.
  - Let's Encrypt SSL via certbot or managed certificate.

**Exit criteria:**

- Odoo CE 18 admin reachable via `https://erp.insightpulseai.net/web`.
- No Enterprise modules present in `addons_path` or installed.

---

## Phase 2 – Expense MVP (`ipai_expense`) – (M2 in PRD)

**Goal:** SAP Concur–style expense + travel flows working using CE/OCA.

- Select and mount OCA repos:
  - Accounting / hr_expense enhancements as needed.
- Implement `addons/ipai_expense`:
  - Extended models for PH expense categories and travel requests.
  - Approval workflow: employee → manager → finance.
  - Basic reports (by category, employee, project).
- Add demo data for a few employees, projects, and categories.

**Exit criteria:**

- Expense and travel workflows complete end-to-end.
- Posting to accounting works using CE accounting modules only.

---

## Phase 3 – Equipment MVP (`ipai_equipment`) – (M3 in PRD)

**Goal:** Cheqroom-style equipment booking flows.

- Mount relevant OCA stock/maintenance repos.
- Implement `addons/ipai_equipment`:
  - Equipment asset model and booking model.
  - Booking conflict checks.
  - Check-out / Check-in, incident reporting.
- Calendar and list views for bookings.

**Exit criteria:**

- Bookings can be created, approved, checked out, and returned.
- Utilization and overdue reports available.

---

## Phase 4 – CE Cleaner & Branding (`ipai_ce_cleaner`) – (M4 in PRD)

**Goal:** Remove Enterprise/IAP/UI noise and enforce InsightPulse branding.

- Implement `addons/ipai_ce_cleaner`:
  - XML overrides to hide "Upgrade to Enterprise" banners.
  - Remove or relink any IAP/odoo.com menus.
  - Add InsightPulse branding to login, navbar, and About.
- Implement additional CI checks:
  - Search for `odoo.com` and known Enterprise markers.
- Wire help links to InsightPulse docs:
  - `docs.insightpulseai.net/erp/expense`
  - `docs.insightpulseai.net/erp/equipment`

**Exit criteria:**

- No visible Enterprise/IAP artifacts in UI.
- Branding consistent with InsightPulse.

---

## Phase 5 – UAT & Production Cutover (M5 in PRD)

**Goal:** Validate with real workflows and declare production-ready.

- Create a "UAT" database with realistic sample data.
- Onboard a small group of users:
  - Employees, managers, finance, equipment manager.
- Collect feedback and issues; fix critical blockers.
- Document:
  - Admin runbook (backup, restore, upgrades).
  - User quick-start for expenses and bookings.

**Exit criteria:**

- UAT sign-off for both Expense and Equipment modules.
- Production database created and connected to `erp.insightpulseai.net`.
