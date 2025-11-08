#!/usr/bin/env bash
# OCA Tools Installation Script
# Purpose: Install and configure OCA maintainer tools, repo-maintainer, and OpenUpgrade
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OCA_TOOLS_DIR="$REPO_ROOT/.oca-tools"

echo "🔧 Installing OCA Automation Tools"
echo "   Location: $OCA_TOOLS_DIR"
echo ""

# Create tools directory
mkdir -p "$OCA_TOOLS_DIR"
cd "$OCA_TOOLS_DIR"

# 1. Install maintainer-tools (validation, pre-commit checks)
echo "📦 Installing maintainer-tools..."
if [ ! -d "maintainer-tools" ]; then
  git clone --depth 1 https://github.com/OCA/maintainer-tools.git
  cd maintainer-tools
  pip3 install -q -r requirements.txt
  cd ..
  echo "   ✅ maintainer-tools installed"
else
  echo "   ⏭️  maintainer-tools already installed"
fi

# 2. Install oca-addons-repo-template (module scaffolding)
echo "📦 Installing oca-addons-repo-template..."
if [ ! -d "oca-addons-repo-template" ]; then
  git clone --depth 1 https://github.com/OCA/oca-addons-repo-template.git
  echo "   ✅ oca-addons-repo-template installed"
else
  echo "   ⏭️  oca-addons-repo-template already installed"
fi

# 3. Install repo-maintainer (dependency management)
echo "📦 Installing repo-maintainer..."
if [ ! -d "repo-maintainer" ]; then
  git clone --depth 1 https://github.com/OCA/repo-maintainer.git
  cd repo-maintainer
  pip3 install -q -e .
  cd ..
  echo "   ✅ repo-maintainer installed"
else
  echo "   ⏭️  repo-maintainer already installed"
fi

# 4. Install OpenUpgrade (migration framework)
echo "📦 Installing OpenUpgrade..."
if [ ! -d "OpenUpgrade" ]; then
  git clone --depth 1 --branch 17.0 https://github.com/OCA/OpenUpgrade.git
  echo "   ✅ OpenUpgrade installed"
else
  echo "   ⏭️  OpenUpgrade already installed"
fi

# 5. Install openupgradelib (migration utilities)
echo "📦 Installing openupgradelib..."
if [ ! -d "openupgradelib" ]; then
  git clone --depth 1 https://github.com/OCA/openupgradelib.git
  cd openupgradelib
  pip3 install -q -e .
  cd ..
  echo "   ✅ openupgradelib installed"
else
  echo "   ⏭️  openupgradelib already installed"
fi

# 6. Install oca-custom (if needed for customization patterns)
echo "📦 Installing oca-custom..."
if [ ! -d "oca-custom" ]; then
  git clone --depth 1 https://github.com/OCA/oca-custom.git
  echo "   ✅ oca-custom installed"
else
  echo "   ⏭️  oca-custom already installed"
fi

# 7. Install additional Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -q \
  click \
  jinja2 \
  manifestoo-core \
  pre-commit \
  pylint-odoo \
  ruff \
  black \
  isort

echo ""
echo "✅ OCA Tools Installation Complete"
echo ""
echo "📍 Installed tools:"
echo "   - maintainer-tools:        $OCA_TOOLS_DIR/maintainer-tools"
echo "   - oca-addons-repo-template: $OCA_TOOLS_DIR/oca-addons-repo-template"
echo "   - repo-maintainer:          $OCA_TOOLS_DIR/repo-maintainer"
echo "   - OpenUpgrade:              $OCA_TOOLS_DIR/OpenUpgrade"
echo "   - openupgradelib:           $OCA_TOOLS_DIR/openupgradelib"
echo "   - oca-custom:               $OCA_TOOLS_DIR/oca-custom"
echo ""
echo "📝 Next steps:"
echo "   1. Set up pre-commit hooks: ./scripts/setup-oca-precommit.sh"
echo "   2. Scaffold a new module:   ./scripts/oca-scaffold-module.sh my_module"
echo "   3. Update dependencies:     ./scripts/oca-update-deps.sh"
echo ""
