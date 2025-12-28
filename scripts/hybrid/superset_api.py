"""Superset API client for hybrid control plane"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional


class SupersetAPI:
    """Client for Superset REST API operations"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None

    def login(self) -> str:
        """Authenticate and get access token"""
        url = f"{self.base_url}/api/v1/security/login"
        payload = {
            "username": self.username,
            "password": self.password,
            "provider": "db",
            "refresh": True
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        return self.token

    def export_dashboards(self, output_dir: Path) -> List[Dict]:
        """Export all dashboards"""
        output_dir.mkdir(parents=True, exist_ok=True)

        url = f"{self.base_url}/api/v1/dashboard/"
        params = {"q": "(page:0,page_size:100)"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        dashboards = response.json().get("result", [])

        for dashboard in dashboards:
            dash_file = output_dir / f"dashboard_{dashboard['id']}.json"
            dash_file.write_text(json.dumps(dashboard, indent=2))

        return dashboards

    def export_charts(self, output_dir: Path) -> List[Dict]:
        """Export all charts"""
        output_dir.mkdir(parents=True, exist_ok=True)

        url = f"{self.base_url}/api/v1/chart/"
        params = {"q": "(page:0,page_size:500)"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        charts = response.json().get("result", [])

        for chart in charts:
            chart_file = output_dir / f"chart_{chart['id']}.json"
            chart_file.write_text(json.dumps(chart, indent=2))

        return charts

    def export_datasets(self, output_dir: Path) -> List[Dict]:
        """Export all datasets"""
        output_dir.mkdir(parents=True, exist_ok=True)

        url = f"{self.base_url}/api/v1/dataset/"
        params = {"q": "(page:0,page_size:500)"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        datasets = response.json().get("result", [])

        for dataset in datasets:
            ds_file = output_dir / f"dataset_{dataset['id']}.json"
            ds_file.write_text(json.dumps(dataset, indent=2))

        return datasets

    def export_databases(self, output_dir: Path) -> List[Dict]:
        """Export all database connections"""
        output_dir.mkdir(parents=True, exist_ok=True)

        url = f"{self.base_url}/api/v1/database/"
        params = {"q": "(page:0,page_size:100)"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        databases = response.json().get("result", [])

        for database in databases:
            db_file = output_dir / f"database_{database['id']}.json"
            db_file.write_text(json.dumps(database, indent=2))

        return databases

    def export_all(self, output_dir: Path) -> Dict[str, int]:
        """Export all assets"""
        self.login()

        stats = {}

        print("   Exporting dashboards...")
        dashboards = self.export_dashboards(output_dir / "dashboards")
        stats["dashboards"] = len(dashboards)

        print("   Exporting charts...")
        charts = self.export_charts(output_dir / "charts")
        stats["charts"] = len(charts)

        print("   Exporting datasets...")
        datasets = self.export_datasets(output_dir / "datasets")
        stats["datasets"] = len(datasets)

        print("   Exporting databases...")
        databases = self.export_databases(output_dir / "databases")
        stats["databases"] = len(databases)

        return stats
