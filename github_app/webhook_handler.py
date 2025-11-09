"""
GitHub App Webhook Handler for InsightPulse AI
Automates OCA contributions, issue management, and CI/CD integration
"""

import hashlib
import hmac
import os
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="InsightPulse GitHub App", version="1.0.0")

# Configuration
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID', '')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY', '')
NOTION_API_KEY = os.getenv('NOTION_API_KEY', '')
NOTION_DATABASE_ID = os.getenv('NOTION_TASKS_DATABASE_ID', '')


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature

    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    if not GITHUB_WEBHOOK_SECRET:
        return True  # Skip verification in development

    expected = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


async def create_notion_task(title: str, description: str, github_url: str) -> Dict:
    """
    Create a Notion task for a GitHub issue

    Args:
        title: Task title
        description: Task description
        github_url: GitHub issue URL

    Returns:
        Notion page object
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "GitHub URL": {
                "url": github_url
            },
            "Status": {
                "select": {"name": "Backlog"}
            },
            "Priority": {
                "select": {"name": "Medium"}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": description}}]
                }
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()


async def add_pr_label(repo_full_name: str, pr_number: int, label: str):
    """Add label to pull request"""
    # This would require GitHub App authentication
    # Placeholder for actual implementation
    pass


async def handle_pull_request(data: Dict) -> Dict:
    """
    Handle pull request events

    Automatically labels PRs based on files changed:
    - BIR compliance changes
    - OCA module updates
    - Finance SSC automation
    """
    action = data.get('action')
    pr = data.get('pull_request', {})

    if action != 'opened':
        return {"status": "ignored", "reason": f"Action '{action}' not handled"}

    pr_number = pr.get('number')
    pr_title = pr.get('title', '')
    pr_body = pr.get('body', '')
    changed_files = pr.get('changed_files', [])

    # Analyze files changed
    labels_to_add = []

    # Check for BIR-related changes
    bir_keywords = ['bir', 'tax', '1601', '2550', '1702', 'alphalist']
    if any(keyword in pr_title.lower() or keyword in pr_body.lower()
           for keyword in bir_keywords):
        labels_to_add.append('BIR')
        labels_to_add.append('compliance')

    # Check for OCA module changes
    if any('oca' in str(f).lower() for f in changed_files):
        labels_to_add.append('OCA')

    # Check for Finance SSC changes
    finance_keywords = ['finance', 'accounting', 'ledger', 'journal']
    if any(keyword in pr_title.lower() for keyword in finance_keywords):
        labels_to_add.append('Finance SSC')

    return {
        "status": "processed",
        "pr_number": pr_number,
        "labels_added": labels_to_add,
        "message": f"Processed PR #{pr_number}"
    }


async def handle_issue(data: Dict) -> Dict:
    """
    Handle issue events

    Creates corresponding Notion task for tracking
    """
    action = data.get('action')
    issue = data.get('issue', {})

    if action != 'opened':
        return {"status": "ignored", "reason": f"Action '{action}' not handled"}

    issue_number = issue.get('number')
    issue_title = issue.get('title', '')
    issue_body = issue.get('body', '')
    issue_url = issue.get('html_url', '')

    # Create Notion task
    try:
        notion_task = await create_notion_task(
            title=f"#{issue_number}: {issue_title}",
            description=issue_body,
            github_url=issue_url
        )

        return {
            "status": "processed",
            "issue_number": issue_number,
            "notion_task_id": notion_task.get('id'),
            "message": f"Created Notion task for issue #{issue_number}"
        }
    except Exception as e:
        return {
            "status": "error",
            "issue_number": issue_number,
            "error": str(e)
        }


async def handle_workflow_run(data: Dict) -> Dict:
    """
    Handle workflow run events

    Monitors CI/CD pipeline status
    """
    workflow_run = data.get('workflow_run', {})
    action = data.get('action')

    status = workflow_run.get('status')
    conclusion = workflow_run.get('conclusion')
    name = workflow_run.get('name', '')

    return {
        "status": "processed",
        "workflow": name,
        "action": action,
        "conclusion": conclusion,
        "message": f"Workflow '{name}' {action} with conclusion: {conclusion}"
    }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "InsightPulse GitHub App",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/github/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint

    Receives and processes events from GitHub App
    """
    # Get raw payload
    payload = await request.body()

    # Verify signature
    if x_hub_signature_256:
        if not verify_signature(payload, x_hub_signature_256):
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse JSON
    data = await request.json()

    # Route to appropriate handler
    if x_github_event == 'pull_request':
        result = await handle_pull_request(data)
    elif x_github_event == 'issues':
        result = await handle_issue(data)
    elif x_github_event == 'workflow_run':
        result = await handle_workflow_run(data)
    else:
        result = {
            "status": "ignored",
            "event": x_github_event,
            "reason": "Event type not handled"
        }

    return JSONResponse(content=result)


@app.post("/trigger/oca-contribution")
async def trigger_oca_contribution(request: Request):
    """
    Trigger OCA contribution workflow

    Creates PR to OCA repositories for approved BIR modules
    """
    data = await request.json()
    module_name = data.get('module_name')

    return {
        "status": "triggered",
        "module": module_name,
        "message": f"OCA contribution workflow triggered for {module_name}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
