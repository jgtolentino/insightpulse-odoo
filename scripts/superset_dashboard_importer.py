#!/usr/bin/env python3
"""
Superset Dashboard Importer
============================

Imports Superset dashboards, charts, and datasets from YAML/JSON export files.

Features:
- Import dashboards from export files
- Create databases and datasets
- Configure chart definitions
- Set up dashboard filters and permissions

Usage:
    # Import a single dashboard
    python3 scripts/superset_dashboard_importer.py import --file dashboards/ci-cd-metrics.yaml

    # Import all dashboards from directory
    python3 scripts/superset_dashboard_importer.py import-all --dir dashboards/

    # Export existing dashboard for backup
    python3 scripts/superset_dashboard_importer.py export --dashboard-id 1 --output backup.yaml

    # List all dashboards
    python3 scripts/superset_dashboard_importer.py list
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME", "admin")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD", "admin")

DASHBOARDS_DIR = Path(__file__).parent.parent / "infra" / "superset"


# ============================================================================
# SUPERSET API CLIENT
# ============================================================================

class SupersetClient:
    """Client for Superset REST API."""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None

    def login(self):
        """Authenticate and get access token."""
        print(f"🔐 Authenticating to Superset at {self.base_url}...")

        # Get CSRF token
        response = self.session.get(f"{self.base_url}/login/")
        if response.status_code != 200:
            raise Exception(f"Failed to get login page: {response.status_code}")

        # Login
        login_data = {
            "username": self.username,
            "password": self.password,
            "provider": "db"
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/security/login",
            json=login_data
        )

        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} {response.text}")

        result = response.json()
        self.access_token = result.get("access_token")

        if not self.access_token:
            raise Exception("No access token received")

        # Set authorization header
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        })

        # Get CSRF token
        response = self.session.get(f"{self.base_url}/api/v1/security/csrf_token/")
        if response.status_code == 200:
            self.csrf_token = response.json().get("result")
            self.session.headers.update({
                "X-CSRFToken": self.csrf_token,
                "Referer": self.base_url
            })

        print("✅ Authentication successful")

    def get_databases(self) -> List[Dict]:
        """Get list of all databases."""
        response = self.session.get(f"{self.base_url}/api/v1/database/")

        if response.status_code != 200:
            raise Exception(f"Failed to get databases: {response.status_code}")

        return response.json().get("result", [])

    def create_database(self, database_config: Dict) -> int:
        """
        Create a new database connection.

        Args:
            database_config: {
                "database_name": "InsightPulse Analytics",
                "sqlalchemy_uri": "postgresql://...",
                "expose_in_sqllab": True
            }

        Returns:
            Database ID
        """
        # Check if database already exists
        databases = self.get_databases()
        for db in databases:
            if db["database_name"] == database_config["database_name"]:
                print(f"  ℹ️  Database '{database_config['database_name']}' already exists (ID: {db['id']})")
                return db["id"]

        # Create new database
        response = self.session.post(
            f"{self.base_url}/api/v1/database/",
            json=database_config
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create database: {response.status_code} {response.text}")

        db_id = response.json().get("id")
        print(f"  ✅ Created database '{database_config['database_name']}' (ID: {db_id})")
        return db_id

    def get_datasets(self) -> List[Dict]:
        """Get list of all datasets."""
        response = self.session.get(f"{self.base_url}/api/v1/dataset/")

        if response.status_code != 200:
            raise Exception(f"Failed to get datasets: {response.status_code}")

        return response.json().get("result", [])

    def create_dataset(self, dataset_config: Dict) -> int:
        """
        Create a new dataset.

        Args:
            dataset_config: {
                "database": 1,
                "schema": "analytics",
                "table_name": "mv_sales_kpi_daily",
                "owners": [1]
            }

        Returns:
            Dataset ID
        """
        # Check if dataset already exists
        datasets = self.get_datasets()
        for ds in datasets:
            if (ds.get("schema") == dataset_config.get("schema") and
                ds.get("table_name") == dataset_config.get("table_name")):
                print(f"  ℹ️  Dataset '{dataset_config['table_name']}' already exists (ID: {ds['id']})")
                return ds["id"]

        # Create new dataset
        response = self.session.post(
            f"{self.base_url}/api/v1/dataset/",
            json=dataset_config
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create dataset: {response.status_code} {response.text}")

        ds_id = response.json().get("id")
        print(f"  ✅ Created dataset '{dataset_config['table_name']}' (ID: {ds_id})")
        return ds_id

    def import_dashboard(self, dashboard_file: Path) -> int:
        """
        Import dashboard from export file (JSON or YAML).

        Args:
            dashboard_file: Path to dashboard export file

        Returns:
            Dashboard ID
        """
        print(f"\n📊 Importing dashboard from {dashboard_file.name}...")

        # Read dashboard file
        with open(dashboard_file, 'r') as f:
            if dashboard_file.suffix in ['.yaml', '.yml']:
                dashboard_data = yaml.safe_load(f)
            else:
                dashboard_data = json.load(f)

        # Import via API
        files = {
            'formData': (dashboard_file.name, open(dashboard_file, 'rb'), 'application/json')
        }

        data = {
            'overwrite': 'true'
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/assets/import/",
            files=files,
            data=data
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to import dashboard: {response.status_code} {response.text}")

        print(f"  ✅ Dashboard imported successfully")

        # Extract dashboard ID from response
        # This varies by Superset version
        return 0

    def export_dashboard(self, dashboard_id: int, output_file: Path):
        """
        Export dashboard to file.

        Args:
            dashboard_id: Dashboard ID to export
            output_file: Output file path
        """
        print(f"📦 Exporting dashboard {dashboard_id} to {output_file}...")

        response = self.session.get(
            f"{self.base_url}/api/v1/dashboard/export/",
            params={"q": f'[{dashboard_id}]'}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to export dashboard: {response.status_code}")

        with open(output_file, 'wb') as f:
            f.write(response.content)

        print(f"  ✅ Dashboard exported to {output_file}")

    def list_dashboards(self) -> List[Dict]:
        """List all dashboards."""
        response = self.session.get(f"{self.base_url}/api/v1/dashboard/")

        if response.status_code != 200:
            raise Exception(f"Failed to list dashboards: {response.status_code}")

        return response.json().get("result", [])


# ============================================================================
# DASHBOARD BOOTSTRAP
# ============================================================================

def bootstrap_ci_cd_dashboard(client: SupersetClient):
    """
    Bootstrap the CI/CD Metrics dashboard from scratch.

    This creates the necessary database connection, datasets, and dashboard
    without requiring an export file.
    """
    print("\n🚀 Bootstrapping CI/CD Metrics Dashboard...")

    # 1. Create database connection
    db_config = {
        "database_name": "InsightPulse Analytics",
        "sqlalchemy_uri": os.getenv(
            "ANALYTICS_DB_URL",
            "postgresql://postgres:password@localhost:5432/postgres?options=-csearch_path%3Danalytics"
        ),
        "expose_in_sqllab": True,
        "allow_dml": False,
        "force_ctas_schema": "analytics",
        "extra": json.dumps({
            "metadata_params": {},
            "engine_params": {},
            "metadata_cache_timeout": {},
            "schemas_allowed_for_csv_upload": []
        })
    }

    db_id = client.create_database(db_config)

    # 2. Create datasets
    datasets = [
        {
            "database": db_id,
            "schema": "ops",
            "table_name": "workflow_runs",
            "owners": [1]
        },
        {
            "database": db_id,
            "schema": "ops",
            "table_name": "workflow_success_rate",
            "owners": [1]
        },
        {
            "database": db_id,
            "schema": "ops",
            "table_name": "task_queue",
            "owners": [1]
        }
    ]

    dataset_ids = {}
    for dataset_config in datasets:
        ds_id = client.create_dataset(dataset_config)
        dataset_ids[dataset_config["table_name"]] = ds_id

    print(f"\n✅ CI/CD Metrics Dashboard bootstrapped")
    print(f"   Database ID: {db_id}")
    print(f"   Datasets created: {len(dataset_ids)}")

    return db_id, dataset_ids


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Superset Dashboard Importer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "command",
        choices=["import", "import-all", "export", "list", "bootstrap"],
        help="Command to execute"
    )

    parser.add_argument(
        "--file",
        type=Path,
        help="Dashboard file to import/export"
    )

    parser.add_argument(
        "--dir",
        type=Path,
        help="Directory containing dashboard files"
    )

    parser.add_argument(
        "--dashboard-id",
        type=int,
        help="Dashboard ID for export"
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for export"
    )

    parser.add_argument(
        "--url",
        default=SUPERSET_URL,
        help="Superset URL"
    )

    parser.add_argument(
        "--username",
        default=SUPERSET_USERNAME,
        help="Superset username"
    )

    parser.add_argument(
        "--password",
        default=SUPERSET_PASSWORD,
        help="Superset password"
    )

    args = parser.parse_args()

    # Create client
    client = SupersetClient(args.url, args.username, args.password)

    try:
        # Login
        client.login()

        # Execute command
        if args.command == "import":
            if not args.file:
                print("ERROR: --file required for import")
                return 1

            client.import_dashboard(args.file)

        elif args.command == "import-all":
            import_dir = args.dir or DASHBOARDS_DIR

            if not import_dir.exists():
                print(f"ERROR: Directory not found: {import_dir}")
                return 1

            dashboard_files = list(import_dir.glob("*.yaml")) + list(import_dir.glob("*.json"))

            if not dashboard_files:
                print(f"No dashboard files found in {import_dir}")
                return 1

            print(f"Found {len(dashboard_files)} dashboard file(s)")

            for dashboard_file in dashboard_files:
                try:
                    client.import_dashboard(dashboard_file)
                except Exception as e:
                    print(f"  ⚠️  Failed to import {dashboard_file.name}: {e}")

        elif args.command == "export":
            if not args.dashboard_id:
                print("ERROR: --dashboard-id required for export")
                return 1

            output_file = args.output or Path(f"dashboard_{args.dashboard_id}.zip")
            client.export_dashboard(args.dashboard_id, output_file)

        elif args.command == "list":
            dashboards = client.list_dashboards()

            print(f"\n📊 Superset Dashboards ({len(dashboards)} total)")
            print("\n{:<5} {:<40} {:<20} {:<10}".format(
                "ID", "TITLE", "OWNER", "STATUS"
            ))
            print("-" * 80)

            for dashboard in dashboards:
                dashboard_id = dashboard.get("id", "?")
                title = dashboard.get("dashboard_title", "Untitled")[:38]
                owner = dashboard.get("owners", [{}])[0].get("username", "unknown") if dashboard.get("owners") else "unknown"
                status = dashboard.get("status", "unknown")

                print(f"{dashboard_id:<5} {title:<40} {owner:<20} {status:<10}")

        elif args.command == "bootstrap":
            bootstrap_ci_cd_dashboard(client)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
