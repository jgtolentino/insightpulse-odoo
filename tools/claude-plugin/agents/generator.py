#!/usr/bin/env python3
"""
Generator Agent - Code Generation
Generates Odoo module code using Jinja2 templates
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


class GeneratorAgent:
    """Generates Odoo module code from plans"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / 'agents' / 'templates'
        self.output_dir = project_root / 'odoo' / 'addons'

        # Initialize Jinja2 environment
        if self.templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            self.jinja_env = None
            logger.warning(f"Templates directory not found: {self.templates_dir}")

    def generate_module(self, plan: dict) -> dict:
        """
        Generate complete Odoo module from plan

        Returns:
        {
            "success": bool,
            "module_path": str,
            "module_name": str,
            "files_generated": [...],
            "errors": [...]
        }
        """
        logger.info(f"Generating module: {plan['module_name']}")

        result = {
            'success': False,
            'module_name': plan['module_name'],
            'files_generated': [],
            'errors': [],
        }

        try:
            # Create module directory
            module_path = self.output_dir / plan['module_name']
            module_path.mkdir(parents=True, exist_ok=True)

            result['module_path'] = str(module_path)

            # Generate each file
            for file_path in plan.get('files_to_generate', []):
                logger.info(f"Generating: {file_path}")

                try:
                    self._generate_file(module_path, file_path, plan)
                    result['files_generated'].append(file_path)
                except Exception as e:
                    logger.error(f"Failed to generate {file_path}: {e}")
                    result['errors'].append({
                        'file': file_path,
                        'message': str(e),
                    })

            result['success'] = len(result['errors']) == 0
            logger.info(f"Generated {len(result['files_generated'])} files")
            return result

        except Exception as e:
            logger.error(f"Module generation failed: {e}")
            result['errors'].append({'message': str(e)})
            return result

    def _generate_file(self, module_path: Path, file_path: str, plan: dict):
        """Generate individual file"""
        target_file = module_path / file_path

        # Create parent directories
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Determine file type and generate
        if file_path == '__manifest__.py':
            self._generate_manifest(target_file, plan)
        elif file_path == '__init__.py':
            self._generate_init(target_file, plan)
        elif file_path.startswith('models/') and file_path.endswith('.py'):
            self._generate_model(target_file, file_path, plan)
        elif file_path.startswith('views/') and file_path.endswith('.xml'):
            self._generate_view(target_file, file_path, plan)
        elif file_path == 'security/ir.model.access.csv':
            self._generate_security_csv(target_file, plan)
        elif file_path == 'README.rst':
            self._generate_readme(target_file, plan)
        elif file_path.startswith('tests/'):
            self._generate_test(target_file, file_path, plan)
        else:
            logger.warning(f"Unknown file type: {file_path}")

    def _generate_manifest(self, target_file: Path, plan: dict):
        """Generate __manifest__.py"""
        manifest = plan['manifest']

        # Build data files list
        data_files = []
        for file_path in plan.get('files_to_generate', []):
            if file_path.startswith(('views/', 'security/', 'data/')):
                data_files.append(file_path)

        manifest['data'] = data_files

        if self.jinja_env and (self.templates_dir / 'manifest.py.j2').exists():
            template = self.jinja_env.get_template('manifest.py.j2')
            content = template.render(manifest=manifest)
        else:
            # Fallback: generate without template
            content = self._generate_manifest_fallback(manifest)

        target_file.write_text(content)

    def _generate_manifest_fallback(self, manifest: dict) -> str:
        """Generate manifest without template"""
        return f"""# -*- coding: utf-8 -*-
{{
    'name': '{manifest['name']}',
    'version': '{manifest['version']}',
    'summary': '{manifest['summary']}',
    'author': '{manifest['author']}',
    'license': '{manifest['license']}',
    'category': '{manifest['category']}',
    'depends': {manifest['depends']},
    'data': {manifest['data']},
    'demo': {manifest.get('demo', [])},
    'installable': {manifest['installable']},
    'application': {manifest.get('application', False)},
    'auto_install': {manifest.get('auto_install', False)},
}}
"""

    def _generate_init(self, target_file: Path, plan: dict):
        """Generate __init__.py"""
        parent_dir = target_file.parent.name

        imports = []
        if parent_dir == 'models':
            # Import all model files
            for model in plan['architecture']['models']:
                model_file = model['name'].replace('.', '_')
                imports.append(f"from . import {model_file}")
        elif parent_dir == 'controllers':
            # Import all controller files
            for controller in plan['architecture']['controllers']:
                controller_file = controller['class_name'].lower()
                imports.append(f"from . import {controller_file}")
        elif parent_dir == 'tests':
            imports.append("from . import test_common")
        else:
            # Root __init__.py
            imports.append("from . import models")
            if plan['architecture']['controllers']:
                imports.append("from . import controllers")

        content = "# -*- coding: utf-8 -*-\n" + "\n".join(imports) + "\n"
        target_file.write_text(content)

    def _generate_model(self, target_file: Path, file_path: str, plan: dict):
        """Generate model file"""
        # Find model spec from file path
        model_name = file_path.split('/')[-1].replace('.py', '').replace('_', '.')
        model = next(
            (m for m in plan['architecture']['models'] if m['name'] == model_name),
            None
        )

        if not model:
            logger.error(f"Model not found in plan: {model_name}")
            return

        if self.jinja_env and (self.templates_dir / 'model.py.j2').exists():
            template = self.jinja_env.get_template('model.py.j2')
            content = template.render(model=model, module_name=plan['module_name'])
        else:
            # Fallback: generate without template
            content = self._generate_model_fallback(model, plan)

        target_file.write_text(content)

    def _generate_model_fallback(self, model: dict, plan: dict) -> str:
        """Generate model without template"""
        class_name = ''.join(word.capitalize() for word in model['name'].split('.'))

        inherits = ', '.join(f"'{i}'" for i in model['inherits'])

        fields_code = []
        for field in model['fields']:
            field_type = field.get('type', 'Char')
            field_name = field.get('name')
            field_attrs = []

            if field.get('string'):
                field_attrs.append(f"string='{field['string']}'")
            if field.get('required'):
                field_attrs.append("required=True")
            if field.get('default'):
                field_attrs.append(f"default={field['default']}")

            attrs_str = ', '.join(field_attrs)
            fields_code.append(f"    {field_name} = fields.{field_type}({attrs_str})")

        fields_str = '\n'.join(fields_code)

        return f"""# -*- coding: utf-8 -*-
from odoo import models, fields, api

class {class_name}(models.Model):
    _name = '{model['name']}'
    _description = '{model['description']}'
    _inherit = [{inherits}]

{fields_str}
"""

    def _generate_view(self, target_file: Path, file_path: str, plan: dict):
        """Generate view XML file"""
        # Extract model and view type from filename
        filename = file_path.split('/')[-1].replace('.xml', '')
        parts = filename.rsplit('_', 1)
        model_name = parts[0].replace('_', '.')
        view_type = parts[1] if len(parts) > 1 else 'form'

        # Find view spec
        view = next(
            (v for v in plan['architecture']['views']
             if v['model'] == model_name and v['type'] == view_type),
            None
        )

        if not view:
            logger.error(f"View not found in plan: {model_name} {view_type}")
            return

        template_name = f"view_{view_type}.xml.j2"
        if self.jinja_env and (self.templates_dir / template_name).exists():
            template = self.jinja_env.get_template(template_name)
            content = template.render(
                view=view,
                module_name=plan['module_name'],
                model_name=model_name
            )
        else:
            # Fallback: generate without template
            content = self._generate_view_fallback(view, plan, view_type)

        target_file.write_text(content)

    def _generate_view_fallback(self, view: dict, plan: dict, view_type: str) -> str:
        """Generate view without template"""
        model_name = view['model']
        view_id = f"{plan['module_name']}.view_{model_name.replace('.', '_')}_{view_type}"

        return f"""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{view_id}" model="ir.ui.view">
        <field name="name">{model_name}.{view_type}</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <{view_type}>
                <!-- Generated view -->
            </{view_type}>
        </field>
    </record>
</odoo>
"""

    def _generate_security_csv(self, target_file: Path, plan: dict):
        """Generate security/ir.model.access.csv"""
        if self.jinja_env and (self.templates_dir / 'security.csv.j2').exists():
            template = self.jinja_env.get_template('security.csv.j2')
            content = template.render(security=plan['architecture']['security'])
        else:
            # Fallback: generate without template
            lines = ['id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink']
            for access in plan['architecture']['security']['access_rights']:
                lines.append(
                    f"{access['id']},{access['name']},{access['model_id']},,1,1,1,1"
                )
            content = '\n'.join(lines) + '\n'

        target_file.write_text(content)

    def _generate_readme(self, target_file: Path, plan: dict):
        """Generate README.rst"""
        content = f"""=============================
{plan['manifest']['name']}
=============================

{plan['manifest']['summary']}

**Author**: {plan['manifest']['author']}
**License**: {plan['manifest']['license']}
**Version**: {plan['manifest']['version']}

Installation
============

No special installation required.

Configuration
=============

No configuration needed.

Usage
=====

This module provides:

"""
        for model in plan['architecture']['models']:
            content += f"* {model['description']}\n"

        content += """
Bug Tracker
===========

Bugs are tracked on GitHub Issues.

Credits
=======

Contributors
------------

* InsightPulse AI Team

Maintainer
----------

This module is maintained by InsightPulse AI.
"""

        target_file.write_text(content)

    def _generate_test(self, target_file: Path, file_path: str, plan: dict):
        """Generate test file"""
        if file_path == 'tests/__init__.py':
            content = "# -*- coding: utf-8 -*-\nfrom . import test_common\n"
        else:
            # test_common.py
            content = f"""# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestCommon(TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup test data
        pass

    def test_module_installation(self):
        \"\"\"Test module is installed\"\"\"
        module = self.env['ir.module.module'].search([
            ('name', '=', '{plan['module_name']}')
        ])
        self.assertTrue(module)
        self.assertEqual(module.state, 'installed')
"""

        target_file.write_text(content)

    def fix_issues(self, generated_files: dict, errors: list) -> dict:
        """Attempt to auto-fix validation errors"""
        logger.info(f"Attempting to fix {len(errors)} validation errors")

        # For now, return original files
        # TODO: Implement auto-fix logic
        return generated_files


if __name__ == '__main__':
    import sys

    # Load plan
    with open(sys.argv[1]) as f:
        plan = json.load(f)

    # Generate module
    generator = GeneratorAgent(Path.cwd())
    result = generator.generate_module(plan)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit code
    exit(0 if result['success'] else 1)
