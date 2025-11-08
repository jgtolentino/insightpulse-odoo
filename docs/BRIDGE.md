# InsightPulse Odoo ⇄ Supabase Bridge

## Executive Summary

The Odoo-Supabase Event Bridge provides **bi-directional, HMAC-signed event synchronization** between Odoo ERP and Supabase. This enables real-time data flows, agent actions, and analytics integration while maintaining security and audit compliance.

**Key Benefits:**
- ✅ Real-time event streaming from Odoo to Supabase
- ✅ Remote action execution from Supabase to Odoo
- ✅ HMAC-SHA256 signed requests for security
- ✅ Row-Level Security (RLS) in Supabase
- ✅ Complete audit trail with correlation IDs
- ✅ FastAPI bridge for development and replay

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Odoo ERP (System of Record)                               │
│  ├─ ip_event_bus addon                                      │
│  ├─ /api/agent/event_push   (receives from Supabase)       │
│  └─ /api/agent/apply        (executes actions)             │
│                                                              │
└──────────────┬───────────────────────────┬───────────────────┘
               │ HMAC-signed               │ HMAC-signed
               │ webhooks                  │ action calls
               ▼                           ▼
┌──────────────────────────┐   ┌───────────────────────────────┐
│ Supabase Edge Functions  │   │  FastAPI Bridge (Optional)    │
│ ├─ odoo_event_ingest     │   │  ├─ /bridge/replay            │
│ └─ push_to_odoo          │   │  ├─ /bridge/apply             │
└──────────┬───────────────┘   │  └─ /bridge/event             │
           │                   └───────────────────────────────┘
           ▼
┌─────────────────────────────────────────────────────────────┐
│ Supabase PostgreSQL                                         │
│ ├─ audit_event (event log)                                 │
│ └─ odoo_action_outbox (pending actions)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Event Flow

### Odoo → Supabase (Event Ingestion)

1. **Odoo** fires a webhook on model change (create/update/delete)
2. Request is **HMAC-signed** with `EDGE_HMAC_SECRET`
3. **Supabase Edge Function** (`odoo_event_ingest`) receives:
   - Verifies HMAC signature
   - Inserts row into `audit_event` table
   - Emits Realtime message (optional)
4. **Downstream consumers** (Superset, agents, etc.) can subscribe to events

**Example Request:**
```bash
curl -X POST "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo_event_ingest" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "x-signature: <hmac-sha256>" \
  -H "content-type: application/json" \
  -d '{
    "event_type": "res.partner.updated",
    "resource_id": 42,
    "payload": {"name": "Acme Corp"}
  }'
```

---

### Supabase → Odoo (Action Execution)

1. **Supabase** (edge function, trigger, or external service) initiates action
2. Request is **HMAC-signed** with `EDGE_HMAC_SECRET`
3. **Odoo controller** (`/api/agent/apply`) receives:
   - Verifies API key (`x-api-key`)
   - Verifies HMAC signature (`x-signature`)
   - Executes action (e.g., post invoice, update partner)
4. Returns success/failure response

**Example Request:**
```bash
curl -X POST "https://erp.insightpulseai.net/api/agent/apply" \
  -H "x-api-key: $ODOO_API_TOKEN" \
  -H "x-signature: <hmac-sha256>" \
  -H "content-type: application/json" \
  -d '{
    "action": "account.move.post",
    "args": {"id": 1234}
  }'
```

---

## Security

### HMAC Signature Verification

All requests **MUST** include an `x-signature` header containing the HMAC-SHA256 of the raw request body:

```python
import hmac
import hashlib

def sign(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
```

**TypeScript (Deno):**
```typescript
async function hmac(content: string, secret: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(content)
  );
  return Array.from(new Uint8Array(sig))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}
```

### Environment Variables

