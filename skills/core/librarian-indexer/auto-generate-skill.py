#!/usr/bin/env python3
"""
Auto-Generate Skills from Python Code

This script analyzes Python modules and automatically generates SKILL.md files
based on code structure, complexity, and patterns.

Usage:
    python auto-generate-skill.py --module path/to/module.py
    python auto-generate-skill.py --directory path/to/dir/ --recursive
"""

import ast
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import re

# Try to import optional dependencies
try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit, h_visit
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False
    print("⚠️  radon not installed. Install with: pip install radon")

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("⚠️  jinja2 not installed. Install with: pip install jinja2")


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    docstring: Optional[str]
    signature: str
    line_number: int
    complexity: int = 0
    is_async: bool = False


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    docstring: Optional[str]
    base_classes: List[str]
    methods: List[FunctionInfo]
    line_number: int


@dataclass
class ModuleAnalysis:
    """Complete analysis of a Python module."""
    file_path: str
    module_name: str
    docstring: Optional[str]
    imports: List[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    complexity: Dict[str, any]
    patterns: List[str]
    dependencies: List[str]
    total_lines: int

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            **asdict(self),
            "functions": [asdict(f) for f in self.functions],
            "classes": [
                {
                    **asdict(c),
                    "methods": [asdict(m) for m in c.methods]
                }
                for c in self.classes
            ]
        }


