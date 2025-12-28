# Constitution — Smart Delta Engine

> Governing principles for enterprise-to-Odoo parity mapping and implementation decisions.

## Purpose

The Smart Delta Engine ensures systematic, disciplined replacement of enterprise SaaS with Odoo CE/OCA, minimizing custom code while maximizing maintainability and upgrade safety.

---

## Core Principles

### 1. Smart Delta Hierarchy

**Always prefer the simplest, most maintainable solution.**

| Priority | Choice      | Description                           |
|----------|-------------|---------------------------------------|
| 1 (Best) | Config      | Native Odoo configuration only        |
| 2        | OCA         | Existing OCA module                   |
| 3        | Custom      | Minimal custom module (reusable)      |
| 4 (Last) | External    | External service (ERP-unsafe ops)     |

**Rationale**: Custom code creates upgrade debt. OCA modules are community-maintained. Config is zero-code.

### 2. Odoo-First Principle

**Every capability MUST resolve to Odoo before considering alternatives.**

Resolution order:
1. Can Odoo Core do this? → Use config
2. Does OCA have this? → Use OCA module
3. Is custom code reusable? → Minimal custom module
4. Is the operation ERP-unsafe? → External service only

### 3. No Tribal Knowledge

**All decisions must be documented and machine-readable.**

- Every capability has explicit gap_level
- Every choice has justification
- Every custom module has OCA contribution path

### 4. Deterministic Outputs

**Same inputs MUST produce same outputs.**

- Canonical URL enforcement
- Stable node IDs
- Reproducible parity maps
- Hash-validated artifacts

### 5. Evidence-Based Gaps

**Gap levels must be verifiable.**

| Gap Level | Meaning           | Evidence Required                |
|-----------|-------------------|----------------------------------|
| 0         | Native parity     | Odoo docs reference              |
| 1         | OCA exists        | OCA repo + module reference      |
| 2         | Minimal custom    | Justification + reuse potential  |
| 3         | External service  | ERP-unsafe justification         |

---

## Non-Negotiables

### 1. No Phantom Custom Modules

```yaml
rule: no_phantom_custom
description: Custom modules MUST NOT be created without gap_level >= 2
enforcement: hard_block
rationale: Prevent unnecessary customization
```

### 2. OCA Reference Required

```yaml
rule: oca_ref_required
description: Gap level 1 MUST include OCA repo + module reference
enforcement: hard_block
rationale: Ensure OCA is actually available
```

### 3. External Justification Required

```yaml
rule: external_justification
description: Gap level 3 MUST include explicit ERP-unsafe justification
enforcement: hard_block
rationale: External services are last resort
```

### 4. Deterministic Hash

```yaml
rule: deterministic_output
description: Parity output MUST produce consistent hash for same input
enforcement: ci_check
rationale: Reproducibility is mandatory
```

### 5. No Write-Back from External

```yaml
rule: no_external_writeback
description: External services MUST NOT write back to Odoo
enforcement: hard_block
rationale: Maintain Odoo as source of truth
```

---

## Decision Matrix

### When to Use Config (Gap 0)

```
IF capability IN odoo_core_modules:
    IF requires_only_settings_changes:
        USE Config
        GAP_LEVEL = 0
```

### When to Use OCA (Gap 1)

```
IF capability NOT IN odoo_core_modules:
    IF oca_module_exists(capability):
        USE OCA module
        GAP_LEVEL = 1
        REQUIRE oca_repo + oca_module reference
```

### When to Use Custom (Gap 2)

```
IF capability NOT IN odoo_core_modules:
    IF NOT oca_module_exists(capability):
        IF is_reusable(capability):
            USE Minimal Custom
            GAP_LEVEL = 2
            REQUIRE justification + OCA contribution path
```

### When to Use External (Gap 3)

```
IF operation IS erp_unsafe:
    # Examples: ML inference, heavy analytics, real-time streaming
    USE External service
    GAP_LEVEL = 3
    REQUIRE erp_unsafe justification
    ENFORCE read_only from Odoo
```

---

## Scope Definition

### In Scope

| Domain    | Capabilities                                    |
|-----------|-------------------------------------------------|
| Finance   | Budgets, commitments, forecasts, approvals      |
| PPM       | Projects, resources, timesheets, milestones     |
| HR        | Employees, payroll, leaves, recruitment         |
| Ops       | Inventory, manufacturing, quality               |
| Analytics | BI dashboards, reports (read-only external OK)  |

### Out of Scope

| Area               | Reason                              |
|--------------------|-------------------------------------|
| Deep ML models     | Not ERP functionality               |
| Real-time trading  | Requires specialized systems        |
| Social media feeds | Not core business process           |

---

## Enforcement Levels

### CI/CD Gates

| Check                        | Enforcement |
|------------------------------|-------------|
| Custom without gap >= 2      | Block merge |
| Missing OCA ref for gap 1    | Block merge |
| External without justification| Block merge |
| Non-deterministic output     | Block merge |

### Advisory Checks

| Check                        | Enforcement |
|------------------------------|-------------|
| High custom code ratio       | Warning     |
| OCA module outdated          | Warning     |
| Missing implementation notes | Warning     |

---

## Success Criteria

| Metric                          | Target  | Measurement              |
|---------------------------------|---------|--------------------------|
| Capabilities mapped             | 100%    | Parity coverage scan     |
| Config-only solutions           | > 60%   | Gap level 0 count        |
| OCA solutions                   | > 30%   | Gap level 1 count        |
| Custom solutions                | < 10%   | Gap level 2 count        |
| External solutions              | < 5%    | Gap level 3 count        |
| Deterministic output hash match | 100%    | CI hash verification     |

---

## Revision History

| Version | Date       | Changes               |
|---------|------------|-----------------------|
| 1.0.0   | 2025-12-21 | Initial constitution  |
