#!/usr/bin/env python3
"""
Error Collector Service
Ingests error events and stores them with normalized fingerprints
"""
import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
from typing import Dict, Any

# Database configuration
DB_KW = {
    'host': os.getenv('SUPABASE_DB_HOST'),
    'dbname': os.getenv('SUPABASE_DB_NAME'),
    'user': os.getenv('SUPABASE_DB_USER'),
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'port': os.getenv('SUPABASE_DB_PORT', '5432'),
}

def normalize_error(error_text: str) -> str:
    """Normalize error text using DB function"""
    try:
        with psycopg.connect(**DB_KW, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute("select public.normalize_error_message(%s) as n", (error_text,))
                result = cur.fetchone()
                return result['n'] if result else error_text
    except Exception as e:
        print(f"Warning: Could not normalize error: {e}")
        return error_text

def get_fingerprint(error_type: str, component: str, error_msg: str) -> str:
    """Get error fingerprint using DB function"""
    try:
        with psycopg.connect(**DB_KW, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select public.error_fingerprint(%s, %s, %s) as fp",
                    (error_type, component, error_msg)
                )
                result = cur.fetchone()
                return str(result['fp']) if result else None
    except Exception as e:
        print(f"Warning: Could not get fingerprint: {e}")
        return None

def ingest_error(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest an error event

    Expected event format:
    {
        "error": "KeyError: 'field_name'",
        "component": "odoo.addons.custom_module",
        "tags": ["odoo", "dev"],
        "context": {...}
    }
    """
    # Extract error details
    error_text = event.get('error', '')
    component = event.get('component', 'unknown')
    tags = event.get('tags', [])

    # Normalize error text
    norm_error = normalize_error(error_text)
    event['norm_error'] = norm_error

    # Get fingerprint
    error_type = error_text.split(':')[0] if ':' in error_text else 'Unknown'
    fingerprint = get_fingerprint(error_type, component, error_text)
    if fingerprint:
        event['fingerprint'] = fingerprint

    # Add timestamp
    event['ts'] = datetime.utcnow().isoformat() + 'Z'

    # Store in database (assuming agent_errors table exists)
    try:
        with psycopg.connect(**DB_KW) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    insert into public.agent_errors (error, component, tags, norm_error, fingerprint, ts)
                    values (%(error)s, %(component)s, %(tags)s, %(norm_error)s, %(fingerprint)s, %(ts)s)
                """, {
                    'error': error_text,
                    'component': component,
                    'tags': tags,
                    'norm_error': norm_error,
                    'fingerprint': fingerprint,
                    'ts': event['ts']
                })
                conn.commit()
    except Exception as e:
        print(f"Warning: Could not store error in database: {e}")

    return event

# Example FastAPI integration (commented out - uncomment if using FastAPI)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Error Collector")

class ErrorEvent(BaseModel):
    error: str
    component: str
    tags: list[str] = []
    context: dict = {}

@app.post("/ingest")
async def ingest_endpoint(event: ErrorEvent):
    try:
        result = ingest_error(event.dict())
        return {"status": "ok", "fingerprint": result.get('fingerprint')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run with: uvicorn services.collector.main:app --port 8787 --reload
"""

if __name__ == "__main__":
    # Example usage
    test_event = {
        "error": "KeyError: 'partner_id'",
        "component": "odoo.addons.sale",
        "tags": ["odoo", "sale", "error"]
    }

    result = ingest_error(test_event)
    print(f"Ingested: {result}")
