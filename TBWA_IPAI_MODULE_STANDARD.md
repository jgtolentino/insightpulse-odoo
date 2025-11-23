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
