# Supabase MCP Implementation Review & Comparison

Analysis of Supabase's MCP server architecture compared to InsightPulse GitHub MCP implementation.

## Supabase MCP Architecture

### URL Structure
```
https://mcp.supabase.com/mcp?project_ref=<project-id>&features=<feature-groups>&read_only=true
```

**Query Parameters**:
- `project_ref`: Scope to specific Supabase project (security isolation)
- `features`: Comma-separated feature groups to enable
- `read_only`: Restrict to read-only operations (safety mode)

### Feature Groups System

Supabase organizes 30+ tools into 8 feature groups:

| Feature Group | Tools Count | Purpose |
|---------------|-------------|---------|
| `account` | 9 tools | Project/organization management |
| `docs` | 1 tool | Documentation search |
| `database` | 5 tools | Schema and query operations |
| `debugging` | 2 tools | Logs and advisories |
| `development` | 3 tools | API keys, URLs, TypeScript types |
| `functions` | 3 tools | Edge Functions deployment |
| `branching` | 6 tools | Database branching (paid plans) |
| `storage` | 3 tools | Storage bucket management (disabled by default) |

### Security Features

1. **Project Scoping**: Prevents cross-project access
2. **Read-Only Mode**: Database queries as read-only Postgres user
3. **Feature Filtering**: Reduce attack surface by limiting available tools
4. **OAuth Dynamic Registration**: Automatic browser-based authentication
5. **Manual Approval**: User confirms each tool execution
6. **Development Branches**: Safe testing without production impact

### Authentication Methods

**Primary**: OAuth Dynamic Client Registration (automatic)
**Fallback**: Personal Access Token (PAT) for CI environments
**Format**: `Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}`

## InsightPulse GitHub MCP Architecture

### Current URL Structure
```
https://insightpulseai.net/mcp/github?project=<owner/repo>&features=<feature-groups>
```

**Query Parameters**:
- `project`: Repository scope (owner/repo format)
- `features`: Comma-separated feature groups

### Current Feature Groups (7 groups, 11 tools)

| Feature Group | Tools | Purpose |
|---------------|-------|---------|
| `branches` | 2 | Branch creation and listing |
| `commits` | 1 | File commits |
| `issues` | 2 | Issue management |
| `pr` | 3 | Pull request operations |
| `workflows` | 1 | GitHub Actions triggering |
| `search` | 1 | Code search |
| `files` | 1 | File reading |

### Current Security

✅ **Implemented**:
- Project scoping via query parameters
- Feature group filtering
- OAuth 2.0 authorization flow
- Token expiration (1 hour)
- Refresh token support

❌ **Missing** (compared to Supabase):
- Read-only mode
- Multi-project isolation (single repo focus)
- Development branch awareness
- Manual tool approval gates
- Cost estimation/confirmation

## Key Differences

### 1. Feature Organization

**Supabase**: 8 groups, 30+ tools, hierarchical organization
**InsightPulse**: 7 groups, 11 tools, flat organization

**Recommendation**: Expand feature groups as more tools are added

### 2. Security Model

**Supabase**:
- Multi-tenant (multiple projects per user)
- Read-only mode for production safety
- Development branches for safe testing
- Disabled-by-default sensitive features (storage)

**InsightPulse**:
- Single-tenant (one repo per server instance)
- No read-only mode
- Direct repository access
- All features enabled by default

**Recommendation**: Add read-only mode and branch awareness

### 3. Tool Approval

**Supabase**: Manual user approval for each tool execution
**InsightPulse**: Automatic execution after OAuth authorization

**Recommendation**: Consider adding approval gates for destructive operations

### 4. Cost Awareness

**Supabase**: `get_cost()` and `confirm_cost()` for pricing transparency
**InsightPulse**: No cost estimation (GitHub API is free for authenticated apps)

**Recommendation**: Not needed for GitHub operations

## Recommended Enhancements

### Priority 1: Read-Only Mode (High Impact)

