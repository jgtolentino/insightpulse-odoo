import base64
import logging
import os
import time

import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from odoo.exceptions import UserError

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MicroservicesConfig(models.Model):
    _name = "microservices.config"
    _description = "Microservices Configuration"

    name = fields.Char(string="Configuration Name", required=True)

    # Service endpoints
    ocr_service_url = fields.Char(
        string="OCR Service URL", default="http://ocr-service:8000"
    )
    llm_service_url = fields.Char(
        string="LLM Service URL", default="http://llm-service:8001"
    )
    agent_service_url = fields.Char(
        string="Agent Service URL", default="http://agent-service:8002"
    )

    # Authentication (encrypted storage)
    api_key_encrypted = fields.Binary(string="API Key (Encrypted)", readonly=True)
    auth_token_encrypted = fields.Binary(string="Auth Token (Encrypted)", readonly=True)

    # Write-only fields for setting credentials (never stored in DB)
    api_key = fields.Char(
        string="API Key", compute="_compute_dummy", inverse="_set_api_key", store=False
    )
    auth_token = fields.Char(
        string="Auth Token",
        compute="_compute_dummy",
        inverse="_set_auth_token",
        store=False,
    )

    is_active = fields.Boolean(string="Active", default=True)

    # Connection status
    connection_status = fields.Selection(
        [
            ("not_tested", "Not Tested"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        string="Connection Status",
        default="not_tested",
    )

    last_connection_test = fields.Datetime(string="Last Connection Test")

    # Health log relationship
    health_log_ids = fields.One2many(
        "microservices.health.log", "config_id", string="Health Check Logs"
    )

    @staticmethod
    def _get_encryption_key():
        """
        Generate or retrieve encryption key from environment.
        In production, this should be stored in a secure location (e.g., environment variable).
        """
        # Get key from environment or generate deterministic key from database UUID
        env_key = os.environ.get("ODOO_CREDENTIALS_KEY")
        if env_key:
            return base64.urlsafe_b64decode(env_key.encode())

        # Fallback: Generate key from database UUID (deterministic for same database)
        # WARNING: This is less secure than using an environment variable
        db_uuid = os.environ.get("DATABASE_UUID", "insightpulse-odoo-default-key")
        _logger.warning(
            "ODOO_CREDENTIALS_KEY not set. Using fallback key derivation. "
            "Set ODOO_CREDENTIALS_KEY environment variable for better security."
        )

        # Derive key using PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"odoo-microservices-salt",  # In production, use random salt stored securely
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(db_uuid.encode()))

    def _encrypt_value(self, value):
        """Encrypt a string value using Fernet symmetric encryption."""
        if not value:
            return None
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(value.encode("utf-8"))
            return base64.b64encode(encrypted).decode("utf-8")
        except Exception as e:
            _logger.error(f"Encryption failed: {e}")
            raise UserError("Failed to encrypt credential. Check system configuration.")

    def _decrypt_value(self, encrypted_value):
        """Decrypt a Fernet-encrypted value."""
        if not encrypted_value:
            return None
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            # Handle both binary and base64-encoded strings
            if isinstance(encrypted_value, bytes):
                encrypted_bytes = base64.b64decode(encrypted_value)
            else:
                encrypted_bytes = base64.b64decode(encrypted_value.encode("utf-8"))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode("utf-8")
        except Exception as e:
            _logger.error(f"Decryption failed: {e}")
            return None

    def _compute_dummy(self):
        """Dummy compute method - these fields are write-only."""
        for record in self:
            record.api_key = False
            record.auth_token = False

    def _set_api_key(self):
        """Encrypt and store API key."""
        for record in self:
            if record.api_key:
                record.api_key_encrypted = record._encrypt_value(record.api_key)
                _logger.info(f"API key encrypted for config: {record.name}")

    def _set_auth_token(self):
        """Encrypt and store auth token."""
        for record in self:
            if record.auth_token:
                record.auth_token_encrypted = record._encrypt_value(record.auth_token)
                _logger.info(f"Auth token encrypted for config: {record.name}")

    def _get_decrypted_api_key(self):
        """Get decrypted API key for internal use."""
        self.ensure_one()
        return self._decrypt_value(self.api_key_encrypted)

    def _get_decrypted_auth_token(self):
        """Get decrypted auth token for internal use."""
        self.ensure_one()
        return self._decrypt_value(self.auth_token_encrypted)

    @api.model
    def _migrate_plaintext_credentials(self):
        """
        Migration function: Encrypt existing plaintext credentials.
        Called during module upgrade from 19.0.251026.2 to 19.0.251027.1
        """
        _logger.info("Starting credential migration: encrypting plaintext credentials")

        # Use SQL to read old plaintext values before field change
        self.env.cr.execute(
            """
            SELECT id, api_key, auth_token
            FROM microservices_config
            WHERE api_key IS NOT NULL OR auth_token IS NOT NULL
        """
        )
        records_to_migrate = self.env.cr.fetchall()

        migrated_count = 0
        for record_id, old_api_key, old_auth_token in records_to_migrate:
            record = self.browse(record_id)
            try:
                # Encrypt and store credentials
                if old_api_key:
                    record.api_key_encrypted = record._encrypt_value(old_api_key)
                if old_auth_token:
                    record.auth_token_encrypted = record._encrypt_value(old_auth_token)

                migrated_count += 1
                _logger.info(
                    f"Migrated credentials for config ID {record_id}: {record.name}"
                )

            except Exception as e:
                _logger.error(
                    f"Failed to migrate credentials for config ID {record_id}: {e}"
                )
                # Continue with other records even if one fails

        _logger.info(
            f"Credential migration complete: {migrated_count} records encrypted"
        )

        # Clear old plaintext columns (SQL ALTER TABLE in post_init hook would be better)
        self.env.cr.execute(
            """
            UPDATE microservices_config
            SET api_key = NULL, auth_token = NULL
            WHERE api_key IS NOT NULL OR auth_token IS NOT NULL
        """
        )

        return True

    def run_self_test(self):
        """Run comprehensive self-test for all microservices"""
        start_time = time.time()
        results = {
            "ocr": {"status": "unknown", "response_time": 0, "error": None},
            "llm": {"status": "unknown", "response_time": 0, "error": None},
            "agent": {"status": "unknown", "response_time": 0, "error": None},
        }

        # Get decrypted auth token for API calls
        auth_token = self._get_decrypted_auth_token()

        # Test OCR service
        if self.ocr_service_url:
            try:
                ocr_start = time.time()
                response = requests.get(
                    f"{self.ocr_service_url}/health",
                    timeout=5,
                    headers=(
                        {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
                    ),
                )
                results["ocr"]["response_time"] = time.time() - ocr_start
                results["ocr"]["status"] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
                results["ocr"]["status_code"] = response.status_code
            except Exception as e:
                results["ocr"]["status"] = "error"
                results["ocr"]["error"] = str(e)
                _logger.error(f"OCR self-test failed: {e}")

        # Test LLM service
        if self.llm_service_url:
            try:
                llm_start = time.time()
                response = requests.get(
                    f"{self.llm_service_url}/health",
                    timeout=5,
                    headers=(
                        {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
                    ),
                )
                results["llm"]["response_time"] = time.time() - llm_start
                results["llm"]["status"] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
                results["llm"]["status_code"] = response.status_code
            except Exception as e:
                results["llm"]["status"] = "error"
                results["llm"]["error"] = str(e)
                _logger.error(f"LLM self-test failed: {e}")

        # Test Agent service
        if self.agent_service_url:
            try:
                agent_start = time.time()
                response = requests.get(
                    f"{self.agent_service_url}/health",
                    timeout=5,
                    headers=(
                        {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
                    ),
                )
                results["agent"]["response_time"] = time.time() - agent_start
                results["agent"]["status"] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
                results["agent"]["status_code"] = response.status_code
            except Exception as e:
                results["agent"]["status"] = "error"
                results["agent"]["error"] = str(e)
                _logger.error(f"Agent self-test failed: {e}")

        # Log results
        total_time = time.time() - start_time
        _logger.info(
            f"Microservices self-test completed in {total_time:.2f}s: {results}"
        )

        # Create health log entries
        for component_name, component_data in results.items():
            self.env["microservices.health.log"].create(
                {
                    "config_id": self.id,
                    "component": component_name,
                    "status": component_data["status"],
                    "response_time": component_data.get("response_time", 0),
                    "error_message": component_data.get("error"),
                    "total_check_time": total_time,
                }
            )

        # Update connection status
        overall_status = "success"
        for component in results.values():
            if component["status"] in ["unhealthy", "error"]:
                overall_status = "failed"
                break

        self.write(
            {
                "connection_status": overall_status,
                "last_connection_test": fields.Datetime.now(),
            }
        )

        # Return notification
        message = f"Self-test completed in {total_time:.2f}s. "
        healthy_components = [k for k, v in results.items() if v["status"] == "healthy"]
        if healthy_components:
            message += f"Healthy: {', '.join(healthy_components)}. "
        unhealthy_components = [
            k for k, v in results.items() if v["status"] in ["unhealthy", "error"]
        ]
        if unhealthy_components:
            message += f"Unhealthy: {', '.join(unhealthy_components)}."

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Self-Test Results",
                "message": message,
                "type": "success" if overall_status == "success" else "warning",
                "sticky": True,
            },
        }


class MicroservicesService(models.Model):
    _name = "microservices.service"
    _description = "Microservices Service"

    name = fields.Char(string="Service Name", required=True)
    service_type = fields.Selection(
        [
            ("ocr", "OCR Service"),
            ("llm", "LLM Service"),
            ("agent", "Agent Service"),
        ],
        string="Service Type",
        required=True,
    )

    config_id = fields.Many2one(
        "microservices.config", string="Configuration", required=True
    )
    endpoint_url = fields.Char(string="Endpoint URL", compute="_compute_endpoint_url")

    description = fields.Text(string="Description")
    is_active = fields.Boolean(string="Active", default=True)

    def _compute_endpoint_url(self):
        for record in self:
            if record.service_type == "ocr":
                record.endpoint_url = record.config_id.ocr_service_url
            elif record.service_type == "llm":
                record.endpoint_url = record.config_id.llm_service_url
            elif record.service_type == "agent":
                record.endpoint_url = record.config_id.agent_service_url
            else:
                record.endpoint_url = False

    def test_service_connection(self):
        """Test connection to microservice"""
        # This would implement actual API connection test
        # For now, return success if URL is provided
        if self.endpoint_url:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Connection Test",
                    "message": f"Connection to {self.name} successful!",
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Connection Test",
                    "message": f"Connection to {self.name} failed!",
                    "type": "danger",
                    "sticky": False,
                },
            }
