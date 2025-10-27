# -*- coding: utf-8 -*-
"""
Security tests for URL injection vulnerability fix (CVSS 6.5)
Validates filter parameter sanitization and encoding
"""

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from odoo.addons.superset_connector.controllers.embedded import SupersetEmbedController


class TestURLInjectionProtection(TransactionCase):
    """Test suite for URL injection vulnerability fixes"""

    def setUp(self):
        super(TestURLInjectionProtection, self).setUp()
        self.controller = SupersetEmbedController()

        # Create test Superset configuration
        self.config = self.env['superset.config'].create({
            'name': 'Test Config',
            'base_url': 'https://superset.example.com',
            'guest_token_secret': 'test-secret-key',
        })

        # Create test dashboard
        self.dashboard = self.env['superset.dashboard'].create({
            'name': 'Test Dashboard',
            'dashboard_id': 'test-uuid-12345',
            'config_id': self.config.id,
        })

        # Create test user and token
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test@example.com',
        })

        self.token = self.env['superset.token'].create({
            'dashboard_id': self.dashboard.id,
            'user_id': self.test_user.id,
            'config_id': self.config.id,
            'token': 'test-guest-token-abc123',
        })

    def test_01_valid_filter_param(self):
        """Test that valid filter parameters pass validation"""
        key, value = self.controller._validate_filter_param('filter_country', 'USA')
        self.assertEqual(key, 'filter_country')
        self.assertEqual(value, 'USA')

    def test_02_valid_filter_with_underscore(self):
        """Test filter with underscores in name"""
        key, value = self.controller._validate_filter_param('filter_user_id', '12345')
        self.assertEqual(key, 'filter_user_id')
        self.assertEqual(value, '12345')

    def test_03_valid_numeric_filter(self):
        """Test filter with numeric value"""
        key, value = self.controller._validate_filter_param('filter_year', 2023)
        self.assertEqual(key, 'filter_year')
        self.assertEqual(value, '2023')

    def test_04_valid_boolean_filter(self):
        """Test filter with boolean value"""
        key, value = self.controller._validate_filter_param('filter_active', True)
        self.assertEqual(key, 'filter_active')
        self.assertEqual(value, 'True')

    def test_05_reject_javascript_injection(self):
        """Test rejection of javascript: protocol injection"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param(
                'filter_name',
                'javascript:alert(document.cookie)'
            )
        self.assertIn('Invalid characters', str(cm.exception))

    def test_06_reject_data_uri_injection(self):
        """Test rejection of data: URI injection"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param(
                'filter_name',
                'data:text/html,<script>alert(1)</script>'
            )
        self.assertIn('Invalid characters', str(cm.exception))

    def test_07_reject_script_tag_injection(self):
        """Test rejection of script tag injection"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param(
                'filter_name',
                '<script>alert("XSS")</script>'
            )
        self.assertIn('Invalid characters', str(cm.exception))

    def test_08_reject_onerror_injection(self):
        """Test rejection of onerror event handler injection"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param(
                'filter_name',
                'x" onerror="alert(1)" x="'
            )
        self.assertIn('Invalid characters', str(cm.exception))

    def test_09_reject_path_traversal(self):
        """Test rejection of path traversal attempts"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param(
                'filter_path',
                '../../../etc/passwd'
            )
        self.assertIn('Invalid characters', str(cm.exception))

    def test_10_reject_protocol_relative_url(self):
        """Test rejection of protocol-relative URLs"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param(
                'filter_url',
                '//evil.com/payload'
            )
        self.assertIn('Invalid characters', str(cm.exception))

    def test_11_reject_invalid_key_format(self):
        """Test rejection of invalid parameter key format"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param(
                'filter-name-with-hyphens',
                'value'
            )
        self.assertIn('Invalid filter parameter format', str(cm.exception))

    def test_12_reject_key_without_filter_prefix(self):
        """Test rejection of keys without filter_ prefix"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param('name', 'value')
        self.assertIn('Invalid filter parameter format', str(cm.exception))

    def test_13_reject_too_long_value(self):
        """Test rejection of excessively long values (DOS prevention)"""
        long_value = 'A' * 501  # Over 500 char limit
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param('filter_name', long_value)
        self.assertIn('too long', str(cm.exception))

    def test_14_accept_max_length_value(self):
        """Test acceptance of value at maximum length"""
        max_value = 'A' * 500  # Exactly 500 chars
        key, value = self.controller._validate_filter_param('filter_name', max_value)
        self.assertEqual(len(value), 500)

    def test_15_reject_invalid_value_type(self):
        """Test rejection of invalid value types (list, dict)"""
        with self.assertRaises(ValidationError) as cm:
            self.controller._validate_filter_param('filter_name', ['value1', 'value2'])
        self.assertIn('Invalid filter value type', str(cm.exception))

    def test_16_build_embed_url_basic(self):
        """Test URL building with no parameters"""
        url = self.controller._build_embed_url(self.dashboard, self.token, None)

        self.assertIn('superset.example.com', url)
        self.assertIn('test-uuid-12345', url)
        self.assertIn('standalone=1', url)
        self.assertIn('guest_token=test-guest-token-abc123', url)

    def test_17_build_embed_url_with_valid_filter(self):
        """Test URL building with valid filter parameter"""
        params = {'filter_country': 'USA'}
        url = self.controller._build_embed_url(self.dashboard, self.token, params)

        self.assertIn('filter_country=USA', url)
        self.assertIn('standalone=1', url)
        self.assertIn('guest_token=test-guest-token-abc123', url)

    def test_18_build_embed_url_with_special_chars(self):
        """Test URL building properly encodes special characters"""
        params = {'filter_name': 'John & Jane'}
        url = self.controller._build_embed_url(self.dashboard, self.token, params)

        # Should be URL encoded: & becomes %26
        self.assertIn('filter_name=John+%26+Jane', url)

    def test_19_build_embed_url_skips_invalid_params(self):
        """Test URL building skips invalid parameters without failing"""
        params = {
            'filter_valid': 'ok',
            'filter_invalid': 'javascript:alert(1)',  # Should be skipped
            'filter_also_valid': 'good',
        }
        url = self.controller._build_embed_url(self.dashboard, self.token, params)

        # Valid params should be present
        self.assertIn('filter_valid=ok', url)
        self.assertIn('filter_also_valid=good', url)

        # Invalid param should NOT be present
        self.assertNotIn('javascript', url)

    def test_20_build_embed_url_with_unicode(self):
        """Test URL building handles Unicode characters"""
        params = {'filter_city': '東京'}  # Tokyo in Japanese
        url = self.controller._build_embed_url(self.dashboard, self.token, params)

        # Unicode should be properly percent-encoded
        self.assertIn('filter_city=', url)
        # Should not contain raw Unicode
        self.assertNotIn('東京', url)

    def test_21_case_insensitive_injection_detection(self):
        """Test that injection detection is case-insensitive"""
        with self.assertRaises(ValidationError):
            self.controller._validate_filter_param('filter_name', 'JAVASCRIPT:alert(1)')

        with self.assertRaises(ValidationError):
            self.controller._validate_filter_param('filter_name', 'DaTa:text/html,<script>')

    def test_22_multiple_filters_in_url(self):
        """Test URL building with multiple filter parameters"""
        params = {
            'filter_country': 'USA',
            'filter_year': '2023',
            'filter_active': 'true',
        }
        url = self.controller._build_embed_url(self.dashboard, self.token, params)

        # All filters should be present
        self.assertIn('filter_country=USA', url)
        self.assertIn('filter_year=2023', url)
        self.assertIn('filter_active=true', url)

    def test_23_non_filter_params_ignored(self):
        """Test that non-filter parameters are ignored"""
        params = {
            'filter_valid': 'ok',
            'random_param': 'should_be_ignored',
            'another_param': 'also_ignored',
        }
        url = self.controller._build_embed_url(self.dashboard, self.token, params)

        # Only filter param should be present
        self.assertIn('filter_valid=ok', url)
        self.assertNotIn('random_param', url)
        self.assertNotIn('another_param', url)

    def test_24_sql_injection_in_filter_value(self):
        """Test that SQL injection attempts in values are safely handled"""
        # Note: This doesn't execute SQL, but validates value is safely passed through
        safe_value = "'; DROP TABLE users; --"
        key, value = self.controller._validate_filter_param('filter_query', safe_value)

        # Should be accepted (SQL injection happens at query time, not URL building)
        # But value will be URL-encoded which prevents it from executing
        self.assertEqual(key, 'filter_query')
        self.assertEqual(value, safe_value)

        # Verify it gets properly encoded in URL
        url = self.controller._build_embed_url(
            self.dashboard,
            self.token,
            {'filter_query': safe_value}
        )

        # Should be URL-encoded, not raw
        self.assertNotIn("'; DROP TABLE", url)
        self.assertIn('filter_query=', url)
