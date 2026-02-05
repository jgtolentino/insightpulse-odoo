#!/usr/bin/env python3
"""
Planner Agent - Strategic Planning & Architecture
Creates comprehensive module plans with OCA compliance validation
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Creates strategic plans for Odoo module development"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.oca_license_options = ['AGPL-3', 'LGPL-3']
        self.required_manifest_fields = [
            'name',
            'version',
            'summary',
            'author',
            'license',
            'category',
            'depends',
            'data',
            'installable',
        ]

    def create_plan(self, params: dict) -> dict:
        """
        Create comprehensive module plan

        Input params:
        {
            "module_name": str,
            "description": str,
            "models": [...],
            "views": [...],
            "security": {...},
            "dependencies": [...]
        }

        Returns:
        {
            "valid": bool,
            "module_name": str,
            "manifest": {...},
            "architecture": {...},
            "files_to_generate": [...],
            "errors": [...]
        }
        """
        logger.info(f"Creating plan for module: {params.get('module_name')}")

        plan = {
            'valid': True,
            'module_name': params.get('module_name'),
            'errors': [],
        }

        # Validate module name
        module_name = params.get('module_name')
        if not module_name or not self._validate_module_name(module_name):
            plan['errors'].append({
                'field': 'module_name',
                'message': 'Invalid module name (must be lowercase, underscore-separated)',
            })
            plan['valid'] = False

        # Create manifest plan
        manifest = self._plan_manifest(params)
        if manifest.get('errors'):
            plan['errors'].extend(manifest['errors'])
            plan['valid'] = False
        plan['manifest'] = manifest

        # Create architecture plan
        architecture = self._plan_architecture(params)
        if architecture.get('errors'):
            plan['errors'].extend(architecture['errors'])
            plan['valid'] = False
        plan['architecture'] = architecture

        # Determine files to generate
        plan['files_to_generate'] = self._determine_files(architecture)

        # Validate OCA compliance
        oca_validation = self._validate_oca_compliance(plan)
        if not oca_validation['compliant']:
            plan['errors'].extend(oca_validation['errors'])
            plan['valid'] = False
        plan['oca_compliance'] = oca_validation

        logger.info(f"Plan created. Valid: {plan['valid']}")
        return plan

    def _validate_module_name(self, name: str) -> bool:
        """Validate module name follows OCA conventions"""
        if not name:
            return False

        # Must be lowercase, underscore-separated
        if not name.islower():
            return False

        # Must start with letter
        if not name[0].isalpha():
            return False

        # Only letters, numbers, underscores
        if not all(c.isalnum() or c == '_' for c in name):
            return False

        return True

    def _plan_manifest(self, params: dict) -> dict:
        """Plan module manifest"""
        manifest = {
            'name': params.get('module_name', '').replace('_', ' ').title(),
            'summary': params.get('description', 'Odoo Module'),
            'version': params.get('version', '18.0.1.0.0'),
            'author': params.get('author', 'InsightPulse AI'),
            'license': params.get('license', 'AGPL-3'),
            'category': params.get('category', 'Uncategorized'),
            'depends': params.get('dependencies', ['base']),
            'data': [],
            'demo': [],
            'installable': True,
            'application': params.get('application', False),
            'auto_install': False,
            'errors': [],
        }

        # Validate license
        if manifest['license'] not in self.oca_license_options:
            manifest['errors'].append({
                'field': 'license',
                'message': f"License must be {' or '.join(self.oca_license_options)}",
            })

        # Validate version format (Odoo 18.0)
        if not manifest['version'].startswith('18.0.'):
            manifest['errors'].append({
                'field': 'version',
                'message': 'Version must start with 18.0. for Odoo 18 CE',
            })

        # Validate depends includes base
        if 'base' not in manifest['depends']:
            manifest['depends'].insert(0, 'base')

        return manifest

    def _plan_architecture(self, params: dict) -> dict:
        """Plan module architecture"""
        architecture = {
            'models': [],
            'views': [],
            'security': {},
            'controllers': [],
            'static': [],
            'errors': [],
        }

        # Plan models
        models = params.get('models', [])
        for model_spec in models:
            model_plan = self._plan_model(model_spec)
            if model_plan.get('errors'):
                architecture['errors'].extend(model_plan['errors'])
            architecture['models'].append(model_plan)

        # Plan views
        views = params.get('views', [])
        for view_spec in views:
            view_plan = self._plan_view(view_spec)
            if view_plan.get('errors'):
                architecture['errors'].extend(view_plan['errors'])
            architecture['views'].append(view_plan)

        # Plan security
        security = params.get('security', {})
        security_plan = self._plan_security(security, architecture['models'])
        if security_plan.get('errors'):
            architecture['errors'].extend(security_plan['errors'])
        architecture['security'] = security_plan

        # Plan controllers (if any)
        controllers = params.get('controllers', [])
        for controller_spec in controllers:
            controller_plan = self._plan_controller(controller_spec)
            if controller_plan.get('errors'):
                architecture['errors'].extend(controller_plan['errors'])
            architecture['controllers'].append(controller_plan)

        return architecture

    def _plan_model(self, model_spec: dict) -> dict:
        """Plan Odoo model"""
        model = {
            'name': model_spec.get('name'),
            'description': model_spec.get('description', ''),
            'inherits': model_spec.get('inherits', ['mail.thread', 'mail.activity.mixin']),
            'fields': model_spec.get('fields', []),
            'methods': model_spec.get('methods', []),
            'errors': [],
        }

        # Validate model name format
        if not model['name'] or not model['name'].islower():
            model['errors'].append({
                'field': 'name',
                'message': 'Model name must be lowercase with dots (e.g., expense.report)',
            })

        # Ensure required fields
        required_fields = ['name', 'active']
        for field in required_fields:
            if not any(f.get('name') == field for f in model['fields']):
                model['fields'].insert(0, {
                    'name': field,
                    'type': 'Char' if field == 'name' else 'Boolean',
                    'default': 'True' if field == 'active' else None,
                })

        return model

    def _plan_view(self, view_spec: dict) -> dict:
        """Plan Odoo view"""
        view = {
            'type': view_spec.get('type', 'form'),  # form, tree, search, kanban
            'model': view_spec.get('model'),
            'arch': view_spec.get('arch', {}),
            'errors': [],
        }

        # Validate view type
        valid_types = ['form', 'tree', 'search', 'kanban', 'calendar', 'graph', 'pivot']
        if view['type'] not in valid_types:
            view['errors'].append({
                'field': 'type',
                'message': f"View type must be one of {valid_types}",
            })

        # Validate model reference
        if not view['model']:
            view['errors'].append({
                'field': 'model',
                'message': 'View must reference a model',
            })

        return view

    def _plan_security(self, security_spec: dict, models: list) -> dict:
        """Plan security rules and access rights"""
        security = {
            'groups': security_spec.get('groups', []),
            'access_rights': [],
            'record_rules': security_spec.get('record_rules', []),
            'errors': [],
        }

        # Generate default access rights for each model
        for model in models:
            model_name = model['name']
            access_id = f"access_{model_name.replace('.', '_')}"

            security['access_rights'].append({
                'id': access_id,
                'name': model_name,
                'model_id': f"model_{model_name.replace('.', '_')}",
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })

        return security

    def _plan_controller(self, controller_spec: dict) -> dict:
        """Plan HTTP controller"""
        controller = {
            'class_name': controller_spec.get('class_name'),
            'routes': controller_spec.get('routes', []),
            'methods': controller_spec.get('methods', []),
            'errors': [],
        }

        # Validate class name
        if not controller['class_name']:
            controller['errors'].append({
                'field': 'class_name',
                'message': 'Controller must have a class name',
            })

        return controller

    def _determine_files(self, architecture: dict) -> list:
        """Determine which files need to be generated"""
        files = [
            '__init__.py',
            '__manifest__.py',
            'models/__init__.py',
            'views/__init__.py',
            'security/ir.model.access.csv',
            'README.rst',
        ]

        # Add model files
        for model in architecture['models']:
            model_file = f"models/{model['name'].replace('.', '_')}.py"
            files.append(model_file)

        # Add view files
        for view in architecture['views']:
            view_file = f"views/{view['model'].replace('.', '_')}_{view['type']}.xml"
            files.append(view_file)

        # Add controller files
        for controller in architecture['controllers']:
            controller_file = f"controllers/{controller['class_name'].lower()}.py"
            files.append(controller_file)
            if 'controllers/__init__.py' not in files:
                files.insert(-1, 'controllers/__init__.py')

        # Add tests
        files.append('tests/__init__.py')
        files.append('tests/test_common.py')

        return files

    def _validate_oca_compliance(self, plan: dict) -> dict:
        """Validate OCA compliance"""
        compliance = {
            'compliant': True,
            'errors': [],
        }

        # Check license
        license = plan['manifest'].get('license')
        if license not in self.oca_license_options:
            compliance['errors'].append({
                'rule': 'OCA License',
                'message': f"License must be {' or '.join(self.oca_license_options)}",
            })
            compliance['compliant'] = False

        # Check required manifest fields
        for field in self.required_manifest_fields:
            if field not in plan['manifest']:
                compliance['errors'].append({
                    'rule': 'OCA Manifest',
                    'message': f"Missing required manifest field: {field}",
                })
                compliance['compliant'] = False

        # Check module name convention
        if not self._validate_module_name(plan['module_name']):
            compliance['errors'].append({
                'rule': 'OCA Naming',
                'message': 'Module name must be lowercase, underscore-separated',
            })
            compliance['compliant'] = False

        # Check README.rst exists
        if 'README.rst' not in plan.get('files_to_generate', []):
            compliance['errors'].append({
                'rule': 'OCA Documentation',
                'message': 'README.rst required for OCA compliance',
            })
            compliance['compliant'] = False

        return compliance


if __name__ == '__main__':
    import sys

    # Load parameters
    with open(sys.argv[1]) as f:
        params = json.load(f)

    # Create plan
    planner = PlannerAgent(Path.cwd())
    plan = planner.create_plan(params)

    # Output plan
    print(json.dumps(plan, indent=2))

    # Exit code
    exit(0 if plan['valid'] else 1)
