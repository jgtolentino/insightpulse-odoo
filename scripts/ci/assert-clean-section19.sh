#!/usr/bin/env bash
set -euo pipefail

chmod +x scripts/skillsmith_sync.py
if ! ./scripts/skillsmith_sync.py --check; then
  echo "::error::Section 19 drift detected. Run: make claude:sync-write"
  exit 1
fi
echo "Section 19 is clean."
