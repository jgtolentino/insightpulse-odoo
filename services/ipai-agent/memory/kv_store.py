"""
Memory Key-Value Store
Durable memory backed by Odoo ip.memory.kv model
"""
import logging
from typing import Optional, Dict, Any
from tools.odoo_client import OdooClient

logger = logging.getLogger(__name__)


class MemoryKVStore:
    """
    Durable memory store for agent preferences, team styles, etc.

    Scopes:
    - user: Per-user preferences
    - team: Team/project-level settings
    - org: Organization-wide config
    """

    def __init__(self, odoo_client: OdooClient):
        self.odoo = odoo_client

    def get(
        self,
        scope: str,
        key: str,
        owner_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get memory value

        Args:
            scope: 'user', 'team', or 'org'
            key: Memory key (e.g., 'writing_style', 'prd_template')
            owner_id: User/team ID for scoped memories

        Returns:
            Value as dict or None if not found
        """
        try:
            value = self.odoo.get_memory(scope=scope, key=key, owner_id=owner_id)
            if value:
                logger.info(f"✅ Memory GET: {scope}/{key} → found")
            else:
                logger.info(f"⚠️  Memory GET: {scope}/{key} → not found")
            return value
        except Exception as e:
            logger.error(f"❌ Memory GET error: {str(e)}")
            return None

    def set(
        self,
        scope: str,
        key: str,
        value: Dict[str, Any],
        owner_id: Optional[int] = None
    ):
        """
        Set memory value

        Args:
            scope: 'user', 'team', or 'org'
            key: Memory key
            value: Value as dict
            owner_id: User/team ID for scoped memories
        """
        try:
            self.odoo.set_memory(
                scope=scope,
                key=key,
                value=value,
                owner_id=owner_id
            )
            logger.info(f"✅ Memory SET: {scope}/{key}")
        except Exception as e:
            logger.error(f"❌ Memory SET error: {str(e)}")
            raise

    def delete(
        self,
        scope: str,
        key: str,
        owner_id: Optional[int] = None
    ):
        """Delete memory value"""
        domain = [
            ('scope', '=', scope),
            ('key', '=', key)
        ]
        if owner_id:
            domain.append(('owner_id', '=', owner_id))

        ids = self.odoo.search('ip.memory.kv', domain)
        if ids:
            self.odoo.unlink('ip.memory.kv', ids)
            logger.info(f"✅ Memory DELETE: {scope}/{key}")

    # Convenience methods for common memories
    def get_writing_style(self, team_id: Optional[int] = None) -> Dict[str, Any]:
        """Get team writing style"""
        return self.get(scope='team', key='writing_style', owner_id=team_id) or {
            'tone': 'professional and concise',
            'format': 'markdown',
            'structure': 'bullets preferred'
        }

    def set_writing_style(self, style: Dict[str, Any], team_id: Optional[int] = None):
        """Set team writing style"""
        self.set(scope='team', key='writing_style', value=style, owner_id=team_id)

    def get_prd_template(self) -> Dict[str, Any]:
        """Get organization PRD template"""
        return self.get(scope='org', key='prd_template') or {
            'sections': [
                'Executive Summary',
                'Background',
                'Goals & Objectives',
                'Requirements',
                'User Stories',
                'Tasks',
                'Success Metrics',
                'Timeline'
            ]
        }

    def set_prd_template(self, template: Dict[str, Any]):
        """Set organization PRD template"""
        self.set(scope='org', key='prd_template', value=template)

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        return self.get(scope='user', key='preferences', owner_id=user_id) or {
            'notifications': True,
            'slack_dm': False
        }

    def set_user_preferences(self, preferences: Dict[str, Any], user_id: int):
        """Set user preferences"""
        self.set(scope='user', key='preferences', value=preferences, owner_id=user_id)

    def get_db_paths(self) -> Dict[str, Any]:
        """Get database path mappings (where things live in Odoo)"""
        return self.get(scope='org', key='db_paths') or {
            'projects': {
                'model': 'project.project',
                'default_stage_ids': []
            },
            'tasks': {
                'model': 'project.task',
                'default_user_id': None
            },
            'pages': {
                'model': 'ip.page',
                'default_owner_id': None
            }
        }

    def set_db_paths(self, paths: Dict[str, Any]):
        """Set database path mappings"""
        self.set(scope='org', key='db_paths', value=paths)

    def get_slack_channels(self) -> Dict[str, str]:
        """Get Slack channel mappings"""
        return self.get(scope='org', key='slack_channels') or {}

    def set_slack_channels(self, channels: Dict[str, str]):
        """
        Set Slack channel mappings

        Example:
        {
            'general': 'C01234567',
            'rim-finance': 'C_RIM_FIN',
            'bir-compliance': 'C_BIR_COMP'
        }
        """
        self.set(scope='org', key='slack_channels', value=channels)
