"""
FastAPI application for Superset BI Developer Agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import NLRequest, AgentResult, DatasetCreateRequest, DashboardCreateRequest
from .agent import run_agent
from .superset_client import client

app = FastAPI(
    title="Superset BI Developer Agent",
    description="Natural language → SQL → Superset charts and dashboards",
    version="1.0.0"
)

# CORS for Odoo integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "superset-bi-agent"}

@app.post("/agent/run", response_model=AgentResult)
async def agent_run(req: NLRequest):
    """
    Execute BI agent workflow: NL → SQL → Chart/Dashboard

    Example request:
    ```json
    {
      "query": "Show top 10 expense categories by total amount",
      "dataset_id": 1,
      "create_dashboard": false
    }
    ```
    """
    try:
        return await run_agent(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dataset/create")
async def create_dataset(req: DatasetCreateRequest):
    """
    Create a Superset dataset from an existing database table

    Example request:
    ```json
    {
      "database_id": 1,
      "schema": "public",
      "table_name": "hr_expense"
    }
    ```
    """
    try:
        dataset_id = client.create_physical_dataset(
            database_id=req.database_id,
            schema=req.schema,
            table_name=req.table_name
        )
        return {"dataset_id": dataset_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dashboard/create")
async def create_dashboard(req: DashboardCreateRequest):
    """
    Create a Superset dashboard with multiple charts

    Example request:
    ```json
    {
      "title": "Expense Analytics Dashboard",
      "chart_ids": [1, 2, 3],
      "css": ""
    }
    ```
    """
    try:
        dashboard_id = client.create_dashboard(
            title=req.title,
            chart_ids=req.chart_ids,
            css=req.css
        )
        dashboard_url = f"{client.base_url}/dashboard/p/{dashboard_id}/"
        return {
            "dashboard_id": dashboard_id,
            "dashboard_url": dashboard_url,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets")
async def list_datasets(database_id: int = None, table_name: str = None):
    """List available Superset datasets"""
    try:
        datasets = client.list_datasets(database_id=database_id, table_name=table_name)
        return {"datasets": datasets, "count": len(datasets)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
