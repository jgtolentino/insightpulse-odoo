import os
import io
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
from supabase import create_client, Client
import uvicorn

app = FastAPI(title="DeepSeek-OCR API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Optional[Client] = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-OCR")
DEVICE = os.getenv("TORCH_DEVICE", "cpu")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "base")  # tiny, small, base, large

# Image size mapping
IMAGE_SIZE_MAP = {
    "tiny": (512, 512),
    "small": (640, 640),
    "base": (1024, 1024),
    "large": (1280, 1280)
}

# Load model and processor
print(f"Loading DeepSeek-OCR model: {MODEL_NAME}")
processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16 if DEVICE == "cuda" else torch.float32,
    trust_remote_code=True
).to(DEVICE)
model.eval()
print(f"Model loaded on device: {DEVICE}")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "device": DEVICE,
        "image_size": IMAGE_SIZE,
        "supabase_connected": supabase is not None
    }

@app.post("/v1/ocr")
async def extract_text(
    file: UploadFile = File(...),
    output_format: str = "markdown"
):
    """
    Extract text from image using DeepSeek-OCR

    Args:
        file: Image file (JPEG, PNG, etc.)
        output_format: Output format (markdown, plain)

    Returns:
        Extracted text and metadata
    """
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Resize based on configuration
        target_size = IMAGE_SIZE_MAP.get(IMAGE_SIZE, (1024, 1024))
        image = image.resize(target_size, Image.Resampling.LANCZOS)

        # Prepare inputs
        prompt = "Extract all text from this document and format as markdown."
        inputs = processor(
            images=image,
            text=prompt,
            return_tensors="pt"
        ).to(DEVICE)

        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=False
            )

        # Decode output
        extracted_text = processor.batch_decode(
            outputs,
            skip_special_tokens=True
        )[0]

        # Store result in Supabase if configured
        result = {
            "text": extracted_text,
            "format": output_format,
            "model": MODEL_NAME,
            "image_size": IMAGE_SIZE,
            "file_name": file.filename
        }

        if supabase:
            try:
                supabase.table("ocr_results").insert({
                    "file_name": file.filename,
                    "extracted_text": extracted_text,
                    "model": MODEL_NAME,
                    "image_size": IMAGE_SIZE,
                    "device": DEVICE
                }).execute()
            except Exception as e:
                print(f"Failed to store result in Supabase: {e}")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/parse")
async def parse_document(file: UploadFile = File(...)):
    """Parse document and extract structured data"""
    return await extract_text(file, output_format="markdown")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
