#!/usr/bin/env python3
"""
Odoo Field Metadata Extraction Tool

Extracts field definitions from Odoo Python model files using AST parsing.
Generates markdown documentation and JSON metadata.

Usage:
    python scripts/extract_odoo_fields.py --addons addons --output docs/fields

Output:
    - docs/fields/{module}.md - Markdown documentation per module
    - docs/fields/metadata.json - Complete JSON metadata
"""

import argparse
import ast
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class OdooFieldExtractor:
    """Extract Odoo field metadata from Python model files."""

    def __init__(self, addon_dirs: List[str]):
        """
        Initialize field extractor.

        Args:
            addon_dirs: List of addon directories to scan
        """
        self.addon_dirs = addon_dirs
        self.all_fields = []

    def extract_fields_from_model(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Extract Odoo field metadata from Python model file.

        Args:
            filepath: Path to Python file

        Returns:
            List of field info dictionaries
        """
        try:
            with open(filepath, "r") as f:
                source = f.read()

            tree = ast.parse(source)
            fields = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class inherits from models.Model
                    is_model = any(
                        isinstance(base, ast.Attribute)
                        and getattr(base.value, "id", None) == "models"
                        for base in node.bases
                    )

                    if is_model:
                        model_name = node.name

                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                # Check if assignment is to a field
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        field_name = target.id

                                        # Check if right side is fields.* call
                                        if isinstance(item.value, ast.Call):
                                            if isinstance(
                                                item.value.func, ast.Attribute
                                            ):
                                                if (
                                                    getattr(
                                                        item.value.func.value,
                                                        "id",
                                                        None,
                                                    )
                                                    == "fields"
                                                ):
                                                    field_type = item.value.func.attr

                                                    # Extract field parameters
                                                    params = {}
                                                    for keyword in item.value.keywords:
                                                        if keyword.arg == "string":
                                                            if isinstance(
                                                                keyword.value,
                                                                ast.Constant,
                                                            ):
                                                                params["label"] = (
                                                                    keyword.value.value
                                                                )
                                                        elif keyword.arg == "help":
                                                            if isinstance(
                                                                keyword.value,
                                                                ast.Constant,
                                                            ):
                                                                params["help"] = (
                                                                    keyword.value.value
                                                                )
                                                        elif keyword.arg == "required":
                                                            if isinstance(
                                                                keyword.value,
                                                                ast.Constant,
                                                            ):
                                                                params["required"] = (
                                                                    keyword.value.value
                                                                )
                                                        elif keyword.arg == "readonly":
                                                            if isinstance(
                                                                keyword.value,
                                                                ast.Constant,
                                                            ):
                                                                params["readonly"] = (
                                                                    keyword.value.value
                                                                )

                                                    field_info = {
                                                        "model": model_name,
                                                        "field_name": field_name,
                                                        "field_type": field_type,
                                                        "params": params,
                                                        "file": filepath,
                                                    }
                                                    fields.append(field_info)

            return fields

        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            return []

    def scan_addons(self) -> int:
        """
        Scan all addon directories for model files.

        Returns:
            Total number of fields extracted
        """
        for addon_dir in self.addon_dirs:
            if not os.path.exists(addon_dir):
                logger.warning(f"Addon directory not found: {addon_dir}")
                continue

            logger.info(f"Scanning addon directory: {addon_dir}")

            for root, dirs, files in os.walk(addon_dir):
                if "models" in root:
                    for file in files:
                        if file.endswith(".py") and file != "__init__.py":
                            filepath = os.path.join(root, file)
                            fields = self.extract_fields_from_model(filepath)
                            self.all_fields.extend(fields)

        logger.info(f"✅ Extracted {len(self.all_fields)} field definitions")
        return len(self.all_fields)

    def generate_documentation(self, output_dir: str):
        """
        Generate markdown documentation for extracted fields.

        Args:
            output_dir: Directory to write documentation files
        """
        os.makedirs(output_dir, exist_ok=True)

        # Group by module
        modules = {}
        for field in self.all_fields:
            # Extract module name from file path
            path_parts = field["file"].split("/")
            if len(path_parts) >= 2:
                module_name = path_parts[1]  # addons/module_name/...
                if module_name not in modules:
                    modules[module_name] = []
                modules[module_name].append(field)

        # Generate documentation for each module
        for module_name, fields in modules.items():
            doc_file = os.path.join(output_dir, f"{module_name}.md")

            with open(doc_file, "w") as f:
                f.write(f"# {module_name} - Field Documentation\n\n")
                f.write(
                    f"Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                )

                # Group by model
                models = {}
                for field in fields:
                    model = field["model"]
                    if model not in models:
                        models[model] = []
                    models[model].append(field)

                for model, model_fields in sorted(models.items()):
                    f.write(f"## Model: `{model}`\n\n")
                    f.write("| Field | Type | Label | Required | Help |\n")
                    f.write("|-------|------|-------|----------|------|\n")

                    for field in sorted(model_fields, key=lambda x: x["field_name"]):
                        name = field["field_name"]
                        ftype = field["field_type"]
                        label = field["params"].get("label", "")
                        required = "✓" if field["params"].get("required") else ""
                        help_text = field["params"].get("help", "")

                        f.write(
                            f"| `{name}` | {ftype} | {label} | {required} | {help_text} |\n"
                        )

                    f.write("\n")

            logger.info(f"📄 Generated: {doc_file}")

        # Save JSON metadata for programmatic access
        metadata_file = os.path.join(output_dir, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "generated_at": datetime.now().isoformat(),
                    "total_fields": len(self.all_fields),
                    "modules": list(modules.keys()),
                    "fields": self.all_fields,
                },
                f,
                indent=2,
            )

        logger.info(f"📄 Generated: {metadata_file}")
        logger.info(f"\n✅ Documentation generation complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract Odoo field metadata")
    parser.add_argument(
        "--addons",
        nargs="+",
        default=["addons", "odoo_addons"],
        help="Addon directories to scan",
    )
    parser.add_argument(
        "--output", default="docs/fields", help="Output directory for documentation"
    )
    args = parser.parse_args()

    extractor = OdooFieldExtractor(addon_dirs=args.addons)
    field_count = extractor.scan_addons()

    if field_count > 0:
        extractor.generate_documentation(output_dir=args.output)
    else:
        logger.warning("No fields found. Ensure addon directories contain Odoo models.")


if __name__ == "__main__":
    main()
