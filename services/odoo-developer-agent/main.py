"""
Odoo Developer Specialist Agent
FastAPI service for Odoo 19.0 module development following OCA standards
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import anthropic
import os
import json
from datetime import datetime

app = FastAPI(
    title="Odoo Developer Agent",
    description="Specialized agent for Odoo 19.0 Enterprise development with OCA compliance",
    version="1.0.0"
)

# CORS middleware for DO AI Agent orchestrator
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to orchestrator URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AgentRequest(BaseModel):
    task: str = Field(..., description="Task description for the Odoo developer agent")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context (agency, odoo_version, etc.)")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for state management")

class AgentResponse(BaseModel):
    result: str = Field(..., description="Agent response with Odoo development guidance")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    actions_taken: List[str] = Field(default_factory=list, description="Actions performed by agent")
    code_artifacts: Optional[List[Dict[str, str]]] = Field(None, description="Generated code files")
    next_steps: Optional[List[str]] = Field(None, description="Recommended next steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class HealthResponse(BaseModel):
    status: str
    agent: str
    version: str
    model: str
    uptime: str

# Load system prompt from SuperClaude framework
ODOO_DEVELOPER_SYSTEM_PROMPT = """You are the odoo_developer specialist agent from the SuperClaude Multi-Agent Framework.

**Core Expertise**:
- Odoo 19.0 Enterprise module development
- OCA (Odoo Community Association) compliance standards
- Python 3.11+ with type hints
- PostgreSQL database modeling
- XML view development (form, tree, kanban, pivot, graph)
- Security (ir.model.access.csv, record rules, RLS)
- Workflow automation (automated actions, server actions)
- API integration (REST, XML-RPC, JSON-RPC)

**Mandatory Standards** (from OCA guidelines):
1. License: AGPL-3.0 only
2. Manifest structure: Complete __manifest__.py with proper metadata
3. Coding style: PEP8, pylint score ≥9.0/10
4. Documentation: README.rst with usage instructions
5. Testing: Unit tests for models, integration tests for workflows
6. Version control: Git with meaningful commit messages
7. Dependencies: Declare all external dependencies in __manifest__.py

**Context**:
- User: Jake Tolentino (Finance SSC Manager, Odoo Developer)
- Agencies: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
- Infrastructure: DigitalOcean (droplet + App Platform), Supabase PostgreSQL
- Odoo Instance: https://erp.insightpulseai.net
- Current Focus: Finance SSC automation, BIR compliance, multi-agency workflows

**Your Role**:
When given a task, you should:
1. Analyze requirements thoroughly
2. Generate OCA-compliant module structure
3. Provide complete, production-ready code (no TODOs or placeholders)
4. Include proper error handling and logging
5. Suggest testing strategies
6. Recommend deployment steps

**Output Format**:
- Provide clear, actionable guidance
- Include code artifacts with file paths
- Explain design decisions
- List next steps for implementation
"""

@app.post("/execute", response_model=AgentResponse)
async def execute_task(
    request: AgentRequest,
    x_orchestrator_key: Optional[str] = Header(None, description="Orchestrator authentication key")
):
    """Execute Odoo development task using Claude API"""

    # Validate orchestrator key (in production)
    # if x_orchestrator_key != os.getenv("ORCHESTRATOR_API_KEY"):
    #     raise HTTPException(status_code=401, detail="Invalid orchestrator key")

    try:
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

        client = anthropic.Anthropic(api_key=api_key)

        # Prepare context-aware prompt
        context_str = json.dumps(request.context, indent=2) if request.context else "None"
        user_prompt = f"""Task: {request.task}

Context:
{context_str}

Please analyze this task and provide OCA-compliant Odoo 19.0 implementation guidance."""

        # Call Claude with specialized system prompt
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",  # Latest model
            max_tokens=8192,
            temperature=0.3,  # More deterministic for code generation
            system=ODOO_DEVELOPER_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        # Extract response
        response_text = message.content[0].text

        # Parse code artifacts if present (look for code blocks)
        code_artifacts = []
        if "```python" in response_text or "```xml" in response_text:
            # Simple extraction - in production, use more robust parsing
            code_artifacts.append({
                "type": "code",
                "language": "python" if "```python" in response_text else "xml",
                "content": "Code artifacts detected - see full response"
            })

        # Build response
        return AgentResponse(
            result=response_text,
            confidence=0.95,  # High confidence for specialized agent
            actions_taken=[
                "analyzed_task",
                "applied_oca_standards",
                "generated_implementation_guidance"
            ],
            code_artifacts=code_artifacts if code_artifacts else None,
            next_steps=[
                "Review generated code for completeness",
                "Create local test environment with `supabase start`",
                "Deploy to staging for integration testing"
            ],
            metadata={
                "agent": "odoo_developer",
                "model": message.model,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
                "cost_usd": calculate_cost(message.usage),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"Anthropic API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        agent="odoo_developer",
        version="1.0.0",
        model="claude-sonnet-4-5-20250929",
        uptime="Managed by DigitalOcean App Platform"
    )

@app.get("/capabilities")
async def get_capabilities():
    """Return agent capabilities for orchestrator discovery"""
    return {
        "agent_name": "odoo_developer",
        "specialization": "Odoo 19.0 Enterprise module development",
        "standards": ["OCA compliance", "AGPL-3.0", "PEP8", "Type hints"],
        "capabilities": [
            "Module scaffolding",
            "Model creation (PostgreSQL ORM)",
            "View development (XML)",
            "Security configuration (RLS, access rules)",
            "Workflow automation",
            "API integration",
            "Testing strategy",
            "Deployment guidance"
        ],
        "triggers": [
            "odoo module",
            "scaffold",
            "model",
            "view",
            "workflow",
            "automation",
            "manifest.py"
        ],
        "context_requirements": {
            "optional": ["agency", "odoo_version", "module_name", "dependencies"]
        }
    }

def calculate_cost(usage) -> float:
    """Calculate approximate API cost"""
    # Claude Sonnet 4.5 pricing (approximate)
    INPUT_COST_PER_1M = 3.00  # USD
    OUTPUT_COST_PER_1M = 15.00  # USD

    input_cost = (usage.input_tokens / 1_000_000) * INPUT_COST_PER_1M
    output_cost = (usage.output_tokens / 1_000_000) * OUTPUT_COST_PER_1M

    return round(input_cost + output_cost, 4)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
