#!/usr/bin/env python3
"""
Natural Language Analytics API
Draxlr-style AI-powered SQL dashboard & analytics

Features (from Draxlr):
- Plain English → SQL → Charts → Dashboards
- No-code data visualization
- Automated alerts (Email/Slack)
- Supports 10+ SQL databases
- Embeddable analytics for SaaS apps

Architecture:
1. FastAPI REST API for natural language analytics
2. Text-to-SQL agent (SmolLM2) for query generation
3. Superset integration for chart/dashboard rendering
4. Webhook alerts for data changes
5. Embeddable iframe widgets

Cost Comparison:
- Draxlr: $49/month (Starter plan)
- InsightPulse: $0 (self-hosted) + $0.0001/query
- Savings: ~$588/year

Usage:
    # Start API server
    python natural_language_analytics_api.py

    # Test endpoints
    curl -X POST http://localhost:8000/api/v1/analytics/ask \
      -H "Content-Type: application/json" \
      -d '{"question": "Show me total expenses by agency for Q4 2024"}'

    curl -X POST http://localhost:8000/api/v1/analytics/dashboard \
      -H "Content-Type: application/json" \
      -d '{"name": "Finance Dashboard", "questions": ["Total revenue", "Top customers"]}'
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

from text_to_sql_agent import TextToSQLAgent
from superset_langchain_agent import SupersetLangChainAgent, SupersetConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Natural Language Analytics API",
    description="Draxlr-style AI-powered SQL analytics with SmolLM2",
    version="1.0.0"
)

# CORS for embeddable widgets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

class AskRequest(BaseModel):
    """Natural language analytics question"""
    question: str = Field(..., description="Natural language question")
    execute: bool = Field(True, description="Execute the query")
    create_chart: bool = Field(False, description="Create Superset chart")
    viz_type: str = Field("table", description="Chart type: table, bar, line, pie")


class AskResponse(BaseModel):
    """Analytics response"""
    question: str
    sql: str
    confidence: float
    results: Optional[Dict] = None
    chart_id: Optional[int] = None
    chart_url: Optional[str] = None


class DashboardRequest(BaseModel):
    """Dashboard creation request"""
    name: str = Field(..., description="Dashboard name")
    questions: List[str] = Field(..., description="List of questions for charts")
    viz_types: Optional[List[str]] = Field(None, description="Chart types for each question")
    description: Optional[str] = Field(None, description="Dashboard description")


class DashboardResponse(BaseModel):
    """Dashboard creation response"""
    dashboard_id: int
    dashboard_url: str
    charts: List[Dict]


class AlertRequest(BaseModel):
    """Data alert configuration"""
    name: str = Field(..., description="Alert name")
    question: str = Field(..., description="SQL query as natural language")
    condition: str = Field(..., description="Alert condition: threshold, change, schedule")
    threshold: Optional[float] = Field(None, description="Numeric threshold for alerts")
    notify_email: Optional[str] = Field(None, description="Email for notifications")
    notify_slack: Optional[str] = Field(None, description="Slack webhook URL")
    schedule: Optional[str] = Field("daily", description="Alert schedule: hourly, daily, weekly")


# ============================================================================
# Dependencies
# ============================================================================

def get_text_to_sql_agent():
    """Dependency: Text-to-SQL agent"""
    return TextToSQLAgent(
        database_url=os.getenv("POSTGRES_URL"),
        device="cpu"
    )


def get_superset_agent():
    """Dependency: Superset LangChain agent"""
    config = SupersetConfig(
        base_url=os.getenv("SUPERSET_URL", "http://localhost:8088"),
        username=os.getenv("SUPERSET_USERNAME", "admin"),
        password=os.getenv("SUPERSET_PASSWORD", "admin"),
        database_id=int(os.getenv("SUPERSET_DATABASE_ID", "1"))
    )
    return SupersetLangChainAgent(config)


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
def root():
    """API documentation"""
    return {
        "name": "Natural Language Analytics API",
        "version": "1.0.0",
        "description": "Draxlr-style AI-powered SQL analytics",
        "endpoints": {
            "ask": "POST /api/v1/analytics/ask",
            "dashboard": "POST /api/v1/analytics/dashboard",
            "alert": "POST /api/v1/analytics/alert",
            "embed": "GET /api/v1/analytics/embed/{chart_id}"
        },
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/v1/analytics/ask", response_model=AskResponse)
async def ask_analytics_question(
    request: AskRequest,
    text_to_sql: TextToSQLAgent = Depends(get_text_to_sql_agent),
    superset: SupersetLangChainAgent = Depends(get_superset_agent)
):
    """
    Convert natural language to SQL, execute, and optionally create chart

    Example:
        POST /api/v1/analytics/ask
        {
            "question": "Show me total expenses by agency for Q4 2024",
            "create_chart": true,
            "viz_type": "bar"
        }
    """
    logger.info(f"Processing question: {request.question}")

    try:
        if request.create_chart:
            # Use Superset agent for chart creation
            result = superset.ask(
                question=request.question,
                create_chart=True,
                viz_type=request.viz_type
            )
        else:
            # Use text-to-SQL agent only
            result = text_to_sql.ask(
                question=request.question,
                execute=request.execute
            )

        return AskResponse(**result)

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analytics/dashboard", response_model=DashboardResponse)
async def create_analytics_dashboard(
    request: DashboardRequest,
    superset: SupersetLangChainAgent = Depends(get_superset_agent)
):
    """
    Create multi-chart dashboard from list of questions

    Example:
        POST /api/v1/analytics/dashboard
        {
            "name": "Finance Dashboard",
            "questions": [
                "Total expenses by agency",
                "Withholding tax trends over 6 months",
                "Top 10 vendors by payment amount"
            ],
            "viz_types": ["bar", "line", "table"]
        }
    """
    logger.info(f"Creating dashboard: {request.name}")

    try:
        result = superset.create_dashboard_from_questions(
            dashboard_name=request.name,
            questions=request.questions,
            viz_types=request.viz_types
        )

        return DashboardResponse(**result)

    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analytics/alert")
async def create_alert(
    request: AlertRequest,
    background_tasks: BackgroundTasks
):
    """
    Create automated data alert

    Draxlr feature: Alert when data changes, crosses threshold, or on schedule

    Example:
        POST /api/v1/analytics/alert
        {
            "name": "High Expenses Alert",
            "question": "Total expenses this month",
            "condition": "threshold",
            "threshold": 1000000,
            "notify_email": "finance@example.com",
            "schedule": "daily"
        }
    """
    logger.info(f"Creating alert: {request.name}")

    # Placeholder: implement alert scheduling
    # Use background tasks with APScheduler or Celery

    alert_id = 123  # Placeholder

    return {
        "alert_id": alert_id,
        "name": request.name,
        "status": "active",
        "next_check": "2024-01-01T00:00:00Z"
    }


@app.get("/api/v1/analytics/embed/{chart_id}")
async def embed_chart(chart_id: int):
    """
    Get embeddable HTML for chart

    Draxlr feature: Embed analytics in your app

    Returns:
        HTML iframe for embedding
    """
    superset_url = os.getenv("SUPERSET_URL", "http://localhost:8088")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Embedded Chart</title>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; }}
            iframe {{ border: 0; width: 100%; height: 100vh; }}
        </style>
    </head>
    <body>
        <iframe src="{superset_url}/explore/?form_data=%7B%22slice_id%22%3A{chart_id}%7D&standalone=3"></iframe>
    </body>
    </html>
    """

    return HTMLResponse(content=html)