#### Supabase (Edge Functions)
Set these in **Supabase Dashboard → Functions → Secrets**:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ODOO_BASE_URL`
- `ODOO_API_TOKEN`
- `EDGE_HMAC_SECRET`

#### Odoo (System Parameters)
Set these in **Settings → Technical → System Parameters**:
- `ip.hmac.secret` = `${EDGE_HMAC_SECRET}`
- `ip.odoo.api_key` = `${ODOO_API_TOKEN}`

---

## Database Schema

### audit_event

Stores all incoming events from Odoo and other sources:

| Column          | Type          | Description                           |
|-----------------|---------------|---------------------------------------|
| id              | bigserial     | Primary key                           |
| source          | text          | Event source: odoo/supabase/bridge    |
| event_type      | text          | Event type (e.g., res.partner.updated)|
| resource_id     | text          | Resource ID (e.g., partner ID)        |
| payload         | jsonb         | Event payload                         |
| correlation_id  | uuid          | Correlation ID for tracing            |
| created_at      | timestamptz   | Timestamp                             |

### odoo_action_outbox

Queue for actions to be executed in Odoo:

| Column          | Type          | Description                           |
|-----------------|---------------|---------------------------------------|
| id              | bigserial     | Primary key                           |
| action          | text          | Action name (e.g., account.move.post) |
| args            | jsonb         | Action arguments                      |
| status          | text          | queued/sent/applied/error             |
| last_error      | text          | Error message if status=error         |
| correlation_id  | uuid          | Correlation ID                        |
| created_at      | timestamptz   | Timestamp                             |
| applied_at      | timestamptz   | When action was applied               |

---

## Supported Actions

### account.move.post
Post an account move (invoice/bill):
```json
{
  "action": "account.move.post",
  "args": {"id": 1234}
}
```

### res.partner.update
Update partner record:
```json
{
  "action": "res.partner.update",
  "args": {
    "id": 42,
    "values": {"name": "New Name", "email": "new@example.com"}
  }
}
```

### Custom Actions
Extend `odoo_addons/ip_event_bus/controllers/event_bus.py` to add more actions.

---

## Replay & Debugging

### Using the FastAPI Bridge

The optional FastAPI bridge provides development endpoints:

**Replay an event:**
```bash
curl -X POST http://localhost:8787/bridge/replay \
  -H "x-signature: <hmac>" \
  -d '{"event_type": "test.event", "payload": {}}'
```

**Apply an action:**
```bash
curl -X POST http://localhost:8787/bridge/apply \
  -d '{"action": "account.move.post", "args": {"id": 1234}}'
```

---

## Deployment

### 1. Deploy Supabase Schema
```bash
make bridge-sql
# Or manually run: supabase/sql/000_init.sql
```

### 2. Deploy Edge Functions
```bash
supabase functions deploy odoo_event_ingest
supabase functions deploy push_to_odoo
```

### 3. Install Odoo Addon
```bash
# Copy addon to Odoo addons path
cp -r odoo_addons/ip_event_bus /path/to/odoo/addons/

# Restart Odoo
sudo systemctl restart odoo

# Install via UI: Apps → Search "InsightPulse Event Bus" → Install
```

### 4. Configure Secrets
- Set Supabase secrets in dashboard
- Set Odoo system parameters: `ip.hmac.secret`, `ip.odoo.api_key`

---

## Testing

### Test Odoo → Supabase
```bash
make bridge-ingest-test
```

### Test Supabase → Odoo
```bash
make bridge-push-test
```

### Test Bridge API
```bash
make bridge-up       # Start bridge
make bridge-test     # Run tests
make bridge-down     # Stop bridge
```

---

## Observability

### Audit Trail
Every event and action writes to:
- **Supabase:** `audit_event` table
- **Odoo:** `ir.logging` table

Query by `correlation_id` to trace end-to-end flows.

### Monitoring
- Check Supabase logs: Dashboard → Functions → Logs
- Check Odoo logs: `/var/log/odoo/odoo.log`

---

## Troubleshooting

### Invalid Signature
- Verify `EDGE_HMAC_SECRET` matches on both sides
- Ensure raw body is used for signature (not parsed JSON)
- Check for encoding issues (UTF-8)

### Action Not Found
- Verify action name in request matches controller code
- Check Odoo logs for detailed error messages

### RLS Policy Errors
- Ensure requests use `SUPABASE_SERVICE_ROLE_KEY`
- Check RLS policies in Supabase Dashboard

---

## References

- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [Odoo HTTP Controllers](https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html)
- [HMAC Security](https://en.wikipedia.org/wiki/HMAC)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-08
**Maintainer:** InsightPulse AI
