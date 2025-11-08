"""
Odoo Client - HMAC-signed HTTP client for calling Odoo controllers
"""

import os
import aiohttp
import json
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

ODOO_BASE_URL = os.environ.get("ODOO_BASE_URL", "https://erp.insightpulseai.net")
ODOO_API_TOKEN = os.environ.get("ODOO_API_TOKEN", "")
ODOO_HMAC_SECRET = os.environ.get("ODOO_HMAC_SECRET", "")


def sign(payload: str) -> str:
    """
    Generate HMAC-SHA256 signature for payload

    Args:
        payload: String payload to sign

    Returns:
        Hex-encoded HMAC signature
    """
    return hmac.new(
        ODOO_HMAC_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


async def call_odoo(path: str, body: dict) -> dict:
    """
    Call Odoo custom controller with signed request

    Args:
        path: API path (e.g., /api/agent/apply)
        body: Request body as dict

    Returns:
        Response dict with status and text

    Raises:
        Exception on network or HTTP errors
    """
    payload = json.dumps(body)
    signature = sign(payload)

    url = f"{ODOO_BASE_URL}{path}"
    headers = {
        "content-type": "application/json",
        "x-api-key": ODOO_API_TOKEN,
        "x-signature": signature,
    }

    logger.info(f"Calling Odoo: {url}")
    logger.debug(f"Payload: {payload[:200]}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                text = await response.text()

                logger.info(f"Odoo response status: {response.status}")
                logger.debug(f"Odoo response: {text[:200]}")

                return {
                    "status": response.status,
                    "text": text,
                    "ok": response.status < 400
                }
    except aiohttp.ClientError as e:
        logger.error(f"HTTP client error calling Odoo: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling Odoo: {str(e)}")
        raise
