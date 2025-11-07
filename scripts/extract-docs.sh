#!/bin/bash
set -e

echo "📚 Extracting documentation from chore file..."

# Create directories
mkdir -p docs/architecture docs/research

# Extract DBML schema (lines 11677-11923)
echo "  Extracting DBML schema..."
sed -n '11677,11923p' chore > docs/architecture/odoo-schema.dbml

# Extract Notion→Odoo mapping (lines 233-11676)
echo "  Extracting Notion→Odoo mapping..."
sed -n '233,11676p' chore > docs/architecture/notion-odoo-complete-mapping.md

# Extract Notion Enterprise features (lines 87-231)
echo "  Extracting Notion Enterprise features..."
sed -n '87,231p' chore > docs/research/notion-enterprise-features.md

# Extract skills inventory (lines 43-86)
echo "  Extracting skills inventory..."
sed -n '43,86p' chore > docs/research/claude-skills-inventory.md

echo "✅ Documentation extraction complete!"
echo ""
echo "Created files:"
echo "  - docs/architecture/odoo-schema.dbml"
echo "  - docs/architecture/notion-odoo-complete-mapping.md"
echo "  - docs/research/notion-enterprise-features.md"
echo "  - docs/research/claude-skills-inventory.md"
