#!/usr/bin/env python3
"""
pulser-hub MCP Server

Model Context Protocol server that exposes GitHub operations
via the pulser-hub GitHub App.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import jwt
import time
import httpx
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="pulser-hub MCP Server",
    description="GitHub operations via pulser-hub GitHub App",
    version="1.0.0"
)

# Configuration from environment
GITHUB_APP_ID = int(os.getenv("GITHUB_APP_ID", "2191216"))
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY", "")
GITHUB_INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID", "")


class MCPRequest(BaseModel):
    """MCP protocol request."""
    method: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """MCP protocol response."""
    result: Optional[Any] = None
    error: Optional[Dict[str, str]] = None


class GitHubClient:
    """GitHub API client using pulser-hub credentials."""

    def __init__(self):
        self.app_id = GITHUB_APP_ID
        self.private_key = GITHUB_PRIVATE_KEY
        self.installation_id = GITHUB_INSTALLATION_ID
        self._token_cache = None
        self._token_expires = 0

    def _generate_jwt(self) -> str:
        """Generate JWT for GitHub App authentication."""
        payload = {
            'iat': int(time.time()),
            'exp': int(time.time()) + (10 * 60),  # 10 minutes
            'iss': self.app_id
        }
        return jwt.encode(payload, self.private_key, algorithm='RS256')

    async def _get_installation_token(self) -> str:
        """Get or refresh installation access token."""
        # Check cache
        if self._token_cache and time.time() < self._token_expires:
            return self._token_cache

        # Generate new token
        jwt_token = self._generate_jwt()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'https://api.github.com/app/installations/{self.installation_id}/access_tokens',
                headers={
                    'Authorization': f'Bearer {jwt_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            response.raise_for_status()
            data = response.json()

            # Cache token (expires in 1 hour, refresh after 50 minutes)
            self._token_cache = data['token']
            self._token_expires = time.time() + (50 * 60)

            return self._token_cache

    async def api_call(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated GitHub API call."""
        token = await self._get_installation_token()

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f'https://api.github.com{endpoint}',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                **kwargs
            )

            if response.status_code >= 400:
                logger.error(f"GitHub API error: {response.status_code} {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"GitHub API error: {response.text}"
                )

            return response.json() if response.content else {}


# Initialize GitHub client
github = GitHubClient()


# ============================================================================
# MCP Protocol Handlers
# ============================================================================

@app.post("/mcp/github")
async def mcp_handler(request: Request):
    """Main MCP protocol handler."""
    try:
        body = await request.json()
        mcp_request = MCPRequest(**body)

        logger.info(f"MCP request: {mcp_request.method}")

        # Route to appropriate handler
        handlers = {
            "tools/list": handle_tools_list,
            "tools/call": handle_tools_call,
        }

        handler = handlers.get(mcp_request.method)
        if not handler:
            return MCPResponse(
                error={"code": "method_not_found", "message": f"Unknown method: {mcp_request.method}"}
            ).dict()

        result = await handler(mcp_request.params)
        return MCPResponse(result=result).dict()

    except Exception as e:
        logger.error(f"MCP handler error: {str(e)}")
        return MCPResponse(
            error={"code": "internal_error", "message": str(e)}
        ).dict()


