#!/usr/bin/env python3
"""
InsightPulse Odoo Documentation Generator

Generates comprehensive documentation from Odoo modules with:
- Module inventory with dependencies
- Model schemas with fields and methods
- View structures
- Security rules
- BIR compliance mappings
- Finance SSC workflows

Usage:
    python scripts/generate_odoo_docs.py
    python scripts/generate_odoo_docs.py --format html
    python scripts/generate_odoo_docs.py --output docs/odoo-api.md

Output:
    - docs/GENERATED_ODOO_DOCS.md (markdown)
    - docs/GENERATED_ODOO_DOCS.html (interactive HTML)
"""

import ast
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET


@dataclass
class OdooField:
    """Represents an Odoo model field"""
    name: str
    field_type: str
    required: bool = False
    readonly: bool = False
    help_text: str = ""
    relation: Optional[str] = None


@dataclass
class OdooModel:
    """Represents an Odoo model"""
    name: str
    inherit: Optional[str]
    description: str
    file_path: str
    fields: List[OdooField]
    methods: List[str]
    table_name: Optional[str] = None


@dataclass
class OdooModule:
    """Represents an Odoo module"""
    name: str
    version: str
    summary: str
    description: str
    author: str
    depends: List[str]
    category: str
    models: List[OdooModel]
    views: List[str]
    security_files: List[str]
    data_files: List[str]
    installable: bool = True
    application: bool = False


