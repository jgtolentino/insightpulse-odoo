#!/bin/bash
set -e

echo "🚨 Emergency documentation deployment"

# 1. Clean build
echo "🧹 Cleaning previous build artifacts..."
rm -rf docs/_site
rm -f docs/GENERATED_ODOO_DOCS.*

# 2. Generate module docs (safe mode)
echo "📚 Generating module documentation..."

if [ -f "scripts/generate_odoo_docs.py" ]; then
    if python3 scripts/generate_odoo_docs.py --format all; then
        echo "✅ Documentation generated successfully"
    else
        echo "⚠️  Documentation generation failed, creating fallback..."

        # Create fallback documentation
        mkdir -p docs

        cat > docs/GENERATED_ODOO_DOCS.md << 'EOF'
# InsightPulse Odoo API Documentation

**Status**: Documentation build temporarily unavailable

The automated documentation generation is currently experiencing issues.
Please check back soon or view the source code directly.

## Quick Links

- [Source Code](https://github.com/jgtolentino/insightpulse-odoo)
- [Module Directory](https://github.com/jgtolentino/insightpulse-odoo/tree/main/odoo/modules)
- [Documentation](https://github.com/jgtolentino/insightpulse-odoo/tree/main/docs)
EOF

        cat > docs/GENERATED_ODOO_DOCS.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>InsightPulse Odoo - Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #0d1117;
            color: #c9d1d9;
        }
        .error {
            background: #ffebee;
            border: 1px solid #f44336;
            padding: 15px;
            border-radius: 4px;
            color: #c62828;
        }
        a {
            color: #58a6ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>🚀 InsightPulse Odoo Documentation</h1>

    <div class="error">
        <h3>⚠️ Documentation Build Error</h3>
        <p>The documentation site is temporarily experiencing build issues. Please check back soon.</p>
    </div>

    <h2>Quick Links</h2>
    <ul>
        <li><a href="https://github.com/jgtolentino/insightpulse-odoo">View Source Code</a></li>
        <li><a href="https://github.com/jgtolentino/insightpulse-odoo/tree/main/odoo/modules">Module Directory</a></li>
        <li><a href="https://github.com/jgtolentino/insightpulse-odoo/tree/main/docs">Documentation</a></li>
    </ul>
</body>
</html>
EOF

        cat > docs/GENERATED_ODOO_DOCS.json << 'EOF'
{
  "generated": "emergency-fallback",
  "stats": {
    "total_modules": 0,
    "total_models": 0,
    "total_fields": 0,
    "total_views": 0,
    "bir_modules": 0,
    "finance_modules": 0
  },
  "modules": [],
  "error": "Documentation generation failed - fallback created"
}
EOF

        echo "📄 Created fallback documentation files"
    fi
else
    echo "❌ Documentation generator script not found at scripts/generate_odoo_docs.py"
    exit 1
fi

# 3. Validate generated files
echo "🔍 Validating generated documentation..."

required_files=(
    "docs/GENERATED_ODOO_DOCS.md"
    "docs/GENERATED_ODOO_DOCS.html"
    "docs/GENERATED_ODOO_DOCS.json"
)

all_exist=true
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        all_exist=false
    else
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
        echo "✅ $file ($size bytes)"
    fi
done

if [ "$all_exist" = false ]; then
    echo "❌ Documentation generation incomplete"
    exit 1
fi

# 4. Display summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Documentation Deployment Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "docs/GENERATED_ODOO_DOCS.json" ]; then
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
import sys

try:
    with open('docs/GENERATED_ODOO_DOCS.json', 'r') as f:
        data = json.load(f)

    if 'error' in data:
        print('⚠️  Fallback documentation created')
    else:
        stats = data.get('stats', {})
        print(f\"✅ Modules: {stats.get('total_modules', 0)}\")
        print(f\"✅ Models: {stats.get('total_models', 0)}\")
        print(f\"✅ Fields: {stats.get('total_fields', 0)}\")
except Exception as e:
    print(f'⚠️  Could not parse JSON: {e}')
    sys.exit(1)
        " || echo "⚠️  JSON validation skipped"
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Emergency documentation deployment complete"