@app.get("/api/v1/analytics/datasets")
async def list_datasets(superset: SupersetLangChainAgent = Depends(get_superset_agent)):
    """
    List available datasets (semantic layer)

    Returns:
        List of published Superset datasets
    """
    try:
        datasets = superset.superset.list_datasets()

        return {
            "count": len(datasets),
            "datasets": [
                {
                    "id": ds["id"],
                    "name": ds["table_name"],
                    "database": ds.get("database", {}).get("database_name"),
                    "schema": ds.get("schema")
                }
                for ds in datasets
            ]
        }
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analytics/sql")
async def execute_raw_sql(
    sql: str,
    text_to_sql: TextToSQLAgent = Depends(get_text_to_sql_agent)
):
    """
    Execute raw SQL query (for advanced users)

    Draxlr feature: Custom SQL editor
    """
    logger.info(f"Executing raw SQL: {sql[:100]}...")

    try:
        result = text_to_sql.execute_sql(sql, validate=True)

        return {
            "success": result["success"],
            "rows": result.get("rows", []),
            "row_count": result.get("row_count", 0),
            "error": result.get("error")
        }
    except Exception as e:
        logger.error(f"Error executing SQL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Background Tasks (Alerts)
# ============================================================================

async def check_alert(alert_id: int, question: str, condition: str, threshold: float):
    """
    Background task: Check alert condition and send notifications

    Runs on schedule (hourly, daily, weekly)
    """
    # Generate SQL from question
    agent = TextToSQLAgent()
    result = agent.ask(question, execute=True)

    if not result["results"]["success"]:
        logger.error(f"Alert {alert_id} failed: {result['results']['error']}")
        return

    # Check condition
    rows = result["results"]["rows"]
    if not rows:
        return

    # Extract numeric value (assumes first row, first column)
    value = list(rows[0].values())[0]

    if condition == "threshold" and value > threshold:
        # Send notification
        logger.info(f"Alert {alert_id} triggered: {value} > {threshold}")
        # TODO: Send email/Slack notification


# ============================================================================
# Main
# ============================================================================

def main():
    """Start API server"""
    port = int(os.getenv("API_PORT", "8000"))

    logger.info("=" * 80)
    logger.info("Natural Language Analytics API")
    logger.info("=" * 80)
    logger.info(f"Starting server on port {port}")
    logger.info(f"Superset: {os.getenv('SUPERSET_URL', 'http://localhost:8088')}")
    logger.info(f"Database: {os.getenv('POSTGRES_URL', 'Not configured')}")
    logger.info("")
    logger.info("API Documentation: http://localhost:{port}/docs")
    logger.info("=" * 80)

    uvicorn.run(
        "natural_language_analytics_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
