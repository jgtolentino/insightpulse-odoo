---
name: oca-devops-professional
description: Professional OCA (Odoo Community Association) development workflow using GitHub bot automation, standardized repo templates, apps discovery, and automated module migration. Use when building OCA-compliant modules, setting up CI/CD, or migrating between Odoo versions.
---

# OCA DevOps Professional

Transform Claude into an OCA DevOps expert using official OCA tools for professional Odoo module development.

## What This Skill Provides

Master the complete OCA ecosystem with 4 critical tools:

1. **OCA GitHub Bot** - Automated PR reviews, merges, and CI/CD
2. **OCA Repo Template** - Standardized project structure
3. **OCA Apps Store** - Discover existing modules before building
4. **Module Migrator** - Automate upgrades between Odoo versions

**Result:** Enterprise-grade modules following OCA standards with automated workflows.

---

## Tool 1: OCA GitHub Bot

**Repository:** https://github.com/OCA/oca-github-bot

### What It Does

The OCA GitHub bot automates GitHub operations for OCA repositories:

- ✅ Auto-mentions maintainers when their code changes
- ✅ Auto-merges PRs after approval + testing
- ✅ Updates README files automatically
- ✅ Manages labels and milestones
- ✅ Publishes Python wheels
- ✅ Handles version bumping

### Bot Commands (Use in PR Comments)

#### `/ocabot merge [major|minor|patch|nobump]`
**Purpose:** Merge PR with version bump and changelog

**What it does:**
1. Rebases PR onto target branch
2. Runs full test suite
3. Bumps version (if specified)
4. Updates changelog
5. Merges to target branch
6. Publishes Python wheel to PyPI

**Examples:**
```bash
# Merge with patch version bump (1.0.0 → 1.0.1)
/ocabot merge patch

# Merge with minor version bump (1.0.1 → 1.1.0)
/ocabot merge minor

# Merge with major version bump (1.1.0 → 2.0.0)
/ocabot merge major

# Merge without version bump
/ocabot merge nobump
```

**When to use each bump:**
- **major** - Breaking changes, incompatible API changes
- **minor** - New features, backward compatible
- **patch** - Bug fixes, no new features
- **nobump** - Documentation only, no code changes

#### `/ocabot rebase`
**Purpose:** Rebase PR onto latest target branch

**When to use:**
- Resolve merge conflicts
- Get latest changes from main branch
- Update stale PRs

**Example:**
```bash
# In PR comment:
/ocabot rebase
```

#### `/ocabot migration [module_name]`
**Purpose:** Link module to migration issue and set milestone

**When to use:**
- Migrating module to new Odoo version
- Track migration progress
- Coordinate with migration team

**Example:**
```bash
/ocabot migration sale_order_custom
```

### Automated Bot Actions (No Command Needed)

**On PR Open:**
- Automatically mentions maintainers whose code was modified
- Requests maintainers if none declared in `__manifest__.py`

**On PR Review:**
- Adds "approved" label after 2 approvals
- Adds "ready to merge" label after 5+ days with approvals

**On CI Success:**
- Adds "needs review" label when tests pass
- Skips if PR title contains "wip:" or "[wip]"

**On PR Merge:**
- Deletes source branch automatically (if same repo)
- Updates addon README files
- Runs setuptools-odoo-make-defaults

**Nightly Jobs:**
- Updates all README tables across repositories
- Generates README.rst from fragments
- Applies default OCA icons to addons without custom icons
- Regenerates setup.py files

### Using the Bot in Your Workflow

**Step 1: Create PR following OCA standards**
```bash
git checkout -b feature/add-custom-field
# Make changes
git commit -m "feat(sale_custom): add customer rating field"
git push origin feature/add-custom-field
# Open PR on GitHub
```

**Step 2: Bot automatically:**
- Mentions maintainers
- Runs CI tests
- Adds labels based on test results

