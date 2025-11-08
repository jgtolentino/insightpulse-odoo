# IPAI Mattermost Bridge

Lightweight webhook ingestion for GitHub/Jira/ServiceNow → Odoo.

## Routes
- `POST /ipai/mattermost/github`
- `POST /ipai/mattermost/jira`
- `POST /ipai/mattermost/servicenow`

## Authentication
Auth header:
```
X-IPAI-Webhook-Secret: <shared-secret>
```

Set secret in **Settings → Technical → System Parameters**:
```
Key: ipai.mm_webhook_secret
Value: <shared-secret>
```

## Logging
Logs appear in `Technical → Logging` and server logs under `ipai_mattermost_bridge`.
