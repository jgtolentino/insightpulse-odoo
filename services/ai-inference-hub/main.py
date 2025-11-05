import io, os, threading, time
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR

app = FastAPI(
    title="AI Inference Hub",
    description="OCR, STT, TTS, and AI Coding Agent Services"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Global state ------------------------------------------------------------
_state = {
    "ocr": {"loaded": False, "error": None},
    "stt": {"loaded": False, "error": None},
    "tts": {"loaded": False, "error": None},
}
_models = {"ocr": None, "stt": None, "tts": None}

# Feature flags (speed up dev boots)
ENABLE_STT = os.getenv("AI_ENABLE_STT", "0") == "1"
ENABLE_TTS = os.getenv("AI_ENABLE_TTS", "0") == "1"

# Model configuration
DEVICE = os.getenv("TORCH_DEVICE", "cpu")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
TTS_MODEL = os.getenv("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")

# ---- Background loader -------------------------------------------------------
def _load_ocr():
    try:
        print("Loading PaddleOCR model...")
        _models["ocr"] = PaddleOCR(use_angle_cls=True, lang="en")  # CPU by default
        _state["ocr"]["loaded"] = True
        print("PaddleOCR model loaded successfully (CPU mode, ~25MB)")
    except Exception as e:
        print(f"Error loading PaddleOCR: {e}")
        _state["ocr"]["error"] = str(e)

def _load_stt():
    if not ENABLE_STT:
        print("STT disabled via AI_ENABLE_STT=0")
        return
    try:
        print(f"Loading Whisper STT model: {WHISPER_MODEL}")
        import whisper
        _models["stt"] = whisper.load_model(WHISPER_MODEL, device=DEVICE)
        _state["stt"]["loaded"] = True
        print("Whisper model loaded successfully")
    except Exception as e:
        print(f"Error loading Whisper: {e}")
        _state["stt"]["error"] = str(e)

def _load_tts():
    if not ENABLE_TTS:
        print("TTS disabled via AI_ENABLE_TTS=0")
        return
    try:
        print(f"Loading TTS model: {TTS_MODEL}")
        from TTS.api import TTS
        _models["tts"] = TTS(model_name=TTS_MODEL, progress_bar=False, gpu=False)
        _state["tts"]["loaded"] = True
        print("TTS model loaded successfully")
    except Exception as e:
        print(f"Error loading TTS: {e}")
        _state["tts"]["error"] = str(e)

def _loader():
    _load_ocr()
    _load_stt()
    _load_tts()

@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=_loader, daemon=True)
    t.start()

# ---- Probes ------------------------------------------------------------------
@app.get("/live")
def live():
    """Liveness: process is up, regardless of model state"""
    return {"status": "alive", "ts": int(time.time())}

@app.get("/health")
def health():
    """Health: always returns quickly with current model states"""
    return {
        "status": "ok",
        "models": _state,
        "ts": int(time.time()),
    }

@app.get("/ready")
def ready():
    """Readiness: only 'True' when required models are loaded"""
    required_ok = _state["ocr"]["loaded"] and _state["ocr"]["error"] is None
    return {"ready": required_ok, "models": _state, "ts": int(time.time())}

# ---- OCR endpoint ------------------------------------------------------------
class OCRItem(BaseModel):
    text: str
    box: Any
    score: float

class OCRResponse(BaseModel):
    lines: list[OCRItem]
    meta: Dict[str, Any]

@app.post("/v1/ocr/receipt", response_model=OCRResponse)
async def ocr_receipt(file: UploadFile = File(...)):
    """Production-safe OCR endpoint for Philippine receipts"""
    if not _state["ocr"]["loaded"]:
        raise HTTPException(status_code=503, detail="OCR not ready")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        # Convert to numpy array for PaddleOCR
        image = Image.open(io.BytesIO(data)).convert("RGB")
        img_array = np.array(image)

        # Run PaddleOCR inference
        result = _models["ocr"].ocr(img_array)

        lines = []
        # PaddleOCR v3.x returns OCRResult object with rec_texts, rec_scores, dt_polys
        if result and result[0]:
            ocr_result = result[0]
            texts = ocr_result.get("rec_texts", [])
            scores = ocr_result.get("rec_scores", [])
            boxes = ocr_result.get("dt_polys", [])

            for i in range(len(texts)):
                lines.append(OCRItem(
                    text=texts[i],
                    box=boxes[i].tolist() if i < len(boxes) else [],
                    score=float(scores[i]) if i < len(scores) else 0.0
                ))

        return OCRResponse(
            lines=lines,
            meta={
                "model": "PaddleOCR",
                "lang": "en",
                "count": len(lines),
                "received_filename": file.filename,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

# Legacy OCR endpoint for backward compatibility
@app.post("/v1/ocr")
async def extract_text(file: UploadFile = File(...)):
    """Legacy OCR endpoint - redirects to /v1/ocr/receipt"""
    result = await ocr_receipt(file)

    # Convert to legacy format
    extracted_text = "\n".join([line.text for line in result.lines])

    return {
        "text": extracted_text,
        "lines": [{"text": line.text, "confidence": line.score, "bbox": line.box} for line in result.lines],
        "format": "plain",
        "model": result.meta["model"],
        "file_name": result.meta["received_filename"]
    }

@app.post("/v1/parse")
async def parse_document(file: UploadFile = File(...)):
    """Parse document - alias for legacy compatibility"""
    return await extract_text(file)
