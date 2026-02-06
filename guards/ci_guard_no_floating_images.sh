#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGETS=(
  "${ROOT}/runtime"
  "${ROOT}/docker-compose.yml"
  "${ROOT}/compose.yml"
)

# Patterns considered floating: :latest, :19, :18, :17, :19.0, etc. Digest-pinned is allowed.
# We allow ${VAR} images in compose (resolved at runtime), and allow @sha256 digests.
FLOATING_REGEX='image:\s*[^$][^@[:space:]]+:(latest|[0-9]+(\.[0-9]+)?)\s*$'

found=0
for t in "${TARGETS[@]}"; do
  [[ -e "${t}" ]] || continue
  hits="$(grep -RInE --include='*.yml' --include='*.yaml' --exclude-dir='.git' "${FLOATING_REGEX}" "${t}" || true)"
  if [[ -n "${hits}" ]]; then
    echo "FAIL: floating image tags detected (use digest or env-var):"
    echo "${hits}"
    found=1
  fi
done

exit "${found}"
