# 🚀 CI/CD Setup Guide - InsightPulse Odoo

Complete guide for the continuous integration and deployment pipeline for InsightPulse Odoo modules and OCA integrations.

## 📋 Table of Contents

- [Overview](#overview)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Local Development](#local-development)
- [Docker Testing](#docker-testing)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Module Testing](#module-testing)
- [OCA Integration](#oca-integration)
- [Troubleshooting](#troubleshooting)

---

## Overview

The InsightPulse Odoo project uses a comprehensive CI/CD pipeline with multiple workflows:

### Automated Workflows

1. **OCA Fetch & Test** (`.github/workflows/oca-fetch-test.yml`)
   - Validates OCA requirements
   - Tests fetch_oca.sh script
   - Checks branch availability
   - Runs weekly update checks
   - Comments on PRs with results

2. **Odoo Module Auto-Test** (`.github/workflows/odoo-module-test.yml`)
   - Detects changed modules automatically
   - Builds test Docker image
   - Runs module tests in isolation
   - Generates test reports
   - Comments on PRs with results

3. **Odoo CI** (`.github/workflows/odoo-ci.yml`)
   - Code linting (ruff, flake8, pylint-odoo)
   - Security scanning (bandit)
   - Manifest validation
   - Documentation checks

4. **Basic CI** (`.github/workflows/ci.yml`)
   - Fast lint and test checks
   - Runs on every push/PR

### Manual Workflows

All workflows support manual triggering via `workflow_dispatch` for on-demand testing.

---

## GitHub Actions Workflows

### OCA Fetch & Test Workflow

**File**: `.github/workflows/oca-fetch-test.yml`

**Triggers:**
- Push to main/develop (OCA files changed)
- Pull requests (OCA files changed)
- Weekly schedule (Monday 2 AM)
- Manual dispatch

**Jobs:**

1. **validate-oca-requirements**
   - Validates `vendor/oca_requirements.txt` format
   - Checks OCA branch availability using `git ls-remote`
   - Outputs: `repos_changed`

2. **test-oca-fetch**
   - Syntax checks `scripts/fetch_oca.sh`
   - Executes fetch script
   - Verifies cloned modules
   - Uploads artifacts

3. **build-docker-with-oca**
   - Builds Docker image with OCA modules
   - Tests image size and functionality

4. **validate-oca-modules**
   - Fetches OCA modules
   - Validates module manifests
   - Checks version compatibility

5. **check-oca-updates** (scheduled only)
   - Checks for new OCA commits
   - Creates GitHub issue with update info

6. **pr-comment-oca-changes** (PRs only)
   - Analyzes OCA changes
   - Posts detailed comment on PR

**Usage Example:**

```bash
# Trigger manually via GitHub UI
# Or modify vendor/oca_requirements.txt and push
```

### Odoo Module Auto-Test Workflow

**File**: `.github/workflows/odoo-module-test.yml`

**Triggers:**
- Push to main/develop (addon files changed)
- Pull requests (addon files changed)
- Manual dispatch with module selection

**Jobs:**

1. **detect-changes**
   - Analyzes git diff
   - Identifies changed modules
   - Supports manual module selection

2. **build-test-image**
   - Builds `Dockerfile.test`
   - Uploads image as artifact
   - Uses build cache for speed

3. **test-modules**
   - Spins up PostgreSQL service
   - Runs tests for each module
   - Generates test reports

4. **code-coverage**
   - Collects coverage metrics
   - Uploads coverage reports

5. **pr-comment**
   - Posts test results to PR
   - Shows passed/failed modules

**Manual Trigger:**

```bash
# Via GitHub Actions UI:
# Workflow: Odoo Module Auto-Test
# Inputs:
#   modules: ipai_expense,ipai_subscriptions
#   test_tags: at_install,post_install
```

---

## Local Development

### CI Runner Script

**File**: `scripts/ci-runner.sh`

**Usage:**

```bash
# Run all checks
./scripts/ci-runner.sh full

# Run specific checks
./scripts/ci-runner.sh lint
./scripts/ci-runner.sh format --fix
./scripts/ci-runner.sh security
./scripts/ci-runner.sh test --modules ipai_expense
./scripts/ci-runner.sh validate
./scripts/ci-runner.sh oca-fetch
./scripts/ci-runner.sh docker-build

# Run with strict mode (fail on warnings)
./scripts/ci-runner.sh full --strict
```

**Commands:**

| Command | Description |
|---------|-------------|
| `lint` | Run ruff, flake8, pylint-odoo |
| `format` | Check/fix code formatting (black, isort) |
| `security` | Run bandit security scan |
| `test` | Run module tests |
| `validate` | Validate module manifests |
| `oca-fetch` | Test OCA fetch script |
| `docker-build` | Build Docker test image |
| `full` | Run all checks |

**Options:**

- `--modules LIST`: Test specific modules
- `--fix`: Auto-fix formatting issues
- `--strict`: Exit on first error/warning

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install pre-commit ruff black isort flake8 pylint-odoo bandit

# Install pre-commit hooks
pre-commit install
```

---

## Docker Testing

### Test Docker Image

**File**: `Dockerfile.test`

**Features:**
- Based on official Odoo 19.0 image
- Includes pytest, coverage, pylint
- Pre-fetches OCA modules at build time
- Configured for testing environment

**Build:**

```bash
docker build -f Dockerfile.test -t insightpulse-odoo:test .
```

**Run Tests:**

```bash
docker-compose up -d postgres

docker run --rm \
  --network host \
  -e DB_HOST=localhost \
  -e DB_USER=odoo \
  -e DB_PASSWORD=odoo \
  insightpulse-odoo:test \
  bash /usr/local/bin/test-odoo-modules.sh
```

### Test Module Script

**File**: `scripts/test-odoo-modules.sh`

**Usage:**

```bash
# Test all modules
./scripts/test-odoo-modules.sh

# Test specific modules
./scripts/test-odoo-modules.sh ipai_expense,ipai_subscriptions

# With environment variables
DB_HOST=localhost \
DB_USER=odoo \
DB_PASSWORD=odoo \
TEST_TAGS=at_install \
./scripts/test-odoo-modules.sh
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_USER` | odoo | Database user |
| `DB_PASSWORD` | odoo | Database password |
| `TEST_TAGS` | (empty) | Odoo test tags |

---

## Pre-commit Hooks

**File**: `.pre-commit-config.yaml`

**Hooks:**
- `trailing-whitespace`: Remove trailing whitespace
- `end-of-file-fixer`: Ensure files end with newline
- `check-yaml`: Validate YAML syntax
- `check-added-large-files`: Block large files
- `check-merge-conflict`: Detect merge conflicts
- `check-ast`: Validate Python syntax
- `black`: Format Python code (line length 88)
- `isort`: Sort Python imports
- `flake8`: Lint Python code
- `bandit`: Security vulnerability scan
- `markdownlint`: Lint Markdown files

**Install:**

```bash
pip install pre-commit
pre-commit install
```

**Run Manually:**

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run black --all-files
```

**Bypass (use sparingly):**

```bash
git commit --no-verify -m "message"
```

---

## Module Testing

### Test Structure

Each Odoo module should have a `tests/` directory:

```
addons/
├── insightpulse/
│   └── finance/
│       └── ipai_expense/
│           ├── __manifest__.py
│           ├── models/
│           ├── views/
│           └── tests/
│               ├── __init__.py
│               ├── test_expense_creation.py
│               ├── test_expense_validation.py
│               └── test_expense_approval.py
```

### Writing Tests

```python
# tests/test_expense_creation.py
from odoo.tests import TransactionCase, tagged

@tagged('at_install', 'post_install')
class TestExpenseCreation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Expense = self.env['ipai.expense']
        self.user = self.env.ref('base.user_admin')

    def test_create_expense(self):
        """Test creating a basic expense record"""
        expense = self.Expense.create({
            'name': 'Test Expense',
            'amount': 100.00,
            'employee_id': self.user.partner_id.id,
        })

        self.assertEqual(expense.name, 'Test Expense')
        self.assertEqual(expense.amount, 100.00)
        self.assertEqual(expense.state, 'draft')
```

### Test Tags

- `at_install`: Run when module is installed
- `post_install`: Run after installation completes
- `-at_install`: Exclude from install-time tests
- Custom tags: Define your own for filtering

### Running Tests Locally

```bash
# Run all tests for a module
odoo -c odoo.conf -d test_db -i ipai_expense --test-enable --stop-after-init

# Run specific test tags
odoo -c odoo.conf -d test_db -i ipai_expense --test-enable --test-tags at_install --stop-after-init

# Run without demo data
odoo -c odoo.conf -d test_db -i ipai_expense --test-enable --without-demo=all --stop-after-init
```

---

## OCA Integration

### OCA Requirements File

**File**: `vendor/oca_requirements.txt`

**Format:**

```
# OCA Requirements for Docker Build
# Format: REPO_URL BRANCH

https://github.com/OCA/contract 19.0
https://github.com/OCA/server-tools 19.0
https://github.com/OCA/reporting-engine 19.0
```

**Features:**
- Comment lines starting with `#`
- Empty lines ignored
- Format: `REPO_URL BRANCH`

### OCA Fetch Script

**File**: `scripts/fetch_oca.sh`

**Usage:**

```bash
# Fetch OCA modules
./scripts/fetch_oca.sh vendor/oca_requirements.txt /path/to/addons/oca
```

**Features:**
- Shallow clones (`--depth 1`) for minimal size
- Comment and empty line support
- Error validation
- Branch availability checking

### Weekly OCA Update Checks

The workflow automatically:
1. Runs every Monday at 2 AM UTC
2. Checks latest commits for all OCA repos
3. Creates a GitHub issue with update info
4. Labels: `oca`, `dependencies`, `automated`

**Manual Check:**

```bash
# Check branch availability
git ls-remote --heads https://github.com/OCA/contract.git | grep 19.0

# Clone specific branch
git clone --depth 1 --branch 19.0 https://github.com/OCA/contract
```

---

## Troubleshooting

### Common Issues

**1. OCA Fetch Fails**

```bash
# Check branch availability
git ls-remote --heads https://github.com/OCA/REPO_NAME | grep BRANCH

# Check script syntax
bash -n scripts/fetch_oca.sh

# Run with verbose output
bash -x scripts/fetch_oca.sh vendor/oca_requirements.txt /tmp/test
```

**2. Module Tests Fail**

```bash
# Check PostgreSQL connection
pg_isready -h localhost -p 5432 -U odoo

# Check Odoo configuration
odoo -c odoo.conf --version

# Run tests with debug logging
odoo -c odoo.conf -d test_db -i MODULE --test-enable --log-level=debug
```

**3. Docker Build Fails**

```bash
# Clear Docker cache
docker builder prune -af

# Build without cache
docker build --no-cache -f Dockerfile.test -t insightpulse-odoo:test .

# Check disk space
df -h
```

**4. Pre-commit Hooks Fail**

```bash
# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install
```

### Debug Mode

Enable debug output in scripts:

```bash
# CI Runner
bash -x scripts/ci-runner.sh full

# Module Tests
DEBUG=1 bash scripts/test-odoo-modules.sh

# OCA Fetch
bash -x scripts/fetch_oca.sh vendor/oca_requirements.txt /tmp/test
```

### Getting Help

1. Check workflow logs in GitHub Actions
2. Review script output in terminal
3. Check Docker logs: `docker logs CONTAINER_ID`
4. Enable verbose mode: `set -x` in shell scripts

---

## Best Practices

### For Module Development

1. **Write tests for all new features**
   - Unit tests for models
   - Integration tests for workflows
   - UI tests for critical paths

2. **Run CI checks before committing**
   ```bash
   ./scripts/ci-runner.sh full
   ```

3. **Keep modules small and focused**
   - Single responsibility principle
   - Clear dependencies
   - Well-documented

4. **Follow OCA guidelines**
   - Use OCA module structure
   - Follow coding conventions
   - Write README.rst

### For OCA Integration

1. **Pin OCA module versions** (in `vendor/oca_repos.lock`)
2. **Test OCA updates** before deploying
3. **Document OCA dependencies** in module manifests
4. **Review OCA migration guides** for version upgrades

### For CI/CD

1. **Keep workflows fast** (< 10 minutes)
2. **Use caching** for dependencies
3. **Run tests in parallel** where possible
4. **Fail fast** on critical errors
5. **Generate artifacts** for debugging

---

## Additional Resources

- [Odoo Testing Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools/wiki)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

**Last Updated**: 2025-10-30
**Odoo Version**: 19.0
**Python Version**: 3.11
**PostgreSQL Version**: 16
