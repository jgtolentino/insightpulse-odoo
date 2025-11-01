#!/usr/bin/env python3
"""
MCP Server for GitHub Operations via pulser-hub

Model Context Protocol (MCP) server that exposes GitHub operations
through the pulser-hub GitHub App, enabling AI assistants to perform
GitHub actions directly.

Architecture:
    AI Assistant (Claude/ChatGPT)
        ↓ MCP Protocol (JSON-RPC)
    MCP Server (this script)
        ↓ GitHub REST API (JWT authentication)
    GitHub Repository (via pulser-hub app)

Authentication:
    - GitHub App: pulser-hub (App ID: 2191216)
    - JWT token generation from private key
    - Installation token caching (50-minute refresh)

Available Tools:
    1. github_create_branch - Create new branches
    2. github_commit_files - Commit multiple files
    3. github_create_pr - Create pull requests
    4. github_list_prs - List pull requests
    5. github_merge_pr - Merge pull requests
    6. github_create_issue - Create issues
    7. github_list_issues - List issues
    8. github_trigger_workflow - Trigger GitHub Actions
    9. github_read_file - Read file contents
    10. github_list_branches - List branches
    11. github_search_code - Search code

Usage:
    # Local development
    export GITHUB_APP_ID=2191216
    export GITHUB_PRIVATE_KEY="$(cat private-key.pem)"
    export GITHUB_INSTALLATION_ID=your_installation_id
    python server.py

    # Production (DigitalOcean)
    Environment variables configured in app.yaml
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import jwt
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="pulser-hub MCP Server",
    description="GitHub operations via Model Context Protocol",
    version="1.0.0"
)

# ============================================================================
# Configuration
# ============================================================================

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "2191216")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY", "")
GITHUB_INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID", "")

if not GITHUB_PRIVATE_KEY:
    logger.warning("GITHUB_PRIVATE_KEY not set - server will not be able to authenticate")

if not GITHUB_INSTALLATION_ID:
    logger.warning("GITHUB_INSTALLATION_ID not set - will attempt to discover it")

# Token cache
_token_cache: Dict[str, Any] = {
    "token": None,
    "expires_at": None
}

# ============================================================================
# GitHub API Client
# ============================================================================

class GitHubClient:
    """GitHub API client with JWT authentication for GitHub Apps"""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.app_id = GITHUB_APP_ID
        self.private_key = GITHUB_PRIVATE_KEY
        self.installation_id = GITHUB_INSTALLATION_ID
        self.client = httpx.AsyncClient(timeout=30.0)

    def generate_jwt(self) -> str:
        """Generate JWT for GitHub App authentication"""
        now = int(time.time())
        payload = {
            "iat": now - 60,  # Issued 60 seconds in past
            "exp": now + (10 * 60),  # Expires in 10 minutes
            "iss": self.app_id
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def get_installation_token(self) -> str:
        """Get installation access token (cached for 50 minutes)"""
        # Check cache
        if _token_cache["token"] and _token_cache["expires_at"]:
            if datetime.now() < _token_cache["expires_at"]:
                logger.debug("Using cached installation token")
                return _token_cache["token"]

        # Generate new token
        logger.info("Generating new installation token")
        jwt_token = self.generate_jwt()

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        url = f"{self.BASE_URL}/app/installations/{self.installation_id}/access_tokens"
        response = await self.client.post(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        token = data["token"]
        expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))

        # Cache token (refresh 10 minutes before expiry)
        _token_cache["token"] = token
        _token_cache["expires_at"] = expires_at - timedelta(minutes=10)

        logger.info(f"Installation token cached until {_token_cache['expires_at']}")
        return token

    async def api_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make authenticated API request to GitHub"""
        token = await self.get_installation_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        url = f"{self.BASE_URL}{endpoint}"
        logger.info(f"{method} {url}")

        response = await self.client.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            params=params
        )

        response.raise_for_status()
        return response.json() if response.content else {}

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global GitHub client
github = GitHubClient()

