from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os

app = FastAPI()

class ClassifyIn(BaseModel):
    text: str

@app.get('/health')
def health():
    return {'ok': True}

@app.post('/ocr/receipt')
async def ocr_receipt(file: UploadFile = File(...)):
    # In MVP, we simulate OCR fields; swap for PaddleOCR-VL
    content = await file.read()
    # TODO: plug actual OCR engine
    return {
        'lines': ['MERCHANT XYZ', 'TOTAL 123.45'],
        'merchant': 'MERCHANT XYZ',
        'total': 123.45,
        'currency': 'USD',
        'conf': 0.83
    }

@app.post('/classify/expense')
async def classify(body: ClassifyIn):
    # Smol heuristic placeholder; replace with tiny model
    cat = 'Meals' if 'restaurant' in body.text.lower() else 'General'
    return {'category': cat, 'conf': 0.70}