Add `read_only` query parameter to prevent destructive operations:

```python
# services/mcp-server/server.py
READ_ONLY_TOOLS = {
    "github_list_branches",
    "github_list_prs",
    "github_list_issues",
    "github_search_code",
    "github_read_file"
}

DESTRUCTIVE_TOOLS = {
    "github_create_branch",
    "github_commit_files",
    "github_create_pr",
    "github_merge_pr",
    "github_create_issue",
    "github_trigger_workflow"
}

def get_enabled_tools(features: Optional[List[str]] = None, read_only: bool = False) -> Dict[str, Any]:
    """Get enabled tools based on features and read_only parameters."""
    enabled_tools = {}

    # Filter by features
    if features:
        for feature in features:
            tool_names = FEATURE_TOOL_MAP.get(feature, [])
            for tool_name in tool_names:
                if tool_name in MCP_TOOLS:
                    enabled_tools[tool_name] = MCP_TOOLS[tool_name]
    else:
        enabled_tools = MCP_TOOLS.copy()

    # Filter by read_only mode
    if read_only:
        enabled_tools = {
            name: func for name, func in enabled_tools.items()
            if name in READ_ONLY_TOOLS
        }

    return enabled_tools
```

**Usage**:
```
https://insightpulseai.net/mcp/github?project=owner/repo&features=all&read_only=true
```

### Priority 2: Branch Awareness (Medium Impact)

Add branch parameter to scope operations to specific branches:

```python
# Query parameter
branch: Optional[str] = None  # e.g., "feat/parity-live-sync"

# Restrict destructive operations to non-main branches
PROTECTED_BRANCHES = {"main", "master", "production"}

async def github_commit_files(params: Dict[str, Any]) -> Dict[str, Any]:
    branch = params["branch"]

    # Prevent commits to protected branches in read-only mode
    if READ_ONLY and branch in PROTECTED_BRANCHES:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot commit to protected branch '{branch}' in read-only mode"
        )

    # Existing commit logic...
```

**Usage**:
```
https://insightpulseai.net/mcp/github?project=owner/repo&branch=feat/test&read_only=false
```

### Priority 3: Tool Approval Gates (Low Impact)

Add confirmation requirement for destructive operations:

```python
class ToolApproval(BaseModel):
    """Tool execution approval."""
    tool_name: str
    params: Dict[str, Any]
    approved: bool = False

# Store pending approvals
_pending_approvals: Dict[str, ToolApproval] = {}

@app.post("/mcp/approve")
async def approve_tool(approval_id: str, approved: bool):
    """User approval for destructive tool execution."""
    if approval_id not in _pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval = _pending_approvals[approval_id]
    approval.approved = approved

    return {"approved": approved, "tool_name": approval.tool_name}

# In tool execution
if tool_name in DESTRUCTIVE_TOOLS and REQUIRE_APPROVAL:
    approval_id = secrets.token_urlsafe(16)
    _pending_approvals[approval_id] = ToolApproval(
        tool_name=tool_name,
        params=tool_params
    )

    return {
        "approval_required": True,
        "approval_id": approval_id,
        "message": f"Approve execution of {tool_name}?"
    }
```

### Priority 4: Enhanced Documentation Tools (Medium Impact)

Add documentation search similar to Supabase's `search_docs`:

```python
async def github_search_docs(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search GitHub documentation."""
    query = params["query"]

    # Search GitHub Docs API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://docs.github.com/search",
            params={"query": query}
        )

        results = response.json()

        return {
            "results": [
                {
                    "title": result["title"],
                    "url": result["url"],
                    "excerpt": result["excerpt"]
                }
                for result in results[:5]
            ]
        }

# Add to feature mapping
FEATURE_TOOL_MAP["docs"] = ["github_search_docs"]
```

### Priority 5: Multi-Repository Support (Low Priority)

Support multiple repositories in single server instance:

