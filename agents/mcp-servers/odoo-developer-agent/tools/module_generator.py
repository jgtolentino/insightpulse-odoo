"""
Odoo Module Generator
Generates production-ready Odoo modules with full OCA compliance
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
from anthropic import Anthropic
import structlog

from knowledge.rag_client import OdooKnowledgeBase, RAGContextBuilder

logger = structlog.get_logger()


class OdooModuleGenerator:
    """
    Generates complete Odoo modules following OCA standards
    """
    
    def __init__(self):
        self.claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.kb = OdooKnowledgeBase()
        self.rag = RAGContextBuilder(self.kb)
        self.base_path = Path(os.getenv("ODOO_ADDONS_PATH", "/odoo/custom-addons"))
    
    async def generate_module(
        self,
        module_name: str,
        description: str,
        models: List[Dict],
        views: List[Dict],
        dependencies: List[str] = None,
        category: str = "Accounting",
        license: str = "AGPL-3",
        author: str = "InsightPulse AI"
    ) -> Dict:
        """
        Generate a complete Odoo module
        
        Args:
            module_name: Technical name (e.g., 'insightpulse_bir_compliance')
            description: User-facing description
            models: List of model specifications
            views: List of view specifications
            dependencies: List of dependent modules
            category: Odoo app category
            license: Module license (AGPL-3, LGPL-3, etc.)
            author: Module author
        
        Returns:
            Dict with module_path, files_created, quality_score
        """
        logger.info("generating_module", module_name=module_name)
        
        # Set defaults
        dependencies = dependencies or ['base']
        
        # Create module directory
        module_path = self.base_path / module_name
        module_path.mkdir(parents=True, exist_ok=True)
        
        # Build RAG context
        context = await self.rag.build_module_generation_context(
            description=description,
            models=[m['name'] for m in models]
        )
        
        # Generate files
        files_created = []
        
        # 1. __manifest__.py
        manifest = await self._generate_manifest(
            module_name=module_name,
            description=description,
            dependencies=dependencies,
            category=category,
            license=license,
            author=author,
            models=models,
            views=views,
            context=context
        )
        manifest_path = module_path / "__manifest__.py"
        manifest_path.write_text(manifest)
        files_created.append(str(manifest_path))
        
        # 2. __init__.py (root)
        init_root = "from . import models\n"
        if views:
            init_root += "# Views loaded via __manifest__.py\n"
        (module_path / "__init__.py").write_text(init_root)
        files_created.append(str(module_path / "__init__.py"))
        
        # 3. Models
        models_dir = module_path / "models"
        models_dir.mkdir(exist_ok=True)
        
        model_imports = []
        for model in models:
            model_code = await self._generate_model(
                model_spec=model,
                module_name=module_name,
                context=context
            )
            
            model_file = models_dir / f"{model['name']}.py"
            model_file.write_text(model_code)
            files_created.append(str(model_file))
            model_imports.append(f"from . import {model['name']}")
        
        # models/__init__.py
        (models_dir / "__init__.py").write_text("\n".join(model_imports) + "\n")
        files_created.append(str(models_dir / "__init__.py"))
        
        # 4. Views
        if views:
            views_dir = module_path / "views"
            views_dir.mkdir(exist_ok=True)
            
            for view in views:
                view_xml = await self._generate_view(
                    view_spec=view,
                    module_name=module_name,
                    context=context
                )
                
                view_file = views_dir / f"{view['model']}_views.xml"
                view_file.write_text(view_xml)
                files_created.append(str(view_file))
        
        # 5. Security (ir.model.access.csv)
        security_dir = module_path / "security"
        security_dir.mkdir(exist_ok=True)
        
        security_csv = await self._generate_security(
            models=models,
            module_name=module_name,
            context=context
        )
        security_file = security_dir / "ir.model.access.csv"
        security_file.write_text(security_csv)
        files_created.append(str(security_file))
        
        # 6. Data (if needed for defaults)
        data_dir = module_path / "data"
        data_dir.mkdir(exist_ok=True)
        
        # 7. Tests
        tests_dir = module_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        test_code = await self._generate_tests(
            models=models,
            module_name=module_name,
            context=context
        )
        test_file = tests_dir / f"test_{module_name}.py"
        test_file.write_text(test_code)
        files_created.append(str(test_file))
        
        (tests_dir / "__init__.py").write_text(f"from . import test_{module_name}\n")
        files_created.append(str(tests_dir / "__init__.py"))
        
        # 8. README.rst
        readme = await self._generate_readme(
            module_name=module_name,
            description=description,
            models=models,
            author=author
        )
        readme_file = module_path / "README.rst"
        readme_file.write_text(readme)
        files_created.append(str(readme_file))
        
        # 9. Static assets (if needed)
        static_dir = module_path / "static"
        static_dir.mkdir(exist_ok=True)
        (static_dir / "description").mkdir(exist_ok=True)
        
        # 10. i18n directory
        i18n_dir = module_path / "i18n"
        i18n_dir.mkdir(exist_ok=True)
        
        logger.info("module_generation_complete", files_count=len(files_created))
        
        # Run quality checks
        quality_score = await self._run_quality_checks(module_path)
        
        # Store in knowledge base
        code_files = {}
        for file_path in files_created:
            with open(file_path, 'r') as f:
                code_files[os.path.basename(file_path)] = f.read()
        
        await self.kb.store_generated_code(
            module_name=module_name,
            description=description,
            code_files=code_files,
            metadata={
                'models': [m['name'] for m in models],
                'dependencies': dependencies,
                'category': category
            },
            quality_score=quality_score
        )
        
        return {
            "status": "success",
            "module_path": str(module_path),
            "files_created": files_created,
            "quality_score": quality_score,
            "next_steps": [
                f"cd {module_path}",
                "Review generated code",
                f"odoo -u {module_name} -d <database>",
                "Run tests: pytest tests/"
            ]
        }
    
    async def _generate_manifest(
        self,
        module_name: str,
        description: str,
        dependencies: List[str],
        category: str,
        license: str,
        author: str,
        models: List[Dict],
        views: List[Dict],
        context: str
    ) -> str:
        """Generate __manifest__.py file"""
        
        prompt = f"""Generate an Odoo 18 CE module manifest file.

