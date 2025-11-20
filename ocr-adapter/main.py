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


def normalize_ocr_response(raw: dict) -> dict:
    """
    Normalize OCR service response to Odoo contract

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

    # Pattern 1: Direct fields (adjust to your OCR service format)
    if "merchant" in raw or "merchant_name" in raw:
        result["merchant_name"] = raw.get("merchant") or raw.get("merchant_name", "Unknown Merchant")

    if "date" in raw or "invoice_date" in raw:
        result["invoice_date"] = raw.get("date") or raw.get("invoice_date")

    if "total" in raw or "total_amount" in raw:
        result["total_amount"] = float(raw.get("total") or raw.get("total_amount", 0.0))

    if "currency" in raw:
        result["currency"] = raw.get("currency", "PHP")

    # Pattern 2: Azure Document Intelligence format (example)
    if "fields" in raw:
        fields = raw["fields"]
        if "MerchantName" in fields and "value" in fields["MerchantName"]:
            result["merchant_name"] = fields["MerchantName"]["value"]
        if "TransactionDate" in fields and "value" in fields["TransactionDate"]:
            result["invoice_date"] = fields["TransactionDate"]["value"]
        if "Total" in fields and "value" in fields["Total"]:
            result["total_amount"] = float(fields["Total"]["value"])

    # Pattern 3: Structured extraction (example)
    if "extracted" in raw and isinstance(raw["extracted"], dict):
        ext = raw["extracted"]
        result["merchant_name"] = ext.get("merchant", result["merchant_name"])
        result["invoice_date"] = ext.get("date", result["invoice_date"])
        result["total_amount"] = float(ext.get("total", result["total_amount"]))
        result["currency"] = ext.get("currency", result["currency"])

    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
