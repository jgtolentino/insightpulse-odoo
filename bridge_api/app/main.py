"""
FastAPI Bridge Application
Optional helper service for replay, dev testing, and advanced workflows
"""

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .crypto import verify_hmac
from .odoo_client import call_odoo
import os
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("BRIDGE_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Odoo-Supabase Bridge",
    description="Optional bridge service for event replay and development",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BRIDGE_HMAC_SECRET = os.environ.get("BRIDGE_HMAC_SECRET", "")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "odoo-supabase-bridge",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check for containers"""
    return {"status": "ok"}

@app.post("/bridge/replay")
async def replay(req: Request, x_signature: str = Header(None)):
    """
    Replay endpoint for event debugging
    Verifies HMAC signature and echoes back the event
    """
    try:
        raw = await req.body()

        # Verify signature
        if not verify_hmac(raw, x_signature or "", BRIDGE_HMAC_SECRET):
            logger.warning("Invalid signature in replay request")
            raise HTTPException(status_code=401, detail="invalid signature")

        body = await req.json()
        logger.info(f"Replay request received: {body.get('event_type', 'unknown')}")

        return {
            "ok": True,
            "echo": body,
            "message": "Event replayed successfully"
        }
    except Exception as e:
        logger.error(f"Error in replay: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bridge/apply")
async def apply_action(body: dict):
    """
    Apply action to Odoo
    Simple dev route to call Odoo /api/agent/apply endpoint
    """
    try:
        logger.info(f"Applying action to Odoo: {body.get('action', 'unknown')}")
        result = await call_odoo("/api/agent/apply", body)
        return result
    except Exception as e:
        logger.error(f"Error applying action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bridge/event")
async def ingest_event(req: Request, x_signature: str = Header(None)):
    """
    Alternative event ingestion endpoint
    Can be used instead of direct Supabase Edge Function calls
    """
    try:
        raw = await req.body()

        # Verify signature
        if not verify_hmac(raw, x_signature or "", BRIDGE_HMAC_SECRET):
            logger.warning("Invalid signature in event ingestion")
            raise HTTPException(status_code=401, detail="invalid signature")

        body = await req.json()
        logger.info(f"Event ingested: {body.get('event_type', 'unknown')}")

        # Here you could forward to Supabase or process directly
        # For now, just acknowledge
        return {
            "ok": True,
            "event_type": body.get("event_type"),
            "message": "Event ingested"
        }
    except Exception as e:
        logger.error(f"Error ingesting event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8787)
