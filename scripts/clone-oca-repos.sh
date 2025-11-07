#!/usr/bin/env bash
set -euo pipefail

# OCA Repository Cloning Script for Odoo 16 and 17
# Clones essential OCA modules for near-Enterprise/SaaS parity

VERSION="${1:-16.0}"
OCA_DIR="./oca/${VERSION}"

echo "=========================================="
echo "OCA Module Cloning Script"
echo "Target Version: ${VERSION}"
echo "Target Directory: ${OCA_DIR}"
echo "=========================================="

# Create OCA directory
mkdir -p "${OCA_DIR}"
cd "${OCA_DIR}"

# Core OCA repositories for SaaS-like parity (repo_name:repo_url format)
REPOS=(
    "account-financial-tools:https://github.com/OCA/account-financial-tools.git"
    "account-invoice-reporting:https://github.com/OCA/account-invoice-reporting.git"
    "account-reconcile:https://github.com/OCA/account-reconcile.git"
    "sale-workflow:https://github.com/OCA/sale-workflow.git"
    "purchase-workflow:https://github.com/OCA/purchase-workflow.git"
    "stock-logistics-warehouse:https://github.com/OCA/stock-logistics-warehouse.git"
    "stock-logistics-tracking:https://github.com/OCA/stock-logistics-tracking.git"
    "stock-logistics-barcode:https://github.com/OCA/stock-logistics-barcode.git"
    "hr:https://github.com/OCA/hr.git"
    "hr-expense:https://github.com/OCA/hr-expense.git"
    "hr-timesheet:https://github.com/OCA/hr-timesheet.git"
    "reporting-engine:https://github.com/OCA/reporting-engine.git"
    "mis-builder:https://github.com/OCA/mis-builder.git"
    "server-tools:https://github.com/OCA/server-tools.git"
    "server-ux:https://github.com/OCA/server-ux.git"
    "web:https://github.com/OCA/web.git"
    "queue:https://github.com/OCA/queue.git"
    "project:https://github.com/OCA/project.git"
    "timesheet:https://github.com/OCA/timesheet.git"
)

echo ""
echo "Cloning ${#REPOS[@]} OCA repositories on branch ${VERSION}..."
echo ""

CLONED=0
FAILED=0

for repo in "${REPOS[@]}"; do
    repo_name="${repo%%:*}"
    repo_url="${repo#*:}"

    if [ -d "${repo_name}" ]; then
        echo "⏭️  Skipping ${repo_name} (already exists)"
        continue
    fi

    echo "📦 Cloning ${repo_name}..."

    if git clone --branch "${VERSION}" --depth 1 "${repo_url}" "${repo_name}" 2>/dev/null; then
        echo "✅ Successfully cloned ${repo_name}"
        ((CLONED++))
    else
        echo "❌ Failed to clone ${repo_name} (branch ${VERSION} may not exist)"
        ((FAILED++))
    fi
    echo ""
done

echo "=========================================="
echo "OCA Cloning Summary"
echo "=========================================="
echo "✅ Successfully cloned: ${CLONED}"
echo "❌ Failed: ${FAILED}"
echo "📁 Total directories: $(ls -1 | wc -l)"
echo ""
echo "OCA modules installed at: ${OCA_DIR}"
echo ""
echo "Next steps:"
echo "1. Review cloned modules: ls -la ${OCA_DIR}"
echo "2. Start Odoo: docker-compose -f docker-compose.odoo${VERSION%.*}.yml up -d"
echo "3. Install modules via Odoo Apps menu"
echo "=========================================="
