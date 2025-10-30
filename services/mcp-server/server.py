"""
FastAPI-based Model Context Protocol (MCP) server for GitHub operations.

Exposes GitHub operations through pulser-hub GitHub App for AI assistants
to perform repository operations (create PRs, commits, issues, workflows, etc.).
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InsightPulse MCP GitHub Server",
    description="Model Context Protocol server for GitHub operations via pulser-hub App",
    version="1.0.0"
)

# GitHub App configuration from environment
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "2191216")  # pulser-hub App ID
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY", "")
GITHUB_INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID", "")
DEFAULT_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "jgtolentino")
DEFAULT_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "insightpulse-odoo")

# Token cache
_token_cache: Dict[str, Any] = {}


class MCPRequest(BaseModel):
    """MCP protocol request schema."""
    jsonrpc: str = Field(default="2.0", pattern="^2\\.0$")
    id: Optional[str] = None
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """MCP protocol response schema."""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


def generate_jwt_token() -> str:
    """Generate GitHub App JWT token for authentication."""
    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued 60 seconds in the past
        "exp": now + (10 * 60),  # Expires in 10 minutes
        "iss": GITHUB_APP_ID
    }

    return jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")


async def get_installation_token() -> str:
    """Get GitHub App installation access token with caching."""
    cache_key = f"installation_{GITHUB_INSTALLATION_ID}"

    # Check cache
    if cache_key in _token_cache:
        token_data = _token_cache[cache_key]
        expires_at = datetime.fromisoformat(token_data["expires_at"].replace("Z", "+00:00"))

        # Return cached token if still valid (with 5-minute buffer)
        if expires_at > datetime.now() + timedelta(minutes=5):
            return token_data["token"]

    # Generate new token
    jwt_token = generate_jwt_token()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/app/installations/{GITHUB_INSTALLATION_ID}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        )

        if response.status_code != 201:
            logger.error(f"Failed to get installation token: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to authenticate with GitHub")

        token_data = response.json()
        _token_cache[cache_key] = token_data

        return token_data["token"]


async def github_api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None
) -> Dict[str, Any]:
    """Make authenticated GitHub API request."""
    token = await get_installation_token()

    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code >= 400:
            logger.error(f"GitHub API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.json())

        return response.json() if response.text else {}


# MCP Tool Handlers

async def github_create_branch(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new branch from a base branch."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    branch = params["branch"]
    from_branch = params.get("from_branch", "main")

    # Get base branch SHA
    base_ref = await github_api_request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{from_branch}")
    base_sha = base_ref["object"]["sha"]

    # Create new branch
    result = await github_api_request(
        "POST",
        f"/repos/{owner}/{repo}/git/refs",
        data={
            "ref": f"refs/heads/{branch}",
            "sha": base_sha
        }
    )

    return {
        "branch": branch,
        "sha": result["object"]["sha"],
        "url": result["url"]
    }


async def github_commit_files(params: Dict[str, Any]) -> Dict[str, Any]:
    """Commit multiple files to a branch."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    branch = params["branch"]
    message = params["message"]
    files = params["files"]  # List of {"path": "...", "content": "..."}

    # Get current branch SHA
    ref = await github_api_request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
    current_sha = ref["object"]["sha"]

    # Get current commit
    commit = await github_api_request("GET", f"/repos/{owner}/{repo}/git/commits/{current_sha}")
    tree_sha = commit["tree"]["sha"]

    # Create blobs for each file
    blobs = []
    for file in files:
        blob = await github_api_request(
            "POST",
            f"/repos/{owner}/{repo}/git/blobs",
            data={"content": file["content"], "encoding": "utf-8"}
        )
        blobs.append({"path": file["path"], "mode": "100644", "type": "blob", "sha": blob["sha"]})

    # Create new tree
    new_tree = await github_api_request(
        "POST",
        f"/repos/{owner}/{repo}/git/trees",
        data={"base_tree": tree_sha, "tree": blobs}
    )

    # Create new commit
    new_commit = await github_api_request(
        "POST",
        f"/repos/{owner}/{repo}/git/commits",
        data={
            "message": message,
            "tree": new_tree["sha"],
            "parents": [current_sha]
        }
    )

    # Update branch reference
    await github_api_request(
        "PATCH",
        f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
        data={"sha": new_commit["sha"]}
    )

    return {
        "commit_sha": new_commit["sha"],
        "commit_url": new_commit["url"],
        "files_committed": len(files)
    }


