#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

EXCLUDES=(
  "${ROOT}/templates"
  "${ROOT}/runtime"
  "${ROOT}/scripts"
  "${ROOT}/guards"
  "${ROOT}/.git"
  "${ROOT}/docs"
)

# Grep target filetypes: python/xml/js/ts
# Forbid direct version sniffing or conditional version logic.
PATTERNS=(
  'odoo\.release'
  'server_version'
  'tools\.config\.get\(.+server_version'
  'if.+(odoo|version)'
  '>=\s*18'
  '>=\s*19'
)

# Build grep exclude args
EXC_ARGS=()
for e in "${EXCLUDES[@]}"; do
  if [[ -e "${e}" ]]; then
    EXC_ARGS+=(--exclude-dir "$(basename "$e")")
  fi
done

hits_all=""
for p in "${PATTERNS[@]}"; do
  hits="$(grep -RInE "${p}" \
    --include='*.py' --include='*.xml' --include='*.js' --include='*.ts' --include='*.tsx' \
    "${ROOT}" "${EXC_ARGS[@]}" 2>/dev/null || true)"
  if [[ -n "${hits}" ]]; then
    hits_all+=$'\n'"PATTERN: ${p}"$'\n'"${hits}"$'\n'
  fi
done

if [[ -n "${hits_all}" ]]; then
  echo "FAIL: version-specific branching detected:"
  echo "${hits_all}"
  exit 1
fi

echo "OK: no version-specific branching detected."
