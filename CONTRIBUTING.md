# Contributing to InsightPulse Odoo

First off, thank you for considering contributing to InsightPulse Odoo! It's people like you that make InsightPulse Odoo such a great tool for the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Quality Standards](#code-quality-standards)
- [Module Development Guidelines](#module-development-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Submitting Changes](#submitting-changes)
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

## Submitting Changes

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows OCA guidelines
- [ ] All tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Tests written (unit + integration)
- [ ] README updated
- [ ] CHANGELOG.md updated
- [ ] No hardcoded secrets
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with main

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

## Review Process

### 1. **Automated Checks**

Your PR will be automatically checked for:
- ✅ Linting (pylint, flake8)
- ✅ Tests (pytest)
- ✅ Security (no secrets in code)
- ✅ OCA compliance

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
