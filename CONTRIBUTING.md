# Contributing to InsightPulse Odoo

First off, thank you for considering contributing to InsightPulse Odoo! It's people like you that make InsightPulse Odoo such a great tool for the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Platform Spec Validation (Required)](#platform-spec-validation-required)
- [Code Quality Standards](#code-quality-standards)
- [Module Development Guidelines](#module-development-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Pre-Commit Guardrails](#pre-commit-guardrails)
- [Submitting Changes](#submitting-changes)
- [CI/CD Pipeline & Required Checks](#cicd-pipeline--required-checks)
- [Review Process](#review-process)

---

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- **Be respectful**: Treat everyone with respect. Disagreement is no excuse for poor behavior.
- **Be collaborative**: Work together to find the best solutions.
- **Be inclusive**: Welcome and support people of all backgrounds and identities.
- **Be professional**: Focus on what is best for the community and the project.

---

## Getting Started

### Prerequisites

- **Docker 24+** & **Docker Compose 2.20+**
- **Python 3.11+** (for local development)
- **Git** with SSH keys configured
- **GitHub account** for pull requests
- **8GB RAM minimum** (16GB recommended)
- **GitHub Copilot** (optional, but recommended) - See [GitHub Copilot Setup Guide](docs/GITHUB_COPILOT_SETUP.md)

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/insightpulse-odoo.git
   cd insightpulse-odoo
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/jgtolentino/insightpulse-odoo.git
   ```

4. **Initialize the project**:
   ```bash
   make init
   ```

5. **Start development environment**:
   ```bash
   make dev
   ```

6. **Verify setup**:
   ```bash
   make health
   ```

---

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
```

**Branch Naming Conventions**:
- `feature/` - New features (e.g., `feature/expense-ocr-validation`)
- `fix/` - Bug fixes (e.g., `fix/approval-workflow-timeout`)
- `docs/` - Documentation updates (e.g., `docs/update-deployment-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/procurement-models`)
- `test/` - Test additions/fixes (e.g., `test/add-integration-tests`)

### 2. Keep Your Branch Updated

Regularly sync with upstream:

```bash
git fetch upstream
git rebase upstream/main
```

### 3. Make Your Changes

Follow our [Code Quality Standards](#code-quality-standards) and [Module Development Guidelines](#module-development-guidelines).

**⚠️ IMPORTANT: Platform Spec Validation**

Before making changes, understand our platform spec:

```bash
# View the canonical platform spec
cat spec/platform_spec.json

# Validate spec compliance
python3 scripts/validate_spec.py
```

See [Platform Spec Validation](#platform-spec-validation-required) for details.

**💡 Using GitHub Copilot** (Optional)

GitHub Copilot can accelerate your development. See [GitHub Copilot Setup Guide](docs/GITHUB_COPILOT_SETUP.md) for:
- How to enable Copilot for this repository
- Best practices for Odoo development with Copilot
- Security considerations and `.copilotignore` usage
- Troubleshooting common issues

**Important**: Always review Copilot suggestions for:
- OCA compliance and Odoo best practices
- Security vulnerabilities
- License compatibility (we use LGPL-3.0)
- BIR regulation adherence (for finance modules)

### 4. Test Your Changes

```bash
# Run all tests
make test

# Run specific test categories
make test-unit
make test-integration
make test-e2e

# Run linting
make lint
```

### 5. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add OCR validation for expense receipts

- Added PaddleOCR integration
- Implemented validation rules
- Added unit tests for OCR service

Closes #123"
```

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7. Create a Pull Request

Go to GitHub and create a pull request from your fork to the main repository.

---

## Platform Spec Validation (Required)

**✅ All contributions must comply with the platform specification.**

### What is the Platform Spec?

The platform spec (`spec/platform_spec.json`) is the **single source of truth** for:
- Service architecture (Odoo, Supabase, Superset, MCP, Pulser)
- CI/CD workflow definitions
- Deployment targets and configurations
- Documentation structure
- Module paths and dependencies

### Validation Requirements

#### 1. **Run Spec Validation Before Committing**

```bash
# Validate platform spec
python3 scripts/validate_spec.py

# Expected output:
# ✅ Schema validation passed
# ✅ All docs files exist
# ✅ All workflow files exist
# ✅ Spec validation complete – all guardrails passed
```

#### 2. **When to Update the Spec**

Update `spec/platform_spec.json` if you:
- Add/remove CI/CD workflows
- Add/remove documentation pages
- Change service architecture
- Modify deployment configuration
- Update module paths

#### 3. **Spec Update Process**

```bash
# 1. Edit the spec
nano spec/platform_spec.json

# 2. Validate against schema
python3 scripts/validate_spec.py

# 3. Commit both spec and related changes together
git add spec/platform_spec.json .github/workflows/my-new-workflow.yml
git commit -m "feat: add new deployment workflow

- Added .github/workflows/my-new-workflow.yml
- Updated spec/platform_spec.json with new workflow definition
- Validated spec compliance"
```

#### 4. **Spec Validation Failures**

If validation fails:

```bash
# Check which files are missing
python3 scripts/validate_spec.py

# Example error:
# ❌ Missing docs page: docs/new-guide.md

# Fix by creating the missing file
touch docs/new-guide.md

# Re-validate
python3 scripts/validate_spec.py
```

### Spec-Kit Architecture

Our spec-kit approach ensures:
- ✅ **Single source of truth** - No drift between code and documentation
- ✅ **Automated validation** - CI/CD enforces spec compliance
- ✅ **Clear boundaries** - Explicit service responsibilities
- ✅ **Deployment safety** - Platform spec guards production deploys

**Required Reading:**
- `spec/platform_spec.json` - The canonical spec
- `spec/platform_spec.schema.json` - JSON schema definition
- `docs/spec-kit/PRD_PLATFORM.md` - Platform spec PRD
- `.github/workflows/spec-guard.yml` - Spec validation workflow

---

## Code Quality Standards

### Python Code Standards

#### 1. **Follow OCA Guidelines**

All Odoo modules must follow [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst):

- ✅ Use OCA module structure
- ✅ Follow OCA naming conventions
- ✅ Include proper licensing headers (LGPL-3.0)
- ✅ Add author and maintainer information

#### 2. **Type Hints (Python 3.11+)**

Always use type hints:

```python
from typing import Dict, List, Optional

def calculate_total(
    amounts: List[float],
    tax_rate: float = 0.12,
    currency: Optional[str] = None
) -> Dict[str, float]:
    """Calculate total with tax.

    Args:
        amounts: List of amounts to sum
        tax_rate: Tax rate (default: 12% Philippines VAT)
        currency: Currency code (default: PHP)

    Returns:
        Dict with 'subtotal', 'tax', and 'total' keys
    """
    subtotal = sum(amounts)
    tax = subtotal * tax_rate
    return {
        "subtotal": subtotal,
        "tax": tax,
        "total": subtotal + tax,
    }
```

#### 3. **Docstrings (Google Style)**

Use Google-style docstrings:

```python
class ExpenseReport(models.Model):
    """Expense report with OCR processing.

    This model extends the base expense report with OCR capabilities
    for automatic receipt processing using PaddleOCR.

    Attributes:
        name: Report reference number
        employee_id: Employee who submitted the report
        total_amount: Total expense amount
        state: Report state (draft, submitted, approved, paid)
    """

    _name = 'expense.report'
    _description = 'Expense Report with OCR'
```

#### 4. **Code Formatting**

Use `black` for code formatting:

```bash
black custom/ --line-length 88
```

Use `isort` for import sorting:

```bash
isort custom/ --profile black
```

#### 5. **Linting**

Code must pass linting:

```bash
# PyLint
pylint custom/ --rcfile=.pylintrc

# Flake8
flake8 custom/ --max-line-length=88 --extend-ignore=E203,W503
```

---

## Module Development Guidelines

### 1. **Module Structure**

Follow OCA module structure:

```
custom/my_new_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   ├── menu.xml
│   └── my_model_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── initial_data.xml
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   └── src/
│       └── js/
├── tests/
│   ├── __init__.py
│   └── test_my_model.py
└── README.md
```

### 2. **Use the Module Generator**

Create new modules using our generator:

```bash
make create-module NAME=my_new_module
```

### 3. **Dependencies**

Declare dependencies in `__manifest__.py`:

```python
{
    'name': 'My New Module',
    'version': '19.0.1.0.0',
    'depends': [
        'base',
        'account',  # OCA module
        'ipai_core',  # Our custom base module
    ],
    ...
}
```

### 4. **Security Rules**

Always define security rules in `security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,0,0,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

### 5. **Avoid Common Pitfalls**

❌ **Don't**:
- Hardcode credentials or secrets
- Use `sudo()` without justification
- Skip security rules
- Write N+1 queries
- Ignore OCA guidelines

✅ **Do**:
- Use environment variables for config
- Document why `sudo()` is needed
- Always define access rules
- Use `read_group()` for aggregations
- Follow OCA structure

---

## Testing Requirements

### 1. **Minimum Test Coverage**

All new features must include:

- ✅ **Unit tests**: Test individual methods/functions
- ✅ **Integration tests**: Test module interactions
- ✅ **E2E tests** (if applicable): Test complete workflows

### 2. **Test Structure**

```python
from odoo.tests import TransactionCase

class TestExpenseReport(TransactionCase):
    """Test expense report functionality."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.ExpenseReport = self.env['expense.report']
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })

    def test_create_expense_report(self):
        """Test expense report creation."""
        report = self.ExpenseReport.create({
            'employee_id': self.employee.id,
            'name': 'Test Report',
        })
        self.assertEqual(report.state, 'draft')
        self.assertTrue(report.name.startswith('EXP'))
```

### 3. **Running Tests**

```bash
# All tests
make test

# Specific module
python -m pytest tests/unit/test_my_module.py -v

# With coverage
pytest tests/ --cov=custom/my_module --cov-report=html
```

---

## Documentation Standards

### 1. **Module README**

Every module must have a `README.md`:

```markdown
# Module Name

## Description

Brief description of what the module does.

## Features

- Feature 1
- Feature 2

## Configuration

How to configure the module.

## Usage

How to use the module.

## Technical Details

- Models
- Views
- Business Logic

## Credits

**Author**: Your Name
**Maintainer**: InsightPulse AI
```

### 2. **Inline Documentation**

Document complex logic:

```python
def complex_calculation(self, values):
    """Complex business logic explanation.

    This method performs a multi-step calculation:
    1. Validates input values
    2. Applies business rules
    3. Calculates final result

    Business Rules:
    - Rule 1: If amount > 10000, requires approval
    - Rule 2: Tax rate varies by category
    """
    # Step 1: Validate
    if not values:
        raise ValidationError("Values cannot be empty")

    # Step 2: Apply rules
    # (explain complex logic here)
```

### 3. **Update Documentation**

When adding features:
- ✅ Update module README
- ✅ Update main README if needed
- ✅ Update CHANGELOG.md
- ✅ Update relevant docs/ files

---

## Pre-Commit Guardrails

**🛡️ Prevent common mistakes before they reach CI/CD**

### 1. **Install Pre-Commit Hooks (Recommended)**

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks on all files
pre-commit run --all-files
```

### 2. **Local Validation Script**

Run this before committing:

```bash
#!/bin/bash
# save as: scripts/pre-flight-check.sh

set -e

echo "🔍 Running pre-flight checks..."

# 1. Spec validation
echo "📋 Validating platform spec..."
python3 scripts/validate_spec.py

# 2. Code formatting
echo "🎨 Checking code formatting..."
black --check . || echo "⚠️  Run: black ."
isort --check-only . || echo "⚠️  Run: isort ."

# 3. Linting
echo "🔍 Running linters..."
flake8 addons/ scripts/ --max-line-length=120 --extend-ignore=E203,W503 || echo "⚠️  Linting issues found"

# 4. Security checks
echo "🔒 Checking for secrets..."
if grep -r "sk-" --include="*.py" --include="*.yml" --include="*.yaml" .; then
  echo "❌ ERROR: Potential API keys found!"
  exit 1
fi

# 5. Test compilation
echo "🧪 Compiling Python modules..."
python -m compileall agents workflows memory addons || echo "⚠️  Compilation issues"

echo "✅ Pre-flight checks complete!"
```

Make it executable:

```bash
chmod +x scripts/pre-flight-check.sh
./scripts/pre-flight-check.sh
```

### 3. **Automated Checks (Mandatory)**

Before pushing, run:

```bash
# Full validation suite
make validate

# Or individual checks
make lint          # Code linting
make format-check  # Code formatting
make test          # Run tests
make spec-validate # Platform spec validation
```

### 4. **Guardrail Checklist**

Before every commit:

- [ ] ✅ Spec validation passes (`python3 scripts/validate_spec.py`)
- [ ] ✅ No secrets in code (check `.env.example` for config)
- [ ] ✅ Code formatted (`black .` and `isort .`)
- [ ] ✅ Linting passes (`make lint`)
- [ ] ✅ Tests pass locally (`make test`)
- [ ] ✅ Documentation updated (README, spec, CHANGELOG)

### 5. **Common Gotchas**

❌ **Don't commit**:
- API keys, tokens, passwords
- `__pycache__/`, `*.pyc`, `.env`
- Large binary files (use Git LFS)
- Merge conflict markers
- `TODO` markers in production code

✅ **Do commit**:
- `.env.example` with placeholder values
- Updated spec when adding workflows/docs
- Tests for new features
- Migration scripts for DB changes

---

## Submitting Changes

### Pull Request Checklist

Before submitting a PR, ensure:

#### **Platform Spec & Architecture (Required)**
- [ ] ✅ Platform spec validation passes (`python3 scripts/validate_spec.py`)
- [ ] ✅ Spec updated if adding workflows/docs/services
- [ ] ✅ Architecture changes documented in `docs/architecture.md`

#### **Code Quality (Required)**
- [ ] ✅ Code follows OCA guidelines
- [ ] ✅ All tests pass (`make test`)
- [ ] ✅ Linting passes (`make lint`)
- [ ] ✅ Type hints added (Python 3.11+)
- [ ] ✅ Docstrings added (Google style)

#### **Testing (Required)**
- [ ] ✅ Unit tests written
- [ ] ✅ Integration tests written (if applicable)
- [ ] ✅ E2E tests written (if applicable)
- [ ] ✅ Test coverage ≥ 80%

#### **Documentation (Required)**
- [ ] ✅ Module README updated
- [ ] ✅ Main README updated (if needed)
- [ ] ✅ CHANGELOG.md updated
- [ ] ✅ Relevant `docs/` files updated
- [ ] ✅ API documentation added (if new endpoints)

#### **Security & Best Practices (Required)**
- [ ] ✅ No hardcoded secrets (use environment variables)
- [ ] ✅ No TODO markers in production code
- [ ] ✅ Security rules defined (`ir.model.access.csv`)
- [ ] ✅ Commit messages follow convention

#### **Git Hygiene (Required)**
- [ ] ✅ Branch is up-to-date with main (`git rebase upstream/main`)
- [ ] ✅ Commits are atomic and well-described
- [ ] ✅ No merge conflicts

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows OCA guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

---

## CI/CD Pipeline & Required Checks

**📊 Understanding our CI/CD architecture (PR #377)**

### Pipeline Architecture

Our CI/CD follows a **spec-driven approach** with guardrails at every stage:

```
┌─────────────────────────────────────────────────────┐
│  1. Push/PR Trigger                                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  2. Required Checks (Must Pass)                      │
│                                                      │
│  ✅ Spec Guard - Validates platform_spec.json       │
│  ✅ CI Unified - Quality checks + tests + security  │
│  ✅ CI - Code Quality & Tests - Odoo module tests   │
│  ✅ Deploy Gates - Pre-deployment validation        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  3. Supporting Checks (Informational)                │
│                                                      │
│  ⚠️  Dependency Scanning - Security vulnerabilities │
│  ⚠️  Automation Health - Infrastructure health      │
│  ⚠️  Documentation - Docs validation                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  4. Code Review (Manual)                             │
│                                                      │
│  👥 Maintainer review                               │
│  💬 Feedback & iteration                            │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  5. Merge to main                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  6. Production Deployment (Automatic)                │
│                                                      │
│  🚀 cd-odoo-prod.yml triggers                       │
│  📦 Docker compose pull/up                          │
│  🌐 Deploy portal (insightpulseai.net)             │
│  🔧 Update nginx config                             │
│  ✅ Triple smoke tests (ERP + Portal + Auth)       │
└─────────────────────────────────────────────────────┘
```

### Required Status Checks

These **must pass** before your PR can merge:

#### **1. Spec Guard**
```yaml
Workflow: .github/workflows/spec-guard.yml
Purpose: Validates spec/platform_spec.json against schema
Runs: On changes to spec/, docs/, .github/workflows/
```

**What it checks:**
- ✅ JSON schema validation
- ✅ All referenced docs files exist
- ✅ All referenced workflow files exist

**How to pass:**
```bash
python3 scripts/validate_spec.py
```

#### **2. CI Unified**
```yaml
Workflow: .github/workflows/ci-unified.yml
Purpose: Unified CI pipeline for quality + tests + security
Runs: On all PRs and pushes to main
```

**What it checks:**
- ✅ Code quality (black, isort, flake8, pylint)
- ✅ Python tests (pytest with coverage)
- ✅ Security scans (basic vulnerability detection)

**How to pass:**
```bash
make lint
make test
```

#### **3. CI - Code Quality & Tests**
```yaml
Workflow: .github/workflows/ci-consolidated.yml
Purpose: Comprehensive code quality and Odoo module tests
Runs: On all PRs (except docs-only changes)
```

**What it checks:**
- ✅ Odoo module tests
- ✅ Pre-commit hooks
- ✅ Code formatting and linting

**How to pass:**
```bash
make test-odoo
pre-commit run --all-files
```

#### **4. Deploy Gates**
```yaml
Workflow: .github/workflows/deploy-gates.yml
Purpose: Pre-deployment quality gates
Runs: On PRs to main
```

**What it checks:**
- ✅ Claude config validation
- ✅ DBML schema compilation (if exists)
- ✅ No TODO markers in generated SQL
- ✅ Repository structure validation

**How to pass:**
```bash
# Run deploy gates locally
scripts/deploy-gates-local.sh
```

### Supporting Checks (Informational)

These provide **valuable feedback** but won't block your PR:

- **Dependency Scanning** - Security vulnerability reports
- **Automation Health** - Infrastructure health monitoring
- **Documentation** - Docs link validation

### Branch Protection Rules

The `main` branch requires:
- ✅ All 4 required checks must pass
- ✅ At least 1 approval from maintainers
- ✅ Branch must be up-to-date with main
- ✅ No force pushes allowed

### Workflow Documentation

See comprehensive workflow documentation:
- `.github/workflows/README.md` - Workflow guide
- `docs/pr-377-fixes.md` - Recent CI/CD improvements
- `docs/guides/workflows-ci-cd.md` - CI/CD best practices

---

## Review Process

### 1. **Automated Checks**

Your PR will be automatically checked for:

#### **Required (Must Pass):**
- ✅ Spec Guard - Platform spec validation
- ✅ CI Unified - Quality + tests + security
- ✅ Code Quality & Tests - Odoo module tests
- ✅ Deploy Gates - Pre-deployment validation

#### **Informational (Advisory):**
- ⚠️ Dependency Scanning - Vulnerability reports
- ⚠️ Automation Health - Infrastructure monitoring
- ⚠️ Documentation - Docs validation

### 2. **Code Review**

Maintainers will review for:
- Code quality
- Test coverage
- Documentation
- Performance
- Security

### 3. **Feedback & Iteration**

- Address review comments
- Push updates to your branch
- Re-request review when ready

### 4. **Merge**

Once approved:
- PR will be merged to main
- Changes will be deployed in next release

---

## Questions?

- **GitHub Issues**: [Open an issue](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **GitHub Discussions**: [Start a discussion](https://github.com/jgtolentino/insightpulse-odoo/discussions)
- **Email**: support@insightpulseai.net

---

## License

By contributing, you agree that your contributions will be licensed under the LGPL-3.0 License.

---

**Thank you for contributing to InsightPulse Odoo!** 🎉