**Step 3: After reviews (2 approvals):**
```bash
# In PR comment:
/ocabot merge patch

# Bot will:
# 1. Rebase
# 2. Test
# 3. Bump version 1.0.0 → 1.0.1
# 4. Update changelog
# 5. Merge
# 6. Publish wheel
```

**Result:** Fully automated merge with zero manual steps!

---

## Tool 2: OCA Addons Repo Template

**Repository:** https://github.com/OCA/oca-addons-repo-template

### What It Provides

Standardized repository structure for OCA addon repositories:

```
your-oca-repo/
├── .github/
│   └── workflows/
│       ├── test.yml              # CI/CD testing
│       ├── pre-commit.yml        # Code quality checks
│       └── stale.yml             # Stale PR management
├── .pre-commit-config.yaml       # Pre-commit hooks
├── .editorconfig                 # Editor settings
├── .gitignore                    # Git ignore rules
├── copier.yml                    # Template configuration
├── pyproject.toml                # Python project metadata
├── poetry.lock                   # Dependency locks
├── pytest.ini                    # Test configuration
├── setup.cfg                     # Python setup
├── README.md                     # Repository README
└── [module_name]/                # Your modules here
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    ├── views/
    └── ...
```

### Supported Odoo Versions

✅ 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0

### How to Use the Template

#### Option 1: Bootstrap New Repository

**Install Copier:**
```bash
pip install copier
```

**Create new repository from template:**
```bash
copier copy --UNSAFE \
    gh:OCA/oca-addons-repo-template \
    ~/projects/my-oca-modules

# Answer prompts:
# - Repository name: my-oca-modules
# - Odoo version: 19.0
# - Organization: InsightPulse
# - License: AGPL-3
```

**Initialize Git and pre-commit:**
```bash
cd ~/projects/my-oca-modules
git init
git add .
pre-commit run --all-files
git commit -m "Initial commit from OCA template"
```

**Create GitHub repository:**
```bash
gh repo create jgtolentino/my-oca-modules --public --source=.
git push -u origin main
```

#### Option 2: Update Existing Repository

**Update to latest template version:**
```bash
cd ~/projects/existing-repo
copier update --UNSAFE
pre-commit run --all-files
git commit -m "Update OCA template"
git push
```

### What's Included

**1. CI/CD Workflows (GitHub Actions)**

**`.github/workflows/test.yml`** - Automated testing:
- Runs on every PR
- Tests against multiple Odoo versions
- Checks Python syntax (pylint, flake8)
- Validates module structure
- Runs unit tests

**`.github/workflows/pre-commit.yml`** - Code quality:
- Checks code formatting (Black, isort)
- Validates YAML/JSON
- Checks for syntax errors
- Ensures file encoding

**2. Pre-commit Hooks**

Automatically run before each commit:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/isort
    hooks:
      - id: isort
  - repo: https://github.com/PyCQA/flake8
    hooks:
      - id: flake8
