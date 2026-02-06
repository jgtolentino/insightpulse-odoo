#!/usr/bin/env python3
import pathlib
import sys
import textwrap

if len(sys.argv) < 2:
    raise SystemExit("usage: scripts/new_module.py <snake_name>")
name = sys.argv[1]
root = pathlib.Path(__file__).resolve().parent.parent
mod = root / "custom_addons" / name
(mod / "models").mkdir(parents=True, exist_ok=True)
(mod / "views").mkdir(parents=True, exist_ok=True)
(mod / "security").mkdir(parents=True, exist_ok=True)
(mod / "__init__.py").write_text("from . import models\n")
(mod / "models" / "__init__.py").write_text(f"from . import {name}\n")
(mod / "models" / f"{name}.py").write_text(textwrap.dedent(f"""
from odoo import models, fields
class {''.join(p.title() for p in name.split('_'))}(models.Model):
    _name = "{name}"
    _description = "{name.replace('_',' ').title()}"
    name = fields.Char(required=True)
""").strip() + "\n")
(mod / "views" / f"{name}_views.xml").write_text(
    textwrap.dedent(f"""<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <record id="view_{name}_tree" model="ir.ui.view">
    <field name="name">{name}.tree</field><field name="model">{name}</field>
    <field name="arch" type="xml"><tree><field name="name"/></tree></field>
  </record>
  <record id="view_{name}_form" model="ir.ui.view">
    <field name="name">{name}.form</field><field name="model">{name}</field>
    <field name="arch" type="xml">
      <form string="{name}"><sheet><group><field name="name"/></group></sheet></form>
    </field>
  </record>
  <record id="action_{name}" model="ir.actions.act_window">
    <field name="name">{name}</field><field name="res_model">{name}</field><field name="view_mode">tree,form</field>
  </record>
  <menuitem id="menu_{name}_root" name="{name}"/>
  <menuitem id="menu_{name}" parent="menu_{name}_root" action="action_{name}"/>
</odoo>
""").strip() + "\n"
)
(mod / "security" / "ir.model.access.csv").write_text(
    "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n"
    f"access_{name}_user,access_{name}_user,model_{name},base.group_user,1,1,1,1\n"
)
(mod / "__manifest__.py").write_text(textwrap.dedent(f"""{{
  "name": "{name.replace('_',' ').title()}","version": "16.0.1.0.0","summary": "Custom module",
  "license": "LGPL-3","depends": ["base"],"data": ["security/ir.model.access.csv","views/{name}_views.xml"]
}}""").strip() + "\n")
print(f"[new_module] created {mod}")
