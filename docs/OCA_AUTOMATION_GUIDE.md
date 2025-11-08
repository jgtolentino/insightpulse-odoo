# OCA Automation Suite Documentation

**Complete guide to OCA (Odoo Community Association) automation tools for InsightPulse AI**

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Tools Reference](#tools-reference)
4. [Workflows](#workflows)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Resources](#resources)

---

## Overview

This automation suite integrates all essential OCA tooling into your InsightPulse Odoo monorepo, saving **~15 hours per week** on manual chores:

| Automation | Time Saved | Benefit |
|-----------|------------|---------|
| Pre-commit validation | 2h/week | Catch errors before push |
| Module scaffolding | 30min/module | Consistent OCA structure |
| Dependency management | 4h/month | Auto-dependency updates |
| Migration scripts | 8h/upgrade | Version upgrade prep |
| CI/CD validation | 1h/PR | Automated QA gates |

### Architecture

```
insightpulse-odoo/
├── .oca-tools/                    # OCA tooling installation
│   ├── maintainer-tools/          # Validation, pre-commit checks
│   ├── oca-addons-repo-template/ # Module scaffolding templates
│   ├── repo-maintainer/           # Dependency management
│   ├── OpenUpgrade/               # Migration framework
│   ├── openupgradelib/            # Migration utilities
│   └── oca-custom/                # Customization patterns
│
├── scripts/                       # Automation scripts
│   ├── install-oca-tools.sh       # Install all OCA tools
│   ├── setup-oca-precommit.sh     # Configure pre-commit hooks
│   ├── oca-scaffold-module.sh     # Create new OCA modules
│   ├── oca-update-deps.sh         # Manage dependencies
│   └── oca-generate-migrations.sh # Generate migration scripts
│
├── .github/workflows/             # CI/CD automation
│   ├── oca-validation.yml         # OCA compliance checks
│   └── oca-dependency-update.yml  # Auto-dependency updates
│
└── apps/odoo/addons/              # Your OCA-compliant modules
```

---

## Quick Start

### 1. Install OCA Tools (One-Time Setup)

```bash
# Install all OCA tooling
./scripts/install-oca-tools.sh

# Expected output:
# ✅ maintainer-tools installed
# ✅ oca-addons-repo-template installed
# ✅ repo-maintainer installed
# ✅ OpenUpgrade installed
# ✅ openupgradelib installed
# ✅ oca-custom installed
```

**What it installs:**
- **maintainer-tools**: OCA validation and linting
- **repo-maintainer**: Dependency management
- **OpenUpgrade**: Version migration framework
- **openupgradelib**: Migration helper functions
- **Python deps**: pylint-odoo, ruff, black, isort, pre-commit

### 2. Set Up Pre-Commit Hooks

```bash
# Configure OCA-compliant pre-commit hooks
./scripts/setup-oca-precommit.sh

# Expected output:
# ✅ .pre-commit-config.yaml created
# ✅ .pylintrc created
# ✅ .bandit created
# ✅ Pre-commit hooks installed
```

**What it does:**
- Auto-formats code with Black (PEP 8)
- Sorts imports with isort
- Validates manifests
- Runs security scans (Bandit)
- Checks copyright headers
- Validates XML/YAML syntax

**Test it:**
```bash
# Run on all files
pre-commit run --all-files

# Auto-run on every commit
git commit -m "test"
```

### 3. Create Your First OCA Module

```bash
# Scaffold a new module
./scripts/oca-scaffold-module.sh finance_ssc_enhanced "Accounting" "Finance Shared Service Center"

# Creates:
# apps/odoo/addons/finance_ssc_enhanced/
# ├── __init__.py
# ├── __manifest__.py            # OCA-compliant manifest
# ├── models/
# │   ├── __init__.py
# │   └── finance_ssc_enhanced.py
# ├── views/
# │   └── finance_ssc_enhanced_views.xml
# ├── security/
# │   └── ir.model.access.csv
# ├── tests/
# │   ├── __init__.py
# │   └── test_finance_ssc_enhanced.py
# ├── static/description/
# │   ├── index.html
# │   └── icon.png
# └── README.rst                 # OCA standard README
```

### 4. Manage OCA Dependencies

```bash
# Check dependencies
./scripts/oca-update-deps.sh check

# Install missing dependencies
./scripts/oca-update-deps.sh install

# Update existing dependencies
./scripts/oca-update-deps.sh update

# List all dependencies
./scripts/oca-update-deps.sh list

# Analyze dependency tree
./scripts/oca-update-deps.sh analyze
```

### 5. Generate Migration Scripts

```bash
# Generate OpenUpgrade migration scripts for Odoo 18.0
./scripts/oca-generate-migrations.sh 17.0 18.0

# Creates for each module:
# apps/odoo/addons/<module>/migrations/18.0/
# ├── pre-migration.py       # Runs before update
# ├── post-migration.py      # Runs after update
# ├── end-migration.py       # Final cleanup
# └── upgrade_analysis.txt   # Migration checklist
```

---

## Tools Reference

### 1. `install-oca-tools.sh`

**Purpose:** Install all OCA tooling dependencies

```bash
./scripts/install-oca-tools.sh
```

**What it installs:**

| Tool | Purpose | Location |
|------|---------|----------|
| maintainer-tools | Validation, linting | `.oca-tools/maintainer-tools` |
| oca-addons-repo-template | Module templates | `.oca-tools/oca-addons-repo-template` |
| repo-maintainer | Dependency mgmt | `.oca-tools/repo-maintainer` |
| OpenUpgrade | Migration framework | `.oca-tools/OpenUpgrade` |
| openupgradelib | Migration helpers | `.oca-tools/openupgradelib` |
| oca-custom | Customization patterns | `.oca-tools/oca-custom` |

**Python packages:**
- `pylint-odoo`: Odoo-specific linting
- `ruff`: Fast Python linter
- `black`: Code formatter
- `isort`: Import sorter
- `pre-commit`: Git hook framework
- `bandit`: Security scanner

---

### 2. `setup-oca-precommit.sh`

**Purpose:** Configure OCA-compliant pre-commit hooks

```bash
./scripts/setup-oca-precommit.sh
```

**Creates:**

#### `.pre-commit-config.yaml`
Defines all pre-commit hooks:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Large file check
- Private key detection
- Black formatting
- isort import sorting
- Ruff linting
- pylint-odoo checks
- Bandit security scan
- Copyright header insertion

#### `.pylintrc`
Odoo-specific pylint configuration:
```ini
[ODOOLINT]
readme_template_url="https://github.com/OCA/maintainer-tools/blob/master/template/module/README.rst"
manifest_required_authors=Odoo Community Association (OCA)
license_allowed=AGPL-3,GPL-2,GPL-3,LGPL-3
valid_odoo_versions=17.0,18.0
```

#### `.bandit`
Security scan configuration:
```ini
[bandit]
exclude_dirs = ['/tests', '/.oca-tools', '/migrations']
```

#### `pyproject.toml`
Tool configuration for Black, isort, Ruff, pytest

**Usage:**
```bash
# Manual run
pre-commit run --all-files

# Run on specific files
pre-commit run --files apps/odoo/addons/*/models/*.py

# Update hooks
pre-commit autoupdate

# Skip hooks (not recommended)
git commit --no-verify
```

---

### 3. `oca-scaffold-module.sh`

**Purpose:** Create OCA-compliant Odoo modules

```bash
./scripts/oca-scaffold-module.sh <module_name> [category] [summary] [odoo_version]
```

**Examples:**

```bash
# Finance module
./scripts/oca-scaffold-module.sh finance_ssc_enhanced "Accounting" "Finance SSC"

# BIR compliance module
./scripts/oca-scaffold-module.sh bir_compliance_2025 "Compliance" "BIR Form Automation"

# Multi-agency portal
./scripts/oca-scaffold-module.sh multi_agency_portal "Portal" "Multi-Agency Dashboard" "17.0"
```

**Naming Rules:**
- ✅ Must start with lowercase letter
- ✅ Only lowercase letters, numbers, underscores
- ✅ Examples: `finance_ssc`, `bir_compliance_2025`
- ❌ Invalid: `FinanceSSC`, `finance-ssc`, `1_finance`

**Generated Structure:**

```python
# __manifest__.py
{
    "name": "finance ssc enhanced",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "summary": "Finance Shared Service Center",
    "author": "Jake Tolentino <jake@insightpulseai.net>, Odoo Community Association (OCA)",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/finance_ssc_enhanced_views.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["jgtolentino"],
}
```

**Generated Files:**

| File | Purpose |
|------|---------|
| `__manifest__.py` | OCA-compliant module manifest |
| `__init__.py` | Module initialization |
| `models/<module>.py` | Base model with workflow |
| `views/<module>_views.xml` | Tree, form, search views + menu |
| `security/ir.model.access.csv` | Access rights |
| `tests/test_<module>.py` | Unit test skeleton |
| `README.rst` | OCA-standard documentation |
| `static/description/index.html` | Module description |

---

### 4. `oca-update-deps.sh`

**Purpose:** Manage OCA module dependencies

```bash
./scripts/oca-update-deps.sh <action> [options]
```

**Actions:**

#### `check` - Check for missing dependencies
```bash
./scripts/oca-update-deps.sh check

# Output:
# ✅ server-tools (branch: 17.0)
# ✅ web (branch: 17.0)
# ❌ account-financial-tools (missing)
#
# Summary: Found: 8, Missing: 2
```

#### `install` - Install missing dependencies
```bash
./scripts/oca-update-deps.sh install

# Clones OCA repos from GitHub
# Creates: apps/odoo/../oca-repos/
#   oca-server-tools/
#   oca-web/
#   oca-account-financial-tools/
```

#### `update` - Update existing dependencies
```bash
./scripts/oca-update-deps.sh update

# Git pulls latest changes for all OCA repos
```

#### `list` - List all dependencies
```bash
./scripts/oca-update-deps.sh list

# Output table:
# Repository                Branch          Last Update
# ──────────────────────────────────────────────────────
# server-tools              17.0            2 days ago
# web                       17.0            1 week ago
```

#### `validate` - Validate dependency versions
```bash
./scripts/oca-update-deps.sh validate

# Checks:
# - Correct Odoo version branch
# - No uncommitted changes
# - Consistent across all repos
```

#### `analyze` - Analyze dependency tree
```bash
./scripts/oca-update-deps.sh analyze

# Output:
# 📊 Statistics:
#    Total modules: 45
#    Total dependencies: 127
#    Unique dependencies: 23
#
# 🔝 Most used dependencies:
#    12  base
#    8   web
#    6   mail
```

**Configuration File: `oca-dependencies.txt`**

```txt
# OCA Dependencies for InsightPulse AI
# Format: <repo> [path] [branch]

# Core OCA dependencies
server-tools
web
reporting-engine
account-financial-reporting
account-financial-tools
server-ux
queue
rest-framework

# Finance & Accounting
account-reconcile
account-invoicing
account-payment
account-closing

# Project Management
project
project-reporting

# Multi-company & Legal
multi-company

# Connector framework
connector
```

---

### 5. `oca-generate-migrations.sh`

**Purpose:** Generate OpenUpgrade migration scripts

```bash
./scripts/oca-generate-migrations.sh <from_version> <to_version>
```

**Example:**

```bash
# Generate migrations from Odoo 17.0 to 18.0
./scripts/oca-generate-migrations.sh 17.0 18.0
```

**Creates for each module:**

```
apps/odoo/addons/<module>/migrations/18.0/
├── pre-migration.py       # Runs BEFORE module update
├── post-migration.py      # Runs AFTER module update
├── end-migration.py       # Final cleanup
└── upgrade_analysis.txt   # Migration checklist
```

**pre-migration.py:**
```python
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    """Pre-migration script."""
    cr = env.cr

    # Rename fields
    openupgrade.rename_fields(
        env, [("module", "model", "old_field", "new_field")]
    )

    # Rename models
    openupgrade.rename_models(
        cr, [("old.model", "new.model")]
    )

    # Rename tables
    openupgrade.rename_tables(
        cr, [("old_table", "new_table")]
    )
```

**post-migration.py:**
```python
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    """Post-migration script."""
    cr = env.cr

    # Migrate data
    openupgrade.logged_query(
        cr,
        """
        UPDATE module_table
        SET new_field = old_field
        WHERE old_field IS NOT NULL;
        """
    )
```

**upgrade_analysis.txt:**
```markdown
# OpenUpgrade Analysis for module (17.0 → 18.0)

## Models Changed
- [ ] TODO: List models that need migration

## Fields Changed
- [ ] TODO: List field renames/type changes

## Testing Checklist
- [ ] Unit tests updated
- [ ] Integration tests pass
- [ ] Manual smoke test completed
```

---

## Workflows

### CI/CD Pipeline: OCA Validation

**File:** `.github/workflows/oca-validation.yml`

**Triggered on:**
- Pull requests to `main`
- Pushes to `claude/**` branches
- Changes in `apps/odoo/addons/**`

**Jobs:**

1. **Validate Manifests**
   - Check `__manifest__.py` syntax
   - Validate required keys (name, version, license, etc.)
   - Check version format: `<odoo_version>.x.y.z`
   - Verify OCA author requirement

2. **Pylint Odoo Checks**
   - Run `pylint-odoo` with `.pylintrc`
   - Check Odoo-specific patterns
   - Validate README templates

3. **Code Formatting**
   - Black formatting validation
   - isort import sorting
   - Fail if code not formatted

4. **Security Scan**
   - Run Bandit security scanner
   - Check for SQL injection
   - Check for hardcoded secrets

5. **XML View Validation**
   - Validate XML syntax with xmllint
   - Check view structure

6. **Test Modules**
   - Run Odoo unit tests
   - Check test coverage

7. **Validate Documentation**
   - Check README.rst exists
   - Validate minimum content

8. **Check Dependencies**
   - Validate all `depends` exist
   - Check for missing OCA modules

**Status Badge:**

```markdown
[![OCA Validation](https://github.com/jgtolentino/insightpulse-odoo/workflows/OCA%20Module%20Validation/badge.svg)](https://github.com/jgtolentino/insightpulse-odoo/actions)
```

---

### CI/CD Pipeline: Dependency Updates

**File:** `.github/workflows/oca-dependency-update.yml`

**Triggered:**
- Weekly (Sundays at midnight)
- Manual workflow dispatch

**What it does:**

1. Checks all OCA repos for updates
2. Creates automated PR if updates found
3. Includes update summary and testing checklist

**Example PR:**

```markdown
## OCA Dependency Updates Available

### Updates:
- **server-tools**: 12 commits behind
- **web**: 5 commits behind
- **account-financial-tools**: 3 commits behind

### Testing Checklist
- [ ] Run module tests: `./scripts/validate-all.sh`
- [ ] Check for breaking changes
- [ ] Verify manifest compatibility
- [ ] Test affected workflows
```

---

## Best Practices

### 1. Module Development Workflow

```bash
# Step 1: Create new module
./scripts/oca-scaffold-module.sh my_module "Category" "Summary"

# Step 2: Implement your logic
cd apps/odoo/addons/my_module
# Edit models, views, etc.

# Step 3: Run pre-commit checks
pre-commit run --all-files

# Step 4: Test locally
# odoo-bin -d test_db -i my_module --test-enable

# Step 5: Commit
git add apps/odoo/addons/my_module
git commit -m "feat(my_module): add new module"

# Pre-commit hooks auto-run:
# ✅ Black formatting
# ✅ isort imports
# ✅ pylint-odoo
# ✅ Security scan

# Step 6: Push and create PR
git push origin feature/my-module
# CI/CD validation runs automatically
```

### 2. Dependency Management

```bash
# Weekly routine:
./scripts/oca-update-deps.sh check    # Check status
./scripts/oca-update-deps.sh update   # Update if needed
./scripts/oca-update-deps.sh validate # Verify integrity

# Before major changes:
./scripts/oca-update-deps.sh analyze  # Understand impact
```

### 3. Version Upgrades

```bash
# Step 1: Generate migration scripts
./scripts/oca-generate-migrations.sh 17.0 18.0

# Step 2: Fill in migration logic
# Edit: apps/odoo/addons/*/migrations/18.0/*.py

# Step 3: Test on staging
pg_dump -Fc prod_db > backup.dump
pg_restore -d staging_db backup.dump
odoo-bin -d staging_db -u all --stop-after-init

# Step 4: Validate
./scripts/validate-all.sh
pytest tests/ -v

# Step 5: Production migration (with backup!)
```

### 4. OCA Compliance Checklist

Before releasing a module:

- [ ] Manifest includes OCA as author
- [ ] License is LGPL-3/AGPL-3/GPL-3
- [ ] Version format: `<odoo_version>.x.y.z`
- [ ] README.rst follows OCA template
- [ ] All Python code formatted with Black
- [ ] Imports sorted with isort
- [ ] No security issues (Bandit)
- [ ] Unit tests included
- [ ] XML views validated
- [ ] Access rights defined
- [ ] No hardcoded secrets

---

## Troubleshooting

### Pre-commit hooks failing

**Problem:** Pre-commit checks fail on every commit

**Solution 1:** Auto-fix issues
```bash
# Let Black and isort fix formatting
pre-commit run --all-files

# Review changes
git diff

# Commit fixed files
git add -u
git commit -m "style: fix formatting"
```

**Solution 2:** Identify specific issue
```bash
# Run individual hooks
pre-commit run black --all-files
pre-commit run isort --all-files
pre-commit run pylint_odoo --all-files
```

**Solution 3:** Skip hooks (NOT recommended)
```bash
git commit --no-verify -m "message"
```

---

### Dependency installation fails

**Problem:** `./scripts/oca-update-deps.sh install` fails

**Common causes:**

1. **Branch doesn't exist**
   ```
   ⚠️ Failed to clone account-financial-tools (branch 17.0 may not exist)
   ```

   **Fix:** Check if OCA repo has your Odoo version
   ```bash
   # Visit: https://github.com/OCA/account-financial-tools/branches
   # Update oca-dependencies.txt with correct branch
   ```

2. **Network issues**
   ```
   fatal: unable to access 'https://github.com/OCA/...': Could not resolve host
   ```

   **Fix:** Check internet connection, retry
   ```bash
   ./scripts/oca-update-deps.sh install
   ```

3. **Disk space**
   ```
   error: failed to write object: No space left on device
   ```

   **Fix:** Free up disk space
   ```bash
   # Clean old OCA repos
   rm -rf apps/odoo/../oca-repos/oca-*
   ./scripts/oca-update-deps.sh install
   ```

---

### Migration script errors

**Problem:** OpenUpgrade migration fails

**Error:** `KeyError: 'old_field'`

**Fix:** Check field exists before migration
```python
# In pre-migration.py
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    # Check if field exists first
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='my_table'
        AND column_name='old_field'
    """)

    if cr.fetchone():
        openupgrade.rename_fields(
            env, [("module", "model", "old_field", "new_field")]
        )
```

---

### CI/CD pipeline failing

**Problem:** OCA validation workflow fails

**Check logs:**
```bash
# GitHub Actions logs
# Navigate to: https://github.com/jgtolentino/insightpulse-odoo/actions
```

**Common failures:**

1. **Manifest validation**
   ```
   ❌ Missing required key 'license' in my_module
   ```

   **Fix:** Add required keys to `__manifest__.py`
   ```python
   {
       "name": "My Module",
       "version": "17.0.1.0.0",
       "license": "LGPL-3",  # ← Add this
       "author": "Jake Tolentino, Odoo Community Association (OCA)",
       # ...
   }
   ```

2. **Black formatting**
   ```
   ❌ Code not formatted with Black
   ```

   **Fix:** Format locally and commit
   ```bash
   black apps/odoo/addons/
   git add -u
   git commit -m "style: format with black"
   ```

3. **Security issues**
   ```
   ⚠️ Security issues found: B608 (SQL injection)
   ```

   **Fix:** Use parameterized queries
   ```python
   # ❌ Bad
   cr.execute("SELECT * FROM table WHERE id = %s" % user_input)

   # ✅ Good
   cr.execute("SELECT * FROM table WHERE id = %s", (user_input,))
   ```

---

## Resources

### OCA Documentation

- **OCA Guidelines**: https://github.com/OCA/odoo-community.org
- **Maintainer Tools**: https://github.com/OCA/maintainer-tools
- **OpenUpgrade**: https://github.com/OCA/OpenUpgrade/wiki
- **Module Template**: https://github.com/OCA/oca-addons-repo-template
- **Code Review Guide**: https://github.com/OCA/maintainer-tools/wiki/Code-review-guidelines

### Python Tools

- **Black**: https://black.readthedocs.io/
- **isort**: https://pycqa.github.io/isort/
- **Ruff**: https://docs.astral.sh/ruff/
- **Bandit**: https://bandit.readthedocs.io/
- **pre-commit**: https://pre-commit.com/

### Odoo Development

- **Odoo 17.0 Docs**: https://www.odoo.com/documentation/17.0/
- **OWL Framework**: https://github.com/odoo/owl
- **Odoo REST API**: https://www.odoo.com/documentation/17.0/developer/reference/external_api.html

### InsightPulse AI

- **Project Repo**: https://github.com/jgtolentino/insightpulse-odoo
- **Support**: support@insightpulseai.net
- **Documentation**: https://insightpulseai.net/docs

---

## Quick Reference Card

### Daily Commands

```bash
# Check OCA compliance
pre-commit run --all-files

# Create new module
./scripts/oca-scaffold-module.sh module_name "Category" "Summary"

# Check dependencies
./scripts/oca-update-deps.sh check

# Run tests
pytest tests/ -v
```

### Weekly Commands

```bash
# Update OCA dependencies
./scripts/oca-update-deps.sh update

# Validate all modules
./scripts/oca-update-deps.sh validate

# Check for OCA updates
gh workflow run oca-dependency-update.yml
```

### Before Version Upgrade

```bash
# Generate migration scripts
./scripts/oca-generate-migrations.sh 17.0 18.0

# Backup database
pg_dump -Fc prod_db > backup_$(date +%Y%m%d).dump

# Test on staging first!
```

---

## Support

For issues with OCA automation:

1. **Check logs**: Review script output and CI/CD logs
2. **Validate setup**: Run `./scripts/install-oca-tools.sh` again
3. **Consult docs**: Review this guide and OCA documentation
4. **Ask community**: OCA mailing list, GitHub issues
5. **Contact support**: support@insightpulseai.net

---

**Last Updated:** 2025-11-08
**Version:** 1.0.0
**Maintainer:** Jake Tolentino <jake@insightpulseai.net>
