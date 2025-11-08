# GitHub Webhooks Integration

**Skill ID:** `github-webhooks-integration`
**Version:** 1.0.0
**Category:** GitHub Developer Program, Event-Driven Architecture
**Expertise Level:** Expert

---

## 🎯 Purpose

This skill enables AI agents to build robust, event-driven integrations with GitHub using webhooks, handling real-time events with proper security, reliability, and scalability.

### Key Capabilities
- Webhook endpoint creation and security
- Event payload validation and signature verification
- Event routing and processing
- Retry logic and idempotency handling
- Rate limiting and backpressure management
- Event streaming to message queues (Redis, RabbitMQ, Kafka)
- Monitoring and observability

---

## 🧠 Core Competencies

### 1. Secure Webhook Endpoints

#### FastAPI Webhook Server with Security
```python
# apps/webhook-server/app.py
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel, ValidationError
from typing import Optional, Dict, Any
import hmac
import hashlib
import os
import time
import json
import logging
from functools import wraps

app = FastAPI(title="GitHub Webhook Server")

# Configuration
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
logger = logging.getLogger(__name__)

# Request tracking for idempotency
processed_events = set()

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature using HMAC SHA-256"""
    if not signature:
        return False

    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)

def check_idempotency(event_id: str) -> bool:
    """Check if event has already been processed"""
    if event_id in processed_events:
        logger.warning(f"Duplicate event detected: {event_id}")
        return True

    processed_events.add(event_id)

    # Clean up old events (keep last 10k)
    if len(processed_events) > 10000:
        processed_events.pop()

    return False

def rate_limit(max_requests: int = 100, window: int = 60):
    """Simple rate limiting decorator"""
    requests = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            client_ip = kwargs.get('request').client.host

            # Clean old entries
            requests[client_ip] = [
                ts for ts in requests.get(client_ip, [])
                if now - ts < window
            ]

            if len(requests.get(client_ip, [])) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {max_requests} requests per {window}s"
                )

            requests.setdefault(client_ip, []).append(now)
            return await func(*args, **kwargs)

        return wrapper
    return decorator

@app.get('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'github-webhook-server',
        'timestamp': int(time.time())
    }

@app.post('/webhooks/github')
@rate_limit(max_requests=100, window=60)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    x_github_hook_id: Optional[str] = Header(None),
    x_github_hook_installation_target_id: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint with full security and validation

    Headers:
    - X-Hub-Signature-256: HMAC signature for verification
    - X-GitHub-Event: Event type (push, pull_request, etc.)
    - X-GitHub-Delivery: Unique delivery ID for idempotency
    - X-GitHub-Hook-ID: Webhook configuration ID
    - X-GitHub-Hook-Installation-Target-ID: Installation/org ID
    """

    # Read payload
    payload_bytes = await request.body()

    # Verify signature
    if not verify_signature(payload_bytes, x_hub_signature_256, WEBHOOK_SECRET):
        logger.error(f"Invalid signature for event {x_github_delivery}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Check idempotency
    if check_idempotency(x_github_delivery):
        return {
            'status': 'duplicate',
            'delivery_id': x_github_delivery,
            'message': 'Event already processed'
        }

    # Parse payload
    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Log event
    logger.info(
        f"Received {x_github_event} event",
        extra={
            'event_type': x_github_event,
            'delivery_id': x_github_delivery,
            'hook_id': x_github_hook_id,
            'installation_id': x_github_hook_installation_target_id
        }
    )

    # Process in background to respond quickly (< 10s timeout)
    background_tasks.add_task(
        process_webhook_event,
        event_type=x_github_event,
        payload=payload,
        delivery_id=x_github_delivery
    )

    # Return 200 immediately
    return {
        'status': 'accepted',
        'delivery_id': x_github_delivery,
        'event_type': x_github_event
    }

async def process_webhook_event(
    event_type: str,
    payload: Dict[str, Any],
    delivery_id: str
):
    """Process webhook event asynchronously"""
    try:
        # Route to appropriate handler
        handlers = {
            'push': handle_push_event,
            'pull_request': handle_pull_request_event,
            'issues': handle_issues_event,
            'issue_comment': handle_issue_comment_event,
            'release': handle_release_event,
            'workflow_run': handle_workflow_run_event,
            'check_run': handle_check_run_event,
            'deployment': handle_deployment_event,
            'deployment_status': handle_deployment_status_event,
            'status': handle_status_event,
            'repository': handle_repository_event,
            'star': handle_star_event,
            'watch': handle_watch_event,
            'fork': handle_fork_event
        }

        handler = handlers.get(event_type)
        if handler:
            result = await handler(payload)
            logger.info(
                f"Processed {event_type} event successfully",
                extra={'delivery_id': delivery_id, 'result': result}
            )
        else:
            logger.warning(f"No handler for event type: {event_type}")

    except Exception as e:
        logger.error(
            f"Error processing {event_type} event: {str(e)}",
            extra={'delivery_id': delivery_id},
            exc_info=True
        )

# Event handlers

async def handle_push_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle push events"""
    ref = payload.get('ref')
    commits = payload.get('commits', [])
    repository = payload['repository']['full_name']

    logger.info(f"Push to {repository}:{ref} with {len(commits)} commits")

    # Example: Trigger deployment on main branch
    if ref == 'refs/heads/main':
        # Trigger deployment
        await trigger_deployment(repository, 'main')
        return {'action': 'deployment_triggered'}

    # Example: Update issue status based on commit messages
    for commit in commits:
        message = commit.get('message', '')
        if 'closes #' in message.lower():
            # Extract issue number and close it
            pass

    return {'action': 'processed', 'commits': len(commits)}

async def handle_pull_request_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle pull request events"""
    action = payload.get('action')
    pr = payload['pull_request']
    number = pr['number']
    repository = payload['repository']['full_name']

    logger.info(f"PR #{number} {action} in {repository}")

    if action == 'opened':
        # Auto-assign reviewers
        await assign_reviewers(repository, number)

        # Auto-label based on PR size
        additions = pr.get('additions', 0)
        deletions = pr.get('deletions', 0)
        await auto_label_pr_size(repository, number, additions, deletions)

        return {'action': 'pr_processed', 'reviewers_assigned': True}

    elif action == 'synchronize':
        # PR updated with new commits
        return {'action': 'pr_synchronized'}

    elif action == 'closed' and pr.get('merged'):
        # PR merged
        await handle_pr_merged(repository, pr)
        return {'action': 'pr_merged'}

    return {'action': action}

async def handle_issues_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle issues events"""
    action = payload.get('action')
    issue = payload['issue']
    number = issue['number']
    repository = payload['repository']['full_name']

    logger.info(f"Issue #{number} {action} in {repository}")

    if action == 'opened':
        # Auto-label based on title/body
        labels = await determine_issue_labels(issue)
        if labels:
            await add_labels(repository, number, labels)

        # Auto-assign based on labels
        assignees = await determine_assignees(labels)
        if assignees:
            await assign_issue(repository, number, assignees)

        return {'action': 'issue_labeled', 'labels': labels}

    return {'action': action}

async def handle_issue_comment_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle issue comment events"""
    action = payload.get('action')
    comment = payload['comment']
    issue = payload['issue']

    # Check for bot commands
    body = comment.get('body', '').strip()

    if body.startswith('/'):
        command = body.split()[0][1:]
        await execute_bot_command(command, issue, comment)
        return {'action': 'command_executed', 'command': command}

    return {'action': action}

async def handle_release_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle release events"""
    action = payload.get('action')
    release = payload['release']

    if action == 'published':
        tag = release['tag_name']
        logger.info(f"Release {tag} published")

        # Trigger production deployment
        await trigger_deployment(payload['repository']['full_name'], tag)

        # Notify team
        await notify_team_release(release)

        return {'action': 'release_deployed', 'tag': tag}

    return {'action': action}

async def handle_workflow_run_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle workflow_run events"""
    action = payload.get('action')
    workflow_run = payload['workflow_run']
    conclusion = workflow_run.get('conclusion')

    if action == 'completed' and conclusion == 'failure':
        # Workflow failed - notify team
        await notify_workflow_failure(workflow_run)

    return {'action': action, 'conclusion': conclusion}

async def handle_check_run_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle check_run events"""
    action = payload.get('action')
    check_run = payload['check_run']

    if action == 'completed' and check_run.get('conclusion') == 'failure':
        # Check failed - create issue if needed
        await handle_check_failure(check_run)

    return {'action': action}

async def handle_deployment_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle deployment events"""
    deployment = payload['deployment']
    environment = deployment.get('environment')

    logger.info(f"Deployment to {environment} requested")

    # Update deployment status
    await update_deployment_status(
        deployment['id'],
        'in_progress',
        f'Deploying to {environment}'
    )

    return {'action': 'deployment_started', 'environment': environment}

async def handle_deployment_status_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle deployment_status events"""
    deployment_status = payload['deployment_status']
    state = deployment_status['state']

    if state == 'success':
        # Deployment succeeded
        await notify_deployment_success(deployment_status)

    elif state == 'failure':
        # Deployment failed
        await notify_deployment_failure(deployment_status)

    return {'action': 'deployment_status', 'state': state}

async def handle_status_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle status events (commit status)"""
    state = payload['state']
    context = payload['context']

    logger.info(f"Status update: {context} = {state}")

    return {'action': 'status_updated', 'state': state}

async def handle_repository_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle repository events"""
    action = payload.get('action')
    repository = payload['repository']

    if action == 'created':
        # New repository created - setup CI/CD, branch protection, etc.
        await setup_repository(repository)

    return {'action': action}

async def handle_star_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle star events"""
    action = payload.get('action')

    if action == 'created':
        # New star - thank user, track analytics
        pass

    return {'action': action}

async def handle_watch_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle watch events"""
    action = payload.get('action')
    return {'action': action}

async def handle_fork_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle fork events"""
    forkee = payload['forkee']
    logger.info(f"Repository forked: {forkee['full_name']}")
    return {'action': 'forked'}

# Helper functions (stubs for demonstration)

async def trigger_deployment(repository: str, ref: str):
    """Trigger deployment for repository and ref"""
    logger.info(f"Triggering deployment for {repository}:{ref}")
    # Implementation: Call deployment API, trigger workflow, etc.

async def assign_reviewers(repository: str, pr_number: int):
    """Auto-assign reviewers to PR"""
    logger.info(f"Assigning reviewers to PR #{pr_number}")
    # Implementation: Use GitHub API to assign reviewers

async def auto_label_pr_size(repository: str, pr_number: int, additions: int, deletions: int):
    """Auto-label PR based on size"""
    total_changes = additions + deletions

    if total_changes < 10:
        label = 'size/XS'
    elif total_changes < 50:
        label = 'size/S'
    elif total_changes < 200:
        label = 'size/M'
    elif total_changes < 500:
        label = 'size/L'
    else:
        label = 'size/XL'

    logger.info(f"Adding label {label} to PR #{pr_number}")
    # Implementation: Use GitHub API to add label

async def handle_pr_merged(repository: str, pr: Dict[str, Any]):
    """Handle merged PR"""
    logger.info(f"PR #{pr['number']} merged")
    # Implementation: Update changelog, trigger deployment, etc.

async def determine_issue_labels(issue: Dict[str, Any]) -> list:
    """Determine labels for issue based on content"""
    labels = []
    title_lower = issue['title'].lower()
    body_lower = (issue.get('body') or '').lower()

    if 'bug' in title_lower or 'error' in title_lower:
        labels.append('bug')
    if 'feature' in title_lower or 'enhancement' in title_lower:
        labels.append('enhancement')
    if 'docs' in title_lower or 'documentation' in title_lower:
        labels.append('documentation')
    if 'urgent' in title_lower or 'critical' in body_lower:
        labels.append('priority:high')

    return labels

async def determine_assignees(labels: list) -> list:
    """Determine assignees based on labels"""
    # Implementation: Use label -> team mapping
    return []

async def add_labels(repository: str, issue_number: int, labels: list):
    """Add labels to issue"""
    logger.info(f"Adding labels {labels} to issue #{issue_number}")

async def assign_issue(repository: str, issue_number: int, assignees: list):
    """Assign issue to users"""
    logger.info(f"Assigning issue #{issue_number} to {assignees}")

async def execute_bot_command(command: str, issue: Dict[str, Any], comment: Dict[str, Any]):
    """Execute bot command from comment"""
    logger.info(f"Executing command: /{command}")
    # Implementation: Handle commands like /assign, /label, /close, etc.

async def notify_team_release(release: Dict[str, Any]):
    """Notify team of new release"""
    logger.info(f"Notifying team of release {release['tag_name']}")

async def notify_workflow_failure(workflow_run: Dict[str, Any]):
    """Notify team of workflow failure"""
    logger.error(f"Workflow {workflow_run['name']} failed")

async def handle_check_failure(check_run: Dict[str, Any]):
    """Handle check run failure"""
    logger.error(f"Check {check_run['name']} failed")

async def update_deployment_status(deployment_id: int, state: str, description: str):
    """Update deployment status"""
    logger.info(f"Updating deployment {deployment_id} status to {state}")

async def notify_deployment_success(deployment_status: Dict[str, Any]):
    """Notify team of successful deployment"""
    logger.info("Deployment succeeded")

async def notify_deployment_failure(deployment_status: Dict[str, Any]):
    """Notify team of failed deployment"""
    logger.error("Deployment failed")

async def setup_repository(repository: Dict[str, Any]):
    """Setup new repository with CI/CD, branch protection, etc."""
    logger.info(f"Setting up repository {repository['full_name']}")
```