async def github_create_pr(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a pull request."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    title = params["title"]
    head = params["head"]
    base = params.get("base", "main")
    body = params.get("body", "")
    draft = params.get("draft", False)

    result = await github_api_request(
        "POST",
        f"/repos/{owner}/{repo}/pulls",
        data={
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }
    )

    return {
        "pr_number": result["number"],
        "pr_url": result["html_url"],
        "state": result["state"]
    }


async def github_list_prs(params: Dict[str, Any]) -> Dict[str, Any]:
    """List pull requests."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    state = params.get("state", "open")

    result = await github_api_request(
        "GET",
        f"/repos/{owner}/{repo}/pulls",
        params={"state": state}
    )

    return {
        "pull_requests": [
            {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "url": pr["html_url"],
                "head": pr["head"]["ref"],
                "base": pr["base"]["ref"]
            }
            for pr in result
        ]
    }


async def github_merge_pr(params: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a pull request."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    pr_number = params["pr_number"]
    merge_method = params.get("merge_method", "merge")

    result = await github_api_request(
        "PUT",
        f"/repos/{owner}/{repo}/pulls/{pr_number}/merge",
        data={"merge_method": merge_method}
    )

    return {
        "merged": result["merged"],
        "sha": result["sha"],
        "message": result["message"]
    }


async def github_create_issue(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a GitHub issue."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    title = params["title"]
    body = params.get("body", "")
    labels = params.get("labels", [])

    result = await github_api_request(
        "POST",
        f"/repos/{owner}/{repo}/issues",
        data={
            "title": title,
            "body": body,
            "labels": labels
        }
    )

    return {
        "issue_number": result["number"],
        "issue_url": result["html_url"],
        "state": result["state"]
    }


async def github_list_issues(params: Dict[str, Any]) -> Dict[str, Any]:
    """List GitHub issues."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    state = params.get("state", "open")

    result = await github_api_request(
        "GET",
        f"/repos/{owner}/{repo}/issues",
        params={"state": state}
    )

    return {
        "issues": [
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "url": issue["html_url"],
                "labels": [label["name"] for label in issue["labels"]]
            }
            for issue in result
        ]
    }


async def github_trigger_workflow(params: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger a GitHub Actions workflow."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    workflow_id = params["workflow_id"]
    ref = params.get("ref", "main")
    inputs = params.get("inputs", {})

    await github_api_request(
        "POST",
        f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
        data={
            "ref": ref,
            "inputs": inputs
        }
    )

    return {
        "workflow_id": workflow_id,
        "ref": ref,
        "status": "triggered"
    }


async def github_read_file(params: Dict[str, Any]) -> Dict[str, Any]:
    """Read file contents from repository."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    path = params["path"]
    ref = params.get("ref", "main")

    result = await github_api_request(
        "GET",
        f"/repos/{owner}/{repo}/contents/{path}",
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


async def github_list_branches(params: Dict[str, Any]) -> Dict[str, Any]:
    """List repository branches."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)

    result = await github_api_request(
        "GET",
        f"/repos/{owner}/{repo}/branches"
    )

    return {
        "branches": [
            {
                "name": branch["name"],
                "sha": branch["commit"]["sha"],
                "protected": branch.get("protected", False)
            }
            for branch in result
        ]
    }


async def github_search_code(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search code in repository."""
    owner = params.get("owner", DEFAULT_REPO_OWNER)
    repo = params.get("repo", DEFAULT_REPO_NAME)
    query = params["query"]

    full_query = f"{query} repo:{owner}/{repo}"

    result = await github_api_request(
        "GET",
        "/search/code",
        params={"q": full_query}
    )

    return {
        "total_count": result["total_count"],
        "items": [
            {
                "name": item["name"],
                "path": item["path"],
                "url": item["html_url"],
                "sha": item["sha"]
            }
            for item in result["items"]
        ]
    }


# MCP Tool Registry
MCP_TOOLS = {
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
    "github_search_code": github_search_code
}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "mcp-github-server",
        "version": "1.0.0",
        "github_app_id": GITHUB_APP_ID
    }


@app.post("/mcp/github")
async def mcp_endpoint(request: Request):
    """MCP protocol endpoint for GitHub operations."""
    try:
        body = await request.json()
        mcp_request = MCPRequest(**body)

        # Handle tools/list method
        if mcp_request.method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": mcp_request.id,
                "result": {
                    "tools": [
                        {"name": name, "description": func.__doc__.strip() if func.__doc__ else ""}
                        for name, func in MCP_TOOLS.items()
                    ]
                }
            })

        # Handle tools/call method
        if mcp_request.method == "tools/call":
            tool_name = mcp_request.params.get("name")
            tool_params = mcp_request.params.get("arguments", {})

            if tool_name not in MCP_TOOLS:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": mcp_request.id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                })

            try:
                result = await MCP_TOOLS[tool_name](tool_params)
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": mcp_request.id,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Tool execution error: {str(e)}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": mcp_request.id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                })

        # Unsupported method
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": mcp_request.id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {mcp_request.method}"
            }
        })

    except Exception as e:
        logger.error(f"MCP request error: {str(e)}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
