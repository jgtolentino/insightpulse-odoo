# GitHub API Integration Development

**Skill ID:** `github-api-integration`
**Version:** 1.0.0
**Category:** GitHub Developer Program, API Integration
**Expertise Level:** Expert

---

## 🎯 Purpose

This skill enables AI agents to build robust integrations with GitHub's REST and GraphQL APIs, following GitHub Developer Program best practices for authentication, rate limiting, pagination, and error handling.

### Key Capabilities
- GitHub REST API v3 integration
- GitHub GraphQL API v4 queries and mutations
- OAuth App and GitHub App authentication
- Rate limiting and pagination handling
- Webhook payload processing
- API versioning and deprecation management

---

## 🧠 Core Competencies

### 1. GitHub REST API Integration

#### Authentication Methods
```python
# scripts/github_api/auth.py
import os
import requests
from typing import Optional

class GitHubAPIClient:
    """GitHub API client with multiple auth strategies"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }

    def get(self, endpoint: str, params: dict = None):
        """Make authenticated GET request with rate limit handling"""
        response = requests.get(
            f'{self.base_url}{endpoint}',
            headers=self.headers,
            params=params
        )

        # Check rate limit
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            raise Exception(f'Rate limited. Resets at {reset_time}')

        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict):
        """Make authenticated POST request"""
        response = requests.post(
            f'{self.base_url}{endpoint}',
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
```

#### Pagination Handling
```python
# scripts/github_api/pagination.py
from typing import Generator, Dict, Any

def paginate_all(client: GitHubAPIClient, endpoint: str, per_page: int = 100) -> Generator[Dict[Any, Any], None, None]:
    """Iterate through all pages of a paginated endpoint"""
    page = 1
    while True:
        items = client.get(endpoint, params={'per_page': per_page, 'page': page})
        if not items:
            break

        for item in items:
            yield item

        page += 1

        # Stop if we got fewer items than requested (last page)
        if len(items) < per_page:
            break

# Usage example
client = GitHubAPIClient()
for repo in paginate_all(client, '/orgs/jgtolentino/repos'):
    print(f"Repository: {repo['name']}")
```

### 2. GitHub GraphQL API Integration

#### GraphQL Query Builder
```python
# scripts/github_api/graphql.py
import requests
from typing import Dict, Any

class GitHubGraphQL:
    """GitHub GraphQL API v4 client"""

    def __init__(self, token: str):
        self.token = token
        self.endpoint = 'https://api.github.com/graphql'
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def query(self, query_string: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        payload = {
            'query': query_string,
            'variables': variables or {}
        }

        response = requests.post(
            self.endpoint,
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()

        data = response.json()
        if 'errors' in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        return data['data']

# Example: Fetch repository issues with labels
ISSUES_QUERY = """
query($owner: String!, $name: String!, $labels: [String!]) {
  repository(owner: $owner, name: $name) {
    issues(first: 50, labels: $labels, states: OPEN) {
      nodes {
        number
        title
        author {
          login
        }
        labels(first: 10) {
          nodes {
            name
          }
        }
        createdAt
      }
    }
  }
}
"""

client = GitHubGraphQL(token=os.getenv('GITHUB_TOKEN'))
result = client.query(ISSUES_QUERY, {
    'owner': 'jgtolentino',
    'name': 'insightpulse-odoo',
    'labels': ['bug', 'urgent']
})
```

### 3. Rate Limiting and Retry Logic

#### Exponential Backoff
```python
# scripts/github_api/retry.py
import time
from functools import wraps
from typing import Callable

def retry_with_backoff(max_retries: int = 4, base_delay: int = 2):
    """Decorator for exponential backoff retry logic"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise

                    delay = base_delay ** attempt
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"   Retrying in {delay}s...")
                    time.sleep(delay)

        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=4, base_delay=2)
def fetch_repo_info(owner: str, repo: str):
    client = GitHubAPIClient()
    return client.get(f'/repos/{owner}/{repo}')
```

### 4. GitHub App Authentication

