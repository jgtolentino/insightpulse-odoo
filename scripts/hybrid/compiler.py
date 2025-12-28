"""Jinja2 template compilation engine for hybrid control plane"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateError
from dotenv import dotenv_values


class TemplateCompiler:
    """Compiles Jinja2 templates into environment-specific YAML bundles"""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.assets_dir = self.base_dir / "assets"
        self.bundles_dir = self.base_dir / "bundles"

    def load_env_vars(self, env: str) -> Dict[str, str]:
        """Load environment variables from bundles/<env>/.env"""
        env_file = self.bundles_dir / env / ".env"

        if not env_file.exists():
            raise FileNotFoundError(f"Environment file not found: {env_file}")

        # Load .env file
        env_vars = dotenv_values(env_file)

        print(f"   Loaded {len(env_vars)} variables from {env_file}")
        return env_vars

    def compile_template(self, template_path: Path, env_vars: Dict[str, str]) -> str:
        """Compile a single Jinja2 template with environment variables"""
        try:
            # Read template
            template_content = template_path.read_text()

            # Create Jinja2 environment
            jinja_env = Environment(
                loader=FileSystemLoader(template_path.parent),
                trim_blocks=True,
                lstrip_blocks=True
            )

            # Render template
            template = jinja_env.from_string(template_content)
            rendered = template.render(**env_vars)

            return rendered
        except TemplateError as e:
            raise RuntimeError(f"Template rendering failed for {template_path}: {e}")

    def validate_yaml(self, content: str, template_path: Path) -> bool:
        """Validate YAML structure"""
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError as e:
            print(f"   ⚠️  YAML validation failed for {template_path}: {e}")
            return False

    def compile_directory(self, template_dir: Path, output_dir: Path, env_vars: Dict[str, str]) -> int:
        """Compile all templates in a directory"""
        if not template_dir.exists():
            return 0

        output_dir.mkdir(parents=True, exist_ok=True)
        compiled_count = 0

        # Find all .j2 templates
        for template_path in template_dir.glob("*.j2"):
            try:
                # Compile template
                rendered = self.compile_template(template_path, env_vars)

                # Validate YAML
                if not self.validate_yaml(rendered, template_path):
                    continue

                # Write output (remove .j2 extension)
                output_path = output_dir / template_path.stem
                output_path.write_text(rendered)

                print(f"   ✅ Compiled: {template_path.name} → {output_path.name}")
                compiled_count += 1

            except Exception as e:
                print(f"   ❌ Failed to compile {template_path.name}: {e}")

        return compiled_count

    def compile_all(self, env: str) -> Dict[str, int]:
        """Compile all asset templates for an environment"""
        print(f"🔨 Compiling templates for environment: {env}")

        # Load environment variables
        try:
            env_vars = self.load_env_vars(env)
        except FileNotFoundError as e:
            print(f"   ❌ {e}")
            return {}

        # Prepare output directory
        bundle_dir = self.bundles_dir / env
        bundle_dir.mkdir(parents=True, exist_ok=True)

        stats = {}

        # Compile each asset type
        asset_types = ["databases", "datasets", "charts", "dashboards"]

        for asset_type in asset_types:
            template_dir = self.assets_dir / asset_type
            output_dir = bundle_dir / asset_type

            count = self.compile_directory(template_dir, output_dir, env_vars)
            stats[asset_type] = count

        # Summary
        total = sum(stats.values())
        print(f"\n   📊 Compilation Summary:")
        for asset_type, count in stats.items():
            print(f"      {asset_type.capitalize()}: {count}")
        print(f"\n   ✅ Compiled {total} templates to {bundle_dir}")

        return stats


def main():
    """CLI entry point for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python compiler.py <environment>")
        sys.exit(1)

    env = sys.argv[1]
    compiler = TemplateCompiler()

    try:
        stats = compiler.compile_all(env)
        sys.exit(0 if sum(stats.values()) > 0 else 1)
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
