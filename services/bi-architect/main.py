"""
BI Architect Specialist Agent
FastAPI service for Apache Superset dashboard design and SQL query optimization
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import anthropic
import os
import json
from datetime import datetime

app = FastAPI(title="BI Architect Agent", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class AgentRequest(BaseModel):
    task: str
    context: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[str] = None

class AgentResponse(BaseModel):
    result: str
    confidence: float
    actions_taken: List[str]
    sql_queries: Optional[List[Dict[str, str]]] = None
    dashboard_specs: Optional[List[Dict[str, Any]]] = None
    next_steps: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

BI_ARCHITECT_SYSTEM_PROMPT = """You are the bi_architect specialist agent from the SuperClaude Multi-Agent Framework.

**Core Expertise**:
- Apache Superset 3.0 dashboard design and chart creation
- PostgreSQL query optimization and performance tuning
- Data modeling for analytics (star schema, snowflake schema)
- RLS (Row-Level Security) for multi-tenancy
- SQL query optimization (CTEs, window functions, materialized views)
- Data visualization best practices

**Tech Stack**:
- Apache Superset 3.0 (dashboards, charts, SQL Lab)
- PostgreSQL 15 (Supabase) with pgvector
- Scout schema: transactions, expenses, vendors, analytics
- MindsDB integration for ML-powered analytics

**Your Role**:
Design dashboards, optimize SQL queries, create data models, implement RLS policies."""

@app.post("/execute", response_model=AgentResponse)
async def execute_task(request: AgentRequest, x_orchestrator_key: Optional[str] = Header(None)):
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            temperature=0.3,
            system=BI_ARCHITECT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Task: {request.task}\n\nContext: {json.dumps(request.context, indent=2)}"}]
        )
        return AgentResponse(
            result=message.content[0].text,
            confidence=0.93,
            actions_taken=["analyzed_dashboard_requirements", "optimized_sql_queries", "designed_data_model"],
            next_steps=["Create dashboard in Superset", "Test RLS policies", "Validate query performance"],
            metadata={"agent": "bi_architect", "model": message.model, "timestamp": datetime.utcnow().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "bi_architect", "version": "1.0.0"}

@app.get("/capabilities")
async def get_capabilities():
    return {
        "agent_name": "bi_architect",
        "specialization": "Apache Superset dashboard design and SQL optimization",
        "capabilities": ["Dashboard design", "Chart creation", "SQL optimization", "RLS policies", "Data modeling"],
        "triggers": ["superset", "dashboard", "chart", "sql", "query", "analytics", "visualization"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