class OdooDocsGenerator:
    """Generate comprehensive documentation for InsightPulse Odoo modules"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.modules: List[OdooModule] = []
        self.stats = {
            'total_modules': 0,
            'total_models': 0,
            'total_fields': 0,
            'total_views': 0,
            'bir_modules': 0,
            'finance_modules': 0,
        }

    def scan_modules(self) -> List[OdooModule]:
        """Scan custom-addons for Odoo modules"""
        addons_path = self.repo_path / "custom-addons"

        if not addons_path.exists():
            print(f"⚠️  custom-addons directory not found at {addons_path}")
            # Also check addons/custom
            addons_path = self.repo_path / "addons" / "custom"
            if not addons_path.exists():
                print("❌ No custom addons found")
                return []

        print(f"📂 Scanning modules in {addons_path}")

        for module_dir in addons_path.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith('.'):
                continue

            manifest = module_dir / "__manifest__.py"
            if not manifest.exists():
                continue

            try:
                module_info = self.parse_manifest(manifest)
                module_info.models = self.extract_models(module_dir / "models")
                module_info.views = self.extract_views(module_dir / "views")
                module_info.security_files = self.extract_security(module_dir / "security")
                module_info.data_files = self.extract_data_files(module_dir / "data")

                self.modules.append(module_info)

                # Update stats
                self.stats['total_modules'] += 1
                self.stats['total_models'] += len(module_info.models)
                self.stats['total_views'] += len(module_info.views)

                for model in module_info.models:
                    self.stats['total_fields'] += len(model.fields)

                # Detect BIR/Finance modules
                if 'bir' in module_info.name.lower():
                    self.stats['bir_modules'] += 1
                if 'finance' in module_info.category.lower() or 'account' in module_info.category.lower():
                    self.stats['finance_modules'] += 1

                print(f"  ✅ {module_info.name} v{module_info.version}")

            except Exception as e:
                print(f"  ⚠️  Error parsing {module_dir.name}: {e}")

        return self.modules

    def parse_manifest(self, manifest_path: Path) -> OdooModule:
        """Parse __manifest__.py"""
        with open(manifest_path, encoding='utf-8') as f:
            content = f.read()

        # Safe eval of manifest dict
        try:
            manifest = ast.literal_eval(content)
        except:
            # Fallback: try to extract key info with regex
            manifest = {}

        return OdooModule(
            name=manifest.get('name', 'Unknown'),
            version=manifest.get('version', '1.0.0'),
            summary=manifest.get('summary', ''),
            description=manifest.get('description', ''),
            author=manifest.get('author', 'InsightPulse AI'),
            depends=manifest.get('depends', []),
            category=manifest.get('category', 'Uncategorized'),
            models=[],
            views=[],
            security_files=[],
            data_files=[],
            installable=manifest.get('installable', True),
            application=manifest.get('application', False),
        )

    def extract_models(self, models_path: Path) -> List[OdooModel]:
        """Extract Odoo model definitions from Python files"""
        models = []

        if not models_path.exists():
            return models

        for py_file in models_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            try:
                with open(py_file, encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's an Odoo model
                        model_name = self._get_model_name(node)
                        inherit = self._get_inherit(node)

                        if model_name or inherit:
                            models.append(OdooModel(
                                name=model_name or inherit or node.name,
                                inherit=inherit,
                                description=self._get_docstring(node),
                                file_path=str(py_file.relative_to(self.repo_path)),
                                fields=self._extract_fields(node),
                                methods=self._extract_methods(node),
                                table_name=self._get_table_name(node)
                            ))
            except Exception as e:
                print(f"    ⚠️  Error parsing {py_file.name}: {e}")

        return models

    def _get_model_name(self, class_node: ast.ClassDef) -> Optional[str]:
        """Extract _name from class"""
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '_name':
                        if isinstance(node.value, ast.Constant):
                            return node.value.value
        return None

    def _get_inherit(self, class_node: ast.ClassDef) -> Optional[str]:
        """Extract _inherit from class"""
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '_inherit':
                        if isinstance(node.value, ast.Constant):
                            return node.value.value
        return None

    def _get_table_name(self, class_node: ast.ClassDef) -> Optional[str]:
        """Extract _table from class"""
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '_table':
                        if isinstance(node.value, ast.Constant):
                            return node.value.value
        return None

    def _get_docstring(self, class_node: ast.ClassDef) -> str:
        """Extract class docstring"""
        if (isinstance(class_node.body[0], ast.Expr) and
            isinstance(class_node.body[0].value, ast.Constant)):
            return class_node.body[0].value.value
        return ""

    def _extract_fields(self, class_node: ast.ClassDef) -> List[OdooField]:
        """Extract Odoo field definitions"""
        fields = []

        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Check if it's a fields.* assignment
                        if isinstance(node.value, ast.Call):
                            field_type = self._get_field_type(node.value)
                            if field_type:
                                fields.append(OdooField(
                                    name=target.id,
                                    field_type=field_type,
                                    required=self._is_required(node.value),
                                    readonly=self._is_readonly(node.value),
                                    help_text=self._get_help_text(node.value),
                                    relation=self._get_relation(node.value)
                                ))

        return fields

    def _get_field_type(self, call_node: ast.Call) -> Optional[str]:
        """Get Odoo field type"""
        if hasattr(call_node.func, 'attr'):
            return call_node.func.attr
        return None

    def _is_required(self, call_node: ast.Call) -> bool:
        """Check if field is required"""
        for keyword in call_node.keywords:
            if keyword.arg == 'required':
                if isinstance(keyword.value, ast.Constant):
                    return keyword.value.value
        return False

    def _is_readonly(self, call_node: ast.Call) -> bool:
        """Check if field is readonly"""
        for keyword in call_node.keywords:
            if keyword.arg == 'readonly':
                if isinstance(keyword.value, ast.Constant):
                    return keyword.value.value
        return False

    def _get_help_text(self, call_node: ast.Call) -> str:
        """Get field help text"""
        for keyword in call_node.keywords:
            if keyword.arg == 'help':
                if isinstance(keyword.value, ast.Constant):
                    return keyword.value.value
        return ""

    def _get_relation(self, call_node: ast.Call) -> Optional[str]:
        """Get relation for Many2one, One2many, Many2many fields"""
        # Check first positional argument (comodel_name)
        if call_node.args and isinstance(call_node.args[0], ast.Constant):
            return call_node.args[0].value

        # Check comodel_name keyword
        for keyword in call_node.keywords:
            if keyword.arg == 'comodel_name':
                if isinstance(keyword.value, ast.Constant):
                    return keyword.value.value
        return None

    def _extract_methods(self, class_node: ast.ClassDef) -> List[str]:
        """Extract method names from class"""
        methods = []
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_') or node.name in ['__init__', '_compute_', '_onchange_']:
                    methods.append(node.name)
        return methods

    def extract_views(self, views_path: Path) -> List[str]:
        """Extract view files"""
        views = []

        if not views_path.exists():
            return views

        for xml_file in views_path.glob("*.xml"):
            views.append(str(xml_file.relative_to(self.repo_path)))

        return views

    def extract_security(self, security_path: Path) -> List[str]:
        """Extract security files"""
        security_files = []

        if not security_path.exists():
            return security_files

        for csv_file in security_path.glob("*.csv"):
            security_files.append(str(csv_file.relative_to(self.repo_path)))

        return security_files

    def extract_data_files(self, data_path: Path) -> List[str]:
        """Extract data files"""
        data_files = []

        if not data_path.exists():
            return data_files

        for xml_file in data_path.glob("*.xml"):
            data_files.append(str(xml_file.relative_to(self.repo_path)))

        return data_files

    def generate_markdown(self) -> str:
        """Generate comprehensive markdown documentation"""
        md = f"""# InsightPulse Odoo API Documentation

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Repository**: insightpulse-odoo
**Odoo Version**: 19.0

