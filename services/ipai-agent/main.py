"""
InsightPulse AI Agent Orchestrator
FastAPI service that coordinates LLM-powered workflows with Odoo
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import logging
from datetime import datetime

from agents.meeting_to_prd import MeetingToPRDAgent
from tools.odoo_client import OdooClient
from tools.slack_client import SlackClient
from memory.kv_store import MemoryKVStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="InsightPulse AI Agent",
    description="Odoo Studio × Notion Agent - Hybrid orchestration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
odoo = OdooClient()
slack = SlackClient()
memory = MemoryKVStore(odoo_client=odoo)

# Initialize agents
meeting_prd_agent = MeetingToPRDAgent(
    odoo_client=odoo,
    slack_client=slack,
    memory_store=memory
)


# Request/Response Models
class MeetingToPRDRequest(BaseModel):
    meeting_id: int
    calendar_event_id: Optional[int] = None
    attendee_emails: List[str] = []
    summary: Optional[str] = None
    user_id: Optional[int] = None


class AgentRunResponse(BaseModel):
    run_id: int
    status: str
    message: str
    page_id: Optional[int] = None
    task_ids: List[int] = []


class GenericAgentRequest(BaseModel):
    agent_slug: str
    input_data: Dict[str, Any]
    user_id: Optional[int] = None


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ipai-agent",
        "timestamp": datetime.utcnow().isoformat(),
        "odoo_connected": odoo.test_connection(),
        "slack_connected": slack.test_connection()
    }


# Agent Endpoints
@app.post("/agent/meeting-to-prd", response_model=AgentRunResponse)
async def run_meeting_to_prd(
    request: MeetingToPRDRequest,
    background_tasks: BackgroundTasks
):
    """
    Process a meeting and generate PRD + tasks

    Workflow:
    1. Fetch meeting details from Odoo
    2. Generate PRD using LLM + team memory
    3. Create ip.page record
    4. Extract tasks → project.task
    5. Post Slack summary
    """
    try:
        logger.info(f"Starting Meeting→PRD workflow for meeting {request.meeting_id}")

        # Create agent run record
        run_id = odoo.create_agent_run(
            agent_slug="meeting-to-prd",
            status="running",
            input_data={
                "meeting_id": request.meeting_id,
                "attendee_emails": request.attendee_emails
            }
        )

        # Execute workflow in background
        background_tasks.add_task(
            meeting_prd_agent.execute,
            meeting_id=request.meeting_id,
            run_id=run_id,
            user_id=request.user_id
        )

        return AgentRunResponse(
            run_id=run_id,
            status="running",
            message="PRD generation started. Check agent run for status."
        )

    except Exception as e:
        logger.error(f"Error in meeting-to-prd: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/execute", response_model=AgentRunResponse)
async def execute_generic_agent(
    request: GenericAgentRequest,
    background_tasks: BackgroundTasks
):
    """Generic agent execution endpoint"""
    try:
        # Map agent slug to handler
        agents = {
            "meeting-to-prd": meeting_prd_agent,
            # Add more agents here
        }

        if request.agent_slug not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{request.agent_slug}' not found"
            )

        # Create run record
        run_id = odoo.create_agent_run(
            agent_slug=request.agent_slug,
            status="running",
            input_data=request.input_data
        )

        # Execute agent
        agent = agents[request.agent_slug]
        background_tasks.add_task(
            agent.execute,
            run_id=run_id,
            user_id=request.user_id,
            **request.input_data
        )

        return AgentRunResponse(
            run_id=run_id,
            status="running",
            message=f"Agent '{request.agent_slug}' started"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Memory Endpoints
@app.get("/memory/{scope}/{key}")
async def get_memory(scope: str, key: str, owner_id: Optional[int] = None):
    """Get memory value"""
    try:
        value = memory.get(scope=scope, key=key, owner_id=owner_id)
        if value is None:
            raise HTTPException(status_code=404, detail="Memory key not found")
        return {"key": key, "value": value}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/{scope}/{key}")
async def set_memory(
    scope: str,
    key: str,
    value: Dict[str, Any],
    owner_id: Optional[int] = None
):
    """Set memory value"""
    try:
        memory.set(scope=scope, key=key, value=value, owner_id=owner_id)
        return {"message": "Memory updated", "key": key}
    except Exception as e:
        logger.error(f"Error setting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Webhook Endpoints (for external triggers)
@app.post("/webhook/calendar/event-ended")
async def calendar_event_ended(
    event_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Triggered when calendar event ends (via pg_cron or Odoo webhook)

    Automatically starts Meeting→PRD workflow
    """
    try:
        meeting_id = event_data.get("meeting_id")
        if not meeting_id:
            raise HTTPException(status_code=400, detail="meeting_id required")

        # Start Meeting→PRD workflow
        request = MeetingToPRDRequest(
            meeting_id=meeting_id,
            attendee_emails=event_data.get("attendee_emails", []),
            summary=event_data.get("summary")
        )

        return await run_meeting_to_prd(request, background_tasks)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in calendar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/slack/command")
async def slack_command(command_data: Dict[str, Any]):
    """
    Handle Slack slash commands

    Examples:
    - /ipai prd from meeting "Project Kickoff"
    - /ipai tasks for page 123
    """
    try:
        command = command_data.get("command")
        text = command_data.get("text", "")
        user_id = command_data.get("user_id")

        # Parse command
        if text.startswith("prd from meeting"):
            # Extract meeting name and trigger workflow
            meeting_name = text.replace("prd from meeting", "").strip().strip('"')
            # Search for meeting in Odoo...
            return {
                "response_type": "in_channel",
                "text": f"🤖 Generating PRD for meeting: {meeting_name}"
            }

        return {
            "response_type": "ephemeral",
            "text": "Unknown command. Try:\n• `/ipai prd from meeting \"Meeting Name\"`"
        }

    except Exception as e:
        logger.error(f"Error in Slack command: {str(e)}")
        return {
            "response_type": "ephemeral",
            "text": f"❌ Error: {str(e)}"
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
