# Auto-Patch Framework

Automated detection and patching of common issues across the codebase.

## Overview

The Auto-Patch framework:
1. Scans the codebase for patterns matching known issues
2. Applies automated fixes based on rules
3. Creates pull requests with the changes
4. Requires human approval before merging

## Files

- `rules.yaml` - Pattern matching rules and fixes
- `autopatch.py` - Main patching script
- `README.md` - This file

## Usage

### Preview Mode (Safe, Default)

Preview what would be patched without making changes:

```bash
make autopatch-preview
# or
python3 auto-patch/autopatch.py
```

### Apply Mode

Apply patches and create a branch:

```bash
make autopatch-apply
# or
APPLY=true python3 auto-patch/autopatch.py
```

This will:
1. Apply all matching rules
2. Create a new branch `auto-patch/update`
3. Commit changes
4. You can then push and create a PR manually or via CI

## Adding New Rules

Edit `rules.yaml`:

```yaml
- id: YOUR-ERROR-ID
  description: Brief description
  paths: ["path/to/files/**/*.py"]
  match: "pattern to find"
  fix: |
    # Describe or implement the fix
  severity: P2
  create_pr:
    title: "Fix: Your fix title"
    labels: ["auto-patch", "component"]
```

## Safety Features

- Preview mode by default (APPLY=false)
- Git branch creation for review
- Requires explicit APPLY=true to modify files
- All changes are committed for easy rollback
- Can be gated by CI/CD approval workflows

## Integration with CI/CD

Add a GitHub Actions workflow:

```yaml
name: Auto-Patch Weekly
on:
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM
  workflow_dispatch:

jobs:
  auto-patch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run auto-patch
        run: APPLY=true python3 auto-patch/autopatch.py
      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          title: 'chore(auto-patch): Apply automated fixes'
          labels: auto-patch, automated
          reviewers: ops-team
```

## Examples

### Example 1: Fix Missing Xpath in Odoo Views

```yaml
- id: ODOO-VIEW-XPATH-ERROR
  description: Fix missing xpath for inherited view
  paths: ["addons/**/views/*.xml"]
  match: '<xpath expr="//field[@name='
  fix: |
    Add position attribute to xpath
```

### Example 2: Add Missing Docstrings

```yaml
- id: PYTHON-MISSING-DOCSTRING
  description: Add docstrings to public methods
  paths: ["**/*.py"]
  match: "def [a-z_]+\(self"
  fix: |
    Add docstring template
```

## Limitations

- Pattern matching is currently regex-based
- Complex fixes may require manual intervention
- Test coverage should be maintained for patched code
- Review all changes before merging

## Future Enhancements

- AST-based patching for Python
- XML parsing for Odoo views
- Integration with pre-commit hooks
- Automatic test generation
- ML-based fix suggestions