### 2. Event Streaming to Message Queue

#### Redis Stream Integration
```python
# apps/webhook-server/event_stream.py
import redis
import json
from typing import Dict, Any

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

async def stream_event_to_redis(
    event_type: str,
    payload: Dict[str, Any],
    delivery_id: str
):
    """Stream GitHub webhook event to Redis Stream"""
    stream_key = f'github:events:{event_type}'

    event_data = {
        'delivery_id': delivery_id,
        'event_type': event_type,
        'payload': json.dumps(payload),
        'timestamp': int(time.time())
    }

    # Add to Redis Stream
    message_id = redis_client.xadd(stream_key, event_data, maxlen=10000)

    # Also publish to pub/sub for real-time consumers
    redis_client.publish(f'github:events', json.dumps({
        'stream': stream_key,
        'message_id': message_id,
        'event_type': event_type,
        'delivery_id': delivery_id
    }))

    return message_id

# Consumer example
def consume_github_events(event_type: str = '*'):
    """Consume GitHub events from Redis Stream"""
    stream_key = f'github:events:{event_type}'
    last_id = '0'

    while True:
        # Read new messages
        messages = redis_client.xread(
            {stream_key: last_id},
            count=10,
            block=5000
        )

        for stream, entries in messages:
            for message_id, data in entries:
                # Process event
                payload = json.loads(data['payload'])
                process_event(data['event_type'], payload)

                # Update last_id
                last_id = message_id
```