```

**Install hooks:**
```bash
pip install pre-commit
pre-commit install
```

**Run manually:**
```bash
pre-commit run --all-files
```

**3. Python Project Configuration**

**`pyproject.toml`** - Modern Python packaging:
```toml
[build-system]
requires = ["setuptools", "setuptools-odoo"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
```

**4. Testing Configuration**

**`pytest.ini`** - Test runner settings:
```ini
[pytest]
addopts = -v --tb=short
testpaths = tests
```

### Benefits of Using Template

✅ **Standardization** - All repos follow same structure
✅ **Automated CI/CD** - Testing on every commit
✅ **Code Quality** - Pre-commit hooks enforce standards
✅ **Easy Updates** - Copier updates template across repos
✅ **OCA Compliance** - Meets all OCA requirements
✅ **Time Savings** - No manual setup needed

### Adding Your Modules

**Create module in repository:**
```bash
cd ~/projects/my-oca-modules
odoo scaffold ipai_expense_ocr ./

# Structure:
my-oca-modules/
├── .github/              # From template
├── ipai_expense_ocr/     # Your module
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   ├── views/
│   └── ...
└── ipai_helpdesk_ai/     # Another module
```

**Commit with pre-commit checks:**
```bash
git add ipai_expense_ocr/
git commit -m "feat: add expense OCR module"
# Pre-commit automatically runs Black, isort, flake8
git push
# GitHub Actions automatically runs full test suite
```

---

## Tool 3: OCA Apps Store

**Repository:** https://github.com/OCA/apps-store

### What It Is

The OCA Apps Store is a catalog of community-developed Odoo modules. It helps you:

- ✅ Discover existing modules before building custom
- ✅ Find modules by category or functionality
- ✅ Check module maturity and maintenance status
- ✅ Identify maintainers and contributors
- ✅ Save development time by reusing

### How to Search for Modules

#### Option 1: Browse on apps.odoo.com

**URL:** https://apps.odoo.com/apps/modules/browse?author=OCA

**Filter by:**
- Odoo version (19.0)
- Category (Accounting, Sales, HR, etc.)
- Author (OCA)
- Technical name

**Example Search:**
"expense management OCA 19.0"

**Results:**
- `hr_expense_advance_clearing` (OCA/hr-expense)
- `hr_expense_sequence` (OCA/hr-expense)
- `hr_expense_invoice` (OCA/hr-expense)

#### Option 2: Search GitHub OCA Organization

**URL:** https://github.com/orgs/OCA/repositories

**Search pattern:**
```
OCA/[category]-related-name
```

**Common repositories:**
- `OCA/account-*` - Accounting modules
- `OCA/sale-*` - Sales modules
- `OCA/project-*` - Project modules
- `OCA/hr-*` - HR modules
- `OCA/purchase-*` - Purchase modules
- `OCA/stock-*` - Inventory modules
- `OCA/helpdesk` - Helpdesk modules
- `OCA/server-tools` - Server utilities

**Example:**
```bash
# Find expense-related modules
curl -s "https://api.github.com/orgs/OCA/repos?per_page=100" | \
    jq '.[] | select(.name | contains("expense")) | .name'

# Output:
# hr-expense
```

#### Option 3: Check OCA Module Index

**Clone index repository:**
```bash
git clone https://github.com/OCA/maintainer-tools.git
cd maintainer-tools/tools
python oca_projects.py list
```

### Workflow: Check Before Building

**Before creating custom module, always check:**

**Step 1: Define requirements**
```
Need: Travel expense management with:
- Receipt OCR scanning
- Multi-level approvals
- BIR tax compliance (Philippines)
- Mobile app support
```

**Step 2: Search OCA for existing modules**
```bash
# Search GitHub
https://github.com/OCA?q=expense&type=repositories

# Found repositories:
# - OCA/hr-expense (8 modules)
```

**Step 3: Check module list**
```bash
git clone https://github.com/OCA/hr-expense.git -b 19.0
cd hr-expense
ls -la

# Modules found:
# - hr_expense_advance_clearing ✅
# - hr_expense_sequence ✅
# - hr_expense_invoice ✅
# - hr_expense_cancel ✅
```

**Step 4: Review module capabilities**
```bash
# Read README
cat hr_expense_advance_clearing/README.rst

# Check manifest
cat hr_expense_advance_clearing/__manifest__.py
```

**Step 5: Decide: Use, Extend, or Build New**

**Option A: Use OCA module as-is** (Matches 80%+ requirements)
```bash
# Vendor OCA module
git submodule add https://github.com/OCA/hr-expense.git oca/hr-expense
```

**Option B: Extend OCA module** (Matches 50-80%)
```python
# Create extension module
# ipai_expense_ocr/__manifest__.py
{
    'name': 'IPAI Expense OCR',
    'depends': ['hr_expense_advance_clearing'],  # Extend OCA
    # Add OCR features on top
}
```

**Option C: Build from scratch** (Matches <50%)
```bash
# Only if no suitable OCA module exists
odoo scaffold ipai_expense_management ./
```

### Benefits of Checking OCA First

✅ **Save development time** - Reuse existing code
✅ **Battle-tested code** - Already used by community
✅ **Active maintenance** - OCA maintains modules
✅ **Standards compliant** - Follows OCA best practices
✅ **Free & open-source** - AGPL-3 licensed

**Example Savings:**
- Build from scratch: 3 months
- Extend OCA module: 2 weeks
- Use OCA as-is: 1 day

---

## Tool 4: Odoo Module Migrator

**Repository:** https://github.com/OCA/odoo-module-migrator

### What It Does

Automates code migration when upgrading Odoo versions:

- ✅ Renames `__openerp__.py` → `__manifest__.py`
- ✅ Converts `openerp` imports → `odoo` imports
- ✅ Updates XML view syntax
- ✅ Removes Python 2 compatibility code
- ✅ Updates deprecated APIs
- ✅ Bumps version numbers
- ✅ Creates Git commits with changes

### Supported Migrations

**Tested migrations:**
- 8.0 → 9.0 → 10.0 → 11.0 → 12.0 → 13.0 → 14.0 → 15.0 → 16.0 → 17.0 → 18.0 → 19.0

**Latest release:** v0.5.0 (August 2025)

### Installation

```bash
pip install odoo-module-migrator
```

Or from source:
```bash
git clone https://github.com/OCA/odoo-module-migrator.git
cd odoo-module-migrator
pip install -e .
```

### How to Use

#### Scenario 1: Migrate Single Module

**Migrate from 16.0 to 19.0:**
```bash
odoo-module-migrate \
    --directory ./addons/ipai_expense_ocr \
    --modules ipai_expense_ocr \
    --init-version-name 16.0 \
    --target-version-name 19.0 \
    --log-level INFO
```

**What happens:**
1. Analyzes module code
2. Applies automatic transformations
3. Creates Git commits for each change
4. Outputs log:
   - INFO: Automatic changes applied
   - WARNING: Manual review needed
   - ERROR: Must fix manually

#### Scenario 2: Migrate Multiple Modules

**Migrate entire repository:**
```bash
odoo-module-migrate \
    --directory ./addons \
    --modules ipai_expense_ocr,ipai_helpdesk_ai,ipai_crm_scoring \
    --init-version-name 16.0 \
    --target-version-name 19.0 \
    --commit
```

#### Scenario 3: OCA Format-Patch Method (Recommended)

**Best practice for OCA modules:**
```bash
# Create patches from original branch
git format-patch 16.0..HEAD -o patches/

# Migrate with patches
odoo-module-migrate \
    --directory ./addons \
    --modules all \
    --init-version-name 16.0 \
    --target-version-name 19.0 \
    --format-patch
```

**Why format-patch?**
- Preserves commit history
- Easier to review changes
- Maintains authorship
- OCA standard practice

### Common Transformations

**1. Manifest Rename**
```bash
# Before:
__openerp__.py

# After:
__manifest__.py
```

**2. Import Changes**
```python
# Before:
from openerp import models, fields, api
from openerp.exceptions import ValidationError

# After:
from odoo import models, fields, api
from odoo.exceptions import ValidationError
```

**3. Remove Python 2 Encoding**
```python
# Before:
# -*- encoding: utf-8 -*-
from odoo import models

# After:
from odoo import models
```

**4. XML View Updates**
```xml
<!-- Before: -->
<act_window id="action_view" name="View"/>

<!-- After: -->
<record id="action_view" model="ir.actions.window">
    <field name="name">View</field>
</record>
```

**5. Version Bump**
```python
# Before (__manifest__.py):
'version': '16.0.1.0.0'

# After:
'version': '19.0.1.0.0'
```

**6. Dependency Updates**
```python
# Before:
'depends': ['base', 'account_payment']

# After (if module moved):
'depends': ['base', 'account']
```

### Migration Workflow

**Step 1: Backup current version**
```bash
git checkout -b 16.0-backup
git push origin 16.0-backup
```

**Step 2: Create migration branch**
```bash
git checkout -b 19.0
```

**Step 3: Run migrator**
```bash
odoo-module-migrate \
    --directory ./addons \
    --modules all \
    --init-version-name 16.0 \
    --target-version-name 19.0 \
    --log-level INFO \
    --commit
```

**Step 4: Review changes**
```bash
git log --oneline
# Shows commits for each transformation

git diff 16.0-backup...19.0
# Review all changes
```

**Step 5: Handle warnings/errors**
```bash
# Check migration log
cat migration.log | grep WARNING
cat migration.log | grep ERROR

# Fix manual issues
vim addons/ipai_expense_ocr/models/expense.py
git commit -m "fix: manual migration fixes"
```

**Step 6: Test migrated modules**
```bash
# Install on Odoo 19.0
odoo-bin -d test_migration -i ipai_expense_ocr --test-enable

# Run unit tests
pytest addons/ipai_expense_ocr/tests/
```

**Step 7: Push migrated branch**
```bash
git push origin 19.0
```

### Log Level Meanings

**INFO** - Automatic changes successfully applied
```
INFO: Renamed __openerp__.py to __manifest__.py
INFO: Updated imports from openerp to odoo
INFO: Bumped version 16.0.1.0.0 → 19.0.1.0.0
```

**WARNING** - Review needed (likely correct but verify)
```
WARNING: Deprecated API usage detected in models/expense.py:45
WARNING: Field 'state_id' may need manual migration
WARNING: Method 'onchange_partner_id' signature changed
```

**ERROR** - Manual fix required
```
ERROR: Cannot resolve dependency 'account_payment' (module removed)
ERROR: Syntax error in views/expense_views.xml:123
ERROR: Missing required field 'date_order' in model
```

### Handling Migration Errors

**Error: Missing Dependency**
```
ERROR: Module 'account_payment' not found in Odoo 19.0
```

**Fix:**
```python
# Check Odoo 19.0 equivalent
# account_payment → account (merged into core)

# Update __manifest__.py
'depends': ['base', 'account'],  # Changed from account_payment
```

**Error: Deprecated API**
```
WARNING: @api.one decorator removed in Odoo 19.0
```

**Fix:**
```python
# Before:
@api.one
def action_approve(self):
    self.state = 'approved'

# After:
@api.multi
def action_approve(self):
    self.ensure_one()
    self.state = 'approved'
```

**Error: XML Syntax**
```
ERROR: Invalid XML syntax in views/form.xml:45
```

**Fix:**
```xml
<!-- Before: -->
<field name="partner_id" select="1"/>

<!-- After (select attribute removed): -->
<field name="partner_id"/>
```

---

## Complete OCA Development Workflow

### Phase 1: Planning (Day 1)

**Step 1: Check OCA Apps Store**
```bash
# Search for existing modules
https://apps.odoo.com/apps/modules/browse?author=OCA&version=19.0

# Found relevant modules:
# - hr_expense_advance_clearing
# - helpdesk_mgmt
# - sale_order_line_sequence
```

**Step 2: Decide approach**
- Use existing OCA module? → Vendor it
- Extend OCA module? → Create extension
- Build from scratch? → Use OCA template

### Phase 2: Repository Setup (Day 1)

**Step 3: Bootstrap repository from OCA template**
```bash
pip install copier
copier copy --UNSAFE gh:OCA/oca-addons-repo-template ./ipai-modules
cd ipai-modules
git init
pre-commit install
git add .
git commit -m "Initial commit from OCA template"
gh repo create jgtolentino/ipai-modules --public --source=.
git push -u origin main
```

**Step 4: Create GitHub branch protection**
```bash
# Require PR reviews
# Require CI tests to pass
# Enable OCA bot
```

### Phase 3: Development (Week 1-4)

**Step 5: Create feature branch**
```bash
git checkout -b feature/expense-ocr
```

**Step 6: Develop module**
```bash
odoo scaffold ipai_expense_ocr ./
# Implement features
# Write tests
```

**Step 7: Commit with pre-commit**
```bash
git add ipai_expense_ocr/
git commit -m "feat(expense_ocr): add PaddleOCR integration"
# Pre-commit automatically runs
git push origin feature/expense-ocr
```

**Step 8: Create PR**
```bash
gh pr create \
    --title "feat: Add expense OCR module" \
    --body "Implements automatic receipt scanning using PaddleOCR"
```

### Phase 4: Review & Merge (Week 4)

**Step 9: OCA Bot automation**
```
# Bot automatically:
# - Mentions maintainers
# - Runs CI tests
# - Adds labels
```

**Step 10: After approvals**
```bash
# In PR comment:
/ocabot merge minor

# Bot automatically:
# - Rebases
# - Tests
# - Bumps version (1.0.0 → 1.1.0)
# - Updates changelog
# - Merges
# - Publishes wheel
```

### Phase 5: Migration (Annual)

**Step 11: Migrate to new Odoo version**
```bash
# When Odoo 20.0 releases:
git checkout -b 20.0
odoo-module-migrate \
    --directory ./ \
    --modules all \
    --init-version-name 19.0 \
    --target-version-name 20.0 \
    --format-patch

# Review changes
# Fix errors/warnings
# Test on Odoo 20.0
# Push to GitHub
```

---

## Best Practices

### ✅ Repository Management

1. **Use OCA template** for all new repositories
2. **Update template regularly** with `copier update`
3. **Enable pre-commit hooks** before first commit
4. **Configure branch protection** on main branch
5. **Use semantic commit messages** (feat:, fix:, docs:)

### ✅ Development Workflow

1. **Search OCA first** before building custom
2. **Create feature branches** for each module
3. **Write unit tests** for all functionality
4. **Run pre-commit** before pushing
5. **Use bot commands** for automated merges
6. **Document everything** in README.rst

### ✅ Version Management

1. **Follow semantic versioning** (MAJOR.MINOR.PATCH)
2. **Use bot for version bumps** (/ocabot merge minor)
3. **Update changelog** automatically via bot
4. **Tag releases** for major versions
5. **Publish wheels** to PyPI via bot

### ✅ Migration Strategy

1. **Test migrator** on backup branch first
2. **Review all WARNING logs** carefully
3. **Fix ERROR logs** before testing
4. **Run full test suite** after migration
5. **Keep old version branch** for rollback

---

## Troubleshooting

### OCA Bot Not Working

**Issue:** Bot doesn't respond to commands

**Check:**
- Repository enabled in OCA organization?
- Correct command syntax? (`/ocabot merge patch`)
- Bot has necessary permissions?
- CI tests passing?

### Pre-commit Hooks Failing

**Issue:** Commits blocked by pre-commit

**Fix:**
```bash
# Run manually to see errors
pre-commit run --all-files

# Auto-fix formatting
black ./
isort ./

# Retry commit
git commit -m "fix: formatting"
```

### Module Migrator Errors

**Issue:** Migration produces many errors

**Common causes:**
- Custom API usage
- Removed dependencies
- Changed field types
- Syntax incompatibilities

**Fix approach:**
1. Review ERROR logs
2. Check Odoo migration docs
3. Fix manually
4. Re-run migrator
5. Test thoroughly

---

## Resources

### Official Documentation
- [OCA GitHub Bot](https://github.com/OCA/oca-github-bot)
- [OCA Repo Template](https://github.com/OCA/oca-addons-repo-template)
- [OCA Apps Store](https://github.com/OCA/apps-store)
- [Module Migrator](https://github.com/OCA/odoo-module-migrator)

### Community Resources
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [OCA Maintainer Tools](https://github.com/OCA/maintainer-tools)
- [OCA Module Template](https://github.com/OCA/oca-module-template)

---

**Build enterprise-grade Odoo modules with professional OCA workflows!** 🚀
