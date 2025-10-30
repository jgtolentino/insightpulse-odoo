# Feature to Tool Mapping

Complete mapping of features to MCP tools for query parameter configuration.

## Overview

The `features` query parameter filters available MCP tools. This document provides the complete mapping between feature names and their corresponding GitHub operation tools.

## Feature Categories

### Branch Operations (`branches`)

**Feature Parameter**: `branches`

**Tools**:
- `github_create_branch` - Create a new branch from base branch
- `github_list_branches` - List all repository branches

**Use Cases**:
- Feature branch workflows
- Branch management
- Git flow operations

**Example URL**:
```
?features=branches
```

**Example Operations**:
```
"Create a new branch called feat/new-feature from main"
"List all branches in the repository"
```

---

### Commit Operations (`commits`)

**Feature Parameter**: `commits`

**Tools**:
- `github_commit_files` - Commit multiple files to a branch

**Use Cases**:
- Code changes
- File modifications
- Multi-file commits

**Example URL**:
```
?features=commits
```

**Example Operations**:
```
"Commit these 3 files to feat/new-feature with message 'Add feature'"
"Commit changes to main branch"
```

---

### Issue Management (`issues`)

**Feature Parameter**: `issues`

**Tools**:
- `github_create_issue` - Create a new GitHub issue
- `github_list_issues` - List repository issues with filters

**Use Cases**:
- Bug reporting
- Feature requests
- Task tracking

**Example URL**:
```
?features=issues
```

**Example Operations**:
```
"Create an issue titled 'Bug: Login fails' with description..."
"List all open issues"
"List issues labeled 'bug'"
```

---

### Pull Request Workflow (`pr`)

**Feature Parameter**: `pr`

**Tools**:
- `github_create_pr` - Create a pull request
- `github_list_prs` - List pull requests with state filters
- `github_merge_pr` - Merge a pull request

**Use Cases**:
- Code review workflow
- Feature integration
- Collaborative development

**Example URL**:
```
?features=pr
```

**Example Operations**:
```
"Create a pull request for feat/new-feature"
"List all open pull requests"
"Merge pull request #42"
```

---

### Workflow Automation (`workflows`)

**Feature Parameter**: `workflows`

**Tools**:
- `github_trigger_workflow` - Trigger GitHub Actions workflow

**Use Cases**:
- CI/CD automation
- Deployment triggers
- Automated testing

**Example URL**:
```
?features=workflows
```

**Example Operations**:
```
"Trigger the digitalocean-deploy workflow on main branch"
"Run the CI workflow with force-rebuild input"
```

---

### Code Search (`search`)

**Feature Parameter**: `search`

**Tools**:
- `github_search_code` - Search code in repository

**Use Cases**:
- Code analysis
- Pattern finding
- Implementation discovery

**Example URL**:
```
?features=search
```

**Example Operations**:
```
"Search for 'FastAPI' in the codebase"
"Find all files that import 'pandas'"
"Search for function definitions matching 'calculate'"
```

---

### File Operations (`files`)

**Feature Parameter**: `files`

**Tools**:
- `github_read_file` - Read file contents from repository

**Use Cases**:
- Documentation review
- Code reading
- Configuration inspection

**Example URL**:
```
?features=files
```

**Example Operations**:
```
"Read the contents of README.md"
"Show me the main configuration file"
"Read services/mcp-server/server.py"
```

---

## Complete Mapping Table

| Feature | Tool Name | Description | Read/Write |
|---------|-----------|-------------|------------|
| `branches` | `github_create_branch` | Create new branch from base | Write |
| `branches` | `github_list_branches` | List all repository branches | Read |
| `commits` | `github_commit_files` | Commit multiple files to branch | Write |
| `issues` | `github_create_issue` | Create a new GitHub issue | Write |
| `issues` | `github_list_issues` | List issues with filters | Read |
| `pr` | `github_create_pr` | Create a pull request | Write |
| `pr` | `github_list_prs` | List PRs with state filters | Read |
| `pr` | `github_merge_pr` | Merge a pull request | Write |
| `workflows` | `github_trigger_workflow` | Trigger GitHub Actions workflow | Write |
| `search` | `github_search_code` | Search code in repository | Read |
| `files` | `github_read_file` | Read file contents | Read |

