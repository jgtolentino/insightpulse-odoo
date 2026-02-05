# Odoo Knowledge Base - Error Prevention & Auto-Patching

**Purpose:** Prevent Odoo custom module errors before they happen and auto-fix when they do.

## Overview

This system scrapes solved Odoo forum issues, extracts fixes, and converts them into:
1. **Preventive Guardrails** - Stop errors before deployment
2. **Auto-Patches** - Fix common issues automatically
3. **Knowledge Base** - Searchable troubleshooting intelligence

## Directory Structure

```
agents/odoo-knowledge/
├── scraper/                    # Forum scraping tools
│   ├── scrape_solved_threads.py    # Main scraper (100 pages)
│   └── process_solutions.py        # Solution extractor
├── guardrails/                 # Prevention rules (YAML)
│   ├── GR-POS-001-field-sync.yaml
│   ├── GR-ACCT-002-invoice-sequence.yaml
│   ├── GR-PORTAL-003-view-inherit.yaml
│   ├── GR-INSTALL-004-manifest.yaml
│   └── GR-CUSTOM-005-field-propagation.yaml
├── autopatches/                # Auto-fix scripts (Python)
│   ├── apply_pos_export_import_fix.py
│   ├── switch_to_ir_sequence.py
│   └── fix_manifest_validation.py
└── knowledge/                  # Scraped data (JSON)
    └── (generated files)
```

## Quick Start

### 1. Scrape Odoo Forum (100 pages of solved issues)

```bash
cd agents/odoo-knowledge/scraper
python scrape_solved_threads.py
```

**Output:** `knowledge/solved_issues_raw.json` (~1,100 solved cases)

### 2. Process Solutions

```bash
python process_solutions.py
```

**Output:** `knowledge/solutions_processed.json` (categorized + code extracted)

### 3. Apply Preventive Guardrails

Guardrails prevent errors **before deployment**:

```bash
# Validate manifest before install
python autopatches/fix_manifest_validation.py ./your_module/

# Check for POS sync issues
python autopatches/apply_pos_export_import_fix.py ./your_module/

# Validate invoice numbering
python autopatches/switch_to_ir_sequence.py ./your_module/
```

## Current Guardrails (v1)

| ID | Name | Severity | Module | Auto-Fix |
|----|------|----------|--------|----------|
| **GR-POS-001** | POS Custom Field Sync | Critical | POS | ✅ Yes |
| **GR-ACCT-002** | Invoice Sequence Usage | High | Accounting | ✅ Yes |
| **GR-PORTAL-003** | Portal View Inheritance | Medium | Portal | ✅ Yes |
| **GR-INSTALL-004** | Manifest Validation | Critical | Base | ✅ Yes |
| **GR-CUSTOM-005** | Custom Field Propagation | Medium | Studio | Partial |

## Auto-Patch Usage

### Example: Fix POS Field Sync

```bash
python autopatches/apply_pos_export_import_fix.py ./my_pos_module/

# Output:
# 🔧 Applying POS export/import fix to: ./my_pos_module/
#    📝 Processing: ./my_pos_module/models/pos_order.py
#       Found custom fields: ['serial_id', 'warranty_info']
#       ✅ Patched! Backup saved to: pos_order.py.backup
```

### Example: Validate Manifest

```bash
python autopatches/fix_manifest_validation.py ./my_module/ --fix --odoo-version=18.0

# Output:
# 🔍 Validating manifest: ./my_module/__manifest__.py
#    ⚠️  Found 2 issues:
#       - Invalid version format: '1.0' (should be like '18.0.1.0.0')
#       - Data file not found: views/missing_view.xml
# 🔧 Applying auto-fixes...
#    ✅ Fixes applied!
```

## Integration with CI/CD

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

for module in addons/*; do
    python agents/odoo-knowledge/autopatches/fix_manifest_validation.py "$module"
    if [ $? -ne 0 ]; then
        echo "❌ Manifest validation failed for $module"
        exit 1
    fi
done
```

### GitHub Action

```yaml
name: Odoo Module Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Guardrails
        run: |
          pip install playwright
          python -m playwright install chromium

          for module in addons/*; do
            python agents/odoo-knowledge/autopatches/fix_manifest_validation.py "$module"
          done
```

## Knowledge Base Stats

Current coverage (to be updated after scraping):

- **Total solved cases:** ~1,100+ (target)
- **Modules covered:** POS, Accounting, Portal, Website, Inventory, Studio
- **Error types:** Manifest, Views, Sync, Sequences, Custom Fields
- **Auto-fixable:** ~60% of common errors

## Roadmap

### Phase 1 (Current)
- [x] Basic scraper infrastructure
- [x] 5 core guardrails
- [x] 3 auto-patches
- [ ] Run full 100-page scrape

### Phase 2 (Next 30 days)
- [ ] AI agent integration (auto-apply patches in CI)
- [ ] Expand to 20+ guardrails
- [ ] Vector search for similar errors
- [ ] Dashboard for error trends

### Phase 3 (60-90 days)
- [ ] Self-healing CI pipeline
- [ ] Predictive error detection
- [ ] Integration with Caesar AI Superior
- [ ] Auto-PR generation for fixes

## Contributing

To add a new guardrail:

1. Create YAML file in `guardrails/` following the template
2. Create corresponding auto-patch in `autopatches/`
3. Add test case
4. Document in this README

## License

MIT - Part of InsightPulse Odoo automation suite

## Contact

For questions or issues, see main project README.
