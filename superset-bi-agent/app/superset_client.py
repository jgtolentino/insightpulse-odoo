import json
import time
from typing import List, Dict, Any, Optional
import requests
from .config import settings

class SupersetClient:
    """Client for Apache Superset REST API"""

    def __init__(self, base_url: str, username: str, password: str, provider: str = "db"):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.provider = provider
        self._access_token: Optional[str] = None
        self._token_ts: Optional[float] = None

    def login(self):
        """Authenticate with Superset and get access token"""
        url = f"{self.base_url}/api/v1/security/login"
        payload = {
            "username": self.username,
            "password": self.password,
            "provider": self.provider,
            "refresh": True,
        }
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        self._access_token = data.get("access_token")
        self._token_ts = time.time()
        if not self._access_token:
            raise RuntimeError("Login succeeded but no access_token returned")

    def _maybe_refresh(self):
        """Refresh token if older than 10 minutes"""
        if not self._token_ts or (time.time() - self._token_ts) > 600:
            self.login()

    @property
    def headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self._access_token:
            self.login()
        self._maybe_refresh()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

    def create_chart(self, dataset_id: int, chart_name: str, viz_type: str, params: Dict[str, Any]) -> int:
        """Create a new Superset chart"""
        url = f"{self.base_url}/api/v1/chart/"
        payload = {
            "slice_name": chart_name,
            "viz_type": viz_type,
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps(params),
        }
        r = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        chart_id = data.get("id") or (data.get("result", {}) or {}).get("id")
        if not chart_id:
            raise RuntimeError(f"Unexpected response creating chart: {data}")
        return int(chart_id)

    def list_datasets(self, database_id: Optional[int] = None, table_name: Optional[str] = None) -> List[Dict]:
        """List Superset datasets"""
        url = f"{self.base_url}/api/v1/dataset/"
        params = {}
        if database_id is not None:
            params["q"] = json.dumps({
                "filters": [{"col": "database", "opr": "rel_o_m", "value": database_id}],
                "page": 0,
                "page_size": 50,
            })
        r = requests.get(url, headers=self.headers, params=params, timeout=30)
        r.raise_for_status()
        items = (r.json().get("result") or {}).get("data") or []
        if table_name:
            items = [i for i in items if i.get("table_name") == table_name]
        return items

    def create_physical_dataset(self, database_id: int, schema: str, table_name: str) -> int:
        """Register an existing DB table as a Superset dataset"""
        url = f"{self.base_url}/api/v1/dataset/"
        payload = {
            "database": database_id,
            "schema": schema,
            "table_name": table_name,
        }
        r = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        ds_id = data.get("id") or (data.get("result", {}) or {}).get("id")
        if not ds_id:
            raise RuntimeError(f"Unexpected dataset response: {data}")
        return int(ds_id)

    def create_dashboard(self, title: str, chart_ids: List[int], css: Optional[str] = None) -> int:
        """Create a Superset dashboard"""
        url = f"{self.base_url}/api/v1/dashboard/"
        payload = {
            "dashboard_title": title,
            "published": True,
            "json_metadata": json.dumps({"expanded_slices": {}, "refresh_frequency": 0}),
            "position_json": json.dumps({}),
            "css": css or "",
            "charts": chart_ids,
        }
        r = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        dash_id = data.get("id") or (data.get("result", {}) or {}).get("id")
        if not dash_id:
            raise RuntimeError(f"Unexpected dashboard response: {data}")
        return int(dash_id)

# Singleton client
client = SupersetClient(
    base_url=settings.superset_url,
    username=settings.superset_username,
    password=settings.superset_password,
    provider=settings.superset_provider,
)
