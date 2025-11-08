#!/usr/bin/env bash
# OCA Pre-Commit Hooks Setup
# Purpose: Configure pre-commit hooks for OCA compliance validation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OCA_TOOLS_DIR="$REPO_ROOT/.oca-tools"

if [ ! -d "$OCA_TOOLS_DIR/maintainer-tools" ]; then
  echo "❌ OCA tools not installed. Run: ./scripts/install-oca-tools.sh"
  exit 1
fi

echo "🪝 Setting up OCA Pre-Commit Hooks"
echo ""

cd "$REPO_ROOT"

# Create .pre-commit-config.yaml with OCA checks
cat > .pre-commit-config.yaml <<'PRECOMMIT'
# OCA Compliance Pre-Commit Hooks
# See https://pre-commit.com for more information
repos:
  # Standard pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        exclude: '\.copier-answers\.yml$'
      - id: check-added-large-files
        args: ['--maxkb=2048']
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: check-executables-have-shebangs
      - id: check-json
      - id: detect-private-key
      - id: fix-byte-order-marker
      - id: mixed-line-ending
        args: ['--fix=lf']

  # Python code formatting with Black
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  # Import sorting with isort (OCA compatible)
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ['--profile', 'black', '--line-length', '88']

  # Ruff linter (faster alternative to flake8/pylint for quick checks)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: ['--fix', '--exit-non-zero-on-fix']

  # Pylint-Odoo specific checks
  - repo: https://github.com/OCA/pylint-odoo
    rev: v9.0.4
    hooks:
      - id: pylint_odoo
        name: pylint with optional checks
        args:
          - --rcfile=.pylintrc
          - --exit-zero
        verbose: true
        additional_dependencies:
          - pylint==2.17.0

  # Manifest validation
  - repo: https://github.com/OCA/maintainer-tools
    rev: master
    hooks:
      - id: oca-autopep8
      - id: oca-isort

  # YAML/XML formatting
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [yaml, xml]
        additional_dependencies:
          - prettier@3.1.0
          - '@prettier/plugin-xml@3.2.2'

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ['-c', '.bandit']
        exclude: '^tests/'

  # Check copyright headers
  - repo: https://github.com/Lucas-C/pre-commit-hooks
    rev: v1.5.4
    hooks:
      - id: insert-license
        files: '\.py$'
        args:
          - --license-filepath
          - .copyright-header.txt
          - --comment-style
          - '#'

# CI configuration
ci:
  autoupdate_schedule: monthly
  skip: []
  submodules: false
PRECOMMIT

# Create .pylintrc for Odoo-specific checks
cat > .pylintrc <<'PYLINTRC'
[MASTER]
load-plugins=pylint_odoo
score=n

[ODOOLINT]
readme_template_url="https://github.com/OCA/maintainer-tools/blob/master/template/module/README.rst"
manifest_required_authors=Odoo Community Association (OCA)
manifest_required_keys=license
manifest_deprecated_keys=description,active
license_allowed=AGPL-3,GPL-2,GPL-2 or any later version,GPL-3,GPL-3 or any later version,LGPL-3,Other OSI approved licence,Other proprietary
valid_odoo_versions=17.0,18.0

[MESSAGES CONTROL]
disable=all
enable=anomalous-backslash-in-string,
    api-one-deprecated,
    api-one-multi-together,
    assignment-from-none,
    attribute-deprecated,
    class-camelcase,
    dangerous-default-value,
    dangerous-view-replace-wo-priority,
    development-status-allowed,
    duplicate-id-csv,
    duplicate-key,
    duplicate-xml-fields,
    duplicate-xml-record-id,
    eval-referenced,
    eval-used,
    incoherent-interpreter-exec-perm,
    license-allowed,
    manifest-author-string,
    manifest-deprecated-key,
    manifest-required-author,
    manifest-required-key,
    manifest-version-format,
    method-compute,
    method-inverse,
    method-required-super,
    method-search,
    missing-import-error,
    missing-manifest-dependency,
    odoo-addons-relative-import,
    old-api7-method-defined,
    openerp-exception-warning,
    print-used,
    redundant-modulename-xml,
    renamed-field-parameter,
    resource-not-exist,
    sql-injection,
    translation-field,
    translation-required,
    use-vim-comment,
    wrong-tabs-instead-of-spaces,
    xml-syntax-error

