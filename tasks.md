# Tasks – InsightPulse Odoo CE

Status: Draft checklist aligned with plan.md

---

## Phase 0 – Repo & CI Skeleton

- [x] Create base directories: `addons/`, `oca/`, `deploy/`, `.github/workflows/`.
- [ ] Add `spec.md`, `plan.md`, `tasks.md` to root.
- [ ] Add `README.md` with high-level description and constraints.
- [ ] Add `.gitignore` tuned for Odoo / Python / Docker.
- [ ] Implement CI guardrail job:
  - [ ] Fail on Enterprise module references.
  - [ ] Fail on `odoo.com` links in templates/code.
- [ ] Wire CI to run on `push` and `pull_request`.

---

## Phase 1 – CE/OCA Base Stack

- [ ] Create `deploy/docker-compose.yml` with:
  - [ ] Odoo CE 18 service.
  - [ ] PostgreSQL service.
  - [ ] Volumes for `addons/` and `oca/`.
- [ ] Add `deploy/odoo.conf` with correct `addons_path` and `dbfilter`.
- [ ] Add `deploy/nginx.conf` (or equivalent) for `erp.insightpulseai.net`.
- [ ] Set up SSL (Let's Encrypt or DO-managed cert).
- [ ] Smoke test Odoo CE:
  - [ ] Login works.
  - [ ] No Enterprise modules visible or installable.

---

## Phase 2 – Expense MVP (`ipai_expense`)

- [ ] Add necessary OCA repos as git submodules (e.g. `oca/account-financial-tools`, `oca/hr`).
- [ ] Scaffold `addons/ipai_expense`:
  - [ ] `__manifest__.py` with CE/OCA dependencies only.
  - [ ] Models for PH expense categories and travel requests.
  - [ ] Views: form, tree, and kanban for expenses and reports.
  - [ ] Security: access and record rules.
- [ ] Implement workflow: Draft → Submitted → Manager Approved → Finance Approved → Posted → Reimbursed.
- [ ] Add demo data for:
  - [ ] Employees.
  - [ ] Expense categories.
  - [ ] Travel requests.
- [ ] Verify posting and basic reporting.

---

## Phase 3 – Equipment MVP (`ipai_equipment`)

- [ ] Add/mount OCA stock/maintenance repos.
- [ ] Scaffold `addons/ipai_equipment`:
  - [ ] `__manifest__.py`.
  - [ ] Models: asset, booking, incident.
  - [ ] Views: catalog, bookings calendar, incident reports.
  - [ ] Security rules.
- [ ] Implement booking conflict checks.
- [ ] Implement check-out/check-in flow.
- [ ] Add demo data for:
  - [ ] Equipment items.
  - [ ] Sample bookings.
- [ ] Validate utilization and overdue reports.

---

## Phase 4 – CE Cleaner & Branding (`ipai_ce_cleaner`)

- [ ] Scaffold `addons/ipai_ce_cleaner`:
  - [ ] XML overrides to hide Enterprise banners.
  - [ ] Removal/override of IAP menus.
  - [ ] Replace `odoo.com` links with InsightPulse or OCA docs.
- [ ] Add InsightPulse logo and color scheme to login/nav.
- [ ] Extend CI guardrails to:
  - [ ] Scan for `odoo.com`.
  - [ ] Scan for known Enterprise modules and IAP strings.
- [ ] Manually verify:
  - [ ] No visible "Upgrade to Enterprise" anywhere.
  - [ ] No IAP UI flows exposed.

---

## Phase 5 – UAT & Production Cutover

- [ ] Create UAT DB and seed with sample data.
- [ ] Invite pilot users and collect feedback.
- [ ] Fix critical issues discovered during UAT.
- [ ] Document:
  - [ ] Admin runbook.
  - [ ] User quick-start guides.
- [ ] Create production DB and point `erp.insightpulseai.net` at it.
- [ ] Final sign-off on MVP readiness.