#### Installation Token Generation
```python
# scripts/github_api/github_app.py
import jwt
import time
import requests
from typing import Dict

class GitHubApp:
    """GitHub App authentication and installation management"""

    def __init__(self, app_id: str, private_key: str):
        self.app_id = app_id
        self.private_key = private_key

    def generate_jwt(self) -> str:
        """Generate JWT for GitHub App authentication"""
        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + 600,  # 10 minutes
            'iss': self.app_id
        }

        return jwt.encode(payload, self.private_key, algorithm='RS256')

    def get_installation_token(self, installation_id: str) -> str:
        """Get installation access token"""
        jwt_token = self.generate_jwt()

        response = requests.post(
            f'https://api.github.com/app/installations/{installation_id}/access_tokens',
            headers={
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {jwt_token}',
                'X-GitHub-Api-Version': '2022-11-28'
            }
        )
        response.raise_for_status()

        return response.json()['token']

# Usage
app = GitHubApp(
    app_id=os.getenv('GITHUB_APP_ID'),
    private_key=open('github-app-private-key.pem').read()
)
installation_token = app.get_installation_token('12345678')
```

### 5. Webhook Processing

#### Webhook Signature Verification
```python
# scripts/github_api/webhooks.py
import hmac
import hashlib
from typing import Dict, Any

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature"""
    expected_signature = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)

def process_webhook(payload: Dict[str, Any], event_type: str) -> Dict[str, Any]:
    """Process GitHub webhook events"""
    handlers = {
        'push': handle_push_event,
        'pull_request': handle_pr_event,
        'issues': handle_issue_event,
        'release': handle_release_event
    }

    handler = handlers.get(event_type)
    if not handler:
        return {'status': 'ignored', 'reason': f'No handler for {event_type}'}

    return handler(payload)

def handle_push_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle push webhook event"""
    ref = payload['ref']
    commits = payload['commits']

    print(f"📦 Push to {ref}: {len(commits)} commits")

    # Example: Trigger deployment on main branch push
    if ref == 'refs/heads/main':
        trigger_deployment()

    return {'status': 'processed', 'action': 'deployment_triggered'}
```

---

## ✅ Validation Criteria

### API Integration Quality
- ✅ Proper authentication (OAuth, GitHub App, PAT)
- ✅ Rate limit handling with exponential backoff
- ✅ Pagination for all list endpoints
- ✅ Error handling with meaningful messages
- ✅ API versioning headers included

### Performance Metrics
- ✅ <100ms response time for cached data
- ✅ <5s for complex GraphQL queries
- ✅ 99.9% uptime for webhook processing
- ✅ <1% rate limit exceeded errors

---

## 🎯 Usage Examples

### Example 1: Fetch All Repository Issues
```python
# Fetch all open issues with pagination
client = GitHubAPIClient()
all_issues = list(paginate_all(client, '/repos/jgtolentino/insightpulse-odoo/issues', per_page=100))

print(f"Total open issues: {len(all_issues)}")
for issue in all_issues:
    print(f"#{issue['number']}: {issue['title']}")
```

### Example 2: Create Pull Request with GraphQL
```python
CREATE_PR_MUTATION = """
mutation($input: CreatePullRequestInput!) {
  createPullRequest(input: $input) {
    pullRequest {
      number
      url
      title
    }
  }
}
"""

client = GitHubGraphQL(token=os.getenv('GITHUB_TOKEN'))
result = client.query(CREATE_PR_MUTATION, {
    'input': {
        'repositoryId': 'R_kgDOH...',
        'baseRefName': 'main',
        'headRefName': 'feature-branch',
        'title': 'Add new feature',
        'body': 'This PR adds...'
    }
})

print(f"Created PR #{result['createPullRequest']['pullRequest']['number']}")
```

### Example 3: Process Webhook with FastAPI
```python
from fastapi import FastAPI, Request, HTTPException, Header
import os

app = FastAPI()

WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

@app.post('/webhooks/github')
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None)
):
    payload = await request.body()

    # Verify signature
    if not verify_webhook_signature(payload, x_hub_signature_256, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail='Invalid signature')

    # Process event
    result = process_webhook(await request.json(), x_github_event)

    return result
```

---

## 📊 Success Metrics

### Integration Effectiveness
- **API Call Success Rate**: >99.5%
- **Average Response Time**: <200ms
- **Rate Limit Utilization**: <80%
- **Webhook Processing Time**: <1s

### Developer Experience
- **Setup Time**: <5 minutes
- **Documentation Coverage**: 100%
- **Error Recovery**: Automatic
- **Code Reusability**: 90%+

---

## 🔗 Related Skills
- `github-apps-development` - Building GitHub Apps
- `github-actions-workflows` - CI/CD automation
- `github-webhooks-integration` - Event-driven integrations

---

## 📚 References

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub GraphQL API Documentation](https://docs.github.com/en/graphql)
- [GitHub Developer Program](https://docs.github.com/developers/overview/github-developer-program)
- [API Versioning Guide](https://docs.github.com/en/rest/overview/api-versions)

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
