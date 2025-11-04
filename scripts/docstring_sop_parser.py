#!/usr/bin/env python3
"""
Docstring SOP Parser

Extracts Standard Operating Procedures from Python docstrings.

Usage:
    python scripts/docstring_sop_parser.py --addons addons --output docs/sops
"""

import os
import ast
import re
import argparse
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def extract_sop_from_docstring(docstring: str):
    """Extract SOP steps from docstring."""
    if not docstring:
        return None

    sop_patterns = [
        r'(?:Procedure|Process|Steps|How to|Instructions):\s*(.*?)(?=\n\n|\Z)',
        r'(\d+\.\s+.+(?:\n\s+.+)*)',  # Numbered lists
    ]

    for pattern in sop_patterns:
        matches = re.findall(pattern, docstring, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches

    return None


def scan_python_file(filepath: str):
    """Scan Python file for SOP-like docstrings."""
    try:
        with open(filepath, 'r') as f:
            source = f.read()

        tree = ast.parse(source)
        sops = []

        for node in ast.walk(tree):
            docstring = ast.get_docstring(node)

            if docstring:
                sop_steps = extract_sop_from_docstring(docstring)

                if sop_steps:
                    name = None
                    if isinstance(node, ast.FunctionDef):
                        name = node.name
                    elif isinstance(node, ast.ClassDef):
                        name = node.name
                    elif isinstance(node, ast.Module):
                        name = os.path.basename(filepath)

                    if name:
                        sop = {
                            'name': name,
                            'type': type(node).__name__,
                            'steps': sop_steps,
                            'file': filepath,
                            'line': node.lineno if hasattr(node, 'lineno') else 0
                        }
                        sops.append(sop)

        return sops
    except Exception as e:
        logger.error(f"Error parsing {filepath}: {e}")
        return []


def generate_sop_docs(all_sops: list, output_dir: str):
    """Generate SOP documentation."""
    os.makedirs(output_dir, exist_ok=True)

    modules = {}
    for sop in all_sops:
        path_parts = sop['file'].split('/')
        if len(path_parts) >= 2:
            module_name = path_parts[1]
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(sop)

    for module_name, sops in modules.items():
        sop_file = os.path.join(output_dir, f"{module_name}.md")

        with open(sop_file, 'w') as f:
            f.write(f"# {module_name} - Standard Operating Procedures\n\n")
            f.write(f"Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")

            for sop in sops:
                f.write(f"## {sop['name']}\n\n")
                f.write(f"**Type:** {sop['type']}  \n")
                f.write(f"**Source:** [`{os.path.basename(sop['file'])}:{sop['line']}`]({sop['file']})\n\n")

                f.write("### Procedure\n\n")
                for step_group in sop['steps']:
                    if isinstance(step_group, str):
                        f.write(f"{step_group}\n\n")
                    elif isinstance(step_group, list):
                        for step in step_group:
                            f.write(f"{step}\n")
                    f.write("\n")

                f.write("---\n\n")

        logger.info(f"📄 Generated: {sop_file}")


def main():
    parser = argparse.ArgumentParser(description='Extract SOPs from docstrings')
    parser.add_argument('--addons', nargs='+', default=['addons', 'odoo_addons'],
                       help='Addon directories to scan')
    parser.add_argument('--output', default='docs/sops', help='Output directory')
    args = parser.parse_args()

    all_sops = []

    for addon_dir in args.addons:
        if os.path.exists(addon_dir):
            for root, dirs, files in os.walk(addon_dir):
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        filepath = os.path.join(root, file)
                        sops = scan_python_file(filepath)
                        all_sops.extend(sops)

    logger.info(f"✅ Found {len(all_sops)} SOPs in docstrings")

    if all_sops:
        generate_sop_docs(all_sops, args.output)


if __name__ == '__main__':
    main()
