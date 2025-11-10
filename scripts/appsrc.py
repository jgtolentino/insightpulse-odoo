#!/usr/bin/env python3
"""
Application Source Analysis Script

This script analyzes Odoo module structure, dependencies, and generates
comprehensive documentation about the application architecture.

Usage:
    python appsrc.py --scan ./addons
    python appsrc.py --scan ./addons --output datasets/app_structure.json
    python appsrc.py --analyze my_module
"""

import argparse
import ast
import json
import pathlib
import sys
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional


class OdooModuleAnalyzer:
    """Analyzes Odoo module structure and dependencies"""

    def __init__(self, base_path: pathlib.Path):
        self.base_path = pathlib.Path(base_path)
        self.modules = {}
        self.dependencies = defaultdict(set)
        self.reverse_dependencies = defaultdict(set)

    def scan_modules(self) -> Dict[str, Any]:
        """Scan all modules in the given path"""
        print(f"Scanning modules in: {self.base_path}")

        for manifest_path in self.base_path.rglob("__manifest__.py"):
            module_info = self._analyze_module(manifest_path)
            if module_info:
                module_name = module_info["technical_name"]
                self.modules[module_name] = module_info

                # Build dependency graph
                for dep in module_info.get("depends", []):
                    self.dependencies[module_name].add(dep)
                    self.reverse_dependencies[dep].add(module_name)

        print(f"Found {len(self.modules)} modules")
        return self.modules

    def _analyze_module(self, manifest_path: pathlib.Path) -> Optional[Dict[str, Any]]:
        """Analyze a single module"""
        try:
            module_path = manifest_path.parent
            module_name = module_path.name

            # Parse manifest
            manifest_data = self._parse_manifest(manifest_path)

            # Analyze Python files
            models = self._find_models(module_path)
            controllers = self._find_controllers(module_path)

            # Analyze XML files
            views = self._find_views(module_path)
            data_files = self._find_data_files(module_path)

            # Analyze security
            security_files = self._find_security_files(module_path)

            module_info = {
                "technical_name": module_name,
                "name": manifest_data.get("name", module_name),
                "version": manifest_data.get("version", ""),
                "summary": manifest_data.get("summary", ""),
                "description": manifest_data.get("description", ""),
                "author": manifest_data.get("author", ""),
                "license": manifest_data.get("license", ""),
                "category": manifest_data.get("category", ""),
                "depends": manifest_data.get("depends", []),
                "data": manifest_data.get("data", []),
                "demo": manifest_data.get("demo", []),
                "installable": manifest_data.get("installable", True),
                "application": manifest_data.get("application", False),
                "auto_install": manifest_data.get("auto_install", False),
                "path": str(module_path.relative_to(self.base_path)),
                "models": models,
                "controllers": controllers,
                "views": views,
                "data_files": data_files,
                "security_files": security_files,
                "analysis_date": datetime.utcnow().isoformat(),
            }

            return module_info

        except Exception as e:
            print(f"Error analyzing {manifest_path}: {e}")
            return None

    def _parse_manifest(self, manifest_path: pathlib.Path) -> Dict[str, Any]:
        """Parse __manifest__.py file"""
        try:
            content = manifest_path.read_text(encoding="utf-8")
            # Safely evaluate the manifest dictionary
            manifest = ast.literal_eval(content)
            return manifest
        except Exception as e:
            print(f"Error parsing manifest {manifest_path}: {e}")
            return {}

    def _find_models(self, module_path: pathlib.Path) -> List[Dict[str, Any]]:
        """Find Odoo models in the module"""
        models = []
        models_dir = module_path / "models"

        if not models_dir.exists():
            return models

        for py_file in models_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                model_info = self._analyze_python_file(py_file)
                if model_info["classes"]:
                    models.append(
                        {"file": py_file.name, "classes": model_info["classes"]}
                    )
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        return models

    def _find_controllers(self, module_path: pathlib.Path) -> List[Dict[str, Any]]:
        """Find controllers in the module"""
        controllers = []
        controllers_dir = module_path / "controllers"

        if not controllers_dir.exists():
            return controllers

        for py_file in controllers_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                controller_info = self._analyze_python_file(py_file)
                if controller_info["classes"]:
                    controllers.append(
                        {"file": py_file.name, "classes": controller_info["classes"]}
                    )
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        return controllers

    def _analyze_python_file(self, py_file: pathlib.Path) -> Dict[str, Any]:
        """Analyze a Python file for classes and methods"""
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": [
                            m.name for m in node.body if isinstance(m, ast.FunctionDef)
                        ],
                        "base_classes": [self._get_name(base) for base in node.bases],
                    }

                    # Try to find _name attribute for Odoo models
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if (
                                    isinstance(target, ast.Name)
                                    and target.id == "_name"
                                ):
                                    if isinstance(item.value, ast.Constant):
                                        class_info["_name"] = item.value.value

                    classes.append(class_info)

            return {"classes": classes}

        except Exception as e:
            print(f"Error parsing Python file {py_file}: {e}")
            return {"classes": []}

    def _get_name(self, node):
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    def _find_views(self, module_path: pathlib.Path) -> List[str]:
        """Find view XML files"""
        views = []
        views_dir = module_path / "views"

        if views_dir.exists():
            views = [f.name for f in views_dir.glob("*.xml")]

        return views

    def _find_data_files(self, module_path: pathlib.Path) -> List[str]:
        """Find data XML files"""
        data_files = []
        data_dir = module_path / "data"

        if data_dir.exists():
            data_files = [f.name for f in data_dir.glob("*.xml")]

        return data_files

    def _find_security_files(self, module_path: pathlib.Path) -> List[str]:
        """Find security files"""
        security_files = []
        security_dir = module_path / "security"

        if security_dir.exists():
            security_files = [f.name for f in security_dir.glob("*")]

        return security_files

    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze module dependency tree"""
        analysis = {
            "total_modules": len(self.modules),
            "dependency_graph": {},
            "circular_dependencies": self._find_circular_dependencies(),
            "module_layers": self._calculate_module_layers(),
            "standalone_modules": self._find_standalone_modules(),
        }

        for module, deps in self.dependencies.items():
            analysis["dependency_graph"][module] = {
                "depends_on": list(deps),
                "depended_by": list(self.reverse_dependencies[module]),
            }

        return analysis

    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies"""
        # Simple cycle detection (DFS-based)
        circular = []
        visited = set()
        rec_stack = set()

        def dfs(module, path):
            visited.add(module)
            rec_stack.add(module)

            for dep in self.dependencies.get(module, []):
                if dep not in visited:
                    if dfs(dep, path + [dep]):
                        return True
                elif dep in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:] + [dep]
                    if cycle not in circular:
                        circular.append(cycle)
                    return True

            rec_stack.remove(module)
            return False

        for module in self.modules:
            if module not in visited:
                dfs(module, [module])

        return circular

    def _calculate_module_layers(self) -> Dict[int, List[str]]:
        """Calculate module layers based on dependencies"""
        layers = defaultdict(list)
        module_layer = {}

        def get_layer(module):
            if module in module_layer:
                return module_layer[module]

            if module not in self.dependencies or not self.dependencies[module]:
                module_layer[module] = 0
                return 0

            max_dep_layer = max(
                get_layer(dep)
                for dep in self.dependencies[module]
                if dep in self.modules
            )
            module_layer[module] = max_dep_layer + 1
            return max_dep_layer + 1

        for module in self.modules:
            layer = get_layer(module)
            layers[layer].append(module)

        return dict(layers)

    def _find_standalone_modules(self) -> List[str]:
        """Find modules with no dependencies (except base)"""
        standalone = []
        for module, deps in self.dependencies.items():
            if not deps or deps == {"base"}:
                standalone.append(module)
        return standalone

    def generate_report(self, output_path: Optional[pathlib.Path] = None):
        """Generate comprehensive analysis report"""
        report = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "base_path": str(self.base_path),
                "total_modules": len(self.modules),
            },
            "modules": self.modules,
            "dependency_analysis": self.analyze_dependencies(),
        }

        if output_path:
            output_path = pathlib.Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"Report written to: {output_path}")
        else:
            print(json.dumps(report, indent=2))

        return report


def main():
    parser = argparse.ArgumentParser(description="Analyze Odoo module structure")
    parser.add_argument("--scan", type=str, help="Path to scan for modules")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument("--analyze", type=str, help="Analyze specific module")

    args = parser.parse_args()

    if not args.scan:
        parser.print_help()
        sys.exit(1)

    analyzer = OdooModuleAnalyzer(args.scan)
    analyzer.scan_modules()
    analyzer.generate_report(args.output)


if __name__ == "__main__":
    main()
