# OCA Module Structure Reference

## Standard Directory Layout

```
addons/[module_name]/
├── __manifest__.py          # Module metadata and configuration
├── __init__.py              # Python package initialization
├── README.rst               # Documentation (OCA format)
├── models/                  # Business logic (Python)
│   ├── __init__.py
│   └── [model_name].py
├── views/                   # User interface (XML)
│   ├── menu_views.xml
│   └── [model_name]_views.xml
├── security/                # Access control
│   └── ir.model.access.csv
├── data/                    # Master data (XML)
│   └── data.xml
├── demo/                    # Demo/test data (XML)
│   └── demo_data.xml
├── static/
│   ├── description/         # Module marketplace info
│   │   ├── index.html
│   │   └── icon.png
│   └── src/                 # Frontend assets
│       ├── js/
│       ├── xml/
│       └── css/
├── tests/                   # Unit tests
│   ├── __init__.py
│   └── test_[feature].py
├── wizards/                 # Transient models
│   ├── __init__.py
│   └── [wizard_name].py
├── reports/                 # Report templates
│   └── report_template.xml
└── controllers/             # HTTP controllers
    ├── __init__.py
    └── main.py
```

## __manifest__.py Template

```python
# Copyright YYYY Author Name
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Module Display Name",
    "version": "19.0.1.0.0",
    "category": "Category Name",
    "author": "Your Company, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/repository-name",
    "license": "AGPL-3",
    "depends": [
        "base",
        # Add dependencies here
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu_views.xml",
        "data/data.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "module_name/static/src/js/*.js",
            "module_name/static/src/xml/*.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
```

### Version Format: `19.0.x.y.z`
- **19.0**: Odoo version (series)
- **x**: Major version (breaking changes)
- **y**: Minor version (new features)
- **z**: Patch version (bug fixes)

## README.rst Template (OCA Format)

```rst
====================
Module Display Name
====================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1| |badge2|

Short description of what the module does.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure this module, you need to:

#. Go to ...
#. Set ...

Usage
=====

To use this module, you need to:

#. Go to ...
#. Do ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/repository-name/issues>`_.

Credits
=======

Authors
~~~~~~~

* Your Company

Contributors
~~~~~~~~~~~~

* Your Name <your.email@example.com>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.
```

## Model Template

```python
# Copyright YYYY Author Name
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ModelName(models.Model):
    _name = "module.model"
    _description = "Model Description"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Optional

    name = fields.Char(required=True, tracking=True)
    description = fields.Text()
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    
    @api.depends("field1", "field2")
    def _compute_computed_field(self):
        for record in self:
            record.computed_field = record.field1 + record.field2
```

## View Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View -->
    <record id="view_model_form" model="ir.ui.view">
        <field name="name">module.model.form</field>
        <field name="model">module.model</field>
        <field name="arch" type="xml">
            <form string="Model Name">
                <header>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="description"/>
                    </group>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- Tree View -->
    <record id="view_model_tree" model="ir.ui.view">
        <field name="name">module.model.tree</field>
        <field name="model">module.model</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_model_search" model="ir.ui.view">
        <field name="name">module.model.search</field>
        <field name="model">module.model</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <filter name="draft" string="Draft" domain="[('state','=','draft')]"/>
                <group expand="0" string="Group By">
                    <filter name="group_state" string="Status" context="{'group_by':'state'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="action_model" model="ir.actions.act_window">
        <field name="name">Model Name</field>
        <field name="res_model">module.model</field>
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Menu -->
    <menuitem id="menu_model" 
              name="Model Name"
              parent="menu_module_root"
              action="action_model"
              sequence="10"/>
</odoo>
```

## Security Template (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,module.model.user,model_module_model,base.group_user,1,0,0,0
access_model_manager,module.model.manager,model_module_model,base.group_system,1,1,1,1
```

## Required License Headers

Every Python file must have:

```python
# Copyright YYYY Author Name
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
```

Every XML file should have:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright YYYY Author Name -->
<!-- License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). -->
<odoo>
    ...
</odoo>
```

## Module Categories

Common categories:
- `Accounting`
- `Sales`
- `Human Resources`
- `Inventory`
- `Manufacturing`
- `Project`
- `Services`
- `Custom`

## Best Practices

1. **Naming**: Use `module_` prefix for all XML IDs
2. **Inheritance**: Use `_inherit` to extend existing models
3. **Dependencies**: List ALL module dependencies in __manifest__.py
4. **Translations**: Use `_()` for translatable strings
5. **Security**: Define access rules for all models
6. **Testing**: Write tests for business logic
7. **Documentation**: Keep README.rst updated

## Validation Checklist

- [ ] __manifest__.py has all required fields
- [ ] License headers on all Python files
- [ ] README.rst in OCA format
- [ ] ir.model.access.csv exists
- [ ] All XML IDs are unique
- [ ] Module installs without errors
- [ ] Security rules tested
