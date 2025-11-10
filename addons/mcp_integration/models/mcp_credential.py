"""MCP Credential - Secure storage for MCP server credentials"""

import logging
import os

from cryptography.fernet import Fernet

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MCPCredential(models.Model):
    """Encrypted credential storage for MCP servers"""

    _name = "mcp.credential"
    _description = "MCP Credential Vault"

    name = fields.Char(string="Credential Name", required=True, index=True)
    credential_type = fields.Selection(
        [
            ("api_token", "API Token"),
            ("oauth", "OAuth"),
            ("basic_auth", "Basic Auth"),
            ("private_key", "Private Key"),
        ],
        string="Type",
        required=True,
    )

    # Encrypted storage
    encrypted_value = fields.Binary(string="Encrypted Value")
    active = fields.Boolean(default=True)

    server_ids = fields.One2many("mcp.server", "credential_id", string="Servers")

    def set_value(self, plaintext_value):
        """Encrypt and store credential value"""
        self.ensure_one()

        # Get encryption key from environment
        encryption_key = os.getenv("MCP_ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("MCP_ENCRYPTION_KEY not set in environment")

        cipher = Fernet(encryption_key.encode())
        encrypted = cipher.encrypt(plaintext_value.encode())

        self.write({"encrypted_value": encrypted})

    def get_value(self):
        """Decrypt and return credential value"""
        self.ensure_one()

        encryption_key = os.getenv("MCP_ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("MCP_ENCRYPTION_KEY not set in environment")

        cipher = Fernet(encryption_key.encode())
        decrypted = cipher.decrypt(self.encrypted_value)

        return decrypted.decode()
