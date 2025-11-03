"""
Skill Hub - Unified API for Claude Skills + Odoo Integration
FastAPI server providing access to MCP servers, SuperClaude skills, and Odoo/Superset actions
"""
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
import os
from datetime import datetime
import asyncio

from odoo_bridge import OdooRPCClient, SupersetClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Skill Hub API",
    description="Unified API for Claude Skills, Odoo, and Superset integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chat.openai.com",
        "https://assistant.openai.com",
        os.getenv("CORS_ORIGIN", "")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration from environment
ODOO_URL = os.getenv("ODOO_URL", "https://erp.insightpulseai.net")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "")
SUPERSET_URL = os.getenv("SUPERSET_URL", "https://insightpulseai.net/superset")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME", "")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD", "")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

# Initialize clients (lazy initialization)
_odoo_client: Optional[OdooRPCClient] = None
_superset_client: Optional[SupersetClient] = None


def get_odoo_client() -> OdooRPCClient:
    """Get or create Odoo client singleton"""
    global _odoo_client
    if _odoo_client is None:
        _odoo_client = OdooRPCClient(
            url=ODOO_URL,
            db=ODOO_DB,
            username=ODOO_USERNAME,
            password=ODOO_PASSWORD,
            protocol="xmlrpc"
        )
        _odoo_client.authenticate()
    return _odoo_client


def get_superset_client() -> SupersetClient:
    """Get or create Superset client singleton"""
    global _superset_client
    if _superset_client is None:
        _superset_client = SupersetClient(
            url=SUPERSET_URL,
            username=SUPERSET_USERNAME,
            password=SUPERSET_PASSWORD
        )
        _superset_client.login()
    return _superset_client


