#!/usr/bin/env python3
"""
Process Intelligence API Service
FastAPI wrapper around SAP Process Intelligence skills
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add skills to Python path
skills_path = Path(__file__).parent.parent.parent / "skills"
sys.path.insert(0, str(skills_path))

from integrations.sap_process_intelligence.sap_executor import SAPProcessIntelligence
from integrations.sap_process_intelligence.models.sap_event_model import (
    ExtractEventsRequest,
    ExtractEventsResponse,
    CorrelateVariantsRequest,
    CorrelateVariantsResponse,
    AnalyzeBottlenecksRequest,
    AnalyzeBottlenecksResponse,
    PredictKPIRequest,
    PredictKPIResponse,
    GenerateProcessMapRequest,
    GenerateProcessMapResponse,
)
from integrations.drawio_adapter.drawio_adapter import (
    DrawIOAdapter,
    CreateDiagramInput,
    ExportDiagramInput,
)

# Initialize engines
sap_engine = SAPProcessIntelligence()
drawio_adapter = DrawIOAdapter()

app = FastAPI(
    title="InsightPulse Process Intelligence API",
    description="SAP S/4HANA process mining and analytics",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export directory
EXPORT_DIR = Path(os.getenv("PI_EXPORT_DIR", "/tmp/pi-exports"))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# Request/Response Models

class HealthResponse(BaseModel):
    ok: bool
    timestamp: str
    version: str


class ExtractQuery(BaseModel):
    process_id: str
    date_range: str
    process_type: str = "PROCURE_TO_PAY"
    system_id: str = "SAP_PROD"


class AnalyzePayload(BaseModel):
    events: List[Dict[str, Any]]


class DiagramPayload(BaseModel):
    process_id: str
    events: List[Dict[str, Any]]
    output_format: str = "mermaid"


# Endpoints

@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint"""
    return HealthResponse(
        ok=True,
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0"
    )


@app.post("/pi/extract", response_model=ExtractEventsResponse)
def extract(query: ExtractQuery):
    """Extract SAP process events"""
    try:
        request = ExtractEventsRequest(
            process_id=query.process_id,
            date_range=query.date_range,
            process_type=query.process_type,
            system_id=query.system_id
        )
        response = sap_engine.extract_process_events(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pi/analyze")
def analyze(payload: AnalyzePayload):
    """Analyze process variants and bottlenecks"""
    try:
        # Correlate variants
        variants_request = CorrelateVariantsRequest(events=payload.events)
        variants_response = sap_engine.correlate_variants(variants_request)

        # Analyze bottlenecks
        bottlenecks_request = AnalyzeBottlenecksRequest(events=payload.events)
        bottlenecks_response = sap_engine.analyze_bottlenecks(bottlenecks_request)

        return {
            "variants": variants_response.dict(),
            "bottlenecks": bottlenecks_response.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pi/predict")
def predict(payload: dict):
    """Predict KPIs"""
    try:
        request = PredictKPIRequest(**payload)
        response = sap_engine.predict_kpi(request)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pi/diagram")
def diagram(payload: DiagramPayload):
    """Generate process diagram"""
    try:
        # Generate process map
        map_request = GenerateProcessMapRequest(
            events=payload.events,
            output_format=payload.output_format
        )
        map_response = sap_engine.generate_process_map(map_request)

        # Create Draw.io diagram
        diagram_filename = EXPORT_DIR / f"sap-{payload.process_id}.drawio"
        diagram_input = CreateDiagramInput(
            source_format=payload.output_format,
            content=map_response.process_map,
            filename=str(diagram_filename)
        )
        diagram_output = drawio_adapter.create_diagram(diagram_input)

        # Export to PNG
        export_input = ExportDiagramInput(
            file_path=diagram_output.file_path,
            format="png",
            scale=2.0
        )
        export_output = drawio_adapter.export_diagram(export_input)

        return {
            "drawio": diagram_output.file_path,
            "png": export_output.export_path,
            "process_map": map_response.process_map,
            "statistics": map_response.statistics.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)
