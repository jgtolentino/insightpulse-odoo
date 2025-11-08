"""
AI Gateway - Unified MCP + REST API Server
Exposes FinServ operations to Claude Desktop (MCP), ChatGPT Custom GPTs (REST), and Claude Web (REST).
"""

import os
import json
import hmac
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Import MCP servers
from mcp_servers.finserv_odoo import FinServOdooMCP
from mcp_servers.finserv_close import FinServCloseMCP
from mcp_servers.finserv_policy import FinServPolicyMCP

app = FastAPI(
    title="InsightPulse AI Gateway",
    description="Unified MCP and REST API for FinServ operations",
    version="1.0.0"
)

# CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://claude.ai", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP servers
odoo_mcp = FinServOdooMCP()
close_mcp = FinServCloseMCP()
policy_mcp = FinServPolicyMCP()

# API key store (in production, use a database or secret manager)
API_KEYS = {
    os.getenv("API_KEY_CHATGPT"): "chatgpt",
    os.getenv("API_KEY_CLAUDE"): "claude",
    os.getenv("API_KEY_INTERNAL"): "internal"
}

# ============================================================================
# Authentication
# ============================================================================

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key and return client type."""
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return API_KEYS[x_api_key]


# ============================================================================
# MCP Protocol (for Claude Desktop)
# ============================================================================

class MCPRequest(BaseModel):
    """MCP JSON-RPC request."""
    method: str
    params: Dict[str, Any] = {}


@app.post("/mcp/odoo")
async def mcp_odoo_endpoint(req: MCPRequest):
    """MCP endpoint for Odoo operations."""
    if req.method == "tools/list":
        return {"tools": await odoo_mcp.get_tools()}

    elif req.method == "tools/call":
        tool_name = req.params.get("name")
        arguments = req.params.get("arguments", {})
        result = await odoo_mcp.call_tool(tool_name, arguments)
        return result

    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {req.method}")


@app.post("/mcp/close")
async def mcp_close_endpoint(req: MCPRequest):
    """MCP endpoint for Close operations."""
    if req.method == "tools/list":
        return {"tools": await close_mcp.get_tools()}

    elif req.method == "tools/call":
        tool_name = req.params.get("name")
        arguments = req.params.get("arguments", {})
        result = await close_mcp.call_tool(tool_name, arguments)
        return result

    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {req.method}")


@app.post("/mcp/policy")
async def mcp_policy_endpoint(req: MCPRequest):
    """MCP endpoint for Policy QA."""
    if req.method == "tools/list":
        return {"tools": await policy_mcp.get_tools()}

    elif req.method == "tools/call":
        tool_name = req.params.get("name")
        arguments = req.params.get("arguments", {})
        result = await policy_mcp.call_tool(tool_name, arguments)
        return result

    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {req.method}")


# ============================================================================
# REST API (for ChatGPT Custom GPT and Claude Web)
# ============================================================================

# --- Odoo Operations ---

@app.get("/api/sale-orders/{order_ref}")
async def api_get_sale_order(order_ref: str, client: str = Depends(verify_api_key)):
    """Get sale order details (REST endpoint)."""
    result = await odoo_mcp.call_tool("odoo_get_sale_order", {"order_ref": order_ref})
    return result


@app.get("/api/expenses")
async def api_list_expenses(
    employee_id: Optional[int] = None,
    state: Optional[str] = None,
    agency_code: Optional[str] = None,
    limit: int = 10,
    client: str = Depends(verify_api_key)
):
    """List expenses with filters."""
    args = {"limit": limit}
    if employee_id:
        args["employee_id"] = employee_id
    if state:
        args["state"] = state
    if agency_code:
        args["agency_code"] = agency_code

    result = await odoo_mcp.call_tool("odoo_list_expenses", args)
    return result


@app.get("/api/expenses/{expense_ref}")
async def api_get_expense(expense_ref: str, client: str = Depends(verify_api_key)):
    """Get expense details."""
    result = await odoo_mcp.call_tool("odoo_get_expense", {"expense_ref": expense_ref})
    return result


@app.post("/api/tasks")
async def api_create_task(
    request: Request,
    client: str = Depends(verify_api_key)
):
    """Create a new task in Odoo."""
    body = await request.json()
    result = await odoo_mcp.call_tool("odoo_create_task", body)
    return result


@app.get("/api/invoices")
async def api_list_invoices(
    partner_id: Optional[int] = None,
    state: Optional[str] = None,
    invoice_type: Optional[str] = None,
    overdue: Optional[bool] = None,
    limit: int = 20,
    client: str = Depends(verify_api_key)
):
    """List invoices with filters."""
    args = {"limit": limit}
    if partner_id:
        args["partner_id"] = partner_id
    if state:
        args["state"] = state
    if invoice_type:
        args["invoice_type"] = invoice_type
    if overdue is not None:
        args["overdue"] = overdue

    result = await odoo_mcp.call_tool("odoo_get_invoices", args)
    return result


# --- Close Operations ---

@app.get("/api/close/status")
async def api_close_status(
    entity_code: Optional[str] = None,
    period: Optional[str] = None,
    client: str = Depends(verify_api_key)
):
    """Get month-end close status."""
    args = {}
    if entity_code:
        args["entity_code"] = entity_code
    if period:
        args["period"] = period

    result = await close_mcp.call_tool("close_get_status", args)
    return result


@app.get("/api/close/checklist")
async def api_close_checklist(
    entity_code: str,
    period: str,
    client: str = Depends(verify_api_key)
):
    """Get close checklist for entity/period."""
    result = await close_mcp.call_tool("close_get_checklist", {
        "entity_code": entity_code,
        "period": period
    })
    return result


@app.post("/api/close/tasks/{task_id}/complete")
async def api_complete_close_task(
    task_id: int,
    request: Request,
    client: str = Depends(verify_api_key)
):
    """Mark close task as complete."""
    body = await request.json()
    result = await close_mcp.call_tool("close_mark_task_complete", {
        "task_id": task_id,
        "notes": body.get("notes", "")
    })
    return result


@app.get("/api/close/exceptions")
async def api_close_exceptions(
    entity_code: Optional[str] = None,
    severity: Optional[str] = None,
    client: str = Depends(verify_api_key)
):
    """Get open close exceptions."""
    args = {}
    if entity_code:
        args["entity_code"] = entity_code
    if severity:
        args["severity"] = severity

    result = await close_mcp.call_tool("close_get_exceptions", args)
    return result


@app.get("/api/close/metrics")
async def api_close_metrics(
    entity_code: Optional[str] = None,
    last_n_periods: int = 6,
    client: str = Depends(verify_api_key)
):
    """Get close cycle metrics."""
    args = {"last_n_periods": last_n_periods}
    if entity_code:
        args["entity_code"] = entity_code

    result = await close_mcp.call_tool("close_get_metrics", args)
    return result


# --- Policy QA ---

@app.post("/api/policy/qa")
async def api_policy_qa(
    request: Request,
    client: str = Depends(verify_api_key)
):
    """Ask a question about policies/SOPs."""
    body = await request.json()
    result = await policy_mcp.call_tool("policy_qa", body)
    return result


@app.post("/api/policy/search")
async def api_policy_search(
    request: Request,
    client: str = Depends(verify_api_key)
):
    """Search policy documents."""
    body = await request.json()
    result = await policy_mcp.call_tool("policy_search", body)
    return result


@app.get("/api/policy/documents/{doc_id}")
async def api_policy_document(
    doc_id: str,
    client: str = Depends(verify_api_key)
):
    """Get full policy document."""
    result = await policy_mcp.call_tool("policy_get_document", {"doc_id": doc_id})
    return result


@app.get("/api/policy/categories")
async def api_policy_categories(client: str = Depends(verify_api_key)):
    """List policy categories."""
    result = await policy_mcp.call_tool("policy_list_categories", {})
    return result


# ============================================================================
# OpenAPI Schema (for ChatGPT Custom GPT)
# ============================================================================

@app.get("/.well-known/openapi.yaml")
async def openapi_yaml():
    """Serve OpenAPI spec for ChatGPT Custom GPT configuration."""
    # Return the OpenAPI schema (ChatGPT needs this at a well-known path)
    return JSONResponse(content=app.openapi())


# ============================================================================
# Health & Info
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai-gateway",
        "version": "1.0.0",
        "endpoints": {
            "mcp": ["/mcp/odoo", "/mcp/close", "/mcp/policy"],
            "rest": ["/api/close/status", "/api/policy/qa", "/api/expenses"]
        }
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "InsightPulse AI Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/.well-known/openapi.yaml",
        "mcp_endpoints": {
            "odoo": "/mcp/odoo",
            "close": "/mcp/close",
            "policy": "/mcp/policy"
        },
        "rest_api": {
            "base": "/api",
            "docs": "/docs",
            "authentication": "X-API-Key header required"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
