#!/bin/bash
# Auto-patch Odoo 19 breaking changes in import statements

set -e

echo "🔧 Auto-patching Odoo 19 import statements..."

# Fix registry imports
find ./addons/custom -name "*.py" -type f -exec sed -i \
  's/from odoo import registry/from odoo.modules.registry import Registry/g' {} +

# Fix xlsxwriter imports
find ./addons/custom -name "*.py" -type f -exec sed -i \
  's/from odoo.tools.misc import xlsxwriter/import xlsxwriter/g' {} +

# Fix deprecated self._uid
find ./addons/custom -name "*.py" -type f -exec sed -i \
  's/self\._uid/self.env.uid/g' {} +

# Fix odoo.osv.Expressions
find ./addons/custom -name "*.py" -type f -exec sed -i \
  's/from odoo.osv import Expressions/from odoo.fields import Domain/g' {} +
find ./addons/custom -name "*.py" -type f -exec sed -i \
  's/Expressions\./Domain./g' {} +

echo "✅ Odoo 19 import statements patched"
echo "📝 Changed files:"
git diff --name-only
