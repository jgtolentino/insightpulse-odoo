"""
Advanced OCR Service with State-of-the-Art Models
Supports: PaddleOCR-VL, DeepSeek-OCR, and fallback options
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InsightPulse OCR Service",
    description="State-of-the-art OCR with PaddleOCR-VL and DeepSeek-OCR",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OCR Engine Configuration
OCR_PROVIDER = os.getenv("OCR_PROVIDER", "paddleocr-vl")  # paddleocr-vl | deepseek | tesseract
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.60"))

# Global OCR engine
ocr_engine = None


class PaddleOCRVL:
    """PaddleOCR-VL: 900M parameter vision-language model for document understanding"""

    def __init__(self, use_gpu: bool = False):
        logger.info("Initializing PaddleOCR-VL (900M params)...")
        try:
            from transformers import AutoProcessor, AutoModelForVision2Seq
            import torch

            self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")

            # Load PaddleOCR-VL model
            model_name = "paddleocr/PaddleOCR-VL"
            self.processor = AutoProcessor.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            self.model = AutoModelForVision2Seq.from_pretrained(
                model_name,
                trust_remote_code=True
            ).to(self.device)

            logger.info("PaddleOCR-VL initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR-VL: {e}")
            logger.info("Falling back to standard PaddleOCR...")
            self._init_fallback()

    def _init_fallback(self):
        """Fallback to standard PaddleOCR if VL model fails"""
        from paddleocr import PaddleOCR
        self.model = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            use_gpu=False,
            show_log=False
        )
        self.is_fallback = True

    def process(self, image: Image.Image) -> Dict[str, Any]:
        """Process image with PaddleOCR-VL"""
        try:
            if hasattr(self, 'is_fallback'):
                return self._process_fallback(image)

            # Convert PIL to numpy
            img_array = np.array(image)

            # Prepare inputs
            inputs = self.processor(
                images=image,
                return_tensors="pt"
            ).to(self.device)

            # Generate output
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=False
            )

            # Decode output
            result = self.processor.batch_decode(
                outputs,
                skip_special_tokens=True
            )[0]

            # Parse JSON output
            try:
                parsed = json.loads(result)
                return {
                    "text": parsed.get("text", ""),
                    "markdown": parsed.get("markdown", ""),
                    "structure": parsed,
                    "confidence": 0.95,
                    "model": "paddleocr-vl-900m"
                }
            except json.JSONDecodeError:
                return {
                    "text": result,
                    "confidence": 0.85,
                    "model": "paddleocr-vl-900m"
                }

        except Exception as e:
            logger.error(f"PaddleOCR-VL processing error: {e}")
            raise

    def _process_fallback(self, image: Image.Image) -> Dict[str, Any]:
        """Process with standard PaddleOCR"""
        img_array = np.array(image)
        result = self.model.ocr(img_array, cls=True)

        # Extract text and confidence
        text_lines = []
        confidences = []

        for line in result[0] if result and result[0] else []:
            text_lines.append(line[1][0])
            confidences.append(line[1][1])

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "text": "\n".join(text_lines),
            "confidence": avg_confidence,
            "model": "paddleocr-standard"
        }


class DeepSeekOCR:
    """DeepSeek-OCR: Alternative SOTA document understanding"""

    def __init__(self, use_gpu: bool = False):
        logger.info("Initializing DeepSeek-OCR...")
        try:
            from transformers import AutoProcessor, AutoModelForVision2Seq
            import torch

            self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")

            # Load DeepSeek-OCR model
            model_name = "deepseek-ai/deepseek-ocr"
            self.processor = AutoProcessor.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            self.model = AutoModelForVision2Seq.from_pretrained(
                model_name,
                trust_remote_code=True
            ).to(self.device)

            logger.info("DeepSeek-OCR initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek-OCR: {e}")
            raise

    def process(self, image: Image.Image) -> Dict[str, Any]:
        """Process image with DeepSeek-OCR"""
        try:
            # Prepare inputs
            inputs = self.processor(
                images=image,
                return_tensors="pt"
            ).to(self.device)

            # Generate output
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048
            )

            # Decode
            result = self.processor.batch_decode(
                outputs,
                skip_special_tokens=True
            )[0]

            return {
                "text": result,
                "confidence": 0.90,
                "model": "deepseek-ocr"
            }

        except Exception as e:
            logger.error(f"DeepSeek-OCR processing error: {e}")
            raise


class TesseractOCR:
    """Fallback Tesseract OCR"""

    def __init__(self):
        logger.info("Initializing Tesseract OCR...")
        import pytesseract
        self.tesseract = pytesseract

    def process(self, image: Image.Image) -> Dict[str, Any]:
        """Process image with Tesseract"""
        text = self.tesseract.image_to_string(image)
        return {
            "text": text,
            "confidence": 0.70,
            "model": "tesseract"
        }


def get_ocr_engine():
    """Initialize OCR engine based on configuration"""
    global ocr_engine

    if ocr_engine is not None:
        return ocr_engine

    provider = OCR_PROVIDER.lower()

    try:
        if provider == "paddleocr-vl":
            ocr_engine = PaddleOCRVL(use_gpu=USE_GPU)
        elif provider == "deepseek":
            ocr_engine = DeepSeekOCR(use_gpu=USE_GPU)
        elif provider == "tesseract":
            ocr_engine = TesseractOCR()
        else:
            logger.warning(f"Unknown provider {provider}, using Tesseract")
            ocr_engine = TesseractOCR()

    except Exception as e:
        logger.error(f"Failed to initialize {provider}, falling back to Tesseract: {e}")
        ocr_engine = TesseractOCR()

    return ocr_engine


def extract_receipt_data(ocr_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured receipt data from OCR result"""
    import re
    from dateutil import parser as date_parser

    text = ocr_result.get("text", "")
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Extract vendor (first non-empty line)
    vendor = lines[0] if lines else "Unknown"

    # Extract amount (look for currency patterns)
    amount = None
    for line in reversed(lines):
        # Match patterns like: 123.45, 1,234.56, $123.45, ₱123.45
        match = re.search(r'[₱$€£¥]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                break
            except ValueError:
                continue

    # Extract date
    date = None
    for line in lines[:10]:  # Usually in first few lines
        try:
            parsed_date = date_parser.parse(line, fuzzy=True)
            date = parsed_date.date().isoformat()
            break
        except (ValueError, TypeError):
            continue

    # Extract currency
    currency = "PHP"  # Default
    if "$" in text[:100]:
        currency = "USD"
    elif "€" in text[:100]:
        currency = "EUR"
    elif "₱" in text[:100]:
        currency = "PHP"

    return {
        "vendor": vendor,
        "amount": amount,
        "currency": currency,
        "date": date,
        "raw_text": text,
        "confidence": ocr_result.get("confidence", 0),
        "model": ocr_result.get("model", "unknown"),
        "markdown": ocr_result.get("markdown"),
        "structure": ocr_result.get("structure")
    }


@app.on_event("startup")
async def startup_event():
    """Initialize OCR engine on startup"""
    logger.info("Starting OCR Service...")
    logger.info(f"Provider: {OCR_PROVIDER}")
    logger.info(f"Use GPU: {USE_GPU}")
    logger.info(f"Confidence Threshold: {OCR_CONFIDENCE_THRESHOLD}")

    # Pre-initialize engine
    try:
        engine = get_ocr_engine()
        logger.info(f"OCR engine ready: {type(engine).__name__}")
    except Exception as e:
        logger.error(f"Failed to initialize OCR engine: {e}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "InsightPulse OCR Service",
        "version": "2.0.0",
        "provider": OCR_PROVIDER,
        "use_gpu": USE_GPU,
        "status": "healthy"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    engine = get_ocr_engine()
    return {
        "status": "healthy",
        "ocr_engine": type(engine).__name__,
        "provider": OCR_PROVIDER,
        "device": "gpu" if USE_GPU else "cpu",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/parse")
async def parse(file: UploadFile = File(...)):
    """
    Parse document/receipt image and extract structured data

    Supports:
    - PaddleOCR-VL (900M params) - SOTA document understanding
    - DeepSeek-OCR - Alternative SOTA
    - Tesseract - Fallback
    """
    try:
        # Read image
        content = await file.read()
        image = Image.open(io.BytesIO(content))

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Get OCR engine
        engine = get_ocr_engine()

        # Process image
        logger.info(f"Processing with {type(engine).__name__}...")
        start_time = datetime.utcnow()

        ocr_result = engine.process(image)

        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Processing completed in {processing_time:.2f}s")

        # Extract receipt data
        result = extract_receipt_data(ocr_result)
        result["processing_time_seconds"] = processing_time

        # Check confidence threshold
        if result["confidence"] < OCR_CONFIDENCE_THRESHOLD:
            logger.warning(f"Low confidence: {result['confidence']:.2f}")
            result["warning"] = f"Confidence below threshold ({OCR_CONFIDENCE_THRESHOLD})"

        return {
            "ok": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Parse error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr")
async def ocr_raw(file: UploadFile = File(...)):
    """
    Raw OCR endpoint - returns only extracted text
    """
    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        engine = get_ocr_engine()
        result = engine.process(image)

        return {
            "ok": True,
            "text": result.get("text", ""),
            "markdown": result.get("markdown"),
            "confidence": result.get("confidence"),
            "model": result.get("model")
        }

    except Exception as e:
        logger.error(f"OCR error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