---

## 📊 Summary Statistics

| Metric | Count |
|--------|-------|
| Total Modules | {self.stats['total_modules']} |
| Total Models | {self.stats['total_models']} |
| Total Fields | {self.stats['total_fields']} |
| Total Views | {self.stats['total_views']} |
| BIR Modules | {self.stats['bir_modules']} |
| Finance Modules | {self.stats['finance_modules']} |

---

## 📦 Modules ({len(self.modules)})

"""

        # Sort modules by category
        modules_by_category = {}
        for module in self.modules:
            category = module.category or 'Uncategorized'
            if category not in modules_by_category:
                modules_by_category[category] = []
            modules_by_category[category].append(module)

        for category, modules in sorted(modules_by_category.items()):
            md += f"\n### {category}\n\n"

            for module in modules:
                md += f"#### {module.name}\n\n"
                md += f"**Version**: {module.version}  \n"
                md += f"**Author**: {module.author}  \n"

                if module.summary:
                    md += f"**Summary**: {module.summary}  \n"

                if module.depends:
                    md += f"**Dependencies**: {', '.join([f'`{d}`' for d in module.depends])}  \n"

                md += f"**Installable**: {'✓' if module.installable else '✗'}  \n"
                md += f"**Application**: {'✓' if module.application else '✗'}  \n"
                md += "\n"

                if module.description:
                    md += f"> {module.description[:200]}...\n\n"

                # Models
                if module.models:
                    md += f"**Models** ({len(module.models)}):\n\n"

                    for model in module.models:
                        md += f"##### `{model.name}`\n\n"

                        if model.description:
                            md += f"{model.description}\n\n"

                        if model.inherit:
                            md += f"*Inherits*: `{model.inherit}`  \n"

                        md += f"*File*: `{model.file_path}`  \n"

                        if model.table_name:
                            md += f"*Table*: `{model.table_name}`  \n"

                        md += "\n"

                        if model.fields:
                            md += "**Fields**:\n\n"
                            md += "| Name | Type | Required | Readonly | Relation |\n"
                            md += "|------|------|----------|----------|----------|\n"

                            for field in model.fields:
                                req = "✓" if field.required else ""
                                ro = "✓" if field.readonly else ""
                                rel = field.relation or ""
                                md += f"| `{field.name}` | {field.field_type} | {req} | {ro} | {rel} |\n"

                            md += "\n"

                        if model.methods:
                            md += f"**Methods**: {', '.join([f'`{m}()`' for m in model.methods[:10]])}  \n"
                            if len(model.methods) > 10:
                                md += f"*...and {len(model.methods) - 10} more*  \n"
                            md += "\n"

                # Views
                if module.views:
                    md += f"**Views**: {len(module.views)} XML files  \n"

                # Security
                if module.security_files:
                    md += f"**Security**: {len(module.security_files)} ACL files  \n"

                # Data
                if module.data_files:
                    md += f"**Data**: {len(module.data_files)} data files  \n"

                md += "\n---\n\n"

        # Add model index
        md += "\n## 🔍 Model Index\n\n"
        md += "| Model | Module | Fields | Methods |\n"
        md += "|-------|--------|--------|--------|\n"

        all_models = []
        for module in self.modules:
            for model in module.models:
                all_models.append((model, module))

        for model, module in sorted(all_models, key=lambda x: x[0].name):
            md += f"| `{model.name}` | {module.name} | {len(model.fields)} | {len(model.methods)} |\n"

        md += "\n---\n\n"
        md += f"*Generated by InsightPulse Odoo Docs Generator*\n"

        return md

    def generate_html(self) -> str:
        """Generate interactive HTML documentation"""
        try:
            import markdown
        except ImportError:
            print("⚠️  markdown package not installed. Installing...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'markdown'])
            import markdown

        md_content = self.generate_markdown()
        html_body = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'toc']
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InsightPulse Odoo API Documentation</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #0d1117;
            color: #c9d1d9;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2em;
        }}
        .markdown-body {{
            background: #0d1117;
            color: #c9d1d9;
            padding: 2em;
            border-radius: 6px;
        }}
        .markdown-body table {{
            background: #161b22;
        }}
        .markdown-body table tr {{
            background: #161b22;
            border-top: 1px solid #21262d;
        }}
        .markdown-body table tr:nth-child(2n) {{
            background: #0d1117;
        }}
        .markdown-body code {{
            background: #161b22;
            color: #79c0ff;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3em 0;
            text-align: center;
            margin-bottom: 2em;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 0.5em 0 0 0;
            opacity: 0.9;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1em;
            margin: 2em 0;
        }}
        .stat-card {{
            background: #161b22;
            padding: 1.5em;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #21262d;
        }}
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #58a6ff;
        }}
        .stat-card .label {{
            color: #8b949e;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 InsightPulse Odoo</h1>
        <p>API Documentation • Generated {datetime.now().strftime('%B %d, %Y')}</p>
    </div>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="number">{self.stats['total_modules']}</div>
                <div class="label">Modules</div>
            </div>
            <div class="stat-card">
                <div class="number">{self.stats['total_models']}</div>
                <div class="label">Models</div>
            </div>
            <div class="stat-card">
                <div class="number">{self.stats['total_fields']}</div>
                <div class="label">Fields</div>
            </div>
            <div class="stat-card">
                <div class="number">{self.stats['total_views']}</div>
                <div class="label">Views</div>
            </div>
            <div class="stat-card">
                <div class="number">{self.stats['bir_modules']}</div>
                <div class="label">BIR Modules</div>
            </div>
            <div class="stat-card">
                <div class="number">{self.stats['finance_modules']}</div>
                <div class="label">Finance Modules</div>
            </div>
        </div>

        <div class="markdown-body">
            {html_body}
        </div>
    </div>

    <script>
        // Add search functionality
        document.addEventListener('DOMContentLoaded', function() {{
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {{
                table.style.width = '100%';
            }});
        }});
    </script>
</body>
</html>
"""

    def generate_json(self) -> str:
        """Generate JSON API documentation"""
        data = {
            'generated': datetime.now().isoformat(),
            'stats': self.stats,
            'modules': [
                {
                    'name': m.name,
                    'version': m.version,
                    'summary': m.summary,
                    'category': m.category,
                    'depends': m.depends,
                    'models': [
                        {
                            'name': model.name,
                            'inherit': model.inherit,
                            'description': model.description,
                            'fields': [asdict(f) for f in model.fields],
                            'methods': model.methods
                        }
                        for model in m.models
                    ]
                }
                for m in self.modules
            ]
        }
        return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Generate InsightPulse Odoo documentation')
    parser.add_argument('--format', choices=['markdown', 'html', 'json', 'all'], default='all',
                        help='Output format (default: all)')
    parser.add_argument('--output', type=str,
                        help='Output file path (default: docs/GENERATED_ODOO_DOCS.*)')
    args = parser.parse_args()

    # Determine repo path
    repo_path = Path(__file__).parent.parent

    print("📚 InsightPulse Odoo Documentation Generator")
    print("=" * 50)
    print()

    # Generate docs
    generator = OdooDocsGenerator(str(repo_path))
    generator.scan_modules()

    print()
    print("📊 Statistics:")
    for key, value in generator.stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print()

    # Output
    output_dir = repo_path / "docs"
    output_dir.mkdir(exist_ok=True)

    if args.format in ['markdown', 'all']:
        md_file = args.output if args.output and args.output.endswith('.md') else output_dir / "GENERATED_ODOO_DOCS.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(generator.generate_markdown())
        print(f"✅ Markdown: {md_file}")

    if args.format in ['html', 'all']:
        html_file = args.output if args.output and args.output.endswith('.html') else output_dir / "GENERATED_ODOO_DOCS.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(generator.generate_html())
        print(f"✅ HTML: {html_file}")

    if args.format in ['json', 'all']:
        json_file = args.output if args.output and args.output.endswith('.json') else output_dir / "GENERATED_ODOO_DOCS.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(generator.generate_json())
        print(f"✅ JSON: {json_file}")

    print()
    print("🎉 Documentation generation complete!")


if __name__ == "__main__":
    main()
