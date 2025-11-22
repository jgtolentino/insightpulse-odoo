#!/usr/bin/env python3
"""
InsightPulse OCR Adapter for Odoo Expenses
Exposes /api/expense/ocr endpoint that matches Odoo's contract
"""
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import logging
from datetime import datetime
from typing import Optional
import re
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InsightPulse OCR Adapter",
    description="OCR service adapter for Odoo expense integration",
    version="1.0.0"
)

# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
OCR_UPSTREAM_URL = os.getenv("UPSTREAM_OCR_URL", "http://localhost:8000/ocr")
API_KEY = os.getenv("IPAI_OCR_API_KEY", "dev-key-insecure")
TIMEOUT = int(os.getenv("OCR_TIMEOUT", "60"))

logger.info(f"OCR Adapter initialized with upstream: {OCR_UPSTREAM_URL}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ocr-adapter",
        "upstream": OCR_UPSTREAM_URL,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/expense/ocr")
async def ocr_expense(
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """
    OCR endpoint for Odoo expense receipts

    Expected by Odoo:
    - Method: POST
    - Body: multipart/form-data with 'file' field
    - Auth: X-API-Key header (optional)

    Returns JSON:
    {
        "merchant_name": "Store Name",
        "invoice_date": "2025-11-20",
        "currency": "PHP",
        "total_amount": 1234.56
    }
    """
    # API key validation (if configured)
    if API_KEY != "dev-key-insecure" and x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt from {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Read file content
    try:
        content = await file.read()
        filename = file.filename or "receipt.jpg"
        content_type = file.content_type or "image/jpeg"

        logger.info(f"Processing OCR request: {filename} ({len(content)} bytes)")

        # Call upstream OCR service
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            files = {"file": (filename, content, content_type)}

            logger.info(f"Calling upstream OCR: {OCR_UPSTREAM_URL}")
            resp = await client.post(OCR_UPSTREAM_URL, files=files)
            resp.raise_for_status()

            raw_response = resp.json()
            logger.info(f"Upstream OCR response: {raw_response}")

        # Normalize response to Odoo contract
        # Adjust field mappings based on your actual OCR service response format
        normalized = normalize_ocr_response(raw_response)

        logger.info(f"Normalized response: {normalized}")
        return JSONResponse(content=normalized)

    except httpx.HTTPStatusError as e:
        logger.error(f"Upstream OCR HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail=f"Upstream OCR service error: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        logger.error(f"Upstream OCR connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to OCR service: {str(e)}"
        )
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )


# PH-specific vendor normalization map
VENDOR_NORMALIZATION = {
    # SM Group
    "sm store": "SM Supermarket",
    "sm dept": "SM Department Store",
    "sm supermarket": "SM Supermarket",
    "sm city": "SM City",
    "sm mall": "SM Mall",

    # Jollibee Foods Corporation
    "jollibee foods": "Jollibee",
    "jfc": "Jollibee",
    "jollibee foods corp": "Jollibee",

    # Convenience Stores
    "7 eleven": "7-Eleven",
    "seven eleven": "7-Eleven",
    "711": "7-Eleven",
    "7eleven": "7-Eleven",
    "ministop": "Ministop",
    "alfamart": "Alfamart",
    "familymart": "FamilyMart",
    "family mart": "FamilyMart",
    "lawson": "Lawson",

    # Restaurants - Filipino
    "max's": "Max's Restaurant",
    "maxs restaurant": "Max's Restaurant",
    "maxs": "Max's Restaurant",
    "mang inasal": "Mang Inasal",
    "manginasal": "Mang Inasal",
    "chowking": "Chowking",
    "chow king": "Chowking",
    "greenwich": "Greenwich",
    "green wich": "Greenwich",
    "goldilocks": "Goldilocks",
    "red ribbon": "Red Ribbon",

    # Fast Food - International
    "kfc": "KFC",
    "kentucky fried chicken": "KFC",
    "mcdonald's": "McDonald's",
    "mcdonalds": "McDonald's",
    "mcdo": "McDonald's",
    "burger king": "Burger King",
    "wendy's": "Wendy's",
    "wendys": "Wendy's",
    "pizza hut": "Pizza Hut",
    "pizzahut": "Pizza Hut",
    "shakey's": "Shakey's Pizza",
    "shakeys": "Shakey's Pizza",
    "shakeys pizza": "Shakey's Pizza",

    # Coffee Shops
    "starbucks": "Starbucks",
    "starbucks coffee": "Starbucks",
    "bo's coffee": "Bo's Coffee",
    "bos coffee": "Bo's Coffee",
    "dunkin donuts": "Dunkin' Donuts",
    "dunkin'": "Dunkin' Donuts",
    "dunkin": "Dunkin' Donuts",

    # Supermarkets
    "puregold": "Puregold",
    "puregold price club": "Puregold",
    "robinsons": "Robinsons Supermarket",
    "robinsons supermarket": "Robinsons Supermarket",
    "savemore": "SaveMore",
    "save more": "SaveMore",
    "rustans": "Rustan's",
    "rustan's": "Rustan's",
    "rustans supermarket": "Rustan's",
    "allday": "AllDay Supermarket",
    "all day": "AllDay Supermarket",
    "landmark": "Landmark",
    "landmark supermarket": "Landmark",

    # Pharmacies
    "mercury drug": "Mercury Drug",
    "mercury drugstore": "Mercury Drug",
    "watsons": "Watsons",
    "watson's": "Watsons",
    "southstar drug": "SouthStar Drug",
    "the generics pharmacy": "The Generics Pharmacy",
    "tgp": "The Generics Pharmacy",

    # Gas Stations
    "petron": "Petron",
    "petron gas": "Petron",
    "shell": "Shell",
    "shell gas": "Shell",
    "caltex": "Caltex",
    "caltex gas": "Caltex",
    "phoenix": "Phoenix Petroleum",
    "phoenix petroleum": "Phoenix Petroleum",
    "seaoil": "Seaoil",

    # Retail
    "national bookstore": "National Bookstore",
    "national book store": "National Bookstore",
    "fully booked": "Fully Booked",
    "fullybooked": "Fully Booked",
    "ace hardware": "Ace Hardware",
    "handyman": "Handyman",
    "wilcon": "Wilcon Depot",
    "wilcon depot": "Wilcon Depot",
}

# PH local vendor patterns for currency defaulting
PH_LOCAL_VENDORS = {
    # Major chains
    "sm", "jollibee", "7-eleven", "max's", "puregold",
    "robinsons", "ministop", "mercury", "watsons", "mercury drug",
    "savemore", "alfamart", "familymart", "lawson",

    # Filipino restaurants
    "mang inasal", "chowking", "greenwich", "goldilocks", "red ribbon",

    # Fast food
    "kfc", "mcdonald", "mcdo", "burger king", "wendy", "pizza hut", "shakey",

    # Coffee
    "starbucks", "bo's coffee", "dunkin",

    # Supermarkets
    "rustans", "rustan", "allday", "landmark",

    # Pharmacies
    "southstar", "generics pharmacy", "tgp",

    # Gas stations
    "petron", "shell", "caltex", "phoenix", "seaoil",

    # Retail
    "national bookstore", "fully booked", "ace hardware", "handyman", "wilcon",

    # Generic
    "supermarket", "sari-sari", "carinderia"
}


def normalize_vendor_name(vendor: str) -> str:
    """Normalize PH vendor names to canonical form"""
    if not vendor:
        return "Unknown Merchant"

    vendor_lower = vendor.lower().strip()

    # Check exact match in normalization map
    if vendor_lower in VENDOR_NORMALIZATION:
        return VENDOR_NORMALIZATION[vendor_lower]

    # Return original with title case
    return vendor.strip()


def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize various date formats to YYYY-MM-DD

    Supports:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - MM/DD/YYYY
    - PH-style: "15 Nov 2025", "Nov 15, 2025"
    """
    if not date_str:
        return None

    try:
        # Use dateutil parser for flexible parsing
        parsed = date_parser.parse(date_str, dayfirst=True)  # PH uses DD/MM/YYYY commonly
        return parsed.strftime("%Y-%m-%d")
    except (ValueError, TypeError) as e:
        logger.warning(f"Date parsing failed for '{date_str}': {e}")
        return None


def should_default_to_php(vendor_name: str) -> bool:
    """Check if vendor is likely PH-local and should default to PHP"""
    if not vendor_name:
        return True  # Default to PHP if no vendor

    vendor_lower = vendor_name.lower()
    return any(ph_vendor in vendor_lower for ph_vendor in PH_LOCAL_VENDORS)


def normalize_ocr_response(raw: dict) -> dict:
    """
    Normalize OCR service response to Odoo contract

    Deliberate normalization passes:
    1. Vendor normalization (PH-specific variants)
    2. Date normalization (multiple formats → YYYY-MM-DD)
    3. Total tolerance (keep raw vs normalized)
    4. Currency defaulting (PHP for local vendors)

    Adjust these mappings based on your actual OCR service response format.
    Common patterns:
    - PaddleOCR-VL: {"merchant": "...", "date": "...", "total": ...}
    - Azure Doc Intelligence: {"fields": {"MerchantName": {"value": "..."}, ...}}
    - Google Vision: {"textAnnotations": [...], "fullTextAnnotation": {...}}
    """
    # Default safe values
    result = {
        "merchant_name": "Unknown Merchant",
        "invoice_date": None,
        "currency": "PHP",
        "total_amount": 0.0,
    }

    # Extract raw fields from different OCR response formats
    raw_vendor = None
    raw_date = None
    raw_total = None
    raw_currency = None

    # Pattern 1: Direct fields (PaddleOCR-VL format)
    if "merchant" in raw or "merchant_name" in raw:
        raw_vendor = raw.get("merchant") or raw.get("merchant_name")

    if "date" in raw or "invoice_date" in raw:
        raw_date = raw.get("date") or raw.get("invoice_date")

    if "total" in raw or "total_amount" in raw:
        raw_total = raw.get("total") or raw.get("total_amount")

    if "currency" in raw:
        raw_currency = raw.get("currency")

    # Pattern 2: Azure Document Intelligence format
    if "fields" in raw:
        fields = raw["fields"]
        if "MerchantName" in fields and "value" in fields["MerchantName"]:
            raw_vendor = fields["MerchantName"]["value"]
        if "TransactionDate" in fields and "value" in fields["TransactionDate"]:
            raw_date = fields["TransactionDate"]["value"]
        if "Total" in fields and "value" in fields["Total"]:
            raw_total = fields["Total"]["value"]

    # Pattern 3: Structured extraction
    if "extracted" in raw and isinstance(raw["extracted"], dict):
        ext = raw["extracted"]
        raw_vendor = ext.get("merchant", raw_vendor)
        raw_date = ext.get("date", raw_date)
        raw_total = ext.get("total", raw_total)
        raw_currency = ext.get("currency", raw_currency)

    # === NORMALIZATION PASS 1: Vendor ===
    if raw_vendor:
        result["merchant_name"] = normalize_vendor_name(raw_vendor)

    # === NORMALIZATION PASS 2: Date ===
    if raw_date:
        result["invoice_date"] = normalize_date(raw_date)

    # === NORMALIZATION PASS 3: Total ===
    if raw_total:
        try:
            result["total_amount"] = float(raw_total)
        except (ValueError, TypeError):
            logger.warning(f"Total parsing failed for '{raw_total}'")
            result["total_amount"] = 0.0

    # === NORMALIZATION PASS 4: Currency ===
    if raw_currency:
        result["currency"] = raw_currency.upper()
    elif should_default_to_php(result["merchant_name"]):
        result["currency"] = "PHP"

    logger.info(f"Normalization: {raw_vendor} → {result['merchant_name']}, {raw_date} → {result['invoice_date']}, {raw_total} → {result['total_amount']} {result['currency']}")

    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
