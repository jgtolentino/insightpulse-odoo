# -*- coding: utf-8 -*-
"""
Security tests for credential encryption (CVSS 8.1 fix)
Target: 80% test coverage for security-critical code
"""

from odoo.tests import TransactionCase
from odoo.exceptions import UserError
from unittest.mock import patch
import base64
from cryptography.fernet import Fernet


class TestCredentialEncryption(TransactionCase):
    """Test suite for encrypted credential storage"""

    def setUp(self):
        super(TestCredentialEncryption, self).setUp()
        self.MicroservicesConfig = self.env['microservices.config']

        # Create test configuration
        self.test_config = self.MicroservicesConfig.create({
            'name': 'Test Config',
            'ocr_service_url': 'http://test-ocr:8000',
            'llm_service_url': 'http://test-llm:8001',
        })

    def test_01_encrypt_api_key(self):
        """Test API key encryption on write"""
        test_key = 'test-api-key-12345'

        # Set API key (should trigger encryption)
        self.test_config.write({'api_key': test_key})

        # Verify encrypted field is populated
        self.assertTrue(self.test_config.api_key_encrypted)
        self.assertIsInstance(self.test_config.api_key_encrypted, str)

        # Verify plaintext field is NOT stored
        self.assertFalse(self.test_config.api_key)

        # Verify decryption returns original value
        decrypted = self.test_config._get_decrypted_api_key()
        self.assertEqual(decrypted, test_key)

    def test_02_encrypt_auth_token(self):
        """Test auth token encryption on write"""
        test_token = 'Bearer test-token-67890'

        # Set auth token (should trigger encryption)
        self.test_config.write({'auth_token': test_token})

        # Verify encrypted field is populated
        self.assertTrue(self.test_config.auth_token_encrypted)
        self.assertIsInstance(self.test_config.auth_token_encrypted, str)

        # Verify plaintext field is NOT stored
        self.assertFalse(self.test_config.auth_token)

        # Verify decryption returns original value
        decrypted = self.test_config._get_decrypted_auth_token()
        self.assertEqual(decrypted, test_token)

    def test_03_encrypt_both_credentials(self):
        """Test simultaneous encryption of API key and token"""
        test_key = 'api-key-both-test'
        test_token = 'token-both-test'

        self.test_config.write({
            'api_key': test_key,
            'auth_token': test_token,
        })

        # Verify both encrypted
        self.assertTrue(self.test_config.api_key_encrypted)
        self.assertTrue(self.test_config.auth_token_encrypted)

        # Verify both decrypt correctly
        self.assertEqual(self.test_config._get_decrypted_api_key(), test_key)
        self.assertEqual(self.test_config._get_decrypted_auth_token(), test_token)

    def test_04_encryption_idempotent(self):
        """Test that re-encrypting same value produces different ciphertext (proper IV)"""
        test_key = 'idempotent-test-key'

        # Encrypt first time
        self.test_config.write({'api_key': test_key})
        first_encrypted = self.test_config.api_key_encrypted

        # Encrypt same value again
        self.test_config.write({'api_key': test_key})
        second_encrypted = self.test_config.api_key_encrypted

        # Ciphertext should differ (IV randomness)
        self.assertNotEqual(first_encrypted, second_encrypted)

        # Both should decrypt to same plaintext
        self.assertEqual(self.test_config._get_decrypted_api_key(), test_key)

    def test_05_null_value_handling(self):
        """Test handling of None/empty credential values"""
        # Test None value
        self.test_config.write({'api_key': False})
        self.assertFalse(self.test_config.api_key_encrypted)

        # Test empty string
        self.test_config.write({'api_key': ''})
        # Empty string should not be encrypted
        self.assertFalse(self.test_config.api_key_encrypted)

    def test_06_decrypt_null_value(self):
        """Test decryption of null/empty encrypted values"""
        # Test with no encrypted data
        self.test_config.api_key_encrypted = False
        decrypted = self.test_config._get_decrypted_api_key()
        self.assertIsNone(decrypted)

    def test_07_encryption_key_derivation(self):
        """Test encryption key is properly derived"""
        key = self.test_config._get_encryption_key()

        # Verify key is bytes and proper length for Fernet (32 bytes base64)
        self.assertIsInstance(key, bytes)
        self.assertEqual(len(key), 44)  # Base64 encoded 32 bytes = 44 chars

        # Verify key is deterministic (same key each call)
        key2 = self.test_config._get_encryption_key()
        self.assertEqual(key, key2)

    def test_08_encryption_key_from_env(self):
        """Test encryption key from environment variable"""
        # Generate test key
        test_key = Fernet.generate_key()
        test_key_b64 = base64.urlsafe_b64encode(test_key).decode()

        with patch.dict('os.environ', {'ODOO_CREDENTIALS_KEY': test_key_b64}):
            key = self.test_config._get_encryption_key()
            self.assertEqual(key, test_key)

    def test_09_invalid_encrypted_value(self):
        """Test handling of corrupted encrypted data"""
        # Set invalid encrypted data
        self.test_config.api_key_encrypted = 'invalid-base64-not-encrypted'

        # Should return None instead of raising exception
        decrypted = self.test_config._get_decrypted_api_key()
        self.assertIsNone(decrypted)

    def test_10_run_self_test_with_encrypted_token(self):
        """Test self-test uses decrypted token for API calls"""
        test_token = 'test-bearer-token'
        self.test_config.write({'auth_token': test_token})

        # Mock requests.get to verify decrypted token is used
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200

            self.test_config.run_self_test()

            # Verify auth header contains decrypted token
            call_args = mock_get.call_args_list[0]
            headers = call_args[1]['headers']
            self.assertEqual(headers.get('Authorization'), f'Bearer {test_token}')

    def test_11_sql_injection_protection(self):
        """Test that credentials with SQL injection attempts are safely encrypted"""
        sql_injection = "'; DROP TABLE microservices_config; --"

        self.test_config.write({'api_key': sql_injection})

        # Should encrypt safely without SQL execution
        self.assertTrue(self.test_config.api_key_encrypted)

        # Should decrypt to original malicious string (safely stored)
        decrypted = self.test_config._get_decrypted_api_key()
        self.assertEqual(decrypted, sql_injection)

    def test_12_unicode_credential_handling(self):
        """Test encryption/decryption of Unicode credentials"""
        unicode_key = 'test-key-日本語-emoji-🔐-中文'

        self.test_config.write({'api_key': unicode_key})

        # Verify Unicode encrypts and decrypts correctly
        decrypted = self.test_config._get_decrypted_api_key()
        self.assertEqual(decrypted, unicode_key)

    def test_13_migration_function(self):
        """Test credential migration from plaintext to encrypted"""
        # Create config with plaintext credentials via SQL (simulating old data)
        self.env.cr.execute("""
            INSERT INTO microservices_config (name, api_key, auth_token, create_uid, write_uid, create_date, write_date)
            VALUES ('Migration Test', 'old-plaintext-key', 'old-plaintext-token', 1, 1, NOW(), NOW())
            RETURNING id
        """)
        config_id = self.env.cr.fetchone()[0]

        # Run migration
        self.MicroservicesConfig._migrate_plaintext_credentials()

        # Verify credentials were encrypted
        migrated_config = self.MicroservicesConfig.browse(config_id)
        self.assertTrue(migrated_config.api_key_encrypted)
        self.assertTrue(migrated_config.auth_token_encrypted)

        # Verify decryption works
        self.assertEqual(migrated_config._get_decrypted_api_key(), 'old-plaintext-key')
        self.assertEqual(migrated_config._get_decrypted_auth_token(), 'old-plaintext-token')

    def test_14_long_credential_handling(self):
        """Test encryption of very long credentials (e.g., JWT tokens)"""
        long_jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' * 50  # 2KB+ token

        self.test_config.write({'auth_token': long_jwt})

        # Verify long value encrypts successfully
        self.assertTrue(self.test_config.auth_token_encrypted)

        # Verify decryption preserves full length
        decrypted = self.test_config._get_decrypted_auth_token()
        self.assertEqual(len(decrypted), len(long_jwt))
        self.assertEqual(decrypted, long_jwt)

    def test_15_credential_update(self):
        """Test updating credentials multiple times"""
        keys = ['key-v1', 'key-v2', 'key-v3']

        for key in keys:
            self.test_config.write({'api_key': key})
            decrypted = self.test_config._get_decrypted_api_key()
            self.assertEqual(decrypted, key)

    def test_16_concurrent_credential_access(self):
        """Test that multiple configs can have different encrypted credentials"""
        config1 = self.test_config
        config2 = self.MicroservicesConfig.create({
            'name': 'Config 2',
            'ocr_service_url': 'http://test2:8000',
        })

        config1.write({'api_key': 'key-for-config-1'})
        config2.write({'api_key': 'key-for-config-2'})

        # Verify each decrypts to correct value
        self.assertEqual(config1._get_decrypted_api_key(), 'key-for-config-1')
        self.assertEqual(config2._get_decrypted_api_key(), 'key-for-config-2')

        # Verify encrypted values are different
        self.assertNotEqual(config1.api_key_encrypted, config2.api_key_encrypted)
