"""
Cryptographic utilities for HMAC signature verification
"""

import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)


def verify_hmac(raw: bytes, sig_hex: str, secret: str) -> bool:
    """
    Verify HMAC-SHA256 signature using timing-safe comparison

    Args:
        raw: Raw bytes of the message
        sig_hex: Hex-encoded HMAC signature to verify
        secret: Shared secret key

    Returns:
        True if signature is valid, False otherwise
    """
    if not secret:
        logger.warning("HMAC secret is empty - signature verification will fail")
        return False

    if not sig_hex:
        logger.warning("No signature provided")
        return False

    try:
        # Calculate expected MAC
        mac = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()

        # Timing-safe comparison
        is_valid = hmac.compare_digest(mac, sig_hex)

        if not is_valid:
            logger.warning("HMAC signature mismatch")
            logger.debug(f"Expected: {mac[:16]}... Got: {sig_hex[:16]}...")

        return is_valid
    except Exception as e:
        logger.error(f"Error verifying HMAC: {str(e)}")
        return False


def generate_hmac(message: str, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for a message

    Args:
        message: Message to sign
        secret: Shared secret key

    Returns:
        Hex-encoded HMAC signature
    """
    return hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