class SkillGenerator:
    """Auto-generate SKILL.md files from Python code."""

    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(__file__),
            "templates"
        )

        if JINJA2_AVAILABLE and os.path.exists(self.templates_dir):
            self.jinja_env = Environment(
                loader=FileSystemLoader(self.templates_dir)
            )
        else:
            self.jinja_env = None

    def analyze_module(self, file_path: str) -> ModuleAnalysis:
        """
        Analyze a Python module and extract all relevant information.

        Args:
            file_path: Path to Python file

        Returns:
            ModuleAnalysis object with all extracted information
        """
        with open(file_path, 'r') as f:
            source_code = f.read()

        # Parse AST
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"❌ Syntax error in {file_path}: {e}")
            return None

        # Extract module name
        module_name = Path(file_path).stem

        # Extract module docstring
        module_docstring = ast.get_docstring(tree)

        # Extract imports
        imports = self._extract_imports(tree)

        # Extract functions
        functions = self._extract_functions(tree)

        # Extract classes
        classes = self._extract_classes(tree)

        # Calculate complexity
        complexity = self._calculate_complexity(source_code, file_path)

        # Detect patterns
        patterns = self._detect_patterns(tree, source_code)

        # Extract dependencies
        dependencies = self._extract_dependencies(imports)

        # Count lines
        total_lines = len(source_code.splitlines())

        return ModuleAnalysis(
            file_path=file_path,
            module_name=module_name,
            docstring=module_docstring,
            imports=imports,
            functions=functions,
            classes=classes,
            complexity=complexity,
            patterns=patterns,
            dependencies=dependencies,
            total_lines=total_lines
        )

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all imports from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)

        return imports

    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        """Extract all module-level functions."""
        functions = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions.append(self._parse_function(node))

        return functions

    def _extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        """Extract all classes with their methods."""
        classes = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(self._parse_class(node))

        return classes

    def _parse_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Parse function node into FunctionInfo."""
        # Extract signature
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        signature = f"{node.name}({', '.join(args)})"

        return FunctionInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            signature=signature,
            line_number=node.lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )

    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        """Parse class node into ClassInfo."""
        # Extract base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}")

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._parse_function(item))

        return ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            base_classes=base_classes,
            methods=methods,
            line_number=node.lineno
        )

    def _calculate_complexity(self, source_code: str, file_path: str) -> Dict:
        """Calculate various complexity metrics."""
        complexity = {
            "cyclomatic": 0,
            "maintainability_index": 0,
            "halstead_metrics": {},
            "lines_of_code": len(source_code.splitlines())
        }

        if RADON_AVAILABLE:
            try:
                # Cyclomatic complexity
                cc_results = cc_visit(source_code)
                if cc_results:
                    avg_complexity = sum(r.complexity for r in cc_results) / len(cc_results)
                    complexity["cyclomatic"] = round(avg_complexity, 2)
                    complexity["max_complexity"] = max(r.complexity for r in cc_results)

                # Maintainability index
                mi_results = mi_visit(source_code, multi=True)
                if mi_results:
                    complexity["maintainability_index"] = round(mi_results, 2)

                # Halstead metrics
                h_results = h_visit(source_code)
                if h_results:
                    complexity["halstead_metrics"] = {
                        "vocabulary": h_results.vocabulary,
                        "length": h_results.length,
                        "difficulty": round(h_results.difficulty, 2),
                        "effort": round(h_results.effort, 2)
                    }
            except Exception as e:
                print(f"⚠️  Error calculating complexity for {file_path}: {e}")

        return complexity

    def _detect_patterns(self, tree: ast.AST, source_code: str) -> List[str]:
        """Detect design patterns and Odoo-specific patterns."""
        patterns = []

        # Check for Odoo patterns
        if "models.Model" in source_code:
            patterns.append("Odoo Model")
        if "models.TransientModel" in source_code:
            patterns.append("Odoo Wizard")
        if "models.AbstractModel" in source_code:
            patterns.append("Odoo Abstract Model")
        if "@api.depends" in source_code:
            patterns.append("Computed Fields")
        if "@api.constrains" in source_code:
            patterns.append("Field Constraints")
        if "state = fields.Selection" in source_code:
            patterns.append("State Machine")

        # Check for general patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Factory pattern
                if any(m.name.startswith("create_") for m in node.body
                      if isinstance(m, ast.FunctionDef)):
                    if "Factory" not in patterns:
                        patterns.append("Factory Pattern")

                # Repository pattern
                if node.name.endswith("Repository"):
                    patterns.append("Repository Pattern")

                # Service pattern
                if node.name.endswith("Service"):
                    patterns.append("Service Layer Pattern")

                # Strategy pattern (multiple classes with same methods)
                method_names = [m.name for m in node.body
                              if isinstance(m, ast.FunctionDef)]
                if len(set(method_names) & {"execute", "process", "handle"}) > 0:
                    if "Strategy Pattern" not in patterns:
                        patterns.append("Strategy Pattern")

        return patterns

    def _extract_dependencies(self, imports: List[str]) -> List[str]:
        """Extract meaningful dependencies."""
        dependencies = []

        for imp in imports:
            # Extract top-level package
            if "." in imp:
                top_level = imp.split(".")[0]
            else:
                top_level = imp

            # Filter standard library and common packages
            if top_level not in ["os", "sys", "re", "json", "datetime",
                                "typing", "pathlib", "collections", "itertools"]:
                if top_level not in dependencies:
                    dependencies.append(top_level)

        return dependencies

    def generate_skill(
        self,
        analysis: ModuleAnalysis,
        output_path: str,
        template_name: str = "skill-base.md.j2"
    ) -> bool:
        """
        Generate SKILL.md file from analysis.

        Args:
            analysis: ModuleAnalysis object
            output_path: Path to output SKILL.md file
            template_name: Template to use

        Returns:
            True if successful, False otherwise
        """
        if not analysis:
            return False

        # Determine expertise level based on complexity
        expertise_level = self._determine_expertise_level(analysis)

        # Generate skill ID
        skill_id = analysis.module_name.replace("_", "-")

        # Prepare template context
        context = {
            "skill_id": skill_id,
            "skill_name": analysis.module_name.replace("_", " ").title() + " Specialist",
            "version": "1.0.0",
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "expertise_level": expertise_level,
            "analysis": analysis.to_dict(),
            "source_module": analysis.file_path,
            "module_docstring": analysis.docstring or "No module docstring available",
            "functions": analysis.functions,
            "classes": analysis.classes,
            "patterns": analysis.patterns,
            "dependencies": analysis.dependencies,
            "complexity": analysis.complexity
        }

        # Render template or use fallback
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template(template_name)
                content = template.render(**context)
            except Exception as e:
                print(f"⚠️  Template error: {e}. Using fallback.")
                content = self._generate_fallback_skill(context)
        else:
            content = self._generate_fallback_skill(context)

        # Write file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)

        print(f"✅ Generated skill: {output_path}")
        return True

    def _determine_expertise_level(self, analysis: ModuleAnalysis) -> str:
        """Determine expertise level based on complexity."""
        cyclomatic = analysis.complexity.get("cyclomatic", 0)
        loc = analysis.total_lines

        if cyclomatic > 20 or loc > 500:
            return "Expert"
        elif cyclomatic > 10 or loc > 200:
            return "Advanced"
        elif cyclomatic > 5 or loc > 50:
            return "Intermediate"
        else:
            return "Beginner"

    def _generate_fallback_skill(self, context: Dict) -> str:
        """Generate skill content without templates."""
        analysis_dict = context["analysis"]

        content = f"""# {context['skill_name']}

