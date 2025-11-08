#!/usr/bin/env bash
# OCA Module Scaffolding Script
# Purpose: Create new Odoo modules following OCA standards and templates
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OCA_TOOLS_DIR="$REPO_ROOT/.oca-tools"
ADDONS_DIR="$REPO_ROOT/apps/odoo/addons"

# Default values
MODULE_NAME="${1:-}"
MODULE_CATEGORY="${2:-InsightPulse AI}"
MODULE_SUMMARY="${3:-}"
ODOO_VERSION="${4:-17.0}"
AUTHOR="Jake Tolentino <jake@insightpulseai.net>"
LICENSE="LGPL-3"
WEBSITE="https://insightpulseai.net"

if [ -z "$MODULE_NAME" ]; then
  echo "Usage: $0 <module_name> [category] [summary] [odoo_version]"
  echo ""
  echo "Examples:"
  echo "  $0 finance_ssc_enhanced 'Accounting' 'Finance Shared Service Center'"
  echo "  $0 bir_compliance_2025 'Compliance' 'BIR Form Automation'"
  echo "  $0 multi_agency_portal 'Portal' 'Multi-Agency Dashboard'"
  echo ""
  echo "Categories:"
  echo "  - Accounting, Sales, Invoicing, Purchase, Warehouse"
  echo "  - Manufacturing, Human Resources, Marketing, Point of Sale"
  echo "  - Productivity, Project, Services, Website, Compliance"
  echo "  - InsightPulse AI (default)"
  exit 1
fi

# Validate module name (must be valid Python identifier)
if ! echo "$MODULE_NAME" | grep -qE '^[a-z][a-z0-9_]*$'; then
  echo "❌ Invalid module name: $MODULE_NAME"
  echo "   Module name must:"
  echo "   - Start with lowercase letter"
  echo "   - Contain only lowercase letters, numbers, underscores"
  echo "   - Example: finance_ssc, bir_compliance_2025"
  exit 1
fi

MODULE_DIR="$ADDONS_DIR/$MODULE_NAME"

if [ -d "$MODULE_DIR" ]; then
  echo "❌ Module already exists: $MODULE_DIR"
  exit 1
fi

if [ ! -d "$OCA_TOOLS_DIR/oca-addons-repo-template" ]; then
  echo "❌ OCA tools not installed. Run: ./scripts/install-oca-tools.sh"
  exit 1
fi

echo "🏗️  Scaffolding OCA-Compliant Odoo Module"
echo "   Name:     $MODULE_NAME"
echo "   Category: $MODULE_CATEGORY"
echo "   Version:  $ODOO_VERSION"
echo "   License:  $LICENSE"
echo ""

# Create module directory structure
mkdir -p "$MODULE_DIR"/{models,views,security,data,static/description,tests,wizards,reports,controllers}

# 1. Create __manifest__.py
cat > "$MODULE_DIR/__manifest__.py" <<MANIFEST
# Copyright 2025 $AUTHOR
# License $LICENSE or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "${MODULE_NAME//_/ }",
    "version": "$ODOO_VERSION.1.0.0",
    "category": "$MODULE_CATEGORY",
    "summary": "${MODULE_SUMMARY:-Advanced module for InsightPulse AI ERP}",
    "author": "$AUTHOR, Odoo Community Association (OCA)",
    "website": "$WEBSITE",
    "license": "$LICENSE",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        # "data/data.xml",
        # "views/views.xml",
        # "views/menu.xml",
    ],
    "demo": [
        # "demo/demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "development_status": "Alpha",
    "maintainers": ["jgtolentino"],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
}
MANIFEST

# 2. Create __init__.py files
cat > "$MODULE_DIR/__init__.py" <<INIT
# Copyright 2025 $AUTHOR
# License $LICENSE or later (https://www.gnu.org/licenses/lgpl.html).

from . import models
# from . import wizards
# from . import controllers
INIT

cat > "$MODULE_DIR/models/__init__.py" <<MODELSINIT
# Copyright 2025 $AUTHOR
# License $LICENSE or later (https://www.gnu.org/licenses/lgpl.html).

# from . import ${MODULE_NAME}
MODELSINIT

cat > "$MODULE_DIR/tests/__init__.py" <<TESTSINIT
# Copyright 2025 $AUTHOR
# License $LICENSE or later (https://www.gnu.org/licenses/lgpl.html).

# from . import test_${MODULE_NAME}
TESTSINIT

