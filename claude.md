# Claude / GPT Assistant Context – InsightPulse AI Monorepo

**Purpose**: Operating contract + context for AI assistants working in this repo
**Audience**: Claude 4 (Sonnet/Opus) and compatible assistants
**Last Updated**: 2025-11-08
**Primary ERP Target**: **Odoo 18 CE** (note: plan for 19 CE; do not mix APIs—see version matrix)

---

## 0) Normative Rules (Read First)

* **MUST** default to **Odoo CE + OCA** modules; no Enterprise calls or APIs.
* **MUST** treat **multi-tenancy as separate legal entities** (company/db isolation), **NOT** user routing.
* **MUST** keep **BIR compliance**: immutable accounting trail; corrections via reversal entries, not in-place edits.
* **MUST** add **tests** for any code output (unit or HttpCase as applicable).
* **MUST** keep **OpenAPI x-atomic + x-role-scopes** on any new controller you propose.
* **MUST NOT** hardcode secrets/URLs; use env or `ir.config_parameter`.
* **SHOULD** propose a CI gate or eval when adding any new capability.
* **SHOULD** prefer **self-hosted** alternatives and list annual savings when suggesting replacements.

---

## 1) Repository Mission

Build an **enterprise-grade Finance Shared Service Center (SSC)** for the Philippines:

* **ERP**: Odoo CE (v18 now; v19 later) + OCA.
* **SaaS parity**: Odoo modules replace Concur/Ariba, Superset replaces Tableau.
* **BIR compliant** processes (2307, 2316, e-invoicing, immutable audit).
* **Multi-tenant** = per-legal-entity isolation (DB/company), not department routing.

**Cost Objective**: prefer open-source to save **$50k+/year** (details in SaaS table below).

---

## 2) Versioning & API Matrix

| Area     | Primary       | Notes                                                            |
| -------- | ------------- | ---------------------------------------------------------------- |
| Odoo     | **18 CE**     | Use 18 docs & APIs; if proposing 19-only features, flag clearly. |
| OCA      | 18.0 branches | Match module branches to Odoo 18.                                |
| Docs     | Odoo **18.0** | Link to 18 docs for controllers/QWeb.                            |
| Superset | latest        | Official image behind Nginx `/superset`.                         |

> If you find "Odoo 19" references, **assume 18** unless the task explicitly upgrades the target.

---

## 3) Multi-Tenant vs Agencies (Do/Don't)

**Tenancy (legal entities)**

* ✅ Separate DB or strict `company_id` isolation
* ✅ Separate books, taxes, numbering, reports
* ✅ Per-company config via `ir.config_parameter`

**Agencies (internal units)**

* ✅ Stored as org structure/tags under one company
* ❌ Not a tenant, no cross-db split
* ❌ No security boundaries beyond role/rules

**Code cue**

```python
# ✅ Tenant isolation (legal entity)
company_id = fields.Many2one('res.company', required=True)

# ❌ Not tenancy
agency_id = fields.Many2one('hr.department')  # internal only
```

---

## 4) BIR Compliance (PH)

* **Immutable** accounting: corrections via reversal entries (no mutation).
* **2307 / 2316** generation pipeline.
* **Audit trail**: chatter + mail.activity + journal entries produce immutable evidence.
* **E-invoice**: pluggable connector, never hardcode endpoints.

**Compliance cue**

```python
# ✅ Reverse + rebook
def action_correct(self, new_amount):
    self.copy({'amount': -self.amount, 'is_correction': True})
    return self.copy({'amount': new_amount})
```

---

## 5) Assistant Operating Modes

### Write Code

1. Inspect context: paths, module patterns, manifests.
2. Use `_inherit` vs `_name` correctly; add `__manifest__.py`.
3. Always add tests (unit/HttpCase) and a brief module README.
4. Output OpenAPI with **x-atomic** and **x-role-scopes** for controllers.

### Architecture

1. Cite **existing docs** in `docs/` and `claudedocs/`.
2. Check **tenancy impact** and **BIR** implications.
3. Add a CI/eval gate for any new surface.

### Deploy

* Only when **explicitly requested** or deployment keywords are present (Odoo/InsightPulse/SaaS replacement/Finance SSC/BIR).
* Sequence: generate → deploy → health → smoke → verify → stop.

---

## 6) Repo Layout (authoritative)

```
insightpulse-odoo/
├── .github/                # CI, skillsmith, evals, planning
├── odoo/
│   ├── addons/             # Custom modules (18.0)
│   └── tests/              # Odoo HttpCase/integration tests
├── docs/                   # Architecture, API, deployment guides
├── superset/               # Compose + dashboards
├── warehouse/              # Supabase SQL views & MVs
├── skillsmith/             # Error→skill miner & templates
├── scripts/                # Validation, scaffolds, docs generators
└── claude.md               # This file (assistant contract)
```