**Skill ID:** `{context['skill_id']}`
**Version:** {context['version']}
**Auto-Generated:** {context['generated_date']}
**Source Module:** `{context['source_module']}`
**Expertise Level:** {context['expertise_level']}

---

## 🎯 Purpose

{context['module_docstring']}

---

## 🧠 Core Competencies

### Module Complexity

- **Cyclomatic Complexity:** {analysis_dict['complexity']['cyclomatic']}
- **Lines of Code:** {analysis_dict['total_lines']}
- **Maintainability Index:** {analysis_dict['complexity'].get('maintainability_index', 'N/A')}

### Functions ({len(context['functions'])})

"""

        for func in context['functions']:
            content += f"""
#### `{func.signature}`

{func.docstring or 'No docstring available'}

- **Line:** {func.line_number}
- **Async:** {func.is_async}

"""

        content += f"""
### Classes ({len(context['classes'])})

"""

        for cls in context['classes']:
            content += f"""
#### `{cls.name}`

{cls.docstring or 'No docstring available'}

**Base Classes:** {', '.join(cls.base_classes) if cls.base_classes else 'None'}

**Methods ({len(cls.methods)}):**
"""
            for method in cls.methods:
                content += f"\n- `{method.signature}`"

            content += "\n\n"

        if context['patterns']:
            content += f"""
### Detected Patterns

"""
            for pattern in context['patterns']:
                content += f"- {pattern}\n"

        if context['dependencies']:
            content += f"""
### Dependencies

"""
            for dep in context['dependencies']:
                content += f"- {dep}\n"

        content += f"""
---

## 📊 Metrics Summary

| Metric | Value |
|--------|-------|
| Cyclomatic Complexity | {analysis_dict['complexity']['cyclomatic']} |
| Lines of Code | {analysis_dict['total_lines']} |
| Functions | {len(context['functions'])} |
| Classes | {len(context['classes'])} |
| Patterns | {len(context['patterns'])} |
| Dependencies | {len(context['dependencies'])} |

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
"""

        return content


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-generate SKILL.md files from Python code"
    )
    parser.add_argument(
        "--module",
        help="Path to a single Python module"
    )
    parser.add_argument(
        "--directory",
        help="Path to directory to scan"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan directory"
    )
    parser.add_argument(
        "--output",
        default="skills/",
        help="Output directory for generated skills"
    )
    parser.add_argument(
        "--template",
        default="skill-base.md.j2",
        help="Template to use"
    )
    parser.add_argument(
        "--min-complexity",
        type=int,
        default=0,
        help="Minimum cyclomatic complexity to generate skill"
    )
    parser.add_argument(
        "--min-loc",
        type=int,
        default=0,
        help="Minimum lines of code to generate skill"
    )

    args = parser.parse_args()

    generator = SkillGenerator()

    # Collect modules to analyze
    modules_to_analyze = []

    if args.module:
        modules_to_analyze.append(args.module)
    elif args.directory:
        if args.recursive:
            for root, dirs, files in os.walk(args.directory):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        modules_to_analyze.append(os.path.join(root, file))
        else:
            for file in os.listdir(args.directory):
                if file.endswith(".py") and not file.startswith("__"):
                    modules_to_analyze.append(os.path.join(args.directory, file))
    else:
        parser.print_help()
        return

    print(f"🔍 Found {len(modules_to_analyze)} modules to analyze")

    # Analyze and generate skills
    generated = 0
    skipped = 0

    for module_path in modules_to_analyze:
        print(f"\n📝 Analyzing: {module_path}")

        analysis = generator.analyze_module(module_path)

        if not analysis:
            skipped += 1
            continue

        # Filter by complexity
        if analysis.complexity["cyclomatic"] < args.min_complexity:
            print(f"⏭️  Skipped (complexity {analysis.complexity['cyclomatic']} < {args.min_complexity})")
            skipped += 1
            continue

        # Filter by LOC
        if analysis.total_lines < args.min_loc:
            print(f"⏭️  Skipped (LOC {analysis.total_lines} < {args.min_loc})")
            skipped += 1
            continue

        # Generate output path
        relative_path = Path(module_path).relative_to(Path(module_path).parents[2])
        skill_dir = os.path.join(args.output, relative_path.parent.name)
        skill_file = os.path.join(skill_dir, "SKILL.md")

        # Generate skill
        success = generator.generate_skill(analysis, skill_file, args.template)

        if success:
            generated += 1

    print(f"\n✨ Summary:")
    print(f"   Generated: {generated}")
    print(f"   Skipped: {skipped}")
    print(f"   Output: {args.output}")


if __name__ == "__main__":
    main()
