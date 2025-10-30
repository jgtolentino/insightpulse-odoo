# ChatGPT Custom GPT Setup Guide

Configure a ChatGPT Custom GPT to use the InsightPulse GitHub MCP Server.

## Prerequisites

- ChatGPT Plus or Enterprise subscription
- Access to Custom GPT creation (GPT Builder)

## Installation

### Step 1: Create Custom GPT

1. Go to [ChatGPT](https://chat.openai.com)
2. Click your profile → "My GPTs"
3. Click "+ Create a GPT"
4. Choose "Configure" tab

### Step 2: Configure Basic Settings

**Name**: `InsightPulse GitHub Assistant`

**Description**:
```
GitHub operations assistant for the InsightPulse Odoo repository. Can create branches, commits, pull requests, issues, and trigger workflows via the pulser-hub GitHub App.
```

**Instructions**:
```
You are a GitHub operations assistant for the InsightPulse Odoo SaaS Platform repository (jgtolentino/insightpulse-odoo).

You have access to GitHub operations through the InsightPulse MCP Server via the pulser-hub GitHub App.

## Available Operations
- **Branch Management**: Create branches, list branches
- **Commits**: Commit multiple files to branches
- **Pull Requests**: Create, list, and merge pull requests
- **Issues**: Create and list GitHub issues
- **Workflows**: Trigger GitHub Actions workflows
- **Code Search**: Search code in the repository
- **File Operations**: Read file contents from repository

## Default Repository
jgtolentino/insightpulse-odoo

## Usage Guidelines
1. Always confirm destructive operations (merge PR, delete branch) before executing
2. Use descriptive commit messages and PR titles
3. Include relevant context when creating issues or PRs
4. Search code before making changes to understand existing patterns
5. Read files to understand current state before modifying

## Response Format
- Provide clear confirmation of completed operations
- Include relevant URLs (PR links, commit SHAs, etc.)
- Suggest next steps when appropriate
- Explain what was done and why

When the user requests GitHub operations, use the available MCP tools to perform the requested actions.
```

**Conversation Starters**:
```
Create a new feature branch for...
List all open pull requests
Search the codebase for...
Read the contents of...
Trigger the deployment workflow
Create an issue for...
```

### Step 3: Add Actions (OpenAPI Specification)

1. Scroll to "Actions" section
2. Click "Create new action"
3. Choose "Import from URL" or "Paste OpenAPI schema"
4. Paste the contents of `openapi.json` (see below)
5. Click "Test" to verify connection
6. Click "Save"

**OpenAPI Schema**: Use the `openapi.json` file in this directory

**Authentication**: None (server uses GitHub App authentication)

**Privacy Policy**: https://insightpulseai.net/privacy (if required)

### Step 4: Configure Action Settings

**Action Name**: InsightPulse GitHub MCP

**Description**: GitHub operations via Model Context Protocol

**Server URL**: https://insightpulseai.net

**Authentication**: None

### Step 5: Test Custom GPT

Try these test prompts:

```
"List all available GitHub tools"
"What branches exist in the repository?"
"Search for 'FastAPI' in the codebase"
"Read the README.md file"
```

### Step 6: Publish (Optional)

1. Set visibility: "Only me" or "Anyone with a link"
2. Click "Save" in top right
3. Copy link to share with team

## Query Parameters

Customize the MCP server behavior with query parameters:

**Change Default Repository**:
```
/mcp/github?project=myorg/myrepo
```

**Limit Features**:
```
/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,pr
```

**Read-Only Mode**:
```
/mcp/github?project=jgtolentino/insightpulse-odoo&features=search,files
```

To use custom query parameters, update the `servers.url` in the OpenAPI specification before importing.

## Available Features

| Feature | Tools | Description |
|---------|-------|-------------|
| `branches` | `github_create_branch`, `github_list_branches` | Branch operations |
| `commits` | `github_commit_files` | Committing files |
| `issues` | `github_create_issue`, `github_list_issues` | Issue management |
| `pr` | `github_create_pr`, `github_list_prs`, `github_merge_pr` | Pull requests |
| `workflows` | `github_trigger_workflow` | GitHub Actions |
| `search` | `github_search_code` | Code search |
| `files` | `github_read_file` | Read files |

## Example Conversations

### Create a Feature Branch and PR

**User**: "Create a new branch called feat/mcp-ui from main, then create a PR for it"

**GPT**:
```
I'll create the branch and PR for you.

1. Creating branch feat/mcp-ui from main...
   ✅ Branch created: feat/mcp-ui (SHA: abc123)

2. Creating pull request...
   ✅ PR created: #42 "Add MCP UI"
   URL: https://github.com/jgtolentino/insightpulse-odoo/pull/42

The PR is now open and ready for review. Would you like me to:
- Add specific content to the PR description?
- Trigger a workflow to test the changes?
- List related open issues?
```

### Search and Modify Code

**User**: "Search for all files that import FastAPI and read the main server file"

**GPT**:
```
Searching for FastAPI imports...

Found 3 files:
1. services/mcp-server/server.py
2. services/api/main.py
3. tests/test_api.py

Reading services/mcp-server/server.py...

[File contents displayed]

This is the main MCP server implementation. Would you like me to:
- Create a branch to make changes?
- Search for specific patterns in this file?
- Read one of the other FastAPI files?
```

## Troubleshooting

### Action Not Working

**Symptom**: ChatGPT can't call GitHub operations

**Solutions**:
1. Verify OpenAPI schema is correctly imported
2. Test the endpoint manually: `curl https://insightpulseai.net/health`
3. Check that MCP server is deployed
4. Re-import the OpenAPI specification
5. Try deleting and recreating the action

### Tools Not Available

**Symptom**: GPT says certain operations aren't available

**Solutions**:
1. Check the `features` parameter in server URL
2. Verify the OpenAPI schema includes all operations
3. Test the MCP endpoint directly with curl
4. Check server logs for errors

### Timeout Errors

**Symptom**: Operations time out

**Solutions**:
1. Verify MCP server is running: `curl https://insightpulseai.net/health`
2. Check DigitalOcean App Platform status
3. Try with a simpler operation first (e.g., list branches)
4. Contact support if persistent

## Advanced Configuration

### Multiple Repositories

Create separate Custom GPTs for different repositories:

**GPT 1**: InsightPulse GitHub (jgtolentino/insightpulse-odoo)
**GPT 2**: Other Project GitHub (otherorg/otherrepo)

Each with its own `project=` parameter in the OpenAPI server URL.

### Feature-Specific GPTs

Create specialized GPTs for specific workflows:

**CI/CD GPT**: Only `workflows` and `pr` features
**Code Review GPT**: Only `search`, `files`, and `pr` features
**Issue Triage GPT**: Only `issues` and `search` features

Update the `features` parameter in the OpenAPI server URL for each.

## Security

- **Authentication**: MCP server uses pulser-hub GitHub App
- **Authorization**: GitHub App permissions control allowed operations
- **No Tokens**: No GitHub tokens needed in Custom GPT configuration
- **Audit Trail**: All operations logged by MCP server
- **Scope Control**: Features parameter limits available operations

## Limitations

- ChatGPT Custom GPTs have rate limits (varies by subscription)
- Large file operations may timeout
- No support for file uploads (use commits instead)
- PR review comments not directly supported (create via issues)

## Support

- **MCP Server Documentation**: [../../README.md](../../README.md)
- **Query Parameters**: [../../docs/QUERY_PARAMETERS.md](../../docs/QUERY_PARAMETERS.md)
- **Feature Mapping**: [../../docs/FEATURE_MAPPING.md](../../docs/FEATURE_MAPPING.md)
- **GitHub Issues**: [https://github.com/jgtolentino/insightpulse-odoo/issues](https://github.com/jgtolentino/insightpulse-odoo/issues)

## Tips

1. **Test First**: Start with read-only operations (search, read files)
2. **Be Specific**: Provide clear repository context in prompts
3. **Confirm Actions**: Ask GPT to confirm before merging PRs or triggering workflows
4. **Chain Operations**: Combine operations in single prompts (e.g., "create branch, commit files, create PR")
5. **Use Examples**: Show GPT examples of good commit messages/PR descriptions
6. **Monitor Usage**: Check MCP server logs to see which operations are being used

## Example OpenAPI URL Configuration

If you want to use custom query parameters, modify the OpenAPI specification before importing:

```json
{
  "servers": [
    {
      "url": "https://insightpulseai.net/mcp/github?project=myorg/myrepo&features=branches,commits,pr"
    }
  ]
}
```

Or keep the base URL and add query parameters dynamically in the Custom GPT instructions.