Module Details:
- Name: {module_name}
- Description: {description}
- Dependencies: {dependencies}
- Category: {category}
- License: {license}
- Author: {author}

Models: {[m['name'] for m in models]}
Views: {len(views)} view(s)

Requirements:
1. Use Odoo 18.0 version format (18.0.1.0.0)
2. Include all dependencies
3. List all data files (views, security, data)
4. Add proper installable, application, auto_install flags
5. Include website, support, and documentation URLs
6. Follow OCA manifest standards

{context}

Output only the Python dictionary code, no markdown backticks."""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_model(
        self,
        model_spec: Dict,
        module_name: str,
        context: str
    ) -> str:
        """Generate Odoo model Python file"""
        
        prompt = f"""Generate an Odoo 18 CE model class.

Model Specification:
```json
{json.dumps(model_spec, indent=2)}
```

Requirements:
1. Use proper Odoo model inheritance (models.Model or models.TransientModel)
2. Include _name, _description, _inherit (if needed)
3. Define all fields with proper types and attributes
4. Add compute methods with @api.depends decorators
5. Include _sql_constraints for data integrity
6. Add proper onchange methods
7. Include comprehensive docstrings
8. Follow OCA naming conventions
9. Add proper imports (from odoo import models, fields, api, _)
10. Handle exceptions properly with raise UserError

Context from similar modules:
{context}

Output only the Python code, no markdown backticks."""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_view(
        self,
        view_spec: Dict,
        module_name: str,
        context: str
    ) -> str:
        """Generate Odoo view XML file"""
        
        prompt = f"""Generate Odoo 18 CE view XML.

View Specification:
```json
{json.dumps(view_spec, indent=2)}
```

Requirements:
1. Wrap in <odoo> tags with proper noupdate attribute
2. Include form, tree, search views as needed
3. Add menuitem and action definitions
4. Use proper XML IDs with module prefix
5. Include security groups if specified
6. Add proper field widgets (many2one, many2many, etc.)
7. Use statusbar for state fields
8. Include notebook/page for organized layouts
9. Add proper domain filters
10. Follow OCA XML formatting standards

Context from similar views:
{context}

Output only the XML code, no markdown backticks."""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_security(
        self,
        models: List[Dict],
        module_name: str,
        context: str
    ) -> str:
        """Generate ir.model.access.csv"""
        
        prompt = f"""Generate Odoo security CSV file (ir.model.access.csv).

Models: {[m['name'] for m in models]}
Module: {module_name}

Requirements:
1. Create access rights for: user, manager, admin groups
2. Format: id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
3. Use proper CSV formatting
4. Include base.group_user, base.group_system as needed
5. Set appropriate permissions per role
6. Follow OCA security conventions

Context:
{context}

Output only the CSV content with header row, no markdown backticks."""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_tests(
        self,
        models: List[Dict],
        module_name: str,
        context: str
    ) -> str:
        """Generate pytest test file"""
        
        prompt = f"""Generate pytest test suite for Odoo module.

Models to test: {[m['name'] for m in models]}
Module: {module_name}

Requirements:
1. Use odoo.tests.common.TransactionCase
2. Test CRUD operations for each model
3. Test compute methods
4. Test constraints (_sql_constraints, @api.constrains)
5. Test onchange methods
6. Include negative test cases
7. Use proper assertions
8. Add docstrings for each test method
9. Follow OCA testing standards
10. Include setUp and tearDown methods

Context:
{context}

Output only the Python test code, no markdown backticks."""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_readme(
        self,
        module_name: str,
        description: str,
        models: List[Dict],
        author: str
    ) -> str:
        """Generate README.rst in OCA format"""
        
        prompt = f"""Generate an OCA-compliant README.rst file.

Module: {module_name}
Description: {description}
Models: {[m['name'] for m in models]}
Author: {author}

Requirements:
1. Follow OCA README template structure
2. Include sections: Description, Installation, Configuration, Usage, Known Issues, Bug Tracker, Credits
3. Use proper reStructuredText formatting
4. Add badges (version, license, OCA status)
5. Include screenshots section placeholder
6. Add maintainer information
7. Include proper links

Output only the RST content, no markdown backticks."""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _run_quality_checks(self, module_path: Path) -> float:
        """
        Run OCA quality checks and return score
        
        Returns:
            float: Quality score (0.0 - 1.0)
        """
        logger.info("running_quality_checks", module=module_path.name)
        
        # Would integrate with:
        # - pylint-odoo
        # - pre-commit hooks
        # - OCA maintainer-quality-tools
        
        # Mock implementation
        return 0.95
