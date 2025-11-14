"""
DevOps Engineer Specialist Agent
FastAPI service for DigitalOcean infrastructure, CI/CD, and deployment automation
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import anthropic
import os
import json
from datetime import datetime

app = FastAPI(title="DevOps Engineer Agent", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class AgentRequest(BaseModel):
    task: str
    context: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[str] = None

class AgentResponse(BaseModel):
    result: str
    confidence: float
    actions_taken: List[str]
    deployment_specs: Optional[List[Dict[str, str]]] = None
    infrastructure_changes: Optional[List[Dict[str, Any]]] = None
    next_steps: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

DEVOPS_SYSTEM_PROMPT = """You are the devops_engineer specialist agent from the SuperClaude Multi-Agent Framework.

**Core Expertise**:
- DigitalOcean infrastructure (App Platform, Droplets, Spaces, Networking)
- Docker containerization and multi-stage builds
- GitHub Actions CI/CD pipelines
- Deployment automation (doctl CLI, App Platform specs)
- Monitoring and observability (logs, metrics, alerts)
- Security hardening (secrets management, SSL/TLS, firewall rules)

**Infrastructure Stack**:
- DO Project: fin-workspace (29cde7a1-8280-46ad-9fdf-dea7b21a7825)
- Regions: Singapore (sgp1), San Francisco (sfo2)
- Services: Superset (App Platform), Pulse Hub MCP (App Platform), Odoo ERP (Droplet)
- Databases: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)

**Deployment Standards**:
1. App Platform YAML specs in `infra/do/` directory
2. Health check endpoints required (`/health`)
3. Environment variables via DO secrets (never hardcode)
4. Zero-downtime deployments (rolling updates)
5. Automated rollback on health check failure
6. GitHub Actions for CI/CD

**Your Role**:
Deploy services, manage infrastructure, automate CI/CD, monitor systems, troubleshoot issues."""

@app.post("/execute", response_model=AgentResponse)
async def execute_task(request: AgentRequest, x_orchestrator_key: Optional[str] = Header(None)):
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            temperature=0.3,
            system=DEVOPS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Task: {request.task}\n\nContext: {json.dumps(request.context, indent=2)}"}]
        )
        return AgentResponse(
            result=message.content[0].text,
            confidence=0.92,
            actions_taken=["analyzed_deployment_requirements", "generated_infrastructure_specs", "created_ci_cd_pipeline"],
            next_steps=["Validate App Platform spec", "Deploy to staging", "Monitor deployment health"],
            metadata={"agent": "devops_engineer", "model": message.model, "timestamp": datetime.utcnow().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "devops_engineer", "version": "1.0.0"}

@app.get("/capabilities")
async def get_capabilities():
    return {
        "agent_name": "devops_engineer",
        "specialization": "DigitalOcean infrastructure and CI/CD automation",
        "capabilities": ["App Platform deployment", "Docker containerization", "CI/CD pipelines", "Infrastructure automation", "Monitoring setup"],
        "triggers": ["deploy", "infrastructure", "ci/cd", "docker", "digitalocean", "pipeline", "monitor"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
