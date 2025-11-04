#!/usr/bin/env bash
set -euo pipefail
MOD=${1:?module}; OUT=${2:-dist}
mkdir -p "$OUT"
zip -r "$OUT/${MOD}.zip" "odoo_addons/${MOD}" -x "*/__pycache__/*" "*.pyc" ".DS_Store"
echo "Packaged $OUT/${MOD}.zip"
