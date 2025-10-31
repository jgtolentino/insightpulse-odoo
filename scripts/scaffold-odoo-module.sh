#!/bin/bash
# Odoo Module Scaffolding Tool
# Generates complete module structure following OCA conventions

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
MODULE_NAME=""
CATEGORY="Uncategorized"
AUTHOR="InsightPulse"
DEPENDS="base"
MODELS=""
LICENSE="LGPL-3"
VERSION="19.0.1.0.0"
OUTPUT_DIR="addons/custom"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            MODULE_NAME="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --author)
            AUTHOR="$2"
            shift 2
            ;;
        --depends)
            DEPENDS="$2"
            shift 2
            ;;
        --models)
            MODELS="$2"
            shift 2
            ;;
        --license)
            LICENSE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --name MODULE_NAME [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --name NAME         Module name (required, e.g., expense_management)"
            echo "  --category CAT      Category (default: Uncategorized)"
            echo "  --author AUTHOR     Author (default: InsightPulse)"
            echo "  --depends DEPS      Dependencies, comma-separated (default: base)"
            echo "  --models MODELS     Models, comma-separated (e.g., expense,category)"
            echo "  --license LICENSE   License (default: LGPL-3)"
            echo "  --output DIR        Output directory (default: addons/custom)"
            echo ""
            echo "Example:"
            echo "  $0 --name expense_management \\"
            echo "     --category \"Human Resources\" \\"
            echo "     --depends hr,account \\"
            echo "     --models expense,expense_category"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$MODULE_NAME" ]; then
    echo -e "${RED}Error: --name is required${NC}"
    exit 1
fi

# Validate module name format
if [[ ! "$MODULE_NAME" =~ ^[a-z_]+$ ]]; then
    echo -e "${RED}Error: Module name must be lowercase with underscores only${NC}"
    exit 1
fi

MODULE_DIR="$OUTPUT_DIR/$MODULE_NAME"

echo -e "${GREEN}🚀 Scaffolding Odoo Module: $MODULE_NAME${NC}"
echo "=========================================="

# Check if module already exists
if [ -d "$MODULE_DIR" ]; then
    echo -e "${YELLOW}⚠️  Module directory already exists: $MODULE_DIR${NC}"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    rm -rf "$MODULE_DIR"
fi

# Create directory structure
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p "$MODULE_DIR"/{models,views,security,data,tests,static/description}

# Create __init__.py files
echo -e "${BLUE}📝 Creating __init__.py files...${NC}"

cat > "$MODULE_DIR/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-
from . import models
EOF

cat > "$MODULE_DIR/models/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > "$MODULE_DIR/tests/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-
EOF

# Create __manifest__.py
echo -e "${BLUE}📝 Creating __manifest__.py...${NC}"

# Convert depends to Python list format
DEPENDS_LIST=$(echo "$DEPENDS" | sed "s/,/','/g" | sed "s/^/'/" | sed "s/$/'/")

cat > "$MODULE_DIR/__manifest__.py" << EOF
# -*- coding: utf-8 -*-
{
    'name': '$(echo $MODULE_NAME | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')',
    'version': '$VERSION',
    'category': '$CATEGORY',
    'summary': 'TODO: Add summary',
    'description': '''
        TODO: Add detailed description
    ''',
    'author': '$AUTHOR',
    'website': 'https://insightpulseai.net',
    'license': '$LICENSE',
    'depends': [$DEPENDS_LIST],
    'data': [
        'security/ir.model.access.csv',
EOF

# Add model views if models specified
if [ -n "$MODELS" ]; then
    IFS=',' read -ra MODEL_ARRAY <<< "$MODELS"
    for model in "${MODEL_ARRAY[@]}"; do
        echo "        'views/${model}_views.xml'," >> "$MODULE_DIR/__manifest__.py"
    done
fi

cat >> "$MODULE_DIR/__manifest__.py" << 'EOF'
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOF

# Generate models
if [ -n "$MODELS" ]; then
    echo -e "${BLUE}📝 Generating models...${NC}"

    IFS=',' read -ra MODEL_ARRAY <<< "$MODELS"
    for model in "${MODEL_ARRAY[@]}"; do
        model=$(echo "$model" | tr -d ' ')
        MODEL_CLASS=$(echo "$model" | sed 's/_\([a-z]\)/\U\1/g' | sed 's/^\([a-z]\)/\U\1/')
        MODEL_NAME="${MODULE_NAME}.${model}"

        echo "from . import ${model}" >> "$MODULE_DIR/models/__init__.py"

        # Create model file
        cat > "$MODULE_DIR/models/${model}.py" << MODELEOF
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ${MODEL_CLASS}(models.Model):
    _name = '${MODEL_NAME}'
    _description = '$(echo $model | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
        help='The name of the ${model}'
    )

    active = fields.Boolean(
        default=True,
        help='If unchecked, it will allow you to hide without removing it'
    )

    description = fields.Text(
        string='Description',
        translate=True
    )

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'Name must be unique!'),
    ]

    @api.constrains('name')
    def _check_name(self):
        """Validate name field"""
        for record in self:
            if not record.name or len(record.name.strip()) == 0:
                raise ValidationError('Name cannot be empty')

    def name_get(self):
        """Custom name_get to display name"""
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result
MODELEOF

        # Create view file
        cat > "$MODULE_DIR/views/${model}_views.xml" << VIEWEOF
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Tree View -->
    <record id="${model}_view_tree" model="ir.ui.view">
        <field name="name">${MODEL_NAME}.tree</field>
        <field name="model">${MODEL_NAME}</field>
        <field name="arch" type="xml">
            <tree string="$(echo $model | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')">
                <field name="name"/>
                <field name="active"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="${model}_view_form" model="ir.ui.view">
        <field name="name">${MODEL_NAME}.form</field>
        <field name="model">${MODEL_NAME}</field>
        <field name="arch" type="xml">
            <form string="$(echo $model | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')">
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="toggle_active" type="object" class="oe_stat_button" icon="fa-archive">
                            <field name="active" widget="boolean_button" options='{"terminology": "archive"}'/>
                        </button>
                    </div>
                    <group>
                        <field name="name"/>
                        <field name="description"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="${model}_view_search" model="ir.ui.view">
        <field name="name">${MODEL_NAME}.search</field>
        <field name="model">${MODEL_NAME}</field>
        <field name="arch" type="xml">
            <search string="$(echo $model | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')">
                <field name="name"/>
                <filter string="Active" name="active" domain="[('active', '=', True)]"/>
                <filter string="Archived" name="inactive" domain="[('active', '=', False)]"/>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="${model}_action" model="ir.actions.act_window">
        <field name="name">$(echo $model | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')</field>
        <field name="res_model">${MODEL_NAME}</field>
        <field name="view_mode">tree,form</field>
        <field name="context">{}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first $(echo $model | tr '_' ' ')
            </p>
        </field>
    </record>

    <!-- Menu -->
    <menuitem id="${model}_menu"
              name="$(echo $model | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')"
              action="${model}_action"
              sequence="10"/>

</odoo>
VIEWEOF

        echo -e "${GREEN}✅ Created model: ${model}${NC}"
    done
fi

# Create security file
echo -e "${BLUE}📝 Creating security rules...${NC}"

cat > "$MODULE_DIR/security/ir.model.access.csv" << 'EOF'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
EOF

if [ -n "$MODELS" ]; then
    IFS=',' read -ra MODEL_ARRAY <<< "$MODELS"
    for model in "${MODEL_ARRAY[@]}"; do
        model=$(echo "$model" | tr -d ' ')
        MODEL_NAME="${MODULE_NAME}.${model}"
        echo "access_${MODULE_NAME}_${model}_user,${MODULE_NAME}.${model}.user,model_${MODULE_NAME}_${model},base.group_user,1,1,1,0" >> "$MODULE_DIR/security/ir.model.access.csv"
        echo "access_${MODULE_NAME}_${model}_manager,${MODULE_NAME}.${model}.manager,model_${MODULE_NAME}_${model},base.group_system,1,1,1,1" >> "$MODULE_DIR/security/ir.model.access.csv"
    done
fi

# Create basic test
echo -e "${BLUE}📝 Creating test template...${NC}"

cat > "$MODULE_DIR/tests/test_${MODULE_NAME}.py" << TESTEOF
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class Test${MODEL_CLASS:-Module}(TransactionCase):

    def setUp(self):
        super().setUp()
        # Add setup code here

    def test_01_basic_test(self):
        """Test basic functionality"""
        # TODO: Add tests
        self.assertTrue(True)
TESTEOF

# Create README.rst
echo -e "${BLUE}📝 Creating README.rst...${NC}"

cat > "$MODULE_DIR/README.rst" << EOF
$(echo $MODULE_NAME | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1')
$(printf '=%.0s' {1..50})

TODO: Add module description

**Table of contents**

.. contents::
   :local:

Installation
============

TODO: Add installation instructions

Configuration
=============

TODO: Add configuration instructions

Usage
=====

TODO: Add usage instructions

Bug Tracker
===========

Bugs are tracked on \`GitHub Issues\`_.

Credits
=======

Authors
~~~~~~~

* $AUTHOR

Contributors
~~~~~~~~~~~~

* Your Name <your.email@example.com>

Maintainers
~~~~~~~~~~~

This module is maintained by $AUTHOR.

EOF

# Create icon placeholder
echo -e "${BLUE}🎨 Creating icon placeholder...${NC}"
cat > "$MODULE_DIR/static/description/icon.png.txt" << 'EOF'
TODO: Add icon.png (128x128 PNG)
EOF

echo ""
echo -e "${GREEN}✅ Module scaffolded successfully!${NC}"
echo ""
echo -e "${BLUE}📁 Module location:${NC} $MODULE_DIR"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review generated files"
echo "  2. Add your business logic"
echo "  3. Install module: docker compose exec odoo odoo-bin -d dev_db -i $MODULE_NAME"
echo "  4. Run tests: pytest $MODULE_DIR/tests/"
echo ""
echo -e "${BLUE}Generated files:${NC}"
tree "$MODULE_DIR" 2>/dev/null || find "$MODULE_DIR" -type f
