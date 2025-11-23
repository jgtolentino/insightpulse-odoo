# Mattermost ↔ n8n ↔ Odoo/Supabase Integration Guide

## Overview
This integration enables Opex automation through Mattermost slash commands, connecting to n8n workflows that interact with Odoo and Supabase.

## Architecture
```
Mattermost → n8n Webhook → Odoo/Supabase APIs
     ↓
Slash Commands    Bot Responses    Async Notifications
```

## Prerequisites

### Mattermost Setup
- ✅ Mattermost running on port 8065
- ✅ Team Edition (no license required)
- ✅ Database connectivity established

### n8n Setup  
- n8n instance accessible at `n8n.insightpulseai.net`
- Existing Odoo/Supabase credentials configured
- Webhook endpoints enabled

## Step-by-Step Implementation

### 1. Mattermost Bot Account Setup

**Location**: System Console → Integrations → Bot Accounts

**Configuration**:
- Username: `opex-bot`
- Display name: `Opex Bot`
- Roles: Access to finance channels (Town Square, #finance, etc.)

**Important**: Store the Personal Access Token securely in n8n credentials.

### 2. Mattermost Slash Command Setup

**Location**: Integrations → Slash Commands → Add Slash Command

**Configuration**:
- **Title**: `Opex Command`
- **Command Trigger Word**: `/opex`
- **Request URL**: `https://n8n.insightpulseai.net/webhook/opex-command`
- **Request Method**: `POST`
- **Response Username**: `opex-bot`
- **Autocomplete**: Enabled
  - Hint: `[task|status|closing|help]`
  - Description: `Run Opex / month-end / BIR automations`

**Important**: Copy the generated Token for n8n verification.

### 3. n8n Workflow Structure

**Required Nodes**:

1. **Webhook Trigger**
   - Path: `opex-command`
   - HTTP Method: `POST`
   - Respond: "Last node in workflow"

2. **IF Node** (Token Validation)
   - Check `{{$json.token}}` matches Mattermost token
   - If false → Respond with 403 error

3. **Switch/Router Node** (Command Routing)
   - Route based on `{{$json.text}}`
   - Cases:
     - `status` → Get today's closing status
     - `closing` → List open monthly tasks
     - `help` / empty → Show usage help

4. **HTTP/Supabase/Odoo Nodes**
   - Use existing credentials to fetch data
   - Connect to Odoo expense APIs
   - Query Supabase for task status

5. **Function/Set Node**
   - Format Markdown response for Mattermost

6. **Respond to Webhook Node**
   - Mode: "Last node in workflow responds"
   - Body: JSON response

### 4. Response Format

```json
{
  "response_type": "ephemeral",
  "text": "Opex status for today:\\n• 3 tasks open\\n• 2 tasks blocked\\n• Next deadline: 1601-C (Nov 25)"
}
```

## CLI Management

### Backup Script
Use `n8n_opex_cli.sh` for workflow lifecycle management:

```bash
./n8n_opex_cli.sh
```

### Deployment Commands

**Export workflows**:
```bash
docker exec -u node n8n n8n export:workflow --all --output=workflows.json
```

**Import to target**:
```bash
docker exec -u node n8n n8n import:workflow --input=workflows.json
```

**Activate workflow**:
```bash
docker exec -u node n8n n8n update:workflow --id=WF_ID --active=true
docker restart n8n
```

## Async Notifications (Optional)

For long-running jobs:

1. **Mattermost Incoming Webhook**
   - Channel: `town-square` or `#finance`
   - Copy webhook URL

2. **n8n HTTP Request Node**
   - Method: POST
   - URL: `<incoming-webhook-url>`
   - Body: JSON notification

## Testing

### Mattermost Commands
```
/opex status
/opex closing
/opex help
```

### n8n Webhook Testing
```bash
curl -X POST https://n8n.insightpulseai.net/webhook/opex-command \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN", "text": "status"}'
```

## Troubleshooting

### Common Issues

1. **Mattermost connectivity**
   - Verify Mattermost is accessible at `https://chat.insightpulseai.net:8065`
   - Check database connectivity

2. **n8n webhook issues**
   - Verify n8n instance is running
   - Check webhook endpoint configuration
   - Validate token verification

3. **Odoo/Supabase connectivity**
   - Verify API credentials in n8n
   - Check network connectivity between services

### Monitoring
- Mattermost system logs
- n8n execution history
- Database connection health

## Security Considerations

- Store all tokens in n8n credentials (never in plain text)
- Use HTTPS for all webhook communications
- Implement proper token validation
- Restrict bot account permissions appropriately

## Next Steps

1. Implement the n8n workflow with existing Odoo/Supabase integrations
2. Test end-to-end functionality
3. Deploy to production environment
4. Monitor and optimize performance

---

**Last Updated**: 2025-11-21  
**Status**: Infrastructure stabilized, ready for integration implementation
