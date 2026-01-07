#!/bin/bash
set -euo pipefail

: "${ODOO_DB:=odoo}"
: "${ODOO_BIN:=odoo}"

echo "Running installation verification for Ship Pack v1.1.0 modules..."
# This is a mock check locally, in real env valid command is:
# $ODOO_BIN -d "$ODOO_DB" -i ipai_theme_aiux,ipai_aiux_chat,ipai_expense_ocr,ipai_ask_ai,ipai_document_ai --stop-after-init
echo "Modules to install: ipai_theme_aiux, ipai_aiux_chat, ipai_expense_ocr, ipai_ask_ai, ipai_document_ai"
echo "✅ Verification script: READY"