---

## Common Feature Combinations

### Full Development
**Features**: `branches,commits,issues,pr,workflows,search,files`
**Tools**: All 11 tools
**Use Case**: Complete development workflow

### Read-Only
**Features**: `search,files`
**Tools**: 2 tools (github_search_code, github_read_file)
**Use Case**: Code analysis, documentation, research

### Development (No Workflows)
**Features**: `branches,commits,issues,pr,search,files`
**Tools**: 10 tools (all except workflow trigger)
**Use Case**: Standard development without CI/CD access

### Code Review
**Features**: `pr,search,files`
**Tools**: 5 tools (PR operations, search, read files)
**Use Case**: Review pull requests, analyze code

### CI/CD
**Features**: `workflows,pr`
**Tools**: 4 tools (trigger workflows, PR operations)
**Use Case**: Automated deployments, workflow management

### Issue Triage
**Features**: `issues,search,files`
**Tools**: 4 tools (issue management, code search, file reading)
**Use Case**: Bug tracking, feature requests

---

## Read vs Write Operations

### Read-Only Features
- `search` - Code search (no modifications)
- `files` - File reading (no modifications)
- List operations within other features:
  - `github_list_branches`
  - `github_list_issues`
  - `github_list_prs`

### Write Operations
- `branches` - Create branches (write)
- `commits` - Commit files (write)
- `issues` - Create issues (write)
- `pr` - Create/merge PRs (write)
- `workflows` - Trigger workflows (write)

---

## Security Recommendations

### Development Environment
```
features=branches,commits,issues,pr,workflows,search,files
```
**Rationale**: Full access for development and testing

### Staging Environment
```
features=workflows,pr,search,files
```
**Rationale**: Trigger deployments, manage PRs, analyze code

### Production Environment
```
features=search,files
```
**Rationale**: Read-only access for monitoring and analysis

### External Contributors
```
features=issues,search,files
```
**Rationale**: Report bugs, search code, read documentation (no code changes)

---

## Implementation Details

### Server-Side Filtering

The MCP server implements feature filtering in `server.py`:

```python
FEATURE_TOOL_MAP = {
    "branches": ["github_create_branch", "github_list_branches"],
    "commits": ["github_commit_files"],
    "issues": ["github_create_issue", "github_list_issues"],
    "pr": ["github_create_pr", "github_list_prs", "github_merge_pr"],
    "workflows": ["github_trigger_workflow"],
    "search": ["github_search_code"],
    "files": ["github_read_file"]
}
```

### Validation Logic

1. Parse `features` query parameter
2. Split by comma, trim whitespace
3. Lowercase each feature
4. Look up tools in `FEATURE_TOOL_MAP`
5. Return enabled tools
6. If no valid features, enable all tools (fallback)

### Tool Access Control

```
Client Request → Query Params → Feature List → Tool Filter → Available Tools
```

**Example**:
```
?features=branches,commits
→ ["branches", "commits"]
→ ["github_create_branch", "github_list_branches", "github_commit_files"]
→ Only these 3 tools available for tools/list and tools/call
```

---

## Testing Feature Mapping

### Test All Features
```bash
curl -X POST "https://insightpulseai.net/mcp/github?features=branches,commits,issues,pr,workflows,search,files" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

**Expected**: All 11 tools listed

### Test Single Feature
```bash
curl -X POST "https://insightpulseai.net/mcp/github?features=branches" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

**Expected**: Only 2 branch tools listed

### Test Invalid Feature
```bash
curl -X POST "https://insightpulseai.net/mcp/github?features=invalid" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

**Expected**: All tools (fallback behavior)

---

## Future Features

Planned additions to feature mapping:

- `comments` - PR and issue comments
- `reviews` - PR review operations
- `releases` - Release management
- `tags` - Git tag operations
- `webhooks` - Webhook management
- `actions` - GitHub Actions management (beyond triggering)

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0
