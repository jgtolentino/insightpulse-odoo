"""
FastAPI-based Model Context Protocol (MCP) server for GitHub operations.

Exposes GitHub operations through pulser-hub GitHub App for AI assistants
to perform repository operations (create PRs, commits, issues, workflows, etc.).
"""

import os
import time
import logging
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import jwt
import httpx
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InsightPulse MCP GitHub Server",
    description="Model Context Protocol server for GitHub operations via pulser-hub App",
    version="1.0.0"
)

# Mount static files for web UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# GitHub App configuration from environment
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "2191216")  # pulser-hub App ID
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY", "")
GITHUB_INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID", "")
DEFAULT_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "jgtolentino")
DEFAULT_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "insightpulse-odoo")

# Token cache
_token_cache: Dict[str, Any] = {}

# OAuth storage (in-memory for now, use Redis/DB in production)
_oauth_codes: Dict[str, Dict[str, Any]] = {}
_oauth_tokens: Dict[str, Dict[str, Any]] = {}

# OAuth configuration
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "insightpulse-mcp-github")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", secrets.token_urlsafe(32))

# Feature to tool mapping for query parameter filtering
FEATURE_TOOL_MAP = {
    "branches": ["github_create_branch", "github_list_branches"],
    "commits": ["github_commit_files"],
    "issues": ["github_create_issue", "github_list_issues"],
    "pr": ["github_create_pr", "github_list_prs", "github_merge_pr"],
    "workflows": ["github_trigger_workflow"],
    "search": ["github_search_code"],
    "files": ["github_read_file"]
}


def parse_project_param(project: str) -> tuple[str, str]:
    """Parse project parameter into owner and repo."""
    if "/" in project:
        parts = project.split("/", 1)
        return parts[0], parts[1]
    return DEFAULT_REPO_OWNER, project


def get_enabled_tools(features: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get enabled tools based on features parameter."""
    if not features:
        return MCP_TOOLS  # All tools enabled if no features specified

    enabled_tools = {}
    for feature in features:
        feature = feature.strip().lower()
        tool_names = FEATURE_TOOL_MAP.get(feature, [])
        for tool_name in tool_names:
            if tool_name in MCP_TOOLS:
                enabled_tools[tool_name] = MCP_TOOLS[tool_name]

    return enabled_tools if enabled_tools else MCP_TOOLS  # Fallback to all tools if no valid features


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


@app.get("/")
async def serve_ui():
    """Serve the MCP server web UI."""
    return FileResponse("static/index.html")


@app.get("/oauth/authorize")
async def oauth_authorize(
    client_id: str,
    redirect_uri: str,
    state: Optional[str] = None,
    scope: Optional[str] = None
):
    """OAuth 2.0 authorization endpoint for ChatGPT integration."""
    # Validate client_id
    if client_id != OAUTH_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid client_id")

    # Generate authorization code
    code = secrets.token_urlsafe(32)

    # Store authorization code with expiration (10 minutes)
    _oauth_codes[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=10),
        "scope": scope or "github:all"
    }

    # Redirect back to ChatGPT with authorization code
    redirect_url = f"{redirect_uri}?code={code}"
    if state:
        redirect_url += f"&state={state}"

    logger.info(f"OAuth authorize: client_id={client_id}, redirect_uri={redirect_uri}")
    return RedirectResponse(url=redirect_url)


@app.post("/oauth/token")
async def oauth_token(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    """OAuth 2.0 token endpoint for ChatGPT integration."""
    # Validate client credentials
    if client_id != OAUTH_CLIENT_ID or client_secret != OAUTH_CLIENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    if grant_type == "authorization_code":
        # Validate authorization code
        if code not in _oauth_codes:
            raise HTTPException(status_code=400, detail="Invalid authorization code")

        code_data = _oauth_codes[code]

        # Check expiration
        if datetime.now() > code_data["expires_at"]:
            del _oauth_codes[code]
            raise HTTPException(status_code=400, detail="Authorization code expired")

        # Validate redirect_uri
        if redirect_uri != code_data["redirect_uri"]:
            raise HTTPException(status_code=400, detail="Redirect URI mismatch")

        # Generate access token
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        # Store tokens
        _oauth_tokens[access_token] = {
            "client_id": client_id,
            "scope": code_data["scope"],
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=1),
            "refresh_token": refresh_token
        }

        # Clean up used authorization code
        del _oauth_codes[code]

        logger.info(f"OAuth token issued: client_id={client_id}")

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token,
            "scope": code_data["scope"]
        }

    elif grant_type == "refresh_token":
        # Handle refresh token flow
        refresh_token = Form(None)
        # Find access token by refresh token
        for token, data in _oauth_tokens.items():
            if data.get("refresh_token") == refresh_token:
                # Generate new access token
                new_access_token = secrets.token_urlsafe(32)
                new_refresh_token = secrets.token_urlsafe(32)

                _oauth_tokens[new_access_token] = {
                    "client_id": client_id,
                    "scope": data["scope"],
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(hours=1),
                    "refresh_token": new_refresh_token
                }

                # Remove old token
                del _oauth_tokens[token]

                return {
                    "access_token": new_access_token,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "refresh_token": new_refresh_token,
                    "scope": data["scope"]
                }

        raise HTTPException(status_code=400, detail="Invalid refresh token")

    raise HTTPException(status_code=400, detail="Unsupported grant type")


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
        # Parse query parameters
        query_params = dict(request.query_params)
        project = query_params.get("project", f"{DEFAULT_REPO_OWNER}/{DEFAULT_REPO_NAME}")
        features_param = query_params.get("features", "")

        # Parse features list
        features = [f.strip() for f in features_param.split(",") if f.strip()] if features_param else None

        # Parse project into owner/repo
        owner, repo = parse_project_param(project)

        # Store in request state for tool access
        request.state.default_owner = owner
        request.state.default_repo = repo
        request.state.enabled_features = features

        # Get enabled tools based on features parameter
        enabled_tools = get_enabled_tools(features)

        # Log query parameters for monitoring
        logger.info(f"MCP request: project={project}, features={features}, enabled_tools={len(enabled_tools)}")

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
                        for name, func in enabled_tools.items()
                    ]
                }
            })

        # Handle tools/call method
        if mcp_request.method == "tools/call":
            tool_name = mcp_request.params.get("name")
            tool_params = mcp_request.params.get("arguments", {})

            # Check if tool is enabled based on features filter
            if tool_name not in enabled_tools:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": mcp_request.id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not enabled or not found: {tool_name}"
                    }
                })

            try:
                result = await enabled_tools[tool_name](tool_params)
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
