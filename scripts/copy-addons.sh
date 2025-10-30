#!/bin/bash
# Conditional addon copying script for Docker build
# Only copies addon directories that exist in the repository

set -e

ADDONS_SOURCE="${1:-addons}"
ADDONS_DEST="${2:-/mnt/extra-addons}"

echo "Copying addons from $ADDONS_SOURCE to $ADDONS_DEST..."

# Core addon directories (required)
CORE_ADDONS=(
    "insightpulse"
    "custom"
    "oca"
)

# Optional addon directories (copy if exists)
OPTIONAL_ADDONS=(
    "bi_superset_agent"
    "knowledge_notion_clone"
    "web_environment_ribbon"
    "web_favicon"
)

# Copy core addons (fail if missing)
for addon in "${CORE_ADDONS[@]}"; do
    if [ -d "$ADDONS_SOURCE/$addon" ]; then
        echo "✓ Copying core addon: $addon"
        cp -r "$ADDONS_SOURCE/$addon" "$ADDONS_DEST/"
    else
        echo "✗ ERROR: Core addon missing: $addon"
        exit 1
    fi
done

# Copy optional addons (skip if missing)
for addon in "${OPTIONAL_ADDONS[@]}"; do
    if [ -d "$ADDONS_SOURCE/$addon" ]; then
        echo "✓ Copying optional addon: $addon"
        cp -r "$ADDONS_SOURCE/$addon" "$ADDONS_DEST/"
    else
        echo "⊘ Skipping optional addon (not present): $addon"
    fi
done

echo "Addon copy completed successfully"