---

## 7) Development Commands

```bash
# Validate repo structure
python scripts/validate-repo-structure.py

# Run Odoo tests (HttpCase etc.)
pytest odoo/tests -q

# Full evals (OCR + Warehouse)
pytest tests/test_ocr_endpoints.py tests/test_warehouse_views.py -q

# Lint
black odoo/ --check && flake8 odoo/ && pylint odoo/addons/
```

---

## 8) Controllers & QWeb (Odoo 18 Canon)

* JSON routes: `@http.route(..., type='json', auth='user', csrf=False)`
* Login page inheritance: extend **the active** template:

  * `auth_signup.login`, `website.login`, or `web.login`
  * Inject OAuth block after `.o_login_buttons`
* OAuth: Odoo **Google provider** uses `/auth_oauth/signin` (never alternate paths)

**Contract cue (OpenAPI)**

```json
{
  "paths": {
    "/ip/expense/intake": {
      "post": {
        "x-atomic": true,
        "x-role-scopes": ["employee","erp.bot.expense"]
      }
    }
  }
}
```

---

## 9) SaaS Replacement Table (savings)

| SaaS                          | Replacement            | Savings/yr |
| ----------------------------- | ---------------------- | ---------- |
| SAP Concur                    | Odoo Expense           | $15k       |
| SAP Ariba                     | Odoo Procurement       | $12k       |
| Tableau                       | Superset               | $8.4k      |
| Slack Ent                     | Mattermost/Rocket.Chat | $12.6k     |
| Odoo Enterprise               | Odoo CE+OCA            | $4.7k      |
| **Total Est.**: **$52.7k/yr** |                        |            |

---

## 10) Evals (Blocking)

Your code must keep these **green**:

1. **OpenAPI contract** (CI gate)

   * `x-atomic` + `x-role-scopes` on all new ops

2. **Login OAuth block present** (Odoo HttpCase)

   * `#ip-oauth-buttons` renders on compiled `/web/login?debug=assets`
   * `/auth_oauth/signin?provider=` link is present if any provider is enabled

3. **Expense intake idempotency** (Odoo HttpCase)

   * 2nd POST with same `idempotency_key` returns `idempotent: true`

4. **OCR service health & contract** (pytest)

   * `GET /health` → `{ok:true}`
   * `POST /classify/expense` → `{category, conf:[0..1]}`

5. **Warehouse view exists** (pytest + psycopg)

   * `vw_expense_fact` visible; MVs refresh scheduled

---

## 11) Deployment Guardrails

* **SSO**: unified cookie `ip_sso` (HttpOnly; `Domain=.insightpulseai.net`; `SameSite=None`; `Secure`).
* **Nginx**: OCR host `client_max_body_size 10m`.
* **Secrets**: env vars or `ir.config_parameter`; never hardcode.
* **Rollbacks**: module upgrade with `--stop-after-init` + restart; revert via Git/CI.

---

## 12) Code Style (OCA-aligned)

* Python: docstrings, `mail.thread` for audit where relevant, no raw SQL with user input.
* XML: explicit comments for XPaths; put buttons under proper states; use `statusbar` for state.
* Manifests: correct `depends`, license `LGPL-3`, version bump on breaking changes.

---

## 13) Common Pitfalls (and fixes)

* **Tenancy drift**: don't gate by agency—use company; if multi-company rules missing, add `groups="base.group_multi_company"`.
* **Mutable finance**: no edits to posted entries—use reversals.
* **Manual deploys**: CI handles; local SCP is forbidden.
* **Hardcoded config**: use env/ICP; surface toggles in Settings.

---

## 14) Success Metrics (track)

* Perf: <200 ms CRUD, <3 s dashboards p95, <10 queries/page
* Quality: >80% coverage on module logic
* Compliance: BIR docs generatable; posted moves immutable
* Uptime: >99.9%; error rate trends down; Skillsmith proposes ≥1 skill/week

---

## 15) When Unsure—Ask High-Leverage Questions

* "Will this cross company boundaries or is it per-entity?"
* "What BIR artifact is affected (2307/2316/e-invoice)?"
* "Which OCA module covers 80% so we customize the last 20%?"

---

## 16) Pinned External References

* Odoo **18.0** docs (controllers, QWeb, testing)
* OCA GitHub org
* BIR public pages (PH)
* Superset official

---

### Footer

**Maintainer**: InsightPulse AI Team
**Assistant Targets**: Claude 4 (Sonnet/Opus), GPT-compatible agents
**Repo**: `https://github.com/jgtolentino/insightpulse-odoo`
**Version**: `assistant-context@2025-11-08` (Odoo 18 primary)