# ============================================================================
# MCP Protocol Models
# ============================================================================

class MCPRequest(BaseModel):
    """MCP protocol request"""
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[int] = None


class MCPResponse(BaseModel):
    """MCP protocol response"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int] = None


class ToolDefinition(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


# ============================================================================
# GitHub Tool Implementations
# ============================================================================

async def github_create_branch(repo: str, branch: str, from_branch: str = "main") -> Dict:
    """Create a new branch"""
    # Get SHA of from_branch
    ref_data = await github.api_request(
        "GET",
        f"/repos/{repo}/git/ref/heads/{from_branch}"
    )
    sha = ref_data["object"]["sha"]

    # Create new branch
    result = await github.api_request(
        "POST",
        f"/repos/{repo}/git/refs",
        json_data={
            "ref": f"refs/heads/{branch}",
            "sha": sha
        }
    )

    return {
        "branch": branch,
        "sha": sha,
        "url": result.get("url")
    }


async def github_commit_files(
    repo: str,
    branch: str,
    files: List[Dict[str, str]],
    message: str
) -> Dict:
    """Commit multiple files to a branch

    Args:
        repo: Repository (owner/name)
        branch: Branch name
        files: List of {"path": "file.py", "content": "file content"}
        message: Commit message
    """
    # Get current branch reference
    ref_data = await github.api_request(
        "GET",
        f"/repos/{repo}/git/ref/heads/{branch}"
    )
    base_sha = ref_data["object"]["sha"]

    # Get base tree
    commit_data = await github.api_request(
        "GET",
        f"/repos/{repo}/git/commits/{base_sha}"
    )
    base_tree_sha = commit_data["tree"]["sha"]

    # Create blobs for each file
    tree = []
    for file in files:
        blob_data = await github.api_request(
            "POST",
            f"/repos/{repo}/git/blobs",
            json_data={
                "content": file["content"],
                "encoding": "utf-8"
            }
        )

        tree.append({
            "path": file["path"],
            "mode": "100644",
            "type": "blob",
            "sha": blob_data["sha"]
        })

    # Create tree
    tree_data = await github.api_request(
        "POST",
        f"/repos/{repo}/git/trees",
        json_data={
            "base_tree": base_tree_sha,
            "tree": tree
        }
    )

    # Create commit
    new_commit = await github.api_request(
        "POST",
        f"/repos/{repo}/git/commits",
        json_data={
            "message": message,
            "tree": tree_data["sha"],
            "parents": [base_sha]
        }
    )

    # Update reference
    await github.api_request(
        "PATCH",
        f"/repos/{repo}/git/refs/heads/{branch}",
        json_data={"sha": new_commit["sha"]}
    )

    return {
        "commit_sha": new_commit["sha"],
        "files_committed": len(files),
        "message": message
    }


async def github_create_pr(
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = ""
) -> Dict:
    """Create a pull request"""
    result = await github.api_request(
        "POST",
        f"/repos/{repo}/pulls",
        json_data={
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
    )

    return {
        "number": result["number"],
        "url": result["html_url"],
        "state": result["state"]
    }


async def github_list_prs(repo: str, state: str = "open") -> List[Dict]:
    """List pull requests"""
    result = await github.api_request(
        "GET",
        f"/repos/{repo}/pulls",
        params={"state": state}
    )

    return [
        {
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"],
            "author": pr["user"]["login"],
            "url": pr["html_url"]
        }
        for pr in result
    ]


async def github_merge_pr(repo: str, pr_number: int, method: str = "merge") -> Dict:
    """Merge a pull request"""
    result = await github.api_request(
        "PUT",
        f"/repos/{repo}/pulls/{pr_number}/merge",
        json_data={"merge_method": method}
    )

    return {
        "merged": result.get("merged", False),
        "sha": result.get("sha"),
        "message": result.get("message")
    }


async def github_create_issue(repo: str, title: str, body: str = "") -> Dict:
    """Create an issue"""
    result = await github.api_request(
        "POST",
        f"/repos/{repo}/issues",
        json_data={
            "title": title,
            "body": body
        }
    )

    return {
        "number": result["number"],
        "url": result["html_url"],
        "state": result["state"]
    }


async def github_list_issues(repo: str, state: str = "open") -> List[Dict]:
    """List issues"""
    result = await github.api_request(
        "GET",
        f"/repos/{repo}/issues",
        params={"state": state}
    )

    # Filter out pull requests (they appear in issues endpoint)
    issues = [item for item in result if "pull_request" not in item]

    return [
        {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "author": issue["user"]["login"],
            "url": issue["html_url"]
        }
        for issue in issues
    ]


async def github_trigger_workflow(
    repo: str,
    workflow_id: str,
    ref: str = "main",
    inputs: Optional[Dict] = None
) -> Dict:
    """Trigger a GitHub Actions workflow"""
    await github.api_request(
        "POST",
        f"/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
        json_data={
            "ref": ref,
            "inputs": inputs or {}
        }
    )

    return {
        "workflow_id": workflow_id,
        "ref": ref,
        "status": "triggered"
    }


async def github_read_file(repo: str, path: str, ref: str = "main") -> Dict:
    """Read file contents"""
    result = await github.api_request(
        "GET",
        f"/repos/{repo}/contents/{path}",
        params={"ref": ref}
    )

    import base64
    content = base64.b64decode(result["content"]).decode("utf-8")

    return {
        "path": path,
        "content": content,
        "sha": result["sha"],
        "size": result["size"]
    }


async def github_list_branches(repo: str) -> List[Dict]:
    """List repository branches"""
    result = await github.api_request(
        "GET",
        f"/repos/{repo}/branches"
    )

    return [
        {
            "name": branch["name"],
            "sha": branch["commit"]["sha"],
            "protected": branch.get("protected", False)
        }
        for branch in result
    ]


async def github_search_code(repo: str, query: str) -> List[Dict]:
    """Search code in repository"""
    result = await github.api_request(
        "GET",
        "/search/code",
        params={
            "q": f"{query} repo:{repo}"
        }
    )

    return [
        {
            "path": item["path"],
            "url": item["html_url"],
            "repository": item["repository"]["full_name"]
        }
        for item in result.get("items", [])
    ]


# ============================================================================
# MCP Tool Registry
# ============================================================================

MCP_TOOLS = [
    ToolDefinition(
        name="github_create_branch",
        description="Create a new branch in a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "branch": {"type": "string", "description": "New branch name"},
                "from_branch": {"type": "string", "description": "Base branch", "default": "main"}
            },
            "required": ["repo", "branch"]
        }
    ),
    ToolDefinition(
        name="github_commit_files",
        description="Commit multiple files to a branch",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "branch": {"type": "string", "description": "Branch name"},
                "files": {
                    "type": "array",
                    "description": "Files to commit",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["path", "content"]
                    }
                },
                "message": {"type": "string", "description": "Commit message"}
            },
            "required": ["repo", "branch", "files", "message"]
        }
    ),
    ToolDefinition(
        name="github_create_pr",
        description="Create a pull request",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "title": {"type": "string", "description": "PR title"},
                "head": {"type": "string", "description": "Head branch"},
                "base": {"type": "string", "description": "Base branch", "default": "main"},
                "body": {"type": "string", "description": "PR description", "default": ""}
            },
            "required": ["repo", "title", "head"]
        }
    ),
    ToolDefinition(
        name="github_list_prs",
        description="List pull requests in a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "state": {"type": "string", "description": "PR state (open/closed/all)", "default": "open"}
            },
            "required": ["repo"]
        }
    ),
    ToolDefinition(
        name="github_merge_pr",
        description="Merge a pull request",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "pr_number": {"type": "integer", "description": "PR number"},
                "method": {"type": "string", "description": "Merge method (merge/squash/rebase)", "default": "merge"}
            },
            "required": ["repo", "pr_number"]
        }
    ),
    ToolDefinition(
        name="github_create_issue",
        description="Create an issue in a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue description", "default": ""}
            },
            "required": ["repo", "title"]
        }
    ),
    ToolDefinition(
        name="github_list_issues",
        description="List issues in a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "state": {"type": "string", "description": "Issue state (open/closed/all)", "default": "open"}
            },
            "required": ["repo"]
        }
    ),
    ToolDefinition(
        name="github_trigger_workflow",
        description="Trigger a GitHub Actions workflow",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "workflow_id": {"type": "string", "description": "Workflow file name or ID"},
                "ref": {"type": "string", "description": "Branch/tag/SHA", "default": "main"},
                "inputs": {"type": "object", "description": "Workflow inputs", "default": {}}
            },
            "required": ["repo", "workflow_id"]
        }
    ),
    ToolDefinition(
        name="github_read_file",
        description="Read file contents from a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "path": {"type": "string", "description": "File path"},
                "ref": {"type": "string", "description": "Branch/tag/SHA", "default": "main"}
            },
            "required": ["repo", "path"]
        }
    ),
    ToolDefinition(
        name="github_list_branches",
        description="List all branches in a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"}
            },
            "required": ["repo"]
        }
    ),
    ToolDefinition(
        name="github_search_code",
        description="Search code in a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository (owner/name)"},
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["repo", "query"]
        }
    ),
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "github_create_branch": github_create_branch,
    "github_commit_files": github_commit_files,
    "github_create_pr": github_create_pr,
    "github_list_prs": github_list_prs,
    "github_merge_pr": github_merge_pr,
    "github_create_issue": github_create_issue,
    "github_list_issues": github_list_issues,
    "github_trigger_workflow": github_trigger_workflow,
    "github_read_file": github_read_file,
    "github_list_branches": github_list_branches,
    "github_search_code": github_search_code,
}

# ============================================================================
# FastAPI Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_id": GITHUB_APP_ID,
        "has_private_key": bool(GITHUB_PRIVATE_KEY),
        "installation_id": GITHUB_INSTALLATION_ID or "auto-discover"
    }


@app.post("/mcp/github")
async def mcp_handler(request: Request):
    """MCP protocol handler"""
    try:
        body = await request.json()
        mcp_request = MCPRequest(**body)

        logger.info(f"MCP Request: {mcp_request.method}")

        # Handle tools/list
        if mcp_request.method == "tools/list":
            return MCPResponse(
                id=mcp_request.id,
                result={"tools": [tool.dict() for tool in MCP_TOOLS]}
            ).dict()

        # Handle tools/call
        elif mcp_request.method == "tools/call":
            tool_name = mcp_request.params.get("name")
            arguments = mcp_request.params.get("arguments", {})

            if tool_name not in TOOL_FUNCTIONS:
                return MCPResponse(
                    id=mcp_request.id,
                    error={"code": -32601, "message": f"Tool not found: {tool_name}"}
                ).dict()

            # Execute tool function
            tool_func = TOOL_FUNCTIONS[tool_name]
            try:
                result = await tool_func(**arguments)
                return MCPResponse(
                    id=mcp_request.id,
                    result=result
                ).dict()
            except Exception as e:
                logger.error(f"Tool execution error: {e}", exc_info=True)
                return MCPResponse(
                    id=mcp_request.id,
                    error={"code": -32000, "message": str(e)}
                ).dict()

        else:
            return MCPResponse(
                id=mcp_request.id,
                error={"code": -32601, "message": f"Method not found: {mcp_request.method}"}
            ).dict()

    except Exception as e:
        logger.error(f"MCP handler error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await github.close()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
