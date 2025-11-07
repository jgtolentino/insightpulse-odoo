#!/bin/bash
# Auto-patch Odoo 19 OWL framework view changes

set -e

echo "🔧 Migrating Kanban views to OWL card syntax..."

# Replace kanban-box with card
find ./addons/custom -name "*.xml" -type f -exec sed -i \
  's/<kanban-box>/<card>/g; s/<\/kanban-box>/<\/card>/g' {} +

echo "✅ Migrated Kanban views to OWL card syntax"
echo "📝 Changed files:"
git diff --name-only --diff-filter=M | grep "\.xml$" || echo "No XML files changed"
