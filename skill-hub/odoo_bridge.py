"""
Odoo Bridge Module for Skill Hub
Provides XML-RPC and JSON-RPC client for Odoo external API integration
"""
import xmlrpc.client
import requests
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class OdooRPCClient:
    """
    Unified Odoo RPC client supporting both XML-RPC and JSON-RPC protocols

    Usage:
        client = OdooRPCClient(
            url="https://erp.insightpulseai.net",
            db="odoo",
            username="api_user",
            password="api_key"
        )

        # Authenticate
        uid = client.authenticate()

        # Execute model methods
        partners = client.execute_kw(
            'res.partner',
            'search_read',
            [[('is_company', '=', True)]],
            {'fields': ['name', 'email'], 'limit': 10}
        )
    """

    def __init__(
        self,
        url: str,
        db: str,
        username: str,
        password: str,
        protocol: str = "xmlrpc"  # or "jsonrpc"
    ):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.protocol = protocol
        self.uid: Optional[int] = None

        if protocol == "xmlrpc":
            self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        elif protocol == "jsonrpc":
            self.endpoint = f"{url}/jsonrpc"
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def authenticate(self) -> int:
        """
        Authenticate with Odoo and return user ID

        Returns:
            int: User ID (uid)

        Raises:
            Exception: If authentication fails
        """
        try:
            if self.protocol == "xmlrpc":
                self.uid = self.common.authenticate(
                    self.db,
                    self.username,
                    self.password,
                    {}
                )
            elif self.protocol == "jsonrpc":
                response = self._jsonrpc_call(
                    "common",
                    "authenticate",
                    [self.db, self.username, self.password, {}]
                )
                self.uid = response

            if not self.uid:
                raise Exception("Authentication failed: Invalid credentials")

            logger.info(f"Authenticated as user {self.username} (uid: {self.uid})")
            return self.uid

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

    def execute_kw(
        self,
        model: str,
        method: str,
        args: List[Any],
        kwargs: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute Odoo model method

        Args:
            model: Odoo model name (e.g., 'res.partner', 'sale.order')
            method: Method name (e.g., 'search', 'read', 'create', 'write')
            args: Positional arguments for the method
            kwargs: Keyword arguments for the method

        Returns:
            Result of the method call

        Examples:
            # Search for partners
            partner_ids = client.execute_kw(
                'res.partner',
                'search',
                [[('is_company', '=', True)]]
            )

            # Create a lead
            lead_id = client.execute_kw(
                'crm.lead',
                'create',
                [{
                    'name': 'New Opportunity',
                    'partner_name': 'Acme Corp',
                    'email_from': 'contact@acme.com'
                }]
            )
        """
        if not self.uid:
            self.authenticate()

        kwargs = kwargs or {}

        try:
            if self.protocol == "xmlrpc":
                result = self.models.execute_kw(
                    self.db,
                    self.uid,
                    self.password,
                    model,
                    method,
                    args,
                    kwargs
                )
            elif self.protocol == "jsonrpc":
                result = self._jsonrpc_call(
                    "object",
                    "execute_kw",
                    [self.db, self.uid, self.password, model, method, args, kwargs]
                )

            logger.debug(f"Executed {model}.{method} successfully")
            return result

        except Exception as e:
            logger.error(f"Error executing {model}.{method}: {e}")
            raise

    def _jsonrpc_call(self, service: str, method: str, params: List[Any]) -> Any:
        """
        Make JSON-RPC 2.0 call to Odoo

        Args:
            service: Service name ('common', 'object', 'db')
            method: Method name
            params: Method parameters

        Returns:
            Result from JSON-RPC call
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": params
            },
            "id": 1
        }

        response = requests.post(
            self.endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()

        result = response.json()

        if "error" in result:
            error = result["error"]
            raise Exception(f"JSON-RPC Error: {error.get('message', 'Unknown error')}")

        return result.get("result")

    # Convenience methods for common operations

    def search_read(
        self,
        model: str,
        domain: List[Any],
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search and read records in one call

        Args:
            model: Model name
            domain: Search domain
            fields: Fields to read
            limit: Maximum number of records
            offset: Number of records to skip
            order: Sort order

        Returns:
            List of record dictionaries
        """
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if limit:
            kwargs['limit'] = limit
        if offset:
            kwargs['offset'] = offset
        if order:
            kwargs['order'] = order

        return self.execute_kw(model, 'search_read', [domain], kwargs)

    def create(self, model: str, values: Dict[str, Any]) -> int:
        """Create a record"""
        return self.execute_kw(model, 'create', [values])

    def write(self, model: str, ids: List[int], values: Dict[str, Any]) -> bool:
        """Update records"""
        return self.execute_kw(model, 'write', [ids, values])

    def unlink(self, model: str, ids: List[int]) -> bool:
        """Delete records"""
        return self.execute_kw(model, 'unlink', [ids])

    def search(self, model: str, domain: List[Any], **kwargs) -> List[int]:
        """Search for record IDs"""
        return self.execute_kw(model, 'search', [domain], kwargs)

    def read(
        self,
        model: str,
        ids: List[int],
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Read records by IDs"""
        kwargs = {'fields': fields} if fields else {}
        return self.execute_kw(model, 'read', [ids], kwargs)

    def get_version(self) -> Dict[str, Any]:
        """Get Odoo version info"""
        if self.protocol == "xmlrpc":
            return self.common.version()
        else:
            return self._jsonrpc_call("common", "version", [])


class SupersetClient:
    """
    Client for Apache Superset REST API

    Usage:
        client = SupersetClient(
            url="https://insightpulseai.net/superset",
            username="admin",
            password="admin"
        )

        # Login
        client.login()

        # Get dashboards
        dashboards = client.get_dashboards()

        # Get chart data
        data = client.get_chart_data(chart_id=1)
    """

    def __init__(self, url: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def login(self) -> Dict[str, str]:
        """
        Authenticate with Superset and get access token

        Returns:
            Dict containing access_token and refresh_token
        """
        login_url = f"{self.url}/api/v1/security/login"

        response = self.session.post(
            login_url,
            json={
                "username": self.username,
                "password": self.password,
                "provider": "db",
                "refresh": True
            },
            timeout=10
        )
        response.raise_for_status()

        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

        # Set authorization header for future requests
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })

        logger.info("Authenticated with Superset")
        return tokens

    def get_dashboards(self, page: int = 0, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of dashboards

        Args:
            page: Page number (0-indexed)
            page_size: Number of results per page

        Returns:
            List of dashboard objects
        """
        if not self.access_token:
            self.login()

        url = f"{self.url}/api/v1/dashboard/"
        params = {"q": json.dumps({"page": page, "page_size": page_size})}

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()["result"]

    def get_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Get dashboard by ID"""
        if not self.access_token:
            self.login()

        url = f"{self.url}/api/v1/dashboard/{dashboard_id}"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()

        return response.json()["result"]

    def get_charts(self, page: int = 0, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get list of charts"""
        if not self.access_token:
            self.login()

        url = f"{self.url}/api/v1/chart/"
        params = {"q": json.dumps({"page": page, "page_size": page_size})}

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()["result"]

    def get_chart_data(
        self,
        chart_id: int,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Get chart data

        Args:
            chart_id: Chart ID
            force: Force refresh cache

        Returns:
            Chart data
        """
        if not self.access_token:
            self.login()

        url = f"{self.url}/api/v1/chart/{chart_id}/data/"
        params = {"force": "true" if force else "false"}

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        return response.json()

    def execute_sql(
        self,
        database_id: int,
        sql: str,
        schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL query via SQL Lab

        Args:
            database_id: Database connection ID
            sql: SQL query to execute
            schema: Database schema (optional)

        Returns:
            Query results
        """
        if not self.access_token:
            self.login()

        url = f"{self.url}/superset/sql_json/"

        payload = {
            "database_id": database_id,
            "sql": sql,
            "runAsync": False,
            "schema": schema
        }

        response = self.session.post(url, json=payload, timeout=60)
        response.raise_for_status()

        return response.json()


# Export clients
__all__ = ['OdooRPCClient', 'SupersetClient']
