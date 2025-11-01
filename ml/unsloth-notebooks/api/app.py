from fastapi import FastAPI
from pydantic import BaseModel
import os

# NOTE: This is a minimal stub. Replace with your Unsloth-loaded model logic.
app = FastAPI(title="Unsloth API", version="0.1.0")

class InferenceIn(BaseModel):
    text: str

class InferenceOut(BaseModel):
    output: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict", response_model=InferenceOut)
def predict(inp: InferenceIn):
    # TODO: run Unsloth pipeline here; for now, echo a toy transform
    return InferenceOut(output=inp.text.strip()[::-1])