# Authentication
async def verify_token(authorization: str = Header(...)):
    """Verify bearer token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")
    if token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return token


# Pydantic models
class OdooAction(BaseModel):
    """Request model for Odoo actions"""
    model: str = Field(..., description="Odoo model name (e.g., 'res.partner')")
    method: str = Field(..., description="Method name (e.g., 'search_read', 'create')")
    args: List[Any] = Field(default_factory=list, description="Positional arguments")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "crm.lead",
                "method": "create",
                "args": [{
                    "name": "New Opportunity",
                    "partner_name": "Acme Corp",
                    "email_from": "contact@acme.com",
                    "type": "opportunity"
                }],
                "kwargs": {}
            }
        }


class SupersetQuery(BaseModel):
    """Request model for Superset queries"""
    action: str = Field(..., description="Action type: 'dashboards', 'charts', 'execute_sql'")
    dashboard_id: Optional[int] = Field(None, description="Dashboard ID (for dashboard actions)")
    chart_id: Optional[int] = Field(None, description="Chart ID (for chart actions)")
    database_id: Optional[int] = Field(None, description="Database ID (for SQL execution)")
    sql: Optional[str] = Field(None, description="SQL query to execute")
    schema: Optional[str] = Field(None, description="Database schema")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "dashboards"
            }
        }


# Health check
@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "skill-hub",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "integrations": {
            "odoo": {"url": ODOO_URL, "configured": bool(ODOO_USERNAME)},
            "superset": {"url": SUPERSET_URL, "configured": bool(SUPERSET_USERNAME)}
        }
    }


# Skills catalog
@app.get("/skills/catalog", tags=["Skills"])
async def get_skills_catalog(token: str = Depends(verify_token)):
    """
    Get unified catalog of all available skills

    Returns:
        Catalog of Skills including Odoo actions, Superset queries, and Claude Skills
    """
    return {
        "total_skills": 43,
        "categories": {
            "odoo_integration": {
                "skills": [
                    {
                        "name": "odoo-create-lead",
                        "description": "Create a new CRM lead/opportunity in Odoo",
                        "parameters": ["name", "partner_name", "email", "phone", "expected_revenue"]
                    },
                    {
                        "name": "odoo-search-partners",
                        "description": "Search for partners/customers in Odoo",
                        "parameters": ["domain", "fields", "limit"]
                    },
                    {
                        "name": "odoo-create-task",
                        "description": "Create a project task in Odoo",
                        "parameters": ["name", "project_id", "user_id", "description", "deadline"]
                    },
                    {
                        "name": "odoo-list-sales-orders",
                        "description": "List sales orders with filtering",
                        "parameters": ["state", "partner_id", "date_from", "date_to", "limit"]
                    }
                ]
            },
            "superset_analytics": {
                "skills": [
                    {
                        "name": "superset-list-dashboards",
                        "description": "List all Superset dashboards",
                        "parameters": []
                    },
                    {
                        "name": "superset-get-dashboard",
                        "description": "Get specific dashboard details",
                        "parameters": ["dashboard_id"]
                    },
                    {
                        "name": "superset-query-data",
                        "description": "Execute SQL query in Superset",
                        "parameters": ["database_id", "sql", "schema"]
                    },
                    {
                        "name": "superset-get-chart-data",
                        "description": "Get data from a specific chart",
                        "parameters": ["chart_id", "force_refresh"]
                    }
                ]
            },
            "odoo_skills": {
                "count": 6,
                "skills": ["odoo19-oca-devops", "odoo-agile-scrum-devops", "odoo-app-automator-final",
                          "odoo-finance-automation", "odoo-knowledge-agent", "bir-tax-filing"]
            },
            "superset_skills": {
                "count": 4,
                "skills": ["superset-chart-builder", "superset-dashboard-automation",
                          "superset-dashboard-designer", "superset-sql-developer"]
            },
            "integration_skills": {
                "count": 5,
                "skills": ["firecrawl-data-extraction", "insightpulse_connection_manager",
                          "mcp-complete-guide", "multi-agency-orchestrator", "supabase-rpc-manager"]
            },
            "utilities": {
                "count": 6,
                "skills": ["drawio-diagrams-enhanced", "librarian-indexer", "notion-workflow-sync",
                          "paddle-ocr-validation", "reddit-product-viability", "travel-expense-management"]
            },
            "document_processing": {
                "count": 4,
                "skills": ["pdf", "docx", "xlsx", "pptx"]
            },
            "notion_integration": {
                "count": 4,
                "skills": ["notion-meeting-intelligence", "notion-knowledge-capture",
                          "notion-research-documentation", "notion-spec-to-implementation"]
            },
            "anthropic_official": {
                "count": 11,
                "skills": ["algorithmic-art", "artifacts-builder", "brand-guidelines",
                          "canvas-design", "internal-comms", "mcp-builder", "skill-creator",
                          "slack-gif-creator", "template-skill", "theme-factory", "webapp-testing"]
            }
        },
        "documentation": "https://github.com/jgtolentino/insightpulse-odoo/blob/main/docs/CLAUDE_CODE_WEB_SKILLS_SETUP.md"
    }


# Odoo integration endpoints
@app.post("/odoo/execute", tags=["Odoo"])
async def execute_odoo_action(
    action: OdooAction,
    token: str = Depends(verify_token)
):
    """
    Execute Odoo model method via XML-RPC

    Args:
        action: Odoo action specification

    Returns:
        Result from Odoo method execution

    Examples:
        # Create a lead
        POST /odoo/execute
        {
            "model": "crm.lead",
            "method": "create",
            "args": [{
                "name": "New Opportunity",
                "partner_name": "Acme Corp"
            }]
        }

        # Search partners
        POST /odoo/execute
        {
            "model": "res.partner",
            "method": "search_read",
            "args": [[("is_company", "=", true)]],
            "kwargs": {"fields": ["name", "email"], "limit": 10}
        }
    """
    try:
        client = get_odoo_client()
        result = client.execute_kw(
            action.model,
            action.method,
            action.args,
            action.kwargs
        )

        return {
            "success": True,
            "result": result,
            "model": action.model,
            "method": action.method,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Odoo execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/odoo/version", tags=["Odoo"])
async def get_odoo_version(token: str = Depends(verify_token)):
    """Get Odoo version information"""
    try:
        client = get_odoo_client()
        version = client.get_version()
        return {
            "success": True,
            "version": version,
            "url": ODOO_URL
        }
    except Exception as e:
        logger.error(f"Error getting Odoo version: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Superset integration endpoints
@app.post("/superset/query", tags=["Superset"])
async def execute_superset_query(
    query: SupersetQuery,
    token: str = Depends(verify_token)
):
    """
    Execute Superset query or retrieve dashboard/chart data

    Args:
        query: Superset query specification

    Returns:
        Result from Superset API

    Examples:
        # List dashboards
        POST /superset/query
        {"action": "dashboards"}

        # Get dashboard
        POST /superset/query
        {"action": "dashboard", "dashboard_id": 1}

        # Execute SQL
        POST /superset/query
        {
            "action": "execute_sql",
            "database_id": 1,
            "sql": "SELECT * FROM sales_orders LIMIT 10"
        }
    """
    try:
        client = get_superset_client()

        if query.action == "dashboards":
            result = client.get_dashboards()
        elif query.action == "dashboard":
            if not query.dashboard_id:
                raise HTTPException(status_code=400, detail="dashboard_id required")
            result = client.get_dashboard(query.dashboard_id)
        elif query.action == "charts":
            result = client.get_charts()
        elif query.action == "chart_data":
            if not query.chart_id:
                raise HTTPException(status_code=400, detail="chart_id required")
            result = client.get_chart_data(query.chart_id)
        elif query.action == "execute_sql":
            if not query.database_id or not query.sql:
                raise HTTPException(
                    status_code=400,
                    detail="database_id and sql required"
                )
            result = client.execute_sql(
                query.database_id,
                query.sql,
                query.schema
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {query.action}")

        return {
            "success": True,
            "result": result,
            "action": query.action,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Superset query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