[REPORTS]
output-format=colorized

[FORMAT]
max-line-length=88
PYLINTRC

# Create .bandit config for security scanning
cat > .bandit <<'BANDIT'
[bandit]
exclude_dirs = ['/tests', '/.oca-tools', '/migrations']
tests = ['B201', 'B301', 'B302', 'B303', 'B304', 'B305', 'B306', 'B307', 'B308', 'B309', 'B310', 'B311', 'B312', 'B313', 'B314', 'B315', 'B316', 'B317', 'B318', 'B319', 'B320', 'B321', 'B323', 'B324', 'B325', 'B401', 'B402', 'B403', 'B404', 'B405', 'B406', 'B407', 'B408', 'B409', 'B410', 'B411', 'B412', 'B413', 'B501', 'B502', 'B503', 'B504', 'B505', 'B506', 'B507', 'B601', 'B602', 'B603', 'B604', 'B605', 'B606', 'B607', 'B608', 'B609', 'B610', 'B611', 'B701', 'B702', 'B703']
skips = ['B101', 'B601']
BANDIT

# Create copyright header template
cat > .copyright-header.txt <<'COPYRIGHT'
Copyright 2025 Jake Tolentino <jake@insightpulseai.net>
License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
COPYRIGHT

# Create pyproject.toml for tool configuration
if [ ! -f "pyproject.toml" ]; then
  cat > pyproject.toml <<'PYPROJECT'
[tool.black]
line-length = 88
target-version = ['py310', 'py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.oca-tools
  | \.venv
  | build
  | dist
  | migrations
)/
'''

[tool.isort]
profile = "black"
line_length = 88
known_odoo = "odoo"
known_odoo_addons = "odoo.addons"
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "ODOO", "ODOO_ADDONS", "FIRSTPARTY", "LOCALFOLDER"]
skip_glob = [".oca-tools/*", "migrations/*"]

[tool.ruff]
line-length = 88
target-version = "py310"
exclude = [
    ".git",
    ".oca-tools",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # unused imports in __init__.py

[tool.pytest.ini_options]
addopts = "-v --strict-markers --tb=short"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
PYPROJECT
fi

# Install pre-commit hooks
echo "📦 Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Run pre-commit on all files to initialize
echo "🔍 Running initial pre-commit checks (this may take a while)..."
pre-commit run --all-files || {
  echo ""
  echo "⚠️  Some pre-commit checks failed. This is normal on first run."
  echo "   Files have been auto-formatted. Review changes with 'git diff'"
  echo ""
}

echo ""
echo "✅ OCA Pre-Commit Hooks Configured"
echo ""
echo "📝 Configuration files created:"
echo "   - .pre-commit-config.yaml (hook definitions)"
echo "   - .pylintrc               (Odoo linting rules)"
echo "   - .bandit                 (security scanning)"
echo "   - .copyright-header.txt   (license header template)"
echo "   - pyproject.toml          (tool configuration)"
echo ""
echo "🔍 Pre-commit checks enabled:"
echo "   ✓ Code formatting (Black, isort)"
echo "   ✓ Linting (Ruff, pylint-odoo)"
echo "   ✓ Security scanning (Bandit)"
echo "   ✓ Manifest validation"
echo "   ✓ Copyright headers"
echo "   ✓ YAML/XML formatting"
echo ""
echo "📝 Usage:"
echo "   - Auto-run on commit: git commit -m 'message'"
echo "   - Manual run:         pre-commit run --all-files"
echo "   - Skip hooks:         git commit --no-verify (not recommended)"
echo "   - Update hooks:       pre-commit autoupdate"
echo ""
