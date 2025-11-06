"""
Odoo XML-RPC Client
Provides high-level interface to Odoo models
"""
import xmlrpc.client
import logging
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class OdooClient:
    """
    Odoo XML-RPC client for agent operations

    Environment variables:
    - ODOO_URL: Odoo base URL (e.g., https://erp.insightpulseai.net)
    - ODOO_DB: Database name (e.g., odoo19)
    - ODOO_USERNAME: Username (e.g., admin)
    - ODOO_PASSWORD: API key or password
    """

    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.url = url or os.getenv('ODOO_URL', 'https://erp.insightpulseai.net')
        self.db = db or os.getenv('ODOO_DB', 'odoo19')
        self.username = username or os.getenv('ODOO_USERNAME', 'admin')
        self.password = password or os.getenv('ODOO_PASSWORD')

        if not self.password:
            raise ValueError("Odoo password/API key required")

        # XML-RPC endpoints
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

        # Authenticate
        self.uid = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Odoo"""
        try:
            self.uid = self.common.authenticate(
                self.db,
                self.username,
                self.password,
                {}
            )
            if not self.uid:
                raise ValueError("Authentication failed")
            logger.info(f"✅ Connected to Odoo as user {self.uid}")
        except Exception as e:
            logger.error(f"❌ Odoo authentication failed: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            version = self.common.version()
            return bool(version)
        except:
            return False

    def execute(
        self,
        model: str,
        method: str,
        args: List[Any],
        kwargs: Optional[Dict] = None
    ) -> Any:
        """Execute Odoo model method"""
        kwargs = kwargs or {}
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs
        )

    def search(
        self,
        model: str,
        domain: List[Any],
        limit: Optional[int] = None,
        offset: int = 0,
        order: Optional[str] = None
    ) -> List[int]:
        """Search for record IDs"""
        kwargs = {'limit': limit, 'offset': offset}
        if order:
            kwargs['order'] = order

        return self.execute(model, 'search', [domain], kwargs)

    def read(
        self,
        model: str,
        ids: List[int],
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Read records"""
        kwargs = {}
        if fields:
            kwargs['fields'] = fields

        return self.execute(model, 'read', [ids], kwargs)

    def search_read(
        self,
        model: str,
        domain: List[Any],
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search and read in one call"""
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if limit:
            kwargs['limit'] = limit
        if offset:
            kwargs['offset'] = offset
        if order:
            kwargs['order'] = order

        return self.execute(model, 'search_read', [domain], kwargs)

    def create(
        self,
        model: str,
        values: Dict[str, Any]
    ) -> int:
        """Create a record"""
        return self.execute(model, 'create', [values])

    def write(
        self,
        model: str,
        ids: List[int],
        values: Dict[str, Any]
    ) -> bool:
        """Update records"""
        return self.execute(model, 'write', [ids, values])

    def unlink(
        self,
        model: str,
        ids: List[int]
    ) -> bool:
        """Delete records"""
        return self.execute(model, 'unlink', [ids])

    # Agent-specific helpers
    def create_agent_run(
        self,
        agent_slug: str,
        status: str = 'running',
        input_data: Optional[Dict] = None
    ) -> int:
        """Create ip.agent.run record"""
        values = {
            'agent_slug': agent_slug,
            'status': status,
            'input_data': input_data or {},
        }
        return self.create('ip.agent.run', values)

    def update_agent_run(
        self,
        run_id: int,
        status: Optional[str] = None,
        output_data: Optional[Dict] = None,
        tokens_used: Optional[int] = None,
        cost_cents: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Update ip.agent.run record"""
        values = {}
        if status:
            values['status'] = status
        if output_data:
            values['output_data'] = output_data
        if tokens_used:
            values['tokens_used'] = tokens_used
        if cost_cents:
            values['cost_cents'] = cost_cents
        if error_message:
            values['error_message'] = error_message

        if values:
            self.write('ip.agent.run', [run_id], values)

    def create_page(
        self,
        title: str,
        body_md: str,
        page_type: str = 'doc',
        **kwargs
    ) -> int:
        """Create ip.page record"""
        values = {
            'name': title,
            'body_md': body_md,
            'page_type': page_type,
        }
        values.update(kwargs)
        return self.create('ip.page', values)

    def create_task(
        self,
        name: str,
        project_id: Optional[int] = None,
        page_id: Optional[int] = None,
        **kwargs
    ) -> int:
        """Create project.task record"""
        values = {
            'name': name,
        }
        if project_id:
            values['project_id'] = project_id
        if page_id:
            values['page_id'] = page_id
        values.update(kwargs)
        return self.create('project.task', values)

    def get_memory(
        self,
        scope: str,
        key: str,
        owner_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Get memory value from ip.memory.kv"""
        domain = [
            ('scope', '=', scope),
            ('key', '=', key)
        ]
        if owner_id:
            domain.append(('owner_id', '=', owner_id))

        records = self.search_read(
            model='ip.memory.kv',
            domain=domain,
            fields=['value_json'],
            limit=1
        )

        return records[0]['value_json'] if records else None

    def set_memory(
        self,
        scope: str,
        key: str,
        value: Dict[str, Any],
        owner_id: Optional[int] = None
    ):
        """Set memory value in ip.memory.kv"""
        # Check if exists
        domain = [
            ('scope', '=', scope),
            ('key', '=', key)
        ]
        if owner_id:
            domain.append(('owner_id', '=', owner_id))

        existing = self.search('ip.memory.kv', domain, limit=1)

        if existing:
            # Update
            self.write('ip.memory.kv', existing, {'value_json': value})
        else:
            # Create
            self.create('ip.memory.kv', {
                'scope': scope,
                'key': key,
                'value_json': value,
                'owner_id': owner_id
            })