# 3. Create sample model
cat > "$MODULE_DIR/models/${MODULE_NAME}.py" <<MODEL
# Copyright 2025 $AUTHOR
# License $LICENSE or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ${MODULE_NAME^}(models.Model):
    """${MODULE_SUMMARY:-Main model for $MODULE_NAME module}."""

    _name = "${MODULE_NAME}"
    _description = "${MODULE_SUMMARY:-$MODULE_NAME description}"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
        index=True,
    )

    active = fields.Boolean(
        default=True,
        string="Active",
        tracking=True,
    )

    description = fields.Text(
        string="Description",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        string="Status",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.constrains("name")
    def _check_name(self):
        """Validate name is not empty."""
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(_("Name cannot be empty."))

    def action_confirm(self):
        """Confirm the record."""
        self.ensure_one()
        self.state = "confirmed"

    def action_set_to_draft(self):
        """Reset to draft."""
        self.ensure_one()
        self.state = "draft"

    def action_done(self):
        """Mark as done."""
        self.ensure_one()
        self.state = "done"

    def action_cancel(self):
        """Cancel the record."""
        self.ensure_one()
        self.state = "cancel"
MODEL

# 4. Create security/ir.model.access.csv
cat > "$MODULE_DIR/security/ir.model.access.csv" <<SECURITY
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_${MODULE_NAME}_user,${MODULE_NAME}.user,model_${MODULE_NAME},base.group_user,1,0,0,0
access_${MODULE_NAME}_manager,${MODULE_NAME}.manager,model_${MODULE_NAME},base.group_system,1,1,1,1
SECURITY

# 5. Create sample view
cat > "$MODULE_DIR/views/${MODULE_NAME}_views.xml" <<VIEWS
<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright 2025 $AUTHOR -->
<!-- License $LICENSE or later (https://www.gnu.org/licenses/lgpl.html) -->
<odoo>
    <!-- Tree View -->
    <record id="${MODULE_NAME}_view_tree" model="ir.ui.view">
        <field name="name">${MODULE_NAME}.view.tree</field>
        <field name="model">${MODULE_NAME}</field>
        <field name="arch" type="xml">
            <tree string="${MODULE_NAME^}">
                <field name="name"/>
                <field name="state"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="${MODULE_NAME}_view_form" model="ir.ui.view">
        <field name="name">${MODULE_NAME}.view.form</field>
        <field name="model">${MODULE_NAME}</field>
        <field name="arch" type="xml">
            <form string="${MODULE_NAME^}">
                <header>
                    <button name="action_confirm" string="Confirm"
                            type="object" states="draft"
                            class="oe_highlight"/>
                    <button name="action_done" string="Done"
                            type="object" states="confirmed"
                            class="oe_highlight"/>
                    <button name="action_cancel" string="Cancel"
                            type="object" states="draft,confirmed"/>
                    <button name="action_set_to_draft" string="Reset to Draft"
                            type="object" states="cancel"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Name..."/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="active"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Description">
                            <field name="description" placeholder="Add description..."/>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="${MODULE_NAME}_view_search" model="ir.ui.view">
        <field name="name">${MODULE_NAME}.view.search</field>
        <field name="model">${MODULE_NAME}</field>
        <field name="arch" type="xml">
            <search string="${MODULE_NAME^}">
                <field name="name"/>
                <filter name="filter_draft" string="Draft"
                        domain="[('state', '=', 'draft')]"/>
                <filter name="filter_confirmed" string="Confirmed"
                        domain="[('state', '=', 'confirmed')]"/>
                <group expand="0" string="Group By">
                    <filter name="group_state" string="Status"
                            context="{'group_by': 'state'}"/>
                    <filter name="group_company" string="Company"
                            context="{'group_by': 'company_id'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="${MODULE_NAME}_action" model="ir.actions.act_window">
        <field name="name">${MODULE_NAME^}</field>
        <field name="res_model">${MODULE_NAME}</field>
        <field name="view_mode">tree,form</field>
        <field name="context">{}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create a new ${MODULE_NAME//_/ }
            </p>
        </field>
    </record>

    <!-- Menu Items -->
    <menuitem id="${MODULE_NAME}_menu_root"
              name="${MODULE_NAME^}"
              sequence="10"/>

    <menuitem id="${MODULE_NAME}_menu_main"
              name="${MODULE_NAME^}"
              parent="${MODULE_NAME}_menu_root"
              action="${MODULE_NAME}_action"
              sequence="10"/>
</odoo>
VIEWS

# 6. Create sample test
cat > "$MODULE_DIR/tests/test_${MODULE_NAME}.py" <<TESTS
# Copyright 2025 $AUTHOR
# License $LICENSE or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class Test${MODULE_NAME^}(TransactionCase):
    """Test cases for ${MODULE_NAME} module."""

    def setUp(self):
        super().setUp()
        self.Model = self.env["${MODULE_NAME}"]

    def test_create_record(self):
        """Test creating a new record."""
        record = self.Model.create({
            "name": "Test Record",
            "description": "Test description",
        })
        self.assertTrue(record)
        self.assertEqual(record.name, "Test Record")
        self.assertEqual(record.state, "draft")

    def test_name_constraint(self):
        """Test name validation constraint."""
        with self.assertRaises(ValidationError):
            self.Model.create({
                "name": "",
            })

    def test_state_transitions(self):
        """Test state workflow transitions."""
        record = self.Model.create({
            "name": "Workflow Test",
        })

        # Draft -> Confirmed
        record.action_confirm()
        self.assertEqual(record.state, "confirmed")

        # Confirmed -> Done
        record.action_done()
        self.assertEqual(record.state, "done")

    def test_cancel_action(self):
        """Test cancel action."""
        record = self.Model.create({
            "name": "Cancel Test",
        })
        record.action_cancel()
        self.assertEqual(record.state, "cancel")

        # Reset to draft
        record.action_set_to_draft()
        self.assertEqual(record.state, "draft")
TESTS

# 7. Create README.rst (OCA standard)
cat > "$MODULE_DIR/README.rst" <<README
=============
${MODULE_NAME^}
=============

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Alpha-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alpha
.. |badge2| image:: https://img.shields.io/badge/licence-$LICENSE-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: $LICENSE

|badge1| |badge2|

${MODULE_SUMMARY:-This module provides enhanced functionality for InsightPulse AI ERP.}

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure this module, you need to:

1. Go to Settings > Technical > ${MODULE_NAME^}
2. Configure the required parameters

Usage
=====

To use this module:

1. Navigate to ${MODULE_NAME^} menu
2. Create a new record
3. Fill in the required information
4. Confirm and process

Bug Tracker
===========

Bugs are tracked on \`GitHub Issues\`_.

.. _GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues

Credits
=======

Authors
~~~~~~~

* $AUTHOR

Contributors
~~~~~~~~~~~~

* $AUTHOR

Maintainers
~~~~~~~~~~~

This module is maintained by InsightPulse AI.

.. image:: https://insightpulseai.net/logo.png
   :alt: InsightPulse AI
   :target: https://insightpulseai.net
README

# 8. Create static/description/index.html
cat > "$MODULE_DIR/static/description/index.html" <<HTML
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>${MODULE_NAME^}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .badge { display: inline-block; padding: 3px 6px; margin: 2px; border-radius: 3px; font-size: 12px; }
        .badge-alpha { background: #e74c3c; color: white; }
        .badge-license { background: #3498db; color: white; }
    </style>
</head>
<body>
    <h1>${MODULE_NAME^}</h1>

    <p>
        <span class="badge badge-alpha">Alpha</span>
        <span class="badge badge-license">License: $LICENSE</span>
    </p>

    <h2>Overview</h2>
    <p>${MODULE_SUMMARY:-This module provides enhanced functionality for InsightPulse AI ERP.}</p>

    <h2>Features</h2>
    <ul>
        <li>OCA-compliant module structure</li>
        <li>Multi-company support</li>
        <li>Activity tracking</li>
        <li>State workflow management</li>
    </ul>

    <h2>Configuration</h2>
    <p>Navigate to Settings > Technical > ${MODULE_NAME^} to configure.</p>

    <h2>Credits</h2>
    <p><strong>Author:</strong> $AUTHOR</p>
    <p><strong>Maintainer:</strong> InsightPulse AI</p>
</body>
</html>
HTML

# 9. Create icon (placeholder)
mkdir -p "$MODULE_DIR/static/description"
# In real scenario, you'd copy an actual icon file here

echo ""
echo "✅ Module Scaffolded Successfully"
echo ""
echo "📁 Location: $MODULE_DIR"
echo ""
echo "📦 Structure created:"
tree -L 2 "$MODULE_DIR" 2>/dev/null || find "$MODULE_DIR" -type f | head -20
echo ""
echo "📝 Next steps:"
echo "   1. Update __manifest__.py with proper dependencies"
echo "   2. Implement your business logic in models/${MODULE_NAME}.py"
echo "   3. Customize views in views/${MODULE_NAME}_views.xml"
echo "   4. Add unit tests in tests/test_${MODULE_NAME}.py"
echo "   5. Run validation: ./scripts/validate-module.sh $MODULE_NAME"
echo "   6. Install module: odoo-bin -d db_name -i $MODULE_NAME"
echo ""
echo "🔍 OCA Compliance Check:"
echo "   pylint --rcfile=.pylintrc $MODULE_DIR"
echo "   pre-commit run --files $MODULE_DIR/**/*.py"
echo ""
