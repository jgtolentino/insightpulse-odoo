"""Bundle validation for hybrid control plane"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple


class BundleValidator:
    """Validates compiled bundle structure and required fields"""

    # Supported schema versions
    SUPPORTED_VERSIONS = ["1.0"]
    SCHEMA_VERSIONS = {
        "databases": "superset_database_v1",
        "datasets": "superset_dataset_v1",
        "charts": "superset_chart_v1",
        "dashboards": "superset_dashboard_v1"
    }

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.bundles_dir = self.base_dir / "bundles"

        # Required fields for each asset type
        self.required_fields = {
            "databases": ["version", "schema_version", "database_name", "sqlalchemy_uri"],
            "datasets": ["version", "schema_version", "table_name", "database_id"],
            "charts": ["version", "schema_version", "slice_name", "viz_type", "params"],
            "dashboards": ["version", "schema_version", "dashboard_title", "position_json"]
        }

    def validate_yaml_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Validate YAML syntax"""
        try:
            with open(file_path) as f:
                yaml.safe_load(f)
            return True, ""
        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"

    def validate_required_fields(self, file_path: Path, asset_type: str) -> Tuple[bool, List[str]]:
        """Validate required fields for asset type"""
        required = self.required_fields.get(asset_type, [])

        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                return False, ["Root must be a dictionary"]

            errors = []

            # Check required fields
            missing = [field for field in required if field not in data]
            if missing:
                errors.extend([f"Missing required field: {field}" for field in missing])

            # Validate version
            version = data.get("version")
            if version and version not in self.SUPPORTED_VERSIONS:
                errors.append(f"Unsupported version: {version} (supported: {', '.join(self.SUPPORTED_VERSIONS)})")

            # Validate schema_version
            expected_schema = self.SCHEMA_VERSIONS.get(asset_type)
            actual_schema = data.get("schema_version")
            if expected_schema and actual_schema and actual_schema != expected_schema:
                errors.append(f"Invalid schema_version: expected {expected_schema}, got {actual_schema}")

            if errors:
                return False, errors
            return True, []

        except Exception as e:
            return False, [f"Failed to load file: {e}"]

    def validate_file(self, file_path: Path, asset_type: str) -> Dict:
        """Validate a single bundle file"""
        result = {
            "file": file_path.name,
            "valid": True,
            "errors": []
        }

        # Check YAML syntax
        syntax_valid, syntax_error = self.validate_yaml_syntax(file_path)
        if not syntax_valid:
            result["valid"] = False
            result["errors"].append(syntax_error)
            return result

        # Check required fields
        fields_valid, missing_fields = self.validate_required_fields(file_path, asset_type)
        if not fields_valid:
            result["valid"] = False
            result["errors"].extend([f"Missing required field: {field}" for field in missing_fields])

        return result

    def validate_directory(self, bundle_dir: Path, asset_type: str) -> List[Dict]:
        """Validate all files in a bundle directory"""
        results = []

        if not bundle_dir.exists():
            return results

        for file_path in bundle_dir.glob("*.yaml"):
            result = self.validate_file(file_path, asset_type)
            results.append(result)

        return results

    def validate_bundle(self, env: str) -> Dict[str, List[Dict]]:
        """Validate entire bundle for an environment"""
        print(f"✓ Validating bundle for environment: {env}")

        bundle_dir = self.bundles_dir / env

        if not bundle_dir.exists():
            print(f"   ❌ Bundle directory not found: {bundle_dir}")
            return {}

        all_results = {}
        asset_types = ["databases", "datasets", "charts", "dashboards"]

        for asset_type in asset_types:
            type_dir = bundle_dir / asset_type
            results = self.validate_directory(type_dir, asset_type)
            all_results[asset_type] = results

        # Print summary
        self._print_validation_summary(all_results)

        return all_results

    def _print_validation_summary(self, results: Dict[str, List[Dict]]):
        """Print validation summary"""
        total_files = 0
        total_valid = 0
        total_invalid = 0

        print("\n   📊 Validation Summary:")

        for asset_type, file_results in results.items():
            if not file_results:
                continue

            valid_count = sum(1 for r in file_results if r["valid"])
            invalid_count = len(file_results) - valid_count

            total_files += len(file_results)
            total_valid += valid_count
            total_invalid += invalid_count

            print(f"      {asset_type.capitalize()}: {valid_count}/{len(file_results)} valid")

            # Print errors
            for result in file_results:
                if not result["valid"]:
                    print(f"         ❌ {result['file']}")
                    for error in result["errors"]:
                        print(f"            - {error}")

        if total_invalid == 0:
            print(f"\n   ✅ Validation complete: {total_valid}/{total_files} files valid")
        else:
            print(f"\n   ⚠️  Validation complete: {total_valid}/{total_files} valid, {total_invalid} invalid")


def main():
    """CLI entry point for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validator.py <environment>")
        sys.exit(1)

    env = sys.argv[1]
    validator = BundleValidator()

    results = validator.validate_bundle(env)

    # Exit code based on validation results
    has_invalid = any(
        not result["valid"]
        for file_results in results.values()
        for result in file_results
    )

    sys.exit(1 if has_invalid else 0)


if __name__ == "__main__":
    main()
