# InsightPulse Odoo CE – Project Spec

Repo: https://github.com/jgtolentino/odoo-ce
Owner: InsightPulseAI – ERP Platform Team
Status: Active

## 1. Overview

This repository contains the **InsightPulse Odoo CE** stack: a fully self-hosted, Odoo Community Edition + OCA–based ERP for expense management and equipment booking.

The system is designed to:

- Replace **SAP Concur** for PH-focused expense & travel workflows.
- Replace **Cheqroom** for equipment catalog, bookings, and incident tracking.
- Run **only** on Odoo Community Edition + OCA modules and custom `ipai_*` addons.
- Avoid all Odoo Enterprise codepaths, IAP services, and odoo.com upsell links.
- Serve exclusively under InsightPulse domains (e.g. `erp.insightpulseai.net`).

## 2. PRDs in This Repo

- [002 – InsightPulse ERP Expense & Equipment MVP](specs/002-odoo-expense-equipment-mvp.prd.md)

(Additional PRDs will be added under `specs/00x-*.prd.md` as the platform grows.)

## 3. In-Scope (Current Wave)

- Odoo CE 18 deployment (Docker/K8s friendly).
- OCA module integration for accounting, expense, and stock/maintenance.
- Custom modules:
  - `ipai_expense` – PH-specific expense + travel workflows.
  - `ipai_equipment` – Cheqroom-style equipment booking.
  - `ipai_ce_cleaner` – removal of Enterprise/IAP UI and odoo.com links.
- Reverse proxy and SSL termination via Nginx or equivalent.
- CI guardrails to enforce:
  - No Enterprise modules present/installed.
  - No `odoo.com` links or IAP references in templates/code.

## 4. Explicitly Out of Scope (MVP)

- Odoo Enterprise modules or licenses.
- Any use of Odoo IAP (SMS, email, or credits) in production.
- Full HR/payroll, manufacturing, or advanced warehouse flows.
- Multi-company consolidations and group reporting.

## 5. Success Criteria (MVP)

- Expense and travel workflows complete from creation → approval → posting, using CE/OCA only.
- Equipment booking lifecycle (reserve → checkout → check-in → incident) works end-to-end.
- UI does **not** display any Enterprise or IAP banners, menus, or upsells.
- Grep across the repo for `odoo.com` returns **no user-facing** links.
- `erp.insightpulseai.net` is the canonical entry point for all users.
- CI/CD fails if Enterprise/IAP traces are introduced.

## 6. Dependencies & Integrations

- PostgreSQL (single instance for MVP).
- Nginx (or equivalent) reverse proxy and SSL termination.
- Optional: centralized logging/monitoring stack (to be defined in a later PRD).

## 7. Roadmap Link

Implementation details and milestones are tracked in:

- [plan.md](plan.md) – phases and milestones.
- [tasks.md](tasks.md) – actionable task checklist.