async def handle_tools_list(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List available tools."""
    return [
        {
            "name": "github_create_branch",
            "description": "Create a new branch from base branch",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository (owner/name)"},
                    "branch": {"type": "string", "description": "New branch name"},
                    "from_branch": {"type": "string", "description": "Base branch", "default": "main"}
                },
                "required": ["repo", "branch"]
            }
        },
        {
            "name": "github_commit_files",
            "description": "Commit files to a branch",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "branch": {"type": "string"},
                    "message": {"type": "string"},
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["repo", "branch", "message", "files"]
            }
        },
        {
            "name": "github_create_pr",
            "description": "Create a pull request",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "head": {"type": "string", "description": "Source branch"},
                    "base": {"type": "string", "description": "Target branch", "default": "main"}
                },
                "required": ["repo", "title", "head"]
            }
        },
        {
            "name": "github_list_prs",
            "description": "List pull requests",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"}
                },
                "required": ["repo"]
            }
        },
        {
            "name": "github_merge_pr",
            "description": "Merge a pull request",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "pr_number": {"type": "integer"},
                    "merge_method": {"type": "string", "enum": ["merge", "squash", "rebase"], "default": "squash"}
                },
                "required": ["repo", "pr_number"]
            }
        },
        {
            "name": "github_create_issue",
            "description": "Create an issue",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "labels": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["repo", "title"]
            }
        },
        {
            "name": "github_list_issues",
            "description": "List issues",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"}
                },
                "required": ["repo"]
            }
        },
        {
            "name": "github_trigger_workflow",
            "description": "Trigger GitHub Actions workflow",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "workflow_id": {"type": "string"},
                    "ref": {"type": "string", "default": "main"},
                    "inputs": {"type": "object"}
                },
                "required": ["repo", "workflow_id"]
            }
        },
        {
            "name": "github_read_file",
            "description": "Read file contents from repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "path": {"type": "string"},
                    "ref": {"type": "string", "default": "main"}
                },
                "required": ["repo", "path"]
            }
        },
        {
            "name": "github_list_branches",
            "description": "List branches in repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"}
                },
                "required": ["repo"]
            }
        },
        {
            "name": "github_search_code",
            "description": "Search code in repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "query": {"type": "string"}
                },
                "required": ["repo", "query"]
            }
        }
    ]


async def handle_tools_call(params: Dict[str, Any]) -> Any:
    """Execute a tool."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    logger.info(f"Executing tool: {tool_name}")

    # Route to tool handler
    tools = {
        "github_create_branch": tool_create_branch,
        "github_commit_files": tool_commit_files,
        "github_create_pr": tool_create_pr,
        "github_list_prs": tool_list_prs,
        "github_merge_pr": tool_merge_pr,
        "github_create_issue": tool_create_issue,
        "github_list_issues": tool_list_issues,
        "github_trigger_workflow": tool_trigger_workflow,
        "github_read_file": tool_read_file,
        "github_list_branches": tool_list_branches,
        "github_search_code": tool_search_code,
    }

    tool = tools.get(tool_name)
    if not tool:
        raise ValueError(f"Unknown tool: {tool_name}")

    return await tool(**arguments)


# ============================================================================
# Tool Implementations
# ============================================================================

async def tool_create_branch(repo: str, branch: str, from_branch: str = "main") -> Dict[str, Any]:
    """Create a new branch."""
    # Get base branch SHA
    base = await github.api_call("GET", f"/repos/{repo}/git/refs/heads/{from_branch}")
    base_sha = base["object"]["sha"]

    # Create new branch
    result = await github.api_call(
        "POST",
        f"/repos/{repo}/git/refs",
        json={
            "ref": f"refs/heads/{branch}",
            "sha": base_sha
        }
    )

    return {"branch": branch, "sha": result["object"]["sha"]}


async def tool_commit_files(repo: str, branch: str, message: str, files: List[Dict[str, str]]) -> Dict[str, Any]:
    """Commit files to a branch."""
    # Get current branch HEAD
    ref = await github.api_call("GET", f"/repos/{repo}/git/refs/heads/{branch}")
    base_tree_sha = ref["object"]["sha"]

    # Get base tree
    commit = await github.api_call("GET", f"/repos/{repo}/git/commits/{base_tree_sha}")
    base_tree = commit["tree"]["sha"]

    # Create blobs for each file
    tree_items = []
    for file in files:
        blob = await github.api_call(
            "POST",
            f"/repos/{repo}/git/blobs",
            json={"content": file["content"], "encoding": "utf-8"}
        )
        tree_items.append({
            "path": file["path"],
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"]
        })

    # Create tree
    tree = await github.api_call(
        "POST",
        f"/repos/{repo}/git/trees",
        json={"base_tree": base_tree, "tree": tree_items}
    )

    # Create commit
    new_commit = await github.api_call(
        "POST",
        f"/repos/{repo}/git/commits",
        json={
            "message": message,
            "tree": tree["sha"],
            "parents": [base_tree_sha]
        }
    )

    # Update ref
    await github.api_call(
        "PATCH",
        f"/repos/{repo}/git/refs/heads/{branch}",
        json={"sha": new_commit["sha"]}
    )

    return {
        "commit": new_commit["sha"],
        "message": message,
        "files_count": len(files)
    }


async def tool_create_pr(repo: str, title: str, head: str, base: str = "main", body: str = "") -> Dict[str, Any]:
    """Create a pull request."""
    result = await github.api_call(
        "POST",
        f"/repos/{repo}/pulls",
        json={
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
    )

    return {
        "number": result["number"],
        "url": result["html_url"],
        "state": result["state"]
    }


async def tool_list_prs(repo: str, state: str = "open") -> List[Dict[str, Any]]:
    """List pull requests."""
    result = await github.api_call("GET", f"/repos/{repo}/pulls", params={"state": state})

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


async def tool_merge_pr(repo: str, pr_number: int, merge_method: str = "squash") -> Dict[str, Any]:
    """Merge a pull request."""
    result = await github.api_call(
        "PUT",
        f"/repos/{repo}/pulls/{pr_number}/merge",
        json={"merge_method": merge_method}
    )

    return {
        "merged": result["merged"],
        "sha": result["sha"],
        "message": result["message"]
    }


async def tool_create_issue(repo: str, title: str, body: str = "", labels: List[str] = None) -> Dict[str, Any]:
    """Create an issue."""
    data = {"title": title, "body": body}
    if labels:
        data["labels"] = labels

    result = await github.api_call("POST", f"/repos/{repo}/issues", json=data)

    return {
        "number": result["number"],
        "url": result["html_url"],
        "state": result["state"]
    }


async def tool_list_issues(repo: str, state: str = "open") -> List[Dict[str, Any]]:
    """List issues."""
    result = await github.api_call("GET", f"/repos/{repo}/issues", params={"state": state})

    return [
        {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "author": issue["user"]["login"],
            "url": issue["html_url"]
        }
        for issue in result
        if "pull_request" not in issue  # Exclude PRs
    ]


async def tool_trigger_workflow(repo: str, workflow_id: str, ref: str = "main", inputs: Dict[str, Any] = None) -> Dict[str, str]:
    """Trigger GitHub Actions workflow."""
    data = {"ref": ref}
    if inputs:
        data["inputs"] = inputs

    await github.api_call(
        "POST",
        f"/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
        json=data
    )

    return {"status": "triggered", "workflow": workflow_id, "ref": ref}


async def tool_read_file(repo: str, path: str, ref: str = "main") -> Dict[str, str]:
    """Read file contents."""
    result = await github.api_call("GET", f"/repos/{repo}/contents/{path}", params={"ref": ref})

    import base64
    content = base64.b64decode(result["content"]).decode("utf-8")

    return {"path": path, "content": content, "sha": result["sha"]}


async def tool_list_branches(repo: str) -> List[Dict[str, str]]:
    """List branches."""
    result = await github.api_call("GET", f"/repos/{repo}/branches")

    return [{"name": branch["name"], "sha": branch["commit"]["sha"]} for branch in result]


async def tool_search_code(repo: str, query: str) -> List[Dict[str, Any]]:
    """Search code in repository."""
    result = await github.api_call(
        "GET",
        "/search/code",
        params={"q": f"{query} repo:{repo}"}
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
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app_id": GITHUB_APP_ID}


@app.get("/")
async def root():
    """Root endpoint with information."""
    return {
        "name": "pulser-hub MCP Server",
        "version": "1.0.0",
        "github_app_id": GITHUB_APP_ID,
        "endpoints": {
            "mcp": "/mcp/github",
            "health": "/health"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
