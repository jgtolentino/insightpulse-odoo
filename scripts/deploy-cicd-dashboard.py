#!/usr/bin/env python3
"""
Deploy CI/CD Metrics Dashboard to Apache Superset

Automates:
1. Database connection setup
2. Dataset creation from ops.workflow_runs
3. Chart creation (success rate, duration trends, status distribution)
4. Dashboard assembly
"""

import os
import requests
import json
from typing import Dict, Any

# Superset configuration
SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME", "admin")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
POSTGRES_URL = os.getenv("POSTGRES_URL")


class SupersetDashboardDeployer:
    """Deploy CI/CD Metrics Dashboard to Superset"""

    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.database_id = None
        self.dataset_id = None
        self.chart_ids = []

    def authenticate(self) -> bool:
        """Authenticate with Superset and get access token"""
        print("🔐 Authenticating with Superset...")

        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/security/login",
            json={
                "username": SUPERSET_USERNAME,
                "password": SUPERSET_PASSWORD,
                "provider": "db",
                "refresh": True
            }
        )

        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            print("✅ Authenticated successfully")
            return True
        else:
            print(f"❌ Authentication failed: {response.text}")
            return False

    def create_database_connection(self) -> bool:
        """Create Supabase database connection in Superset"""
        print("🔗 Creating Supabase database connection...")

        payload = {
            "database_name": "InsightPulse Supabase",
            "sqlalchemy_uri": POSTGRES_URL,
            "expose_in_sqllab": True,
            "allow_ctas": True,
            "allow_cvas": True,
            "allow_dml": False
        }

        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/database/",
            json=payload
        )

        if response.status_code in [200, 201]:
            self.database_id = response.json()["id"]
            print(f"✅ Database connection created (ID: {self.database_id})")
            return True
        elif "already exists" in response.text.lower():
            # Get existing database ID
            databases = self.session.get(f"{SUPERSET_URL}/api/v1/database/").json()
            for db in databases.get("result", []):
                if "supabase" in db["database_name"].lower():
                    self.database_id = db["id"]
                    print(f"✅ Using existing database (ID: {self.database_id})")
                    return True

        print(f"❌ Database connection failed: {response.text}")
        return False

    def create_dataset(self) -> bool:
        """Create ops.workflow_runs dataset"""
        print("📊 Creating workflow_runs dataset...")

        payload = {
            "database": self.database_id,
            "schema": "ops",
            "table_name": "workflow_runs"
        }

        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/dataset/",
            json=payload
        )

        if response.status_code in [200, 201]:
            self.dataset_id = response.json()["id"]
            print(f"✅ Dataset created (ID: {self.dataset_id})")
            return True
        elif "already exists" in response.text.lower():
            # Get existing dataset ID
            datasets = self.session.get(f"{SUPERSET_URL}/api/v1/dataset/").json()
            for ds in datasets.get("result", []):
                if ds["table_name"] == "workflow_runs" and ds["schema"] == "ops":
                    self.dataset_id = ds["id"]
                    print(f"✅ Using existing dataset (ID: {self.dataset_id})")
                    return True

        print(f"❌ Dataset creation failed: {response.text}")
        return False

    def create_success_rate_chart(self) -> int:
        """Create workflow success rate big number chart"""
        print("📈 Creating success rate chart...")

        payload = {
            "slice_name": "Overall Success Rate",
            "viz_type": "big_number_total",
            "datasource_id": self.dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "metric": {
                    "expressionType": "SQL",
                    "sqlExpression": "COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*)",
                    "label": "Success Rate %"
                },
                "adhoc_filters": [],
                "time_range": "Last 7 days"
            })
        }

        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/chart/",
            json=payload
        )

        if response.status_code in [200, 201]:
            chart_id = response.json()["id"]
            self.chart_ids.append(chart_id)
            print(f"✅ Success rate chart created (ID: {chart_id})")
            return chart_id

        print(f"❌ Chart creation failed: {response.text}")
        return None

    def create_duration_chart(self) -> int:
        """Create workflow duration line chart"""
        print("⏱️  Creating duration trends chart...")

        payload = {
            "slice_name": "Workflow Duration Trends",
            "viz_type": "line",
            "datasource_id": self.dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "metrics": ["AVG(duration_seconds)"],
                "groupby": ["workflow_name"],
                "time_range": "Last 30 days",
                "adhoc_filters": []
            })
        }

        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/chart/",
            json=payload
        )

        if response.status_code in [200, 201]:
            chart_id = response.json()["id"]
            self.chart_ids.append(chart_id)
            print(f"✅ Duration chart created (ID: {chart_id})")
            return chart_id

        print(f"❌ Chart creation failed: {response.text}")
        return None

    def create_status_distribution_chart(self) -> int:
        """Create status distribution pie chart"""
        print("🥧 Creating status distribution chart...")

        payload = {
            "slice_name": "Workflow Status Distribution",
            "viz_type": "pie",
            "datasource_id": self.dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "metric": "COUNT(*)",
                "groupby": ["status"],
                "adhoc_filters": []
            })
        }

        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/chart/",
            json=payload
        )

        if response.status_code in [200, 201]:
            chart_id = response.json()["id"]
            self.chart_ids.append(chart_id)
            print(f"✅ Status distribution chart created (ID: {chart_id})")
            return chart_id

        print(f"❌ Chart creation failed: {response.text}")
        return None

    def create_dashboard(self) -> bool:
        """Assemble CI/CD Metrics Dashboard"""
        print("🎨 Assembling dashboard...")

        payload = {
            "dashboard_title": "CI/CD Metrics",
            "slug": "cicd-metrics",
            "published": True,
            "json_metadata": json.dumps({
                "color_scheme": "supersetColors",
                "label_colors": {},
                "refresh_frequency": 300  # 5 minutes
            }),
            "position_json": json.dumps({
                "DASHBOARD_VERSION_KEY": "v2",
                "GRID_ID": {
                    "type": "GRID",
                    "id": "GRID_ID",
                    "children": [f"CHART-{i}" for i in range(len(self.chart_ids))],
                    "parents": ["ROOT_ID"]
                },
                **{
                    f"CHART-{i}": {
                        "type": "CHART",
                        "id": f"CHART-{i}",
                        "children": [],
                        "parents": ["GRID_ID"],
                        "meta": {
                            "width": 4,
                            "height": 4,
                            "chartId": chart_id
                        }
                    }
                    for i, chart_id in enumerate(self.chart_ids)
                }
            })
        }

        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/dashboard/",
            json=payload
        )

        if response.status_code in [200, 201]:
            dashboard_id = response.json()["id"]
            print(f"✅ Dashboard created (ID: {dashboard_id})")
            print(f"🌐 Access at: {SUPERSET_URL}/superset/dashboard/{dashboard_id}/")
            return True

        print(f"❌ Dashboard creation failed: {response.text}")
        return False

    def deploy(self) -> bool:
        """Execute full deployment pipeline"""
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 CI/CD Metrics Dashboard Deployment")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        steps = [
            ("Authenticate", self.authenticate),
            ("Create Database Connection", self.create_database_connection),
            ("Create Dataset", self.create_dataset),
            ("Create Success Rate Chart", self.create_success_rate_chart),
            ("Create Duration Chart", self.create_duration_chart),
            ("Create Status Distribution Chart", self.create_status_distribution_chart),
            ("Assemble Dashboard", self.create_dashboard)
        ]

        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Deployment failed at: {step_name}")
                return False
            print()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ Deployment Complete!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        return True


def main():
    """Main entry point"""
    # Validate environment variables
    required_vars = [
        "SUPERSET_PASSWORD",
        "POSTGRES_URL",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return 1

    deployer = SupersetDashboardDeployer()
    success = deployer.deploy()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
