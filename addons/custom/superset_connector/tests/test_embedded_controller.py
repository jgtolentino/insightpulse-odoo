"""Tests for Embedded Dashboard Controller"""

from odoo.tests.common import HttpCase


class TestEmbeddedController(HttpCase):
    """Test Embedded Dashboard Controller functionality"""

    def setUp(self):
        super().setUp()

        # Create test configuration
        self.config = self.env["superset.config"].create(
            {
                "name": "Test Superset Config",
                "base_url": "https://test-superset.example.com",
                "api_key": "test_api_key",
                "allowed_origins": "https://test-superset.example.com",
            }
        )

        # Create test dashboard
        self.dashboard = self.env["superset.dashboard"].create(
            {
                "name": "Test Dashboard",
                "dashboard_id": "test-dashboard-uuid",
                "config_id": self.config.id,
                "description": "Test dashboard for integration tests",
            }
        )

    def test_dashboard_list_endpoint(self):
        """Test that dashboard list endpoint returns dashboards"""
        self.authenticate("admin", "admin")

        response = self.url_open("/superset/dashboards")

        self.assertEqual(
            response.status_code, 200, "Dashboard list endpoint should return 200"
        )
        self.assertIn(
            b"Superset Dashboards",
            response.content,
            "Response should contain dashboard list title",
        )

    def test_embed_endpoint_requires_auth(self):
        """Test that embed endpoint requires authentication"""
        # Try to access without auth
        response = self.url_open(f"/superset/embed/{self.dashboard.id}")

        # Should redirect to login
        self.assertIn(
            response.status_code, [302, 303], "Should redirect unauthenticated users"
        )

    def test_embed_endpoint_with_auth(self):
        """Test that embed endpoint works with authentication"""
        self.authenticate("admin", "admin")

        response = self.url_open(f"/superset/embed/{self.dashboard.id}")

        self.assertEqual(
            response.status_code, 200, "Embed endpoint should return 200 with auth"
        )

    def test_csp_headers_present(self):
        """Test that CSP headers are present in embed response"""
        self.authenticate("admin", "admin")

        response = self.url_open(f"/superset/embed/{self.dashboard.id}")

        self.assertIn(
            "Content-Security-Policy",
            response.headers,
            "Response should include CSP header",
        )
        self.assertIn(
            "X-Frame-Options",
            response.headers,
            "Response should include X-Frame-Options header",
        )