```python
# Configuration
ALLOWED_REPOS = os.getenv("ALLOWED_REPOS", "").split(",")
# Example: "jgtolentino/insightpulse-odoo,jgtolentino/other-repo"

def parse_project_param(project: str) -> tuple[str, str]:
    """Parse and validate project parameter."""
    if "/" in project:
        owner, repo = project.split("/", 1)

        # Validate against allowed repos
        if ALLOWED_REPOS and f"{owner}/{repo}" not in ALLOWED_REPOS:
            raise HTTPException(
                status_code=403,
                detail=f"Repository {owner}/{repo} not allowed"
            )

        return owner, repo

    raise HTTPException(status_code=400, detail="Invalid project format")
```

## Implementation Roadmap

### Phase 1: Security Enhancements (Week 1)
- ✅ OAuth 2.0 implementation (COMPLETED)
- ⏳ Read-only mode parameter
- ⏳ Protected branch validation
- ⏳ Destructive operation categorization

### Phase 2: Enhanced Tooling (Week 2)
- ⏳ Documentation search tool
- ⏳ Branch awareness parameters
- ⏳ Repository validation
- ⏳ Enhanced error messages

### Phase 3: Advanced Features (Week 3)
- ⏳ Manual tool approval gates
- ⏳ Multi-repository support
- ⏳ Usage analytics
- ⏳ Rate limiting per project

### Phase 4: Production Hardening (Week 4)
- ⏳ Redis token storage (replace in-memory)
- ⏳ Database OAuth storage
- ⏳ Comprehensive logging
- ⏳ Monitoring and alerting

## Configuration Examples

### Minimal (Read-Only, Single Feature)
```
https://insightpulseai.net/mcp/github?project=owner/repo&features=pr&read_only=true
```
- Only PR listing
- No destructive operations
- Safe for production use

### Standard (Development Workflow)
```
https://insightpulseai.net/mcp/github?project=owner/repo&features=branches,pr,commits&branch=feat/*
```
- Branch operations
- PR management
- Commits to feature branches only
- Main branch protected

### Full Access (Admin Operations)
```
https://insightpulseai.net/mcp/github?project=owner/repo&features=all&read_only=false
```
- All tools enabled
- Full write access
- No restrictions

### CI/CD Integration
```
https://insightpulseai.net/mcp/github?project=owner/repo&features=workflows,pr&read_only=true
```
- Workflow triggering
- PR status checking
- No code modifications

## Lessons from Supabase MCP

### 1. Feature Organization Matters
Group tools logically to help users understand capabilities and control access granularly.

### 2. Security is Paramount
Multi-layer security (scoping, read-only, approvals) reduces risk from prompt injection and unauthorized access.

### 3. Documentation is a Tool
Treat documentation search as a first-class MCP tool for AI assistant discoverability.

### 4. Cost Transparency Builds Trust
When operations have costs, make pricing explicit and require confirmation.

### 5. Development Isolation is Critical
Support safe testing environments (branches, sandboxes) to prevent production damage.

## Conclusion

**Supabase MCP Strengths**:
- Comprehensive feature groups (8 groups, 30+ tools)
- Multi-tenant security model
- Read-only mode and branch awareness
- Development branch support
- Cost estimation and confirmation

**InsightPulse GitHub MCP Strengths**:
- Clean OAuth 2.0 implementation
- Query parameter filtering
- Multi-client support (Claude Code, Cursor, ChatGPT)
- Focused GitHub operations
- Simple single-repository model

**Recommended Next Steps**:
1. ✅ Implement read-only mode (high impact, low effort)
2. ✅ Add branch awareness (medium impact, medium effort)
3. ✅ Create documentation search tool (medium impact, low effort)
4. Consider manual approval gates (low impact, high effort)
5. Plan multi-repository support (low priority, medium effort)

The InsightPulse GitHub MCP server has a solid foundation with OAuth 2.0 support. Adding Supabase-inspired security features (read-only mode, branch awareness) will significantly enhance production readiness while maintaining simplicity.
