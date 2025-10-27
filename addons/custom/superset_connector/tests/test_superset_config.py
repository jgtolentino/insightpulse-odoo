"""Tests for Superset Configuration Model"""
from odoo.tests.common import TransactionCase


class TestSupersetConfig(TransactionCase):
    """Test Superset Configuration functionality"""

    def setUp(self):
        super().setUp()

    def test_config_creation(self):
        """Test that configurations are created correctly"""
        config = self.env['superset.config'].create({
            'name': 'Test Config',
            'base_url': 'https://superset.example.com',
            'api_key': 'test_api_key',
        })

        self.assertEqual(config.name, 'Test Config')
        self.assertEqual(config.base_url, 'https://superset.example.com')
        self.assertTrue(config.is_active)

    def test_allowed_origins_default(self):
        """Test that allowed_origins defaults to base_url"""
        config = self.env['superset.config'].create({
            'name': 'Test Config',
            'base_url': 'https://superset.example.com',
            'api_key': 'test_api_key',
        })

        # Trigger onchange
        config._onchange_base_url()

        self.assertEqual(config.allowed_origins, config.base_url,
                        "Allowed origins should default to base URL")

    def test_connection_test(self):
        """Test connection testing functionality"""
        config = self.env['superset.config'].create({
            'name': 'Test Config',
            'base_url': 'https://superset.example.com',
            'api_key': 'test_api_key',
        })

        # Test connection
        status = config.test_connection()

        self.assertEqual(status, 'success', "Connection test should succeed with valid URL")
        self.assertTrue(config.last_connection_test, "Last connection test time should be set")
