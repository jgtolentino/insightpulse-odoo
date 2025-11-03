"""
PaddleOCR Service - FastAPI Application
Provides OCR API for receipt and document scanning
"""

import io
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
import redis.asyncio as aioredis
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="PaddleOCR Service",
    description="OCR API for receipt and document scanning using PaddleOCR",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
ocr_requests_total = Counter('ocr_requests_total', 'Total OCR requests')
ocr_requests_success = Counter('ocr_requests_success', 'Successful OCR requests')
ocr_requests_failed = Counter('ocr_requests_failed', 'Failed OCR requests')
ocr_processing_time = Histogram('ocr_processing_seconds', 'OCR processing time')

# Global variables
ocr_engine: Optional[PaddleOCR] = None
redis_client: Optional[aioredis.Redis] = None

# Models
class OCRResult(BaseModel):
    """OCR result model"""
    success: bool = Field(..., description="Whether OCR was successful")
    confidence: float = Field(..., description="Average confidence score")
    merchant_name: Optional[str] = Field(None, description="Merchant/vendor name")
    date: Optional[str] = Field(None, description="Transaction date")
    total_amount: Optional[float] = Field(None, description="Total amount")
    currency: Optional[str] = Field(None, description="Currency code")
    tax_amount: Optional[float] = Field(None, description="Tax amount")
    line_items: list[Dict[str, Any]] = Field(default_factory=list, description="Line items")
    raw_text: str = Field(..., description="Raw OCR text")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    ocr_engine_loaded: bool


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize OCR engine and Redis connection on startup"""
    global ocr_engine, redis_client

    try:
        logger.info("Initializing PaddleOCR engine...")
        ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            use_gpu=False,  # Set to True if GPU available
            enable_mkldnn=True,  # CPU optimization
            show_log=False
        )
        logger.info("PaddleOCR engine initialized successfully")

        # Initialize Redis connection
        logger.info("Connecting to Redis...")
        redis_client = await aioredis.from_url(
            "redis://redis:6379",
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connection established")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global redis_client

    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


# Helper functions
def extract_receipt_data(ocr_result: list) -> Dict[str, Any]:
    """Extract structured data from OCR result"""
    extracted = {
        "merchant_name": None,
        "date": None,
        "total_amount": None,
        "currency": "USD",
        "tax_amount": None,
        "line_items": [],
        "raw_text": "",
        "confidence_scores": []
    }

    all_text = []

    for line in ocr_result:
        if not line:
            continue

        for detection in line:
            if len(detection) < 2:
                continue

            text = detection[1][0] if isinstance(detection[1], tuple) else detection[1]
            confidence = detection[1][1] if isinstance(detection[1], tuple) and len(detection[1]) > 1 else 0.0

            all_text.append(text)
            extracted["confidence_scores"].append(confidence)

            # Extract merchant name (usually first/top line)
            if not extracted["merchant_name"] and confidence > 0.8:
                extracted["merchant_name"] = text

            # Extract date (look for date patterns)
            if not extracted["date"]:
                import re
                date_patterns = [
                    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                    r'\d{4}[/-]\d{1,2}[/-]\d{1,2}'
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, text)
                    if match:
                        extracted["date"] = match.group(0)
                        break

            # Extract total amount (look for total/amount keywords)
            if not extracted["total_amount"]:
                import re
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in ['total', 'amount', 'sum']):
                    # Look for currency amounts in next line or same line
                    amount_pattern = r'[\$€£¥]?\s*(\d+[.,]\d{2})'
                    match = re.search(amount_pattern, text)
                    if match:
                        amount_str = match.group(1).replace(',', '.')
                        try:
                            extracted["total_amount"] = float(amount_str)
                        except ValueError:
                            pass

            # Extract tax amount
            if not extracted["tax_amount"]:
                import re
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in ['tax', 'vat', 'gst']):
                    amount_pattern = r'[\$€£¥]?\s*(\d+[.,]\d{2})'
                    match = re.search(amount_pattern, text)
                    if match:
                        amount_str = match.group(1).replace(',', '.')
                        try:
                            extracted["tax_amount"] = float(amount_str)
                        except ValueError:
                            pass

    extracted["raw_text"] = "\n".join(all_text)

    return extracted


# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "PaddleOCR Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        ocr_engine_loaded=ocr_engine is not None
    )


@app.post("/api/v1/ocr/scan", response_model=OCRResult)
async def scan_receipt(
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """
    Scan receipt or document using OCR

    Args:
        file: Image file (JPEG, PNG)
        x_api_key: API key for authentication (optional)

    Returns:
        OCRResult: Structured OCR result with extracted data
    """
    ocr_requests_total.inc()
    start_time = time.time()

    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            ocr_requests_failed.inc()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Only JPEG/PNG supported."
            )

        # Read image file
        contents = await file.read()

        # Validate file size (max 10MB)
        if len(contents) > 10 * 1024 * 1024:
            ocr_requests_failed.inc()
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )

        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))

        # Convert to numpy array
        img_array = np.array(image)

        # Perform OCR
        logger.info(f"Processing OCR for file: {file.filename}")
        ocr_result = ocr_engine.ocr(img_array, cls=True)

        # Extract structured data
        extracted = extract_receipt_data(ocr_result[0] if ocr_result else [])

        # Calculate average confidence
        avg_confidence = (
            sum(extracted["confidence_scores"]) / len(extracted["confidence_scores"])
            if extracted["confidence_scores"] else 0.0
        )

        processing_time = time.time() - start_time
        ocr_processing_time.observe(processing_time)

        # Build result
        result = OCRResult(
            success=True,
            confidence=avg_confidence,
            merchant_name=extracted["merchant_name"],
            date=extracted["date"],
            total_amount=extracted["total_amount"],
            currency=extracted["currency"],
            tax_amount=extracted["tax_amount"],
            line_items=extracted["line_items"],
            raw_text=extracted["raw_text"],
            processing_time=processing_time
        )

        ocr_requests_success.inc()
        logger.info(f"OCR completed successfully in {processing_time:.2f}s (confidence: {avg_confidence:.2f})")

        return result

    except HTTPException:
        raise
    except Exception as e:
        ocr_requests_failed.inc()
        logger.error(f"OCR processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=2)
