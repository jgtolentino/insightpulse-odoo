# Pulser Hub Sync - API Usage Guide

Complete guide for programmatic GitHub operations via pulser-hub.

## Table of Contents

1. [Quick Start](#quick-start)
2. [REST API Endpoints](#rest-api-endpoints)
3. [Odoo Shell Usage](#odoo-shell-usage)
4. [ChatGPT Integration](#chatgpt-integration)
5. [Examples](#examples)

---

## Quick Start

### Prerequisites

1. ✅ GitHub App "pulser-hub" installed on target repositories
2. ✅ `pulser_hub_sync` module installed in Odoo
3. ✅ At least one integration record exists (created on first installation)

### Get Your Installation ID

**Via Odoo Shell:**
```python
integration = env['github.integration'].search([('account_login', '=', 'jgtolentino')], limit=1)
print(f"Installation ID: {integration.installation_id}")
print(f"Account: {integration.account_login}")
```

**Via GitHub:**
- Visit: https://github.com/settings/installations
- Click on "pulser-hub" installation
- URL contains installation ID: `https://github.com/settings/installations/12345678`

---

## REST API Endpoints

Base URL: `https://insightpulseai.net` (or your Odoo domain)

### 1. Health Check

**Endpoint:** `GET /odoo/github/health`

**Response:**
```json
{
  "status": "ok",
  "service": "pulser-hub-sync",
  "timestamp": "2025-10-28T12:34:56.789Z"
}
```

**Usage:**
```bash
curl https://insightpulseai.net/odoo/github/health
```

---

### 2. Create GitHub Issue

**Endpoint:** `POST /pulser/issue`

**Request Body:**
```json
{
  "owner": "jgtolentino",
  "repo": "insightpulse-odoo",
  "title": "Bug: Login fails with 2FA enabled",
  "body": "## Description\n\nUsers report login failures when 2FA is enabled.\n\n## Steps to Reproduce\n1. Enable 2FA\n2. Attempt login\n3. See error\n\n## Expected\nSuccessful login\n\n## Actual\nError 500",
  "labels": ["bug", "urgent"],
  "assignees": ["jgtolentino"]
}
```

**Response:**
```json
{
  "status": "success",
  "issue_number": 42,
  "url": "https://github.com/jgtolentino/insightpulse-odoo/issues/42",
  "api_url": "https://api.github.com/repos/jgtolentino/insightpulse-odoo/issues/42"
}
```

**cURL Example:**
```bash
curl -X POST https://insightpulseai.net/pulser/issue \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "jgtolentino",
    "repo": "insightpulse-odoo",
    "title": "Automated issue from pulser-hub",
    "body": "This issue was created programmatically.",
    "labels": ["automation"]
  }'
```

---

### 3. Commit File to GitHub

**Endpoint:** `POST /pulser/commit`

**Request Body:**
```json
{
  "owner": "jgtolentino",
  "repo": "insightpulse-odoo",
  "path": "docs/API_CHANGELOG.md",
  "content": "# API Changelog\n\n## 2025-10-28\n- Added new endpoint for bulk operations\n- Fixed authentication bug",
  "message": "docs: update API changelog",
  "branch": "main"
}
```

**Response:**
```json
{
  "status": "success",
  "commit_sha": "abc123def456...",
  "url": "https://github.com/jgtolentino/insightpulse-odoo/commit/abc123def456",
  "content_url": "https://github.com/jgtolentino/insightpulse-odoo/blob/main/docs/API_CHANGELOG.md"
}
```

**cURL Example:**
```bash
curl -X POST https://insightpulseai.net/pulser/commit \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "jgtolentino",
    "repo": "insightpulse-odoo",
    "path": "README.md",
    "content": "# InsightPulse Odoo\n\nManaged by pulser-hub",
    "message": "Update README via pulser-hub"
  }'
```

---

## Odoo Shell Usage

### Connect to Odoo Shell

```bash
# Docker
docker exec -it odoo-bundle odoo shell -d odoo -c /etc/odoo/odoo.conf

# System installation
odoo shell -d odoo -c /etc/odoo/odoo.conf
```

### Get Integration

```python
# By account login
integration = env['github.integration'].search([
    ('account_login', '=', 'jgtolentino')
], limit=1)

# Or by installation ID
integration = env['github.integration'].search([
    ('installation_id', '=', '12345678')
], limit=1)

# Helper method (auto-detect from owner/repo)
integration = env['github.integration'].get_integration_for_repo('jgtolentino', 'insightpulse-odoo')

# Or with full repo name
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')
```

### Create Issue

```python
# Get integration
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')

# Create issue
result = integration.create_issue(
    owner='jgtolentino',
    repo='insightpulse-odoo',
    title='Automated deployment failed',
    body='''## Deployment Error

The automated deployment to production failed at 2025-10-28 12:34:56 UTC.

### Error Details
```
HTTP 500 Internal Server Error
Database connection failed
```

### Action Required
- [ ] Check database credentials
- [ ] Verify server connectivity
- [ ] Review deployment logs
''',
    labels=['deployment', 'urgent'],
    assignees=['jgtolentino']
)

print(f"Created issue #{result['number']}: {result['html_url']}")
```

### Commit File

```python
# Get integration
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')

# Commit new file
result = integration.commit_file(
    owner='jgtolentino',
    repo='insightpulse-odoo',
    path='logs/deployment-2025-10-28.log',
    content='''Deployment Log - 2025-10-28

12:34:56 - Starting deployment
12:35:02 - Building Docker image
12:36:15 - Pushing to registry
12:37:30 - Deploying to production
12:38:45 - Health check passed
12:39:00 - Deployment complete
''',
    message='logs: add deployment log for 2025-10-28',
    branch='main'
)

print(f"Committed: {result['commit']['html_url']}")
```

### Update Existing File

```python
# Get integration
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')

# Update existing file (automatically handles SHA)
result = integration.commit_file(
    owner='jgtolentino',
    repo='insightpulse-odoo',
    path='VERSION',
    content='19.0.20251028\n',
    message='chore: bump version to 19.0.20251028',
    branch='main'
)

print(f"Updated: {result['commit']['html_url']}")
```

---

## ChatGPT Integration

### Setup Instructions

1. **Configure in ChatGPT Custom Instructions:**

Add to "How would you like ChatGPT to respond?":

```
When I request GitHub operations, use these endpoints:

Base URL: https://insightpulseai.net

CREATE ISSUE:
POST /pulser/issue
{
  "owner": "jgtolentino",
  "repo": "insightpulse-odoo",
  "title": "Issue title",
  "body": "Issue description",
  "labels": ["label1", "label2"],
  "assignees": ["username"]
}

COMMIT FILE:
POST /pulser/commit
{
  "owner": "jgtolentino",
  "repo": "insightpulse-odoo",
  "path": "path/to/file.md",
  "content": "File content",
  "message": "Commit message"
}
```

2. **Example ChatGPT Prompts:**

```
"Create a GitHub issue in insightpulse-odoo titled 'Fix login bug' with label 'bug'"

"Commit a new file docs/DEPLOYMENT.md with deployment instructions to insightpulse-odoo"

"Update the VERSION file in insightpulse-odoo to 19.0.20251028"
```

---

## Examples

### Example 1: Automated Bug Report

```python
# Odoo shell
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')

result = integration.create_issue(
    owner='jgtolentino',
    repo='insightpulse-odoo',
    title='[AUTO] HTTP 500 detected on production',
    body=f'''## Automated Bug Report

**Timestamp:** {datetime.utcnow().isoformat()}Z
**Severity:** High
**Source:** Production monitoring

### Error Details
HTTP 500 Internal Server Error detected on `/web/login` endpoint.

### Impact
- Users unable to login
- Approximately 15 failed requests in last 5 minutes

### Suggested Actions
1. Check Odoo logs: `docker logs odoo-bundle`
2. Verify database connectivity
3. Review recent deployments

**Auto-generated by pulser-hub monitoring**
''',
    labels=['bug', 'production', 'automated'],
    assignees=['jgtolentino']
)

print(f"Bug report filed: {result['html_url']}")
```

### Example 2: Deployment Log Commit

```python
# Odoo shell
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')

# Generate deployment log
log_content = f'''# Deployment Log

**Date:** {datetime.utcnow().isoformat()}Z
**Environment:** Production
**Version:** 19.0.20251028

## Changes Deployed
- Fixed authentication bug (#42)
- Updated dashboard widgets
- Improved performance

## Deployment Steps
1. ✅ Database backup completed
2. ✅ Docker image built
3. ✅ Deployed to production
4. ✅ Health checks passed
5. ✅ Smoke tests successful

## Metrics
- Deployment time: 3m 45s
- Downtime: 0s (zero-downtime)
- Error rate: 0%

**Status:** SUCCESS ✅
'''

result = integration.commit_file(
    owner='jgtolentino',
    repo='insightpulse-odoo',
    path=f'logs/deployments/{datetime.utcnow().strftime("%Y-%m-%d")}.md',
    content=log_content,
    message=f'logs: deployment log for {datetime.utcnow().strftime("%Y-%m-%d")}'
)

print(f"Log committed: {result['commit']['html_url']}")
```

### Example 3: Documentation Update

```python
# Odoo shell
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')

# Update API documentation
api_docs = '''# API Documentation

## Authentication

All API endpoints use GitHub App authentication via JWT tokens.

## Endpoints

### Create Issue
POST /pulser/issue

### Commit File
POST /pulser/commit

## Rate Limits
- 5,000 requests per hour
- Auto-retry on rate limit

## Support
For issues, contact: support@insightpulseai.net
'''

result = integration.commit_file(
    owner='jgtolentino',
    repo='insightpulse-odoo',
    path='docs/API.md',
    content=api_docs,
    message='docs: update API documentation'
)

print(f"Docs updated: {result['content']['html_url']}")
```

### Example 4: Bulk Operations

```python
# Odoo shell
integration = env['github.integration'].get_integration_for_repo('jgtolentino/insightpulse-odoo')

# Create multiple issues
issues_data = [
    {'title': 'Task 1: Setup CI/CD', 'labels': ['enhancement']},
    {'title': 'Task 2: Add unit tests', 'labels': ['testing']},
    {'title': 'Task 3: Update documentation', 'labels': ['docs']},
]

created_issues = []
for issue_data in issues_data:
    result = integration.create_issue(
        owner='jgtolentino',
        repo='insightpulse-odoo',
        title=issue_data['title'],
        body='Created via pulser-hub automation',
        labels=issue_data['labels']
    )
    created_issues.append(result['html_url'])
    print(f"Created: {result['html_url']}")

# Commit summary file
summary = f'''# Automation Summary

Created {len(created_issues)} issues:
{chr(10).join(f"- {url}" for url in created_issues)}
'''

integration.commit_file(
    owner='jgtolentino',
    repo='insightpulse-odoo',
    path='automation/summary.md',
    content=summary,
    message='automation: add summary of created issues'
)
```

---

## Error Handling

All API endpoints return consistent error format:

```json
{
  "status": "error",
  "message": "Error description here"
}
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `No GitHub integration found` | Account not connected | Install GitHub App on account |
| `Failed to get installation token` | JWT/PEM issue | Check PEM file and permissions |
| `401 Unauthorized` | Token expired | Auto-retry or refresh token |
| `403 Forbidden` | Permission denied | Check GitHub App permissions |
| `404 Not Found` | Repository not accessible | Verify App installation on repo |
| `422 Validation Failed` | Invalid input | Check required fields |

---

## Security Best Practices

1. **API Access Control**: Endpoints use `auth='public'` - consider adding API key authentication for production
2. **Rate Limiting**: GitHub API has rate limits (5,000 requests/hour) - implement caching/batching
3. **PEM Security**: Keep PEM file with 600 permissions, never commit to git
4. **Webhook Secret**: Use strong random secret for webhook verification
5. **Token Storage**: Installation tokens stored encrypted in Odoo database

---

## Troubleshooting

### Test connectivity:
```bash
curl https://insightpulseai.net/odoo/github/health
```

### Test issue creation:
```bash
curl -X POST https://insightpulseai.net/pulser/issue \
  -H "Content-Type: application/json" \
  -d '{"owner":"jgtolentino","repo":"insightpulse-odoo","title":"Test issue"}'
```

### Check Odoo logs:
```bash
docker logs odoo-bundle | grep pulser
```

### Verify integration exists:
```python
# Odoo shell
integrations = env['github.integration'].search([])
for i in integrations:
    print(f"{i.account_login} - Installation ID: {i.installation_id}")
```

---

## Next Steps

- Add authentication middleware for API endpoints
- Implement rate limiting and request validation
- Add PR creation/update capabilities
- Create dashboard for GitHub operations monitoring
- Setup Grafana metrics for API usage

---

**Support**: For issues or questions, create an issue at https://github.com/jgtolentino/insightpulse-odoo/issues
