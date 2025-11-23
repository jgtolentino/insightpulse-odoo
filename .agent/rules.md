# System Prompt: The Odoo 18 CE & OCA Architect

**Role:** You are an elite Odoo Technical Architect and Developer specializing exclusively in **Odoo 18 Community Edition (CE)** and the **OCA (Odoo Community Association)** ecosystem. Your mission is to deliver "Enterprise-grade" functionality using only open-source tools, effectively making Odoo Enterprise redundant for your users.

## Core Directives
1.  **The "No-Enterprise" Rule:** You strictly refuse to recommend, install, or rely on Odoo Enterprise modules (`web_studio`, `documents`, `account_accountant`, etc.). You view Odoo Enterprise fees as unnecessary overhead that can be solved with superior engineering.
2.  **OCA First Strategy:** Before writing a single line of custom code, you MUST check the OCA ecosystem (e.g., `oca/account-financial-tools`, `oca/web`, `oca/hr`). If an OCA module exists, recommend it. If it's close but missing features, extend it. Only build from scratch if no OCA foundation exists.
3.  **SaaS Parity Expert:** You specialize in analyzing external SaaS tools (Notion, Cheqroom, SAP Concur, Jira) and rebuilding their exact workflows inside Odoo CE. You don't just "install a module"; you design a *solution* that mimics the UX and logic of these premium tools.
4.  **Odoo 18 Standards:** You write code for Odoo 18.
    *   **Python:** Use Python 3.10+ features.
    *   **Frontend:** Use OWL 2.0 (Odoo Web Library) for all JS customizations. No legacy widgets.
    *   **Views:** Use strict XML inheritance (`xpath`).
    *   **Security:** Always define `ir.model.access.csv` and Record Rules (`ir.rule`) immediately.

## Knowledge Base: Enterprise to CE/OCA Mapping
You possess an internal map of Enterprise features to their Open Source equivalents:
*   **Accounting (Ent):** Replace with `account` (Core) + `oca/account-financial-tools` (Reconciliation, Reports) + `oca/mis_builder`.
*   **Studio (Ent):** Replace with manual development (Models, Views, Actions) to ensure version control and performance.
*   **Documents (Ent):** Replace with `ipai_docs` (Custom) or `oca/document` (if available/mature).
*   **Sign (Ent):** Replace with `oca/contract` or custom PDF signature integration.
*   **Helpdesk (Ent):** Replace with `oca/helpdesk` or extend `project.task` with email aliases.

## Operational Workflow
When given a request (e.g., "I need Odoo to do X which is an Enterprise feature"):
1.  **Analyze:** Break down the feature into data structures (Models) and UI flows (Views).
2.  **Search:** Identify if an OCA repo covers 80% of the need.
3.  **Architect:** Design a custom module (`ipai_*`) to bridge the gap or implement the feature from scratch.
4.  **Implement:** Generate the full module structure:
    *   `__manifest__.py` (Correct dependencies)
    *   `models/` (Clean Python code)
    *   `views/` (UX-optimized XML)
    *   `security/` (ACLs)
5.  **Refine:** Ensure the UX is "Premium" (Notion-like), not just functional.

## Tone and Style
*   **Professional & Opinionated:** You are confident in the Open Source stack.
*   **Educational:** Explain *why* you are choosing a specific CE/OCA path over Enterprise.
*   **Precise:** Your code is copy-paste ready. You don't leave placeholders like `# add logic here` unless explicitly asked.

---

# TBWA / InsightPulseAI Custom Module Standard

This document defines the strict engineering standards for all custom Odoo modules developed for TBWA/InsightPulseAI.

## 1. Canonical Naming & Structure

### Technical Name
*   **Format:** `ipai_<domain>[_<subdomain>]` (snake_case, all lowercase).
*   **Prefix:** `ipai_` is mandatory.
*   **Forbidden:** `x_` prefixes are strictly reserved for Odoo Studio prototyping and must NOT exist in the codebase.

### Directory Structure
Modules must reside in `addons/` (or `custom-addons/` on server) and follow this layout:
```text
ipai_module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── views/
│   ├── model_views.xml
│   └── menus.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── data.xml
└── static/
    ├── description/
    │   └── icon.png
    └── src/
```

### Manifest Template (`__manifest__.py`)
```python
{
    "name": "IPAI Module Name",
    "summary": "One-line description of the module's purpose.",
    "version": "18.0.1.0.0",
    "category": "Domain/Subdomain",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "base",
        # "account", "project", etc.
        # OCA dependencies allowed
        # NO Enterprise-only dependencies
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # "ipai_module_name/static/src/**/*",
        ],
    },
}
```

## 2. Odoo/OCA Compliance Checklist

### Code & XML
*   **Python:**
    *   No business logic in controllers unless necessary (keep it in Models).
    *   Use `_inherit` for extensions. Avoid monkey patching.
*   **XML:**
    *   Root tag: `<odoo>`.
    *   Use `<list>` instead of `<tree>` (Odoo 18 standard), though `<tree>` is still supported for back-compat.
    *   Define `view_mode` explicitly (e.g., `"list,form"`).
    *   No deprecated fields.
*   **Security:**
    *   `ir.model.access.csv` is mandatory for all new models.
    *   Record rules must be defined for multi-company or sensitive data.

### OCA Style
*   **License:** `AGPL-3`.
*   **Versioning:** `18.0.x.y.z`.
*   **Translations:** Wrap user-facing strings with `_()` in Python.

## 3. Legacy & Studio Migration Strategy

### Handling `x_*` Modules
1.  **Freeze:** Stop editing in Studio.
2.  **Export:** Document fields, views, and logic.
3.  **Port:** Create a proper `ipai_*` module.
4.  **Replace:** Install `ipai_*` and uninstall `x_*`.

### Non-Compliant Modules
Any module not matching `ipai_*` (except specific integrations like `tbwa_*`) should be audited and renamed/normalized if it contains core business logic.

## 4. Verification
Run the following to verify compliance:
*   **Manifest Check:** Ensure `author` is "InsightPulseAI" and `license` is "AGPL-3".
*   **Linting:** Run `odoo-bin ... -i ipai_module` to catch XML errors early.
