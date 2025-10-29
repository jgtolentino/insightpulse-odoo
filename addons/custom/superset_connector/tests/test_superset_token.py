"""Tests for Superset Token Model"""

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSupersetToken(TransactionCase):
    """Test Superset Token functionality"""

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
                "description": "Test dashboard for unit tests",
            }
        )

        # Create test user
        self.test_user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user@example.com",
            }
        )

    def test_token_creation(self):
        """Test that tokens are created with secure random values"""
        token = self.env["superset.token"].create(
            {
                "dashboard_id": self.dashboard.id,
                "user_id": self.test_user.id,
                "config_id": self.config.id,
            }
        )

        self.assertTrue(token.token, "Token should be generated")
        self.assertEqual(
            len(token.token), 43, "Token should be 43 characters (base64url)"
        )
        self.assertTrue(token.is_active, "Token should be active by default")
        self.assertTrue(token.expires_at, "Token should have expiry date")

    def test_token_expiry(self):
        """Test that token expiry is set correctly"""
        token = self.env["superset.token"].create(
            {
                "dashboard_id": self.dashboard.id,
                "user_id": self.test_user.id,
                "config_id": self.config.id,
            }
        )

        # Check that expiry is approximately 24 hours from now
        expected_expiry = datetime.now() + timedelta(hours=24)
        time_diff = abs((token.expires_at - expected_expiry).total_seconds())
        self.assertLess(
            time_diff, 60, "Expiry should be approximately 24 hours from creation"
        )

    def test_get_or_create_token_reuse(self):
        """Test that valid tokens are reused instead of creating new ones"""
        # Create initial token
        token1 = self.env["superset.token"].get_or_create_token(
            dashboard_id=self.dashboard.id, user_id=self.test_user.id
        )

        # Try to get token again - should return same token
        token2 = self.env["superset.token"].get_or_create_token(
            dashboard_id=self.dashboard.id, user_id=self.test_user.id
        )

        self.assertEqual(token1.id, token2.id, "Should reuse existing valid token")
        self.assertEqual(token2.use_count, 1, "Use count should increment")

    def test_get_or_create_token_force_new(self):
        """Test that force_new creates a new token"""
        token1 = self.env["superset.token"].get_or_create_token(
            dashboard_id=self.dashboard.id, user_id=self.test_user.id
        )

        token2 = self.env["superset.token"].get_or_create_token(
            dashboard_id=self.dashboard.id, user_id=self.test_user.id, force_new=True
        )

        self.assertNotEqual(
            token1.id, token2.id, "Should create new token when force_new=True"
        )

    def test_token_invalidation(self):
        """Test that tokens can be invalidated"""
        token = self.env["superset.token"].create(
            {
                "dashboard_id": self.dashboard.id,
                "user_id": self.test_user.id,
                "config_id": self.config.id,
            }
        )

        self.assertTrue(token.is_active, "Token should be active initially")

        token.invalidate_token()

        self.assertFalse(token.is_active, "Token should be inactive after invalidation")

    def test_cleanup_expired_tokens(self):
        """Test that expired tokens are cleaned up"""
        # Create expired token
        expired_token = self.env["superset.token"].create(
            {
                "dashboard_id": self.dashboard.id,
                "user_id": self.test_user.id,
                "config_id": self.config.id,
                "expires_at": datetime.now() - timedelta(hours=1),
            }
        )

        # Create valid token
        valid_token = self.env["superset.token"].create(
            {
                "dashboard_id": self.dashboard.id,
                "user_id": self.test_user.id,
                "config_id": self.config.id,
            }
        )

        self.assertTrue(
            expired_token.is_active, "Expired token should be active before cleanup"
        )
        self.assertTrue(valid_token.is_active, "Valid token should be active")

        # Run cleanup
        self.env["superset.token"].cleanup_expired_tokens()

        self.assertFalse(
            expired_token.is_active, "Expired token should be inactive after cleanup"
        )
        self.assertTrue(valid_token.is_active, "Valid token should still be active")

    def test_immutable_fields(self):
        """Test that immutable fields cannot be modified"""
        token = self.env["superset.token"].create(
            {
                "dashboard_id": self.dashboard.id,
                "user_id": self.test_user.id,
                "config_id": self.config.id,
            }
        )

        with self.assertRaises(ValidationError):
            token.write({"user_id": self.env.user.id})

    def test_token_stats(self):
        """Test token statistics method"""
        # Create some tokens
        for i in range(3):
            self.env["superset.token"].create(
                {
                    "dashboard_id": self.dashboard.id,
                    "user_id": self.test_user.id,
                    "config_id": self.config.id,
                }
            )

        stats = self.env["superset.token"].get_token_stats()

        self.assertGreaterEqual(
            stats["total_tokens"], 3, "Should have at least 3 tokens"
        )
        self.assertGreaterEqual(
            stats["active_tokens"], 3, "Should have at least 3 active tokens"
        )
        self.assertIsInstance(
            stats["most_used_tokens"], list, "Should return list of most used tokens"
        )
