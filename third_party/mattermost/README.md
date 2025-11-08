# Mattermost Integration Blueprint (InsightPulse)

This package turns Mattermost into an **integration hub** for InsightPulse:
- Installs/updates selected plugins from the Marketplace (GitHub, Metrics, User Survey)
- Provides an **Odoo webhook bridge** to ingest GitHub/Jira/ServiceNow events

## Prereqs
- Mattermost Base URL: `MM_BASE_URL` (e.g., https://chat.insightpulseai.net)
- Admin PAT: `MM_ADMIN_TOKEN` (create in Account Settings → Security → Personal Access Tokens)
- Marketplace must be enabled in System Console.

## Quickstart
```bash
# install plugins + health check
make mm-plugins
make mm-health

# install/upgrade Odoo webhook bridge module
make odoo-bridge-install
```

## Webhook Endpoints (Odoo)
```
POST /ipai/mattermost/github
POST /ipai/mattermost/jira
POST /ipai/mattermost/servicenow
```

Auth: set system parameter `ipai.mm_webhook_secret` to the shared secret; call with header:
```
X-IPAI-Webhook-Secret: <your-secret>
```

Payloads are logged to `ir.logging` and available for downstream automation.

## Notes
- The "Playbooks" and MS Teams Meetings plugins may require licenses/versions. Kept out by default.
- You can extend plugin list via `third_party/mattermost/plugins.yaml`.