---

## ✅ Validation Criteria

### Webhook Security
- ✅ Signature verification on all requests
- ✅ Idempotency handling with delivery IDs
- ✅ Rate limiting per IP/installation
- ✅ HTTPS-only endpoints
- ✅ Request timeout < 10s response time

### Reliability
- ✅ Background processing for long-running tasks
- ✅ Retry logic with exponential backoff
- ✅ Dead letter queue for failed events
- ✅ Event deduplication
- ✅ Monitoring and alerting

---

## 🎯 Usage Examples

### Example 1: Deploy with Docker
```yaml
# docker-compose.yml
version: '3.8'

services:
  webhook-server:
    build: apps/webhook-server
    ports:
      - "8080:8080"
    environment:
      GITHUB_WEBHOOK_SECRET: ${GITHUB_WEBHOOK_SECRET}
      REDIS_HOST: redis
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  worker:
    build: apps/webhook-server
    command: python worker.py
    environment:
      REDIS_HOST: redis
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
```

---

## 📊 Success Metrics

### Performance
- **Response Time**: <200ms p95
- **Throughput**: 1000+ events/second
- **Processing Success Rate**: >99.9%

---

## 🔗 Related Skills
- `github-api-integration` - GitHub API
- `github-apps-development` - GitHub Apps

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
