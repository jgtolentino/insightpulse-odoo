# PRD — Smart Delta Engine

**Enterprise Docs → Odoo CE/OCA 18 SaaS Parity System**

## 1. Purpose

Build a production-grade system that **ingests enterprise SaaS documentation (SAP, Notion, Databricks-class)** and converts it into:

* A normalized **capability catalog**
* A deterministic **parity map** to Odoo CE 18 + OCA 18
* An **executable implementation plan** (modules, configs, automations)
* A repeatable **docs-to-code workflow** for ERP SaaS parity

This enables **systematic replacement or parity of enterprise SaaS** using Odoo CE/OCA with minimal custom code.

---

## 2. Goals

### Primary

* Achieve **feature-level parity mapping** from enterprise SaaS → Odoo CE/OCA
* Enforce **Smart Delta rules** automatically
* Produce **Spec-Kit artifacts** ready for CI/CD and agent execution

### Secondary

* Track coverage, gaps, and deltas across vendors
* Enable roadmap-driven OCA contribution requests
* Support multi-tenant ERP SaaS planning

---

## 3. Non-Goals

* No UI builder (CLI + artifacts only)
* No monolithic "super module"
* No deep vendor API re-implementation unless unavoidable

---

## 4. Users

| Persona              | Needs                             |
| -------------------- | --------------------------------- |
| ERP Architect        | Parity confidence, gap visibility |
| Odoo Tech Lead       | Exact modules, install order      |
| Automation Engineer  | n8n hooks, workflows              |
| Product Owner        | Roadmap, gap severity             |
| Agent (Claude/Codex) | Deterministic execution plan      |

---

## 5. Inputs

### Supported Doc Sources (Recursive Crawl)

* SAP Help Portal
* Notion Product Docs
* Odoo 18 Official Docs
* Odoo Community (OCA) Docs
* OCA Feature Request Registry

Each page is normalized into:

* Capability
* Sub-capability
* Configuration surface
* Data model hints
* Automation hooks

---

## 6. Core System Components

### 6.1 Docs Crawler

* Recursive, canonical-URL based
* Stable node IDs
* Leaf-level extraction only
* Deduplication enforced

**Output:** Capability Tree (JSON)

---

### 6.2 Capability Normalizer

Maps raw docs → normalized enterprise capabilities:

Example:

```
Enterprise: Budget Control → Commitments → Forecast Lock
```

---

### 6.3 Parity Mapper (Core Engine)

For each capability:

| Field          | Description                      |
| -------------- | -------------------------------- |
| enterprise_ref | Source doc IDs                   |
| odoo_core      | Native CE modules                |
| oca            | Repo + module                    |
| alt_stack      | Supabase / n8n / OSS             |
| gap_level      | 0–3                              |
| smart_delta    | Config / OCA / Custom / External |

**Gap Levels**

* 0 = Native parity
* 1 = OCA exists
* 2 = Minimal custom module
* 3 = External service

---

### 6.4 Smart Delta Decision Engine

Hard rules:

1. **Config beats code**
2. **OCA beats custom**
3. **Custom only if reusable**
4. **External only if ERP-unsafe**

Violations are rejected.

---

### 6.5 Spec-Kit Generator

Auto-generates:

```
spec/smart-delta-engine/
├── constitution.md
├── prd.md
├── plan.md
└── tasks.md
```

All files are **machine-readable and CI-validated**.

---

## 7. Functional Requirements

### FR-1: Full Capability Coverage

* 100% of crawled leaf nodes mapped or marked "out of scope"

### FR-2: Deterministic Output

* Same input → same parity result

### FR-3: Odoo-First Resolution

* Every capability must resolve to:

  * Odoo Core OR
  * OCA OR
  * Minimal Custom OR
  * External (explicit justification)

### FR-4: Automation Hooks

* Each capability includes:

  * Config steps
  * n8n workflow references
  * CI validation checks

---

## 8. Data Model (Logical)

```yaml
Capability:
  id
  name
  domain
  enterprise_sources[]
  odoo_core_modules[]
  oca_modules[]
  alt_components[]
  gap_level
  smart_delta_choice
  implementation_notes
```

---

## 9. Automation & CI/CD

### CI Gates

* No custom module without gap_level >= 2
* No external dependency without justification
* No missing OCA reference for gap_level 1

### n8n

* Doc crawl scheduling
* Parity diff alerts
* OCA request auto-drafting

---

## 10. Security & Governance

* Read-only crawl
* No credential scraping
* All outputs version-controlled
* Deterministic agent execution only

---

## 11. Success Metrics

* % enterprise capabilities mapped
* % parity achieved without custom code
* Reduction in enterprise SaaS dependencies
* Time-to-parity per module

---

## 12. Risks & Mitigations

| Risk                | Mitigation                |
| ------------------- | ------------------------- |
| Doc structure drift | Canonical URL enforcement |
| Over-customization  | Smart Delta hard gates    |
| OCA gaps            | Auto OCA request drafts   |

---

## 13. Next Execution Steps

1. Lock capability taxonomy
2. Run full crawl (SAP → Notion → Odoo/OCA)
3. Generate parity map
4. Produce Spec-Kit bundle
5. Execute via Claude Code / Codex CLI
